"""
Fund configuration and screening criteria.
Customize this to match your fund's thesis.
"""

FUND_CONFIG = {
    "name": "Your Fund Name",
    "thesis": "Early-stage B2B SaaS and AI startups",
    "stage_focus": ["Pre-Seed", "Seed", "Series A"],
    "check_size": "$100K - $500K",
    "geography": ["US", "Europe", "Global"],
    "sectors_of_interest": [
        "Artificial Intelligence",
        "B2B SaaS",
        "Fintech",
        "Health Tech",
        "Developer Tools",
        "Cybersecurity",
        "Climate Tech",
    ],
    "sectors_to_avoid": [
        "Gambling",
        "Tobacco",
        "Weapons",
    ]
}

SCORING_CRITERIA = {
    "team": {
        "weight": 0.25,
        "description": "Founder experience, domain expertise, completeness"
    },
    "market": {
        "weight": 0.20,
        "description": "TAM size, growth rate, timing"
    },
    "traction": {
        "weight": 0.20,
        "description": "Revenue, users, growth rate, retention"
    },
    "product": {
        "weight": 0.15,
        "description": "Differentiation, defensibility, product-market fit signals"
    },
    "thesis_fit": {
        "weight": 0.10,
        "description": "Alignment with fund thesis and focus areas"
    },
    "deal_terms": {
        "weight": 0.10,
        "description": "Valuation reasonableness, round structure"
    }
}

THRESHOLDS = {
    "fast_track": 7.5,   # Score >= 7.5 out of 10
    "review": 5.0,       # Score >= 5.0
    "pass": 0            # Score < 5.0
}