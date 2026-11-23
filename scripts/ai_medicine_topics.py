"""AI-medicine topic taxonomy shared by the theme mapper and the news engine.

Each topic has:
- ``article``: regex that assigns a frontier article (one that need not name any
  company) to the topic;
- ``needs_ai``: when true, the article must also mention AI, so routine imaging or
  cardiology news does not count as AI-medicine news;
- ``filings``: SEC full-text search phrases used to measure which companies are
  exposed to the topic from their own filings (no hand-written company lists);
- ``fda_devices``: exposure also comes from FDA AI-device clearances (policy topics);
- ``device``: device and care-delivery topics exclude drug developers (SIC 2833-2836),
  whose filings use words like "pathology", "cardiac" or "reimbursement" about drugs.
"""
from __future__ import annotations

import re

AI_TERMS = re.compile(r"\b(ai|a\.i\.|artificial intelligence|machine learning|deep learning|algorithm|foundation model|large language model|llm|neural network|generative)\b", re.I)

TOPICS = [
    {"key": "imaging", "label": "AI medical imaging", "needs_ai": True,
     "article": r"radiolog|medical imag|\bct scan|\bmri\b|mammogra|ultrasound|x-ray|chest imag",
     "filings": ['"artificial intelligence" "radiology"', '"deep learning" "medical imaging"', '"artificial intelligence" "imaging"', '"machine learning" "imaging"'], "device": True},
    {"key": "pathology", "label": "Digital & AI pathology", "needs_ai": False,
     "article": r"digital patholog|computational patholog|whole[- ]slide|histopatholog|ai patholog|cytology|slide imaging",
     "filings": ['"digital pathology"', '"computational pathology"']},
    {"key": "liquid_biopsy", "label": "Liquid biopsy & cancer screening", "needs_ai": False,
     "article": r"liquid biopsy|cell-free dna|cfdna|ctdna|minimal residual|\bmrd\b|multi-cancer|early cancer detection|colorectal (cancer )?screening",
     "filings": ['"liquid biopsy"', '"minimal residual disease"', '"multi-cancer early detection"']},
    {"key": "drug_discovery", "label": "AI drug discovery & protein design", "needs_ai": False,
     "article": r"ai drug discovery|ai-designed|drug discovery .*(ai|machine learning)|(ai|machine learning).* drug discovery|protein design|de novo protein|alphafold|generative chemistry|biology foundation model",
     "filings": ['"artificial intelligence" "drug discovery"', '"machine learning" "drug discovery"', '"protein design"']},
    {"key": "biosimulation", "label": "Biosimulation & model-informed development", "needs_ai": False,
     "article": r"biosimulation|pharmacometric|model-informed|in silico trial|virtual (clinical )?trial|digital twin",
     "filings": ['"biosimulation"', '"model-informed drug development"']},
    {"key": "cardiac", "label": "Cardiac AI", "needs_ai": True,
     "article": r"cardiac|coronary|\becg\b|\bekg\b|arrhythmi|atrial fibrillation|heart failure|cardiolog",
     "filings": ['"artificial intelligence" "coronary"', '"ECG" "artificial intelligence"', '"artificial intelligence" "cardiac"', '"artificial intelligence" "heart"'], "device": True},
    {"key": "neuro", "label": "Neuro monitoring & stroke AI", "needs_ai": True,
     "article": r"\beeg\b|seizure|stroke|neurolog|brain monitor",
     "filings": ['"EEG" "artificial intelligence"', '"stroke" "artificial intelligence"', '"artificial intelligence" "neurolog"', '"artificial intelligence" "brain"'], "device": True},
    {"key": "robotics", "label": "Surgical robotics", "needs_ai": False,
     "article": r"surgical robot|robotic surgery|robot-assisted|robotic-assisted",
     "filings": ['"robotic surgery"', '"surgical robot"'], "device": True},
    {"key": "remote_care", "label": "Remote monitoring & digital care", "needs_ai": False,
     "article": r"remote (patient )?monitoring|wearable|sleep apnea|digital therapeutic|virtual care|telehealth|digital health app",
     "filings": ['"remote patient monitoring"', '"digital therapeutics"', '"virtual care"'], "device": True},
    {"key": "genomics", "label": "Clinical genomics & sequencing", "needs_ai": False,
     "article": r"whole[- ]genome|exome|genome sequencing|rare disease diagnos|genetic test|newborn sequencing|long-read",
     "filings": ['"whole genome sequencing"', '"exome sequencing"']},
    {"key": "rwd_trials", "label": "Real-world data & AI in trials", "needs_ai": False,
     "article": r"real-world (data|evidence)|clinical trial (design|recruitment|matching)|trial enrollment .*ai|ehr data",
     "filings": ['"real-world data" "artificial intelligence"']},
    {"key": "ai_regulation", "label": "AI medical-device regulation", "needs_ai": True,
     # Needs device/software regulation wording: "AI drug hype without FDA wins" is drug news, not device policy.
     "article": r"(\bfda\b|\bhhs\b|\bema\b|regulator).{0,80}(guidance|framework|rule|device|software|clearance|oversight|policy)|software as a medical device|\bsamd\b|predetermined change control|ai (regulation|rules|policy) .*health",
     "filings": [], "fda_devices": True, "device": True},
    {"key": "ai_reimbursement", "label": "Payment for AI in care", "needs_ai": True,
     "article": r"\bcms\b|medicare|\bcpt\b|reimburs|payment (code|rule)|payer|coverage",
     "filings": ['"artificial intelligence" "CPT code"', '"artificial intelligence" "Medicare reimbursement"'], "device": True},
]

POSITIVE_THEME = re.compile(r"approv|clear|authoriz|launch|adopt|expand|outperform|accura|beats|breakthrough|funding|grant|payment|coverage for|recommend", re.I)
NEGATIVE_THEME = re.compile(r"recall|warning|ban|restrict|halt|reject|fail|bias|harm|lawsuit|cut|underperform|crackdown|delay", re.I)


def classify_topics(text: str) -> list[str]:
    """Topics an article belongs to. AI-dependent topics also need an AI term."""
    lowered = text.lower()
    has_ai = bool(AI_TERMS.search(lowered))
    return [t["key"] for t in TOPICS if re.search(t["article"], lowered) and (has_ai or not t["needs_ai"])]


def theme_direction(text: str) -> int:
    pos, neg = bool(POSITIVE_THEME.search(text)), bool(NEGATIVE_THEME.search(text))
    if pos and not neg:
        return 1
    if neg and not pos:
        return -1
    return 0
