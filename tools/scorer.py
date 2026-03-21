"""
Scoring engine using Groq (free, fast, generous limits).
"""

import os
import time
import json
import re
from groq import Groq
from dotenv import load_dotenv
from settings_store import load_settings

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_KEY:
    print("❌ No GROQ_API_KEY found in .env file!")
else:
    print(f"✅ Groq configured (key ends in ...{GROQ_KEY[-4:]})")

client = None
if GROQ_KEY:
    client = Groq(api_key=GROQ_KEY)

# Models to rotate if one gets rate limited
MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "openai/gpt-oss-120b",
    "moonshotai/kimi-k2-instruct",
    "qwen/qwen3-32b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]


def get_llm_response(prompt: str) -> str:
    """
    Send prompt to Groq with automatic model rotation.
    """
    if not client:
        return "ERROR: No GROQ_API_KEY found. Add it to your .env file."

    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert investment deal screener at a top venture capital firm. Be thorough, precise, and data-driven in your analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4096
            )
            result = response.choices[0].message.content
            print(f"✅ Groq ({model}) responded")
            return result

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                print(f"⚠️ {model} rate limited, trying next...")
                time.sleep(2)
            else:
                print(f"❌ {model} error: {error_msg}")
                continue

    return "ERROR: All models rate limited. Please wait a moment and try again."


def extract_scores_from_text(scoring_text: str) -> dict:
    """
    Parse the LLM scoring response to extract numerical scores.
    """
    scores = {
        "team": 0,
        "market": 0,
        "traction": 0,
        "product": 0,
        "thesis_fit": 0,
        "deal_terms": 0,
        "composite": 0
    }

    patterns = {
        "team": r"Team Score:\s*(\d+\.?\d*)\s*/\s*10",
        "market": r"Market Score:\s*(\d+\.?\d*)\s*/\s*10",
        "traction": r"Traction Score:\s*(\d+\.?\d*)\s*/\s*10",
        "product": r"Product Score:\s*(\d+\.?\d*)\s*/\s*10",
        "thesis_fit": r"Thesis Fit Score:\s*(\d+\.?\d*)\s*/\s*10",
        "deal_terms": r"Deal Terms Score:\s*(\d+\.?\d*)\s*/\s*10",
        "composite": r"COMPOSITE SCORE:\s*(\d+\.?\d*)\s*/\s*10"
    }

    for key, pattern in patterns.items():
        scores[key] = _extract_score_with_pattern(scoring_text, pattern)

    # Fallback 1: JSON block
    if _missing_score_count(scores) >= 3:
        json_scores = _extract_scores_from_json_block(scoring_text)
        for key, value in json_scores.items():
            if key in scores and scores[key] == 0:
                scores[key] = value

    # Fallback 2: permissive label parsing
    if _missing_score_count(scores) >= 2:
        label_patterns = {
            "team": [r"team"],
            "market": [r"market"],
            "traction": [r"traction"],
            "product": [r"product"],
            "thesis_fit": [r"thesis\s*fit", r"thesis"],
            "deal_terms": [r"deal\s*terms?", r"terms"],
            "composite": [r"composite"],
        }
        for key, aliases in label_patterns.items():
            if scores[key] == 0:
                scores[key] = _extract_score_by_aliases(scoring_text, aliases)

    if scores["composite"] == 0:
        settings = load_settings()
        weights = {
            key: value.get("weight", 0)
            for key, value in settings["scoring_criteria"].items()
        }
        weighted_sum = sum(scores[k] * weights[k] for k in weights)
        scores["composite"] = round(weighted_sum, 1)

    return _validate_and_normalize_scores(scores)


def _extract_score_with_pattern(text: str, pattern: str) -> float:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return 0
    try:
        return float(match.group(1))
    except (TypeError, ValueError):
        return 0


def _extract_scores_from_json_block(text: str) -> dict:
    block_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.IGNORECASE | re.DOTALL)
    if not block_match:
        return {}
    try:
        parsed = json.loads(block_match.group(1))
    except json.JSONDecodeError:
        return {}

    return {
        key: _to_float(parsed.get(key, 0))
        for key in ["team", "market", "traction", "product", "thesis_fit", "deal_terms", "composite"]
    }


def _extract_score_by_aliases(text: str, aliases: list[str]) -> float:
    for alias in aliases:
        pattern = rf"{alias}[^\n:]*[:\-]?\s*(\d+\.?\d*)\s*/?\s*10"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return _to_float(match.group(1))
    return 0


def _to_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


def _missing_score_count(scores: dict) -> int:
    return sum(1 for key, value in scores.items() if key != "composite" and value == 0)


def _validate_and_normalize_scores(scores: dict) -> dict:
    cleaned = {}
    for key, value in scores.items():
        numeric = _to_float(value)
        cleaned[key] = max(0, min(10, round(numeric, 1)))
    return cleaned


def get_decision(composite_score: float) -> dict:
    """
    Determine pass/review/fast-track based on composite score.
    """
    thresholds = load_settings()["thresholds"]
    if composite_score >= float(thresholds["fast_track"]):
        return {
            "decision": "🟢 FAST TRACK",
            "action": "Schedule partner meeting immediately",
            "color": "green"
        }
    elif composite_score >= float(thresholds["review"]):
        return {
            "decision": "🟡 REVIEW",
            "action": "Add to weekly review queue",
            "color": "orange"
        }
    else:
        return {
            "decision": "🔴 PASS",
            "action": "Send polite decline email",
            "color": "red"
        }


def generate_decline_email(company_name: str, pass_reason: str) -> str:
    """
    Generate a polite decline email for passed deals.
    """
    from prompts.screening import DECLINE_EMAIL_PROMPT

    prompt = DECLINE_EMAIL_PROMPT.format(
        company_name=company_name,
        pass_reason=pass_reason
    )

    return get_llm_response(prompt)
