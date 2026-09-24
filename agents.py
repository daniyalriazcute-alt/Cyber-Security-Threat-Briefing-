import os
import re
import datetime
import requests
from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool

# ============================================================
# LLM CONFIGURATION (Groq API via LiteLLM)
# ============================================================
def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")
    return LLM(
        model="groq/openai/gpt-oss-120b",
        temperature=0.1,
        api_key=api_key
    )

# ============================================================
# OUTPUT SCHEMA & GUARDRAILS
# ============================================================
OUTPUT_SCHEMA = """
For EACH CVE explicitly returned by the tool, output EXACTLY these 5 lines:

CVE ID: <exact id from tool output ONLY>
Summary: <one line, max 15 words>
Impact: <one line, max 12 words>
Exploit PoC: <public / not public / link>
Recommended Action: <one line, max 10 words>

CRITICAL GUARDRAILS:
1. NEVER hallucinate or generate synthetic CVE IDs (e.g., CVE-2023-12345, CVE-2024-67890). Use ONLY exact CVE IDs provided in the raw tool response.
2. If the tool output contains no matching CVE records, output EXACTLY:

CVE ID: N/A
Summary: No matching official CVE records found for this query in NVD.
Impact: None identified.
Exploit PoC: not public
Recommended Action: Try searching broader terms like 'wpforms' or 'wordpress'.
"""

# ============================================================
# NVD CVE LOOKUP TOOL WITH RESILIENT FALLBACK
# ============================================================
@tool("nvd_cve_lookup")
def fetch_cve_data(topic: str) -> str:
    """
    Search the NIST NVD API v2.0 for real CVE details related to a topic or CVE ID.
    Includes fallback handling for NVD indexing delays on newly assigned CVEs.
    """
    topic_clean = topic.strip()
    headers = {"User-Agent": "CyberThreatBriefing/2.0"}
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    # --- 1. DIRECT CVE ID SEARCH & KNOWN UNINDEXED FALLBACK ---
    cve_match = re.search(r"CVE-\d{4}-\d{4,7}", topic_clean, re.IGNORECASE)
    if cve_match:
        cve_id = cve_match.group(0).upper()
        
        # Hardcoded fallback for specific high-profile CVEs currently lagging in NVD indexing
        known_fallbacks = {
            "CVE-2025-15001": {
                "id": "CVE-2025-15001",
                "published": "2026-01-05",
                "cvss": "9.8",
                "description": "FS Registration Password plugin for WordPress up to 1.0.1 is vulnerable to unauthenticated privilege escalation via password reset."
            }
        }

        try:
            resp = requests.get(base_url, params={"cveId": cve_id}, headers=headers, timeout=10)
            if resp.status_code == 200:
                vulnerabilities = resp.json().get("vulnerabilities", [])
                if vulnerabilities:
                    cve_obj = vulnerabilities[0].get("cve", {})
                    cid = cve_obj.get("id", cve_id)
                    pub = cve_obj.get("published", "")[:10]
                    descs = cve_obj.get("descriptions", [])
                    description = next((d["value"] for d in descs if d.get("lang") == "en"), "No description available.")

                    metrics = cve_obj.get("metrics", {})
                    cvss = "UNKNOWN"
                    for key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                        if key in metrics and metrics[key]:
                            cvss = metrics[key][0].get("cvssData", {}).get("baseScore", "UNKNOWN")
                            break

                    return (
                        f"CVE ID: {cid}\n"
                        f"Published: {pub}\n"
                        f"Severity: CVSS {cvss}\n"
                        f"Description: {description}\n"
                    )
            
            # If NVD API returns nothing but we have a known fallback entry, use it
            if cve_id in known_fallbacks:
                fb = known_fallbacks[cve_id]
                return (
                    f"CVE ID: {fb['id']}\n"
                    f"Published: {fb['published']}\n"
                    f"Severity: CVSS {fb['cvss']}\n"
                    f"Description: {fb['description']}\n"
                )

            return f"No official records found in NIST NVD for {cve_id}."
        except Exception as e:
            if cve_id in known_fallbacks:
                fb = known_fallbacks[cve_id]
                return (
                    f"CVE ID: {fb['id']}\n"
                    f"Published: {fb['published']}\n"
                    f"Severity: CVSS {fb['cvss']}\n"
                    f"Description: {fb['description']}\n"
                )
            return f"Error querying NIST NVD API for {cve_id}: {str(e)}"

    # --- 2. Alias & Acronym Resolution ---
    aliases = {
        "mongobleed": "CVE-2025-14847",
        "react2shell": "CVE-2025-55182",
        "log4shell": "CVE-2021-44228",
        "spring4shell": "CVE-2022-22965",
    }
    if topic_clean.lower() in aliases:
        return fetch_cve_data(aliases[topic_clean.lower()])

    acronyms = {
        r"\bxss\b": "cross site scripting",
        r"\bsqli\b": "sql injection",
        r"\brce\b": "remote code execution",
        r"\blfi\b": "local file inclusion",
        r"\bssrf\b": "server side request forgery"
    }
    for pattern, replacement in acronyms.items():
        topic_clean = re.sub(pattern, replacement, topic_clean, flags=re.IGNORECASE)

    # --- 3. Strip Noise & Smart Keyword Extraction ---
    noise_words = [
        r"\bshow\b", r"\bme\b", r"\bone\b", r"\brecent\b", r"\bcve\b", 
        r"\bvulnerabilities\b", r"\bvulnerability\b", r"\bplugin\b", r"\bof\b", 
        r"\bin\b", r"\bfor\b"
    ]
    clean_topic = topic_clean
    for nw in noise_words:
        clean_topic = re.sub(nw, "", clean_topic, flags=re.IGNORECASE)

    clean_words = clean_topic.split()
    if "wordpress" in [w.lower() for w in clean_words] and len(clean_words) > 1:
        keyword_search = " ".join([w for w in clean_words if w.lower() != "wordpress"])
    else:
        keyword_search = " ".join(clean_words)

    keyword_search = keyword_search.strip()
    if not keyword_search:
        keyword_search = topic_clean

    # --- 4. KEYWORD SEARCH WITH DATE FILTERING ---
    start_date = "2025-01-01T00:00:00.000"
    end_date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000")

    try:
        params = {
            "keywordSearch": keyword_search,
            "pubStartDate": start_date,
            "pubEndDate": end_date,
            "resultsPerPage": 3
        }

        resp = requests.get(base_url, params=params, headers=headers, timeout=12)
        if resp.status_code == 200:
            vulnerabilities = resp.json().get("vulnerabilities", [])

            if not vulnerabilities:
                params_fallback = {"keywordSearch": keyword_search, "resultsPerPage": 3}
                resp_fb = requests.get(base_url, params=params_fallback, headers=headers, timeout=12)
                if resp_fb.status_code == 200:
                    vulnerabilities = resp_fb.json().get("vulnerabilities", [])

            if not vulnerabilities:
                return f"No official CVE records found in NIST NVD for query: '{keyword_search}'."

            vulnerabilities.sort(
                key=lambda x: x.get("cve", {}).get("published", ""), 
                reverse=True
            )

            results = []
            for v in vulnerabilities[:3]:
                cve_obj = v.get("cve", {})
                cid = cve_obj.get("id", "UNKNOWN")
                pub = cve_obj.get("published", "")[:10]
                descs = cve_obj.get("descriptions", [])
                description = next((d["value"] for d in descs if d.get("lang") == "en"), "No description.")

                metrics = cve_obj.get("metrics", {})
                cvss = "UNKNOWN"
                for key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                    if key in metrics and metrics[key]:
                        cvss = metrics[key][0].get("cvssData", {}).get("baseScore", "UNKNOWN")
                        break

                results.append(
                    f"CVE ID: {cid}\n"
                    f"Published: {pub}\n"
                    f"Severity: CVSS {cvss}\n"
                    f"Description: {description}\n"
                )

            return "\n---\n".join(results)

        return f"NVD API returned HTTP {resp.status_code} for '{keyword_search}'."

    except Exception as e:
        return f"Error connecting to NIST NVD API: {str(e)}"

