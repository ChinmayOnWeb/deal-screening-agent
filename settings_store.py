"""Persistent fund settings helpers."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any

from config import FUND_CONFIG, SCORING_CRITERIA, THRESHOLDS

SETTINGS_PATH = "data/settings.json"


def _default_settings() -> dict[str, Any]:
    return {
        "fund_config": deepcopy(FUND_CONFIG),
        "scoring_criteria": deepcopy(SCORING_CRITERIA),
        "thresholds": deepcopy(THRESHOLDS),
    }


def load_settings() -> dict[str, Any]:
    defaults = _default_settings()
    if not os.path.exists(SETTINGS_PATH):
        return defaults

    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            stored = json.load(f)
    except (json.JSONDecodeError, OSError):
        return defaults

    merged = defaults
    merged["fund_config"].update(stored.get("fund_config", {}))

    for key, value in stored.get("scoring_criteria", {}).items():
        if key in merged["scoring_criteria"] and isinstance(value, dict):
            merged["scoring_criteria"][key].update(value)

    merged["thresholds"].update(stored.get("thresholds", {}))
    return merged


def save_settings(settings: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def get_runtime_fund_config() -> dict[str, Any]:
    return load_settings()["fund_config"]
