"""
Prompt templates for the screening workflow.
"""

EXTRACTION_PROMPT = """
You are an investment deal screener. Extract the following information from this pitch deck text.
If information is not found, say "Not mentioned".

PITCH DECK TEXT:
{deck_text}

Extract and return a structured analysis in this EXACT format:

## Company Overview
- **Company Name:** 
- **One-Line Description:** 
- **Sector/Industry:** 
- **Stage:** (Pre-Seed / Seed / Series A / etc.)
- **Location:** 
- **Founded:** 

## Problem & Solution
- **Problem:** (2-3 sentences)
- **Solution:** (2-3 sentences)

## Business Model
- **Revenue Model:** (SaaS, Marketplace, Transaction fee, etc.)
- **Pricing:** (if mentioned)

## Traction & Metrics
- **Revenue:** (ARR/MRR if mentioned)
- **Users/Customers:** 
- **Growth Rate:** 
- **Key Metrics:** (any other notable metrics)

## Team
- **Founders:** (names and brief backgrounds)
- **Team Size:** 
- **Notable Experience:** (previous exits, FAANG, domain expertise)

## Market
- **TAM:** 
- **Target Customer:** 
- **Competitors Mentioned:** 

## Fundraising
- **Amount Raising:** 
- **Valuation:** (if mentioned)
- **Use of Funds:** 
- **Previous Funding:** 

## Initial Red Flags
- List any concerns or missing information

## Initial Green Flags
- List any strong positive signals

## Confidence & Source Trace
- **Company Name:** [High/Medium/Low] | Source: [Deck/Enrichment/Inference] | Note: (1 short sentence)
- **Sector/Industry:** [High/Medium/Low] | Source: [Deck/Enrichment/Inference] | Note: (1 short sentence)
- **Stage:** [High/Medium/Low] | Source: [Deck/Enrichment/Inference] | Note: (1 short sentence)
- **Revenue:** [High/Medium/Low] | Source: [Deck/Enrichment/Inference] | Note: (1 short sentence)
- **Users/Customers:** [High/Medium/Low] | Source: [Deck/Enrichment/Inference] | Note: (1 short sentence)
- **Founders:** [High/Medium/Low] | Source: [Deck/Enrichment/Inference] | Note: (1 short sentence)
- **TAM:** [High/Medium/Low] | Source: [Deck/Enrichment/Inference] | Note: (1 short sentence)
- **Amount Raising:** [High/Medium/Low] | Source: [Deck/Enrichment/Inference] | Note: (1 short sentence)
- **Valuation:** [High/Medium/Low] | Source: [Deck/Enrichment/Inference] | Note: (1 short sentence)
"""

SCORING_PROMPT = """
You are a senior investment deal screener at a fund with this thesis: {fund_thesis}

Based on the following company analysis, provide a detailed scoring.

COMPANY ANALYSIS:
{company_analysis}

ADDITIONAL CONTEXT:
{enrichment_data}

Score each category from 1-10 and provide brief justification.

Return your analysis in this EXACT format:

## SCORES

### Team Score: X/10
**Justification:** (2-3 sentences on founder quality, experience, completeness)

### Market Score: X/10
**Justification:** (2-3 sentences on market size, timing, dynamics)

### Traction Score: X/10  
**Justification:** (2-3 sentences on current traction and growth signals)

### Product Score: X/10
**Justification:** (2-3 sentences on differentiation, defensibility, PMF signals)

### Thesis Fit Score: X/10
**Justification:** (2-3 sentences on alignment with fund thesis)

### Deal Terms Score: X/10
**Justification:** (2-3 sentences on valuation, round structure reasonableness)

## COMPOSITE SCORE: X.X/10
(Weighted average based on: Team 25%, Market 20%, Traction 20%, Product 15%, Thesis Fit 10%, Deal Terms 10%)

## MACHINE READABLE SCORES (JSON)
```json
{
  "team": X,
  "market": X,
  "traction": X,
  "product": X,
  "thesis_fit": X,
  "deal_terms": X,
  "composite": X.X
}
```

## KEY RISKS
1. 
2. 
3. 

## KEY STRENGTHS
1. 
2. 
3. 

## QUESTIONS FOR FOUNDERS
1. 
2. 
3. 
4. 
5. 

## RECOMMENDATION
FAST TRACK / REVIEW / PASS

**Reasoning:** (3-4 sentences on overall recommendation)

## COMPARABLE COMPANIES
List 3-5 similar companies that have raised funding or exited, with brief comparison.
"""

DECLINE_EMAIL_PROMPT = """
Write a polite, professional decline email for a startup pitch.

Company Name: {company_name}
Key Reason for Pass: {pass_reason}

The email should:
- Be warm and respectful
- Thank them for sharing
- Give a brief, honest reason (without being harsh)
- Leave the door open for future
- Be concise (under 150 words)

Write the email:
"""

SUMMARY_PROMPT = """
Based on this full analysis, write a concise 3-paragraph executive summary 
suitable for sharing in a Slack message to partners.

FULL ANALYSIS:
{full_analysis}

Format:
**[Company Name] - [One liner]**

Paragraph 1: What they do and why it matters
Paragraph 2: Key metrics and traction highlights  
Paragraph 3: Recommendation and key risks

Keep it under 200 words total.
"""
