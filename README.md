# Deal Screener

An AI-powered deal intelligence workbench that analyzes startup pitch decks and produces structured investment recommendations.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## What It Does

Upload any startup pitch deck (PDF) and get:

- **Smart PDF Parsing** - Reads both text-based and image-based decks using Llama 4 Vision.
- **Company Extraction** - Automatically extracts team, traction, market, and business model information.
- **Web Enrichment** - Researches the company online via DuckDuckGo and Google Trends.
- **Structured Scoring** - Scores deals on six criteria: Team, Market, Traction, Product, Thesis Fit, and Deal Terms.
- **Investment Recommendation** - Produces Fast Track, Review, or Pass recommendations.
- **Executive Summary** - Writes partner-ready investment summaries.
- **Decline Email Drafting** - Generates concise, professional decline emails for passed deals.
- **Deal History** - Tracks screened deals with scores and decisions.
- **Report Export** - Downloads markdown reports for sharing or archiving.

## Product Experience

The current interface uses a professional investment-workbench layout with:

- a dark enterprise-style sidebar,
- a high-contrast hero section,
- card-based score and decision summaries,
- a visible screening pipeline,
- tabbed analysis views for memo, extraction, scoring, research, confidence, and communications,
- deal history analytics and configurable fund settings.

## Fellowship Technical Sample Slides

A simple presentation deck for fellowship applications is available at [`docs/fellowship_technical_sample_slides.md`](docs/fellowship_technical_sample_slides.md). It is written in Markdown/Marp format so it can be previewed as slides or copied into Google Slides/PowerPoint.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **LLM** | Groq (Llama 4 Scout, GPT-OSS-120B, Kimi K2, Qwen3) |
| **Vision AI** | Llama 4 Scout & Maverick for image PDFs |
| **PDF Parsing** | PyMuPDF with multiple extraction methods |
| **Web Research** | DuckDuckGo, Google Trends |
| **Storage** | Local JSON |
| **Cost** | 100% free infrastructure path |
