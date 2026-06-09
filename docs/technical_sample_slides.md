---
marp: true
title: Deal Screener Technical Sample
description: Professional technical sample slides for an AI-powered startup deal intelligence workbench.
theme: default
paginate: true
style: |
  section {
    background: #f8fafc;
    color: #102033;
    font-family: Inter, Aptos, Arial, sans-serif;
    letter-spacing: -0.01em;
  }
  h1 { color: #0f172a; font-size: 2.7rem; }
  h2 { color: #1f5eff; font-size: 1.35rem; text-transform: uppercase; letter-spacing: .08em; }
  strong { color: #0f172a; }
  table { font-size: 0.78rem; }
  th { background: #eaf1ff; color: #0f172a; }
  .lead { color: #5f6f85; font-size: 1.15rem; max-width: 780px; }
  .kicker { color: #1f5eff; font-size: .75rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
  .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
  .card { background: white; border: 1px solid #d9e2ec; border-radius: 18px; padding: 18px; box-shadow: 0 14px 35px rgba(16,32,51,.08); }
  .metric { font-size: 2.2rem; font-weight: 900; color: #1f5eff; }
  .muted { color: #5f6f85; }
---

<div class="kicker">Technical Sample</div>

# Deal Screener

<p class="lead">An AI-native deal intelligence workbench that converts unstructured pitch decks into source-aware investment memos, scoring rationale, and partner-ready recommendations.</p>

**Stack:** Python, Streamlit, Groq-hosted LLMs, Llama 4 Vision, PyMuPDF, DuckDuckGo, Google Trends, local JSON storage.

---

<div class="kicker">Problem</div>

# Early deal review is high-volume and evidence-poor

<div class="grid">
<div class="card">
<strong>Analyst bottleneck</strong><br />
Decks arrive faster than teams can parse, summarize, and compare them.
</div>
<div class="card">
<strong>Inconsistent artifacts</strong><br />
Slides mix text, images, screenshots, and ambiguous claims.
</div>
<div class="card">
<strong>Subjective scoring</strong><br />
First-pass recommendations vary by reviewer and context window.
</div>
<div class="card">
<strong>Weak audit trail</strong><br />
Investment claims often lack structured evidence and confidence markers.
</div>
</div>

---

<div class="kicker">Product</div>

# From pitch deck to investment memo

1. Upload a PDF or paste deck text.
2. Extract company, team, market, traction, product, and deal terms.
3. Enrich with public web and trends context.
4. Score the company against a configurable fund thesis.
5. Produce a recommendation, executive memo, diligence questions, and optional decline communication.
6. Save the record for historical pipeline analytics.

---

<div class="kicker">Architecture</div>

# Screening pipeline

```mermaid
flowchart LR
    A[Deck PDF or Manual Text] --> B[Layered Parser]
    B --> C[Company Extraction]
    C --> D[Research Enrichment]
    C --> E[Confidence Trace]
    D --> F[Scoring Engine]
    E --> F
    F --> G[Decision Policy]
    G --> H[Investment Workbench]
    G --> I[Deal History]
    G --> J[Report Export]
```

The pipeline is intentionally modular so each stage can become a specialized agent or independent service.

---

<div class="kicker">Implementation</div>

# Current technical depth

| Layer | Implementation |
|---|---|
| Interface | Streamlit multipage workbench with professional cards, tabs, and analytics |
| Parsing | PyMuPDF text, blocks, spans, and Llama 4 Vision fallback |
| Extraction | Structured LLM prompt for company, team, market, traction, risks, and confidence |
| Enrichment | DuckDuckGo web search and Google Trends sector momentum |
| Scoring | Weighted six-factor framework with configurable thresholds |
| Storage | Local JSON deal archive for rapid prototyping |

---

<div class="kicker">Scoring</div>

# Investment decision framework

| Criterion | Weight | Signal |
|---|---:|---|
| Team | 25% | Founder-market fit, domain expertise, completeness |
| Market | 20% | TAM, growth, timing, category pressure |
| Traction | 20% | Revenue, users, retention, customer quality |
| Product | 15% | Differentiation, defensibility, PMF evidence |
| Thesis Fit | 10% | Alignment with fund stage, sector, geography |
| Deal Terms | 10% | Valuation, round structure, ownership potential |

Decision policy: **Fast Track** at 7.5+, **Review** at 5.0-7.4, **Pass** below 5.0.

---

<div class="kicker">Open-Source Inspiration</div>

# What stronger AI products do well

<div class="grid">
<div class="card">
<strong>Dify-style workflows</strong><br />
Visual, inspectable steps with model, prompt, latency, and logs per node.
</div>
<div class="card">
<strong>LangGraph-style state</strong><br />
Graph execution, human review gates, retries, and persistent checkpoints.
</div>
<div class="card">
<strong>Kotaemon-style evidence</strong><br />
Source citations, PDF highlights, low-confidence warnings, and retrieval traces.
</div>
<div class="card">
<strong>OpenBB-style data layer</strong><br />
Standardized connectors that make public and proprietary data reusable.
</div>
</div>

---

<div class="kicker">Design Upgrade</div>

# Professional workbench experience

The UI now moves away from playful emoji labels and toward an enterprise analytics aesthetic:

- high-contrast dark navigation,
- clear hero sections,
- decision cards with semantic color rather than icons,
- score cards with progress bars,
- a visible pipeline trace,
- tabbed memo, extraction, research, confidence, and communication views,
- deal history analytics for pipeline review.

---

<div class="kicker">Reliability</div>

# Guardrails already in place

- Manual text fallback when PDF extraction fails.
- Multiple PDF extraction strategies before using vision models.
- Model rotation across Groq-hosted models for rate limits and failures.
- Score parsing fallbacks: strict regex, JSON block, permissive labels, and weighted composite calculation.
- Configurable fund thesis, scoring weights, and decision thresholds.
- Confidence trace for key extracted fields.

---

<div class="kicker">Next Build Phase</div>

# Make it sophisticated

1. Refactor orchestration into a graph of specialist diligence agents.
2. Store structured JSON claims with slide or URL evidence.
3. Add PDF preview with highlighted source snippets.
4. Add a benchmark dataset for extraction accuracy and score stability.
5. Replace local JSON with SQLite or Postgres.
6. Add FastAPI endpoints for programmatic screening.
7. Add observability: token cost, latency, model used, retry count, and failure reason.

---

<div class="kicker">Differentiation</div>

# Why this is more than an LLM wrapper

<div class="grid">
<div class="card"><div class="metric">1</div><strong>Workflow depth</strong><br /><span class="muted">Document AI, enrichment, scoring, memo generation, and archive.</span></div>
<div class="card"><div class="metric">2</div><strong>Investment framing</strong><br /><span class="muted">Outputs are designed around venture analyst and partner workflows.</span></div>
<div class="card"><div class="metric">3</div><strong>Explainability path</strong><br /><span class="muted">Confidence traces create a foundation for source-grounded diligence.</span></div>
<div class="card"><div class="metric">4</div><strong>Extensible architecture</strong><br /><span class="muted">Each stage can become a specialized agent, tool, or service.</span></div>
</div>

---

<div class="kicker">Talk Track</div>

# Suggested 3-minute walkthrough

1. **Problem:** early-stage teams need faster, more consistent first-pass review.
2. **Demo:** upload deck, inspect pipeline, review scorecard, open investment memo.
3. **Engineering:** explain layered parsing, prompt structure, enrichment, score extraction, and thresholds.
4. **Trust:** show confidence trace and discuss source-grounded next phase.
5. **Roadmap:** describe graph agents, evidence citations, evals, and persistent data layer.
