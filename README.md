# Candidate Intelligence System

I built this system to solve one specific problem:
given a large number of internship applicants, how do we quickly identify the ones worth shortlisting without manually reading everything?

Instead of going fully ML-heavy, I used a hybrid approach:

* deterministic rules for structured signals
* LLM evaluation for subjective answer quality

---

## How the System Works

The pipeline processes candidates step by step:

Raw CSV → Cleaning → Rule Scoring → LLM Evaluation → Score Normalization → Ranking → Output

Each candidate ends up with:

* rule score
* LLM score
* final score
* tier (Fast-Track / Standard / Review / Reject)
* explanation (why they got that score)

---

## Project Structure

genotek-ai-agent/
├── app/
│   ├── main.py              # CLI entry point
│   ├── pipeline.py          # End-to-end processing
│   ├── config.py            # Scoring weights & thresholds
│
│   ├── scoring/
│   │   ├── rule_engine.py   # Skills, projects, GitHub, generic detection
│   │   └── github_checker.py # GitHub validation (with retries)
│
│   ├── llm/
│   │   ├── evaluator.py     # LLM-based evaluation
│   │   └── prompts.py       # Prompt tuning
│
│   ├── processing/
│   │   ├── cleaner.py       # Handles messy input
│   │   └── validator.py     # Basic validation
│
│   └── utils/
│       └── logger.py        # Logging
│
├── data/
├── output/
├── Dockerfile
└── requirements.txt

---

## Scoring Logic

### 1. Rule-Based Scoring

This handles structured signals:

* Skills → keyword matching with caps
* Projects → based on count (to avoid overfitting)
* GitHub:

  * missing / invalid / empty / active profiles
  * avoids giving credit for just having a link
* Generic detection:

  * phrases like "comprehensive overview"
  * very short or vague answers

---

### 2. LLM-Based Evaluation

Used for subjective quality:

* checks if the answer shows actual understanding
* penalizes generic / templated responses
* looks for practical thinking instead of just wording

---

### 3. Score Combination

One issue I ran into was scale mismatch:

* rule score → up to 100
* LLM score → up to 40

This caused all final scores to cluster in a narrow range.

Fix:

* scaled LLM score to 0–100 before combining

Final score = weighted combination of rule + LLM

---

## Tiers

| Score | Tier       |
| ----- | ---------- |
| ≥60   | Fast-Track |
| ≥50   | Standard   |
| ≥35   | Review     |
| <35   | Reject     |

---

## Things I Ran Into (Important)

This part actually mattered more than the code.

* Initially, all candidates had identical LLM scores → turned out mock fallback was being used silently
* First Groq model I used was deprecated → had to switch
* LLM was too harsh → adjusted prompt to reward partial understanding
* GitHub links were messy → added normalization + validation
* Missing fields caused crashes → added defensive handling

---

## Running the Project

### Local

export PYTHONPATH=$(pwd)
python app/main.py

---

### Docker

docker build -t candidate-intelligence .
docker run candidate-intelligence

---

### Mock Mode (no API needed)

Set in config:

USE_MOCK_LLM = True

---

## Environment Variables

* INPUT_CSV → input file
* OUTPUT_CSV → output file
* GROQ_API_KEY → required for real LLM

---

## Final Note

The goal here wasn’t to build a perfect model, but to build something that behaves like a real system:

* handles messy data
* doesn’t crash on missing fields
* explains its decisions
* and can be extended into a larger pipeline
