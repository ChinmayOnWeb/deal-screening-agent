"""
Main screening agent that orchestrates the entire
deal screening workflow.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from tools.deck_parser import extract_text_from_pdf, extract_key_fields
from tools.enrichment import enrich_company, format_enrichment_for_llm
from tools.scorer import get_llm_response, extract_scores_from_text, get_decision, generate_decline_email
from prompts.screening import EXTRACTION_PROMPT, SCORING_PROMPT, SUMMARY_PROMPT
from config import FUND_CONFIG

# Load .env from the project root directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class DealScreener:
    """
    Orchestrates the full deal screening pipeline:
    PDF → Parse → Extract → Enrich → Score → Decision
    """

    def __init__(self):
        self.fund_config = FUND_CONFIG

    def screen_deal(self, uploaded_file, manual_text=None, progress_callback=None) -> dict:
        """
        Run the full screening pipeline on an uploaded pitch deck.

        Args:
            uploaded_file: Streamlit uploaded file object
            manual_text: Optional manually pasted text
            progress_callback: Optional function to update progress

        Returns:
            Dictionary with all screening results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "status": "processing",
            "stages": {}
        }

        # ── Stage 1: Parse PDF ──────────────────────────────
        if progress_callback:
            progress_callback("📄 Parsing pitch deck... (image decks take ~1-2 min)", 10)

        # Use manual text if provided, otherwise parse PDF
        if manual_text:
            deck_text = manual_text
            print("✅ Using manually provided text")
        elif uploaded_file:
            deck_text = extract_text_from_pdf(uploaded_file)
        else:
            results["status"] = "error"
            results["error"] = "No input provided"
            return results

        if deck_text.startswith("ERROR"):
            results["status"] = "error"
            results["error"] = deck_text
            return results

        key_fields = extract_key_fields(deck_text)
        results["stages"]["parsing"] = {
            "deck_text_length": len(deck_text),
            "key_fields": key_fields
        }

        # ── Stage 2: LLM Extraction ────────────────────────
        if progress_callback:
            progress_callback("🔍 Extracting company information...", 30)

        extraction_prompt = EXTRACTION_PROMPT.format(deck_text=deck_text[:15000])
        company_analysis = get_llm_response(extraction_prompt)

        if company_analysis.startswith("ERROR"):
            results["status"] = "error"
            results["error"] = company_analysis
            return results

        results["stages"]["extraction"] = company_analysis

        # ── Stage 3: Extract company name for enrichment ────
        company_name = self._extract_company_name(company_analysis)
        sector = self._extract_sector(company_analysis)
        results["company_name"] = company_name
        results["sector"] = sector

        # ── Stage 4: Web Enrichment ─────────────────────────
        if progress_callback:
            progress_callback("🌐 Researching company online...", 50)

        try:
            enrichment_data = enrich_company(company_name, sector)
            enrichment_text = format_enrichment_for_llm(enrichment_data)
            results["stages"]["enrichment"] = enrichment_text
        except Exception as e:
            enrichment_text = f"Enrichment failed: {str(e)}"
            results["stages"]["enrichment"] = enrichment_text

        # ── Stage 5: Scoring ────────────────────────────────
        if progress_callback:
            progress_callback("📊 Scoring deal...", 70)

        scoring_prompt = SCORING_PROMPT.format(
            fund_thesis=self.fund_config["thesis"],
            company_analysis=company_analysis,
            enrichment_data=enrichment_text
        )
        scoring_response = get_llm_response(scoring_prompt)

        scores = extract_scores_from_text(scoring_response)
        decision = get_decision(scores["composite"])

        results["stages"]["scoring"] = scoring_response
        results["scores"] = scores
        results["decision"] = decision

        # ── Stage 6: Executive Summary ──────────────────────
        if progress_callback:
            progress_callback("📝 Writing summary...", 90)

        summary_prompt = SUMMARY_PROMPT.format(
            full_analysis=f"{company_analysis}\n\n{scoring_response}"
        )
        summary = get_llm_response(summary_prompt)
        results["stages"]["summary"] = summary

        # ── Stage 7: Decline Email (if pass) ────────────────
        if decision["color"] == "red":
            if progress_callback:
                progress_callback("✉️ Drafting decline email...", 95)

            decline_email = generate_decline_email(
                company_name=company_name,
                pass_reason="Does not meet current investment criteria"
            )
            results["stages"]["decline_email"] = decline_email

        # ── Done ────────────────────────────────────────────
        results["status"] = "complete"
        if progress_callback:
            progress_callback("✅ Screening complete!", 100)

        # Save to local database
        self._save_deal(results)

        return results

    def _extract_company_name(self, analysis: str) -> str:
        """Extract company name from LLM analysis."""
        import re
        match = re.search(
            r"\*\*Company Name:\*\*\s*(.+)",
            analysis
        )
        if match:
            name = match.group(1).strip()
            name = name.replace("*", "").strip()
            return name
        return "Unknown Company"

    def _extract_sector(self, analysis: str) -> str:
        """Extract sector from LLM analysis."""
        import re
        match = re.search(
            r"\*\*Sector/Industry:\*\*\s*(.+)",
            analysis
        )
        if match:
            return match.group(1).strip().replace("*", "").strip()
        return ""

    def _save_deal(self, results: dict) -> None:
        """Save screening results to local JSON file."""
        try:
            deals_file = "data/deals.json"

            if os.path.exists(deals_file):
                with open(deals_file, "r") as f:
                    deals = json.load(f)
            else:
                deals = []

            deal_record = {
                "timestamp": results["timestamp"],
                "company_name": results.get("company_name", "Unknown"),
                "sector": results.get("sector", "Unknown"),
                "scores": results.get("scores", {}),
                "decision": results.get("decision", {}).get("decision", "Unknown"),
                "status": results["status"]
            }

            deals.append(deal_record)

            with open(deals_file, "w") as f:
                json.dump(deals, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save deal - {str(e)}")