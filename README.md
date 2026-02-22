# 🏦 VC Analyst Intern Agent

An AI-powered deal screening tool that analyzes startup pitch decks and provides instant investment recommendations.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 What It Does

Upload any startup pitch deck (PDF) and get:

- **📄 Smart PDF Parsing** — Reads both text-based and image-based decks using Llama 4 Vision
- **🔍 Company Extraction** — Automatically extracts team, traction, market, business model info
- **🌐 Web Enrichment** — Researches the company online via DuckDuckGo and Google Trends
- **📊 Scoring** — Scores deals on 6 criteria (Team, Market, Traction, Product, Thesis Fit, Deal Terms)
- **🚦 Decision** — Makes Fast Track 🟢 / Review 🟡 / Pass 🔴 recommendations
- **📝 Summary** — Writes executive summaries for partner meetings
- **✉️ Decline Emails** — Auto-generates polite decline emails for passed deals
- **📁 Deal History** — Tracks all screened deals with scores and decisions
- **📥 Reports** — Downloadable markdown reports

## 📸 Screenshots

### Deal Screening
Upload a deck → Get instant analysis

### Score Breakdown
6-criteria scoring with color-coded indicators

### Deal History
Track all your screened deals over time

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **LLM** | Groq (Llama 4 Scout, GPT-OSS-120B, Kimi K2, Qwen3) |
| **Vision AI** | Llama 4 Scout & Maverick (for image PDFs) |
| **PDF Parsing** | PyMuPDF (4 extraction methods) |
| **Web Research** | DuckDuckGo, Google Trends |
| **Storage** | Local JSON |
| **Cost** | 100% Free |