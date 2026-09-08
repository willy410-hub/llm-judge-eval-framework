# LLM Judge Eval Framework

An automated LLM-as-a-Judge evaluation pipeline: runs a target model
against a suite of test cases, then uses a second, stronger model to
judge each response against an expected answer and classify failures
into a defined taxonomy (hallucination, logical fallacy, schema
mismatch, over-refusal).

> **Note on scope:** this is a reference implementation of the
> LLM-as-a-Judge evaluation pattern. Running it end-to-end requires a
> Groq API key (both the target and judge models are Groq-hosted). The
> unit test suite needs neither — every test mocks the Groq client
> boundary. See **Running Tests** below.

---

## How It Works

1. **Dataset ingestion** — test cases (prompt, expected answer, and
   optionally an `as_of_date` for time-sensitive facts) are loaded and
   validated against a Pydantic schema.
2. **Target execution** — the target model generates a raw response to
   each prompt under controlled parameters.
3. **Judging** — a separate, stronger judge model compares the response
   against the expected answer and returns a structured verdict:
   correctness, a 0.0–1.0 score, a failure-mode classification, and
   reasoning — enforced by a strict Pydantic schema.
4. **Reporting** — results are compiled into a pass/fail table with
   per-case failure-mode breakdown.

---

## What Changed From the Original Prototype

This is a rebuild of an earlier prototype. The LLM-as-a-Judge
*architecture* was sound; two of the four bundled test cases had a
real, independently-verified problem with their gold-standard answers,
and one classification path was undocumented:

- **TC-001's expected answer was mathematically wrong.** The prompt
  ("you and I have $1.10, you have $1 less than me — how much do *I*
  have?") solves to $1.05 (21 nickels) for "I". The original dataset
  listed "1 nickel (5 cents)" — that's *your* amount, not mine, per the
  prompt as literally worded. This wasn't a guess: solving the algebra
  independently (`me + you = 1.10`, `you = me - 1.00` → `me = 1.05`)
  confirms it, and the original README's own sample report shows
  TC-001 failing with "Factual Hallucination" — consistent with a
  judge correctly penalizing answers that matched the *wrong* expected
  value. Fixed in `dataset/test_cases.json`, with a `notes` field
  explaining the original error.
- **TC-002's expected answer was a frozen, undated snapshot for a
  "Time-Sensitive Knowledge" test.** Jupiter's confirmed moon count
  was roughly 95 in early 2024, but had moved to 97 (April 2025), 101
  (March 2026), and 115 (August 2026) per IAU Minor Planet Center
  announcements — verified via web search while rebuilding this
  project. A category literally named "time-sensitive" needs a
  timestamp on its gold standard, or it penalizes models for being
  *more* current and correct. Fixed: test cases now support an
  optional `as_of_date` field, and when present, the judge prompt is
  extended with an explicit instruction not to penalize a more recent,
  verifiably correct answer as a hallucination.
- **`failure_mode="Pipeline Error"` was an undeclared fallback value.**
  The judge's own system prompt only listed five failure-mode options;
  the exception-handling fallback silently returned a sixth value never
  mentioned anywhere. `FailureMode` in `app/schemas.py` is now a strict
  `Literal` type that includes `"Pipeline Error"` as an official,
  documented category — and a judge response with any other
  undeclared value now fails Pydantic validation and correctly falls
  back to it too (see `tests/test_judge.py`).
- **Duplicated Groq client construction.** `main.py` and
  `evaluator/judge.py` each built their own `Groq` client independently.
  Both now share one lazily-constructed client
  (`app/core/groq_client.py`).
- **No tests existed.** This rebuild adds **19 unit tests** — covering
  dataset validation, the judge's parsing and fallback paths (bad JSON,
  API exceptions, and a judge hallucinating an undeclared failure
  mode), the target-model runner, and report formatting — all against
  mocks, with zero live API calls.

---

## Project Structure

```text
llm-judge-eval-framework/
├── main.py                        # CLI entrypoint
├── app/
│   ├── schemas.py                   # TestCase, EvaluationResult, CaseOutcome (strict FailureMode literal)
│   ├── dataset_loader.py             # Validated test-case loading
│   ├── target_runner.py              # Runs the target model against a prompt
│   ├── judge.py                      # LLM-as-a-Judge (time-sensitivity aware)
│   ├── pipeline.py                   # Orchestrates load -> execute -> judge
│   ├── report.py                     # Formats results into a pass/fail table
│   └── core/
│       ├── config.py                   # Centralized, env-driven settings + failure taxonomy
│       ├── exceptions.py               # Domain-specific exception types
│       └── groq_client.py              # Shared, lazily-constructed Groq client
├── dataset/
│   └── test_cases.json              # 4 test cases, TC-001/TC-002 corrected
├── tests/                          # 19 tests, fully mocked, no API key needed
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your API key

```bash
cp .env.example .env
# edit .env: set EVAL_GROQ_API_KEY to your Groq key
```

### 3. Run it

```bash
python main.py
```

---

## Running Tests

No Groq API key or network access is required.

```bash
pip install -r requirements-dev.txt
pytest -v
```

---

## Extending

- **Add a test case:** append to `dataset/test_cases.json` following the
  `TestCase` schema (`id`, `category`, `prompt`, `expected_answer`, and
  optionally `as_of_date` / `notes`). Any time-sensitive fact should
  carry an `as_of_date` — see TC-002 for the pattern.
- **Add a failure mode:** extend `FailureMode` in `app/schemas.py` and
  the corresponding list in the judge's system prompt
  (`app/judge.py`) together, so the two never drift apart again.
- **Swap models:** set `EVAL_TARGET_MODEL` / `EVAL_JUDGE_MODEL` in
  `.env` — no code changes needed.