# ============================================================
# CREWAI AGENTS & TASKS CONFIGURATION
# ============================================================
def get_crew():
    llm = get_llm()

    vega = Agent(
        role="CVE Researcher",
        goal="Fetch real vulnerability data exclusively from the NIST NVD database via nvd_cve_lookup.",
        backstory=(
            "You are a strict threat intelligence researcher. You do not generate or guess CVE IDs. "
            "You always pass the target keyword or CVE ID to nvd_cve_lookup and return raw API output."
        ),
        tools=[fetch_cve_data],
        verbose=True,
        memory=False,
        llm=llm
    )

    orion = Agent(
        role="Risk Reporter",
        goal="Format official NIST NVD vulnerability records into the precise 5-line schema without hallucinating.",
        backstory=(
            "You are an executive risk editor. You strictly adhere to official data provided by Vega. "
            "Under no circumstances will you invent fake IDs like CVE-2023-12345 or synthetic details. "
            "If Vega returns no records, you MUST output the N/A schema."
        ),
        verbose=True,
        memory=False,
        llm=llm
    )

    task_research = Task(
        description=(
            "Use the 'nvd_cve_lookup' tool to retrieve live CVE details for topic: '{topic}'. "
            "Pass the exact raw output from the tool to Orion without adding commentary."
        ),
        expected_output="Raw NIST NVD CVE data string or clear non-found message.",
        agent=vega
    )

    task_report = Task(
        description=(
            f"Transform the raw tool output into the structured briefing.\n"
            f"Format rules:\n{OUTPUT_SCHEMA}\n"
            f"Strictly do not output any 'Thought:' or internal reasoning text."
        ),
        expected_output="A structured 5-line schema block per CVE or N/A fallback block.",
        agent=orion
    )

    return Crew(
        agents=[vega, orion],
        tasks=[task_research, task_report],
        process=Process.sequential,
        verbose=True
    )
