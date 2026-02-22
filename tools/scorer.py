"""
Scoring engine using Groq (free, fast, generous limits).
"""

import re
import os
import time
from groq import Groq
from dotenv import load_dotenv

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
                        "content": "You are an expert VC analyst at a top venture capital firm. Be thorough, precise, and data-driven in your analysis."
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
        match = re.search(pattern, scoring_text, re.IGNORECASE)
        if match:
            scores[key] = float(match.group(1))

    if scores["composite"] == 0:
        weights = {
            "team": 0.25,
            "market": 0.20,
            "traction": 0.20,
            "product": 0.15,
            "thesis_fit": 0.10,
            "deal_terms": 0.10
        }
        weighted_sum = sum(scores[k] * weights[k] for k in weights)
        scores["composite"] = round(weighted_sum, 1)

    return scores


def get_decision(composite_score: float) -> dict:
    """
    Determine pass/review/fast-track based on composite score.
    """
    if composite_score >= 7.5:
        return {
            "decision": "🟢 FAST TRACK",
            "action": "Schedule partner meeting immediately",
            "color": "green"
        }
    elif composite_score >= 5.0:
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