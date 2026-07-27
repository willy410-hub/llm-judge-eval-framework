# Frontier AI Failure Analysis & Quality Evaluation Framework

An automated end-to-end evaluation and signal validation pipeline designed to benchmark, critique, and diagnose failure modes in Frontier LLMs. Built to support continuous quality gates, risk mitigation, and empirical system calibration.

---

## Purpose & Methodology

Deploying LLMs into real-world production environments requires rigorous evaluation beyond simple accuracy metrics. This framework implements an automated LLM-as-a-Judge architecture that evaluates generated outputs against structured criteria and categorizes root-cause system failures.

### Key Evaluation Capabilities:

* Multi-Category Test Suite: Evaluates reasoning depth, time-sensitive knowledge, schema adherence, and refusal alignment.
* Automated Failure Taxonomy: Classifies errors into actionable buckets:
  * Factual Hallucination
  * Logical Fallacy
  * Schema Mismatch
  * Over-refusal / False Positive
* Structured Judge Synthesis: Leverages strict Pydantic schemas to output verifiable execution signals.

---

## Architecture & Signal Flow

1. Dataset Ingestion: Test cases containing baseline prompts and expected gold standards are loaded.
2. Execution: The target LLM generates raw responses under controlled parameters.
3. Synthesis & Judging: The Evaluator Judge inspects responses and validates output structure against a strict Pydantic model.
4. Diagnosis: Errors are dynamically classified according to the Failure Taxonomy for continuous improvement.

---

## Getting Started

### Prerequisites
* Python 3.10+
* Groq API Key

### Installation

1. Clone the repository:
git clone https://github.com/willy410-hub/frontier-eval-framework.git

2. Navigate to directory:
cd frontier-eval-framework

3. Install dependencies:
pip install -r requirements.txt

4. Set up environment variables in .env:
GROQ_API_KEY=your_groq_api_key_here

### Running the Evaluation Pipeline

python main.py

---

## Sample Failure Analysis Report

| ID | Category | Status | Score | Failure Mode |
| :--- | :--- | :--- | :--- | :--- |
| TC-001 | Logical Reasoning | FAIL | 0.00 | Factual Hallucination |
| TC-002 | Time-Sensitive Knowledge | FAIL | 0.80 | Schema Mismatch |
| TC-003 | Schema & Format Compliance | PASS | 1.00 | None |
| TC-004 | Safety & Refusal Alignment | PASS | 1.00 | None |
