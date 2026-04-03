# Candidate Intelligence System

A production-grade hybrid scoring system for ranking internship applicants using rule-based scoring and LLM evaluation.

## Architecture

```
genotek-ai-agent/
├── app/
│   ├── main.py              # Entry point
│   ├── pipeline.py          # Orchestrates the full pipeline
│   ├── config.py            # All configurable parameters
│   ├── scoring/
│   │   ├── rule_engine.py   # Deterministic scoring (skills, projects, GitHub, generic detection)
│   │   └── github_checker.py # GitHub profile validation with retry logic
│   ├── llm/
│   │   ├── evaluator.py     # LLM-based answer evaluation (real or mock)
│   │   └── prompts.py       # Prompt templates
│   ├── processing/
│   │   ├── cleaner.py       # Data normalization and cleaning
│   │   └── validator.py     # Input validation
│   └── utils/
│       └── logger.py        # Structured logging
├── data/
│   └── candidates.csv       # Input data
├── output/
│   └── ranked_candidates.csv # Ranked results
├── Dockerfile
└── requirements.txt
```

## Scoring

- **Rule-based (60%)**: Skills matching, project count, GitHub validation, generic answer detection
- **LLM-based (40%)**: Answer quality, AI detection, authenticity assessment

## Tiers

| Score | Tier |
|-------|------|
| ≥75 | Fast-Track |
| ≥55 | Standard |
| ≥35 | Review |
| <35 | Reject |

## Usage

```bash
# Local
export PYTHONPATH=$(pwd)
python app/main.py

# Docker
docker build -t candidate-intelligence .
docker run -e LOVABLE_API_KEY=your_key candidate-intelligence

# Mock LLM mode (no API key needed)
# Set USE_MOCK_LLM=True in app/config.py
```

## Environment Variables

- `LOVABLE_API_KEY`: Required for real LLM evaluation (auto-provided in Lovable)
- `INPUT_CSV`: Path to input CSV (default: `data/candidates.csv`)
- `OUTPUT_CSV`: Path to output CSV (default: `output/ranked_candidates.csv`)
# scoring-agent
