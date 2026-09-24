# 🛡️ Cyber Threat Briefing

> A multi-agent AI system that automatically researches the latest CVEs and generates executive-level threat briefings in plain language.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)](https://streamlit.io/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.20+-orange.svg)](https://www.crewai.com/)
[![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.3%2070B-purple.svg)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)

---

## 📖 Overview

**Cyber Threat Briefing** is a demonstration of a collaborative AI agent workflow built to solve a real-world cybersecurity problem: the gap between **raw vulnerability data** (from sources like NVD) and **actionable business intelligence** for decision-makers.

Two specialized AI agents work in sequence:

1.  🔍 **Vega — CVE Researcher:** Queries vulnerability databases to identify high-severity CVEs, extracting CVE IDs, CVSS scores, and exploit status.
2.  📝 **Orion — Risk Reporter:** Consumes the researcher's findings and translates them into a concise, plain-language briefing suitable for a CISO or non-technical executive.

The system combines **long-term memory (ChromaDB)**, **secure authentication (SQLite + bcrypt)**, and **OWASP LLM Top 10 (2025) guardrails** into a single, deployable Streamlit application.

---

## ✨ Key Features

| Category | Feature |
| :--- | :--- |
| **AI Agents** | Two collaborating agents (Researcher → Reporter) powered by **CrewAI** |
| **LLM Backend** | **Groq's `openai/gpt-oss-120b`** — free, fast, and OpenAI-compatible |
| **Long-Term Memory** | **ChromaDB** persistent vector store for cross-session context |
| **Authentication** | Secure **SQLite + bcrypt** login/registration system |
| **UI** | Professional **Streamlit** dashboard with **Dark/Light mode** toggle |
| **Security** | OWASP LLM Top 10 (2025) compliant system prompts |
| **Reliability** | Hard iteration limit (`max_iter=2`) to prevent runaway agent loops |
| **UX** | End Chat & Clear Memory functionality for session hygiene |
| **Output** | Concise, token-efficient briefings (max ~150 words) |

---

## 🧠 System Architecture
