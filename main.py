import json
import os
from dotenv import load_dotenv
from evaluator.judge import LLMJudge
from groq import Groq
from tabulate import tabulate

load_dotenv()


def run_evaluation_pipeline():
  groq_api_key = os.getenv('GROQ_API_KEY')
  if not groq_api_key:
    print('❌ Error: GROQ_API_KEY environment variable not set in .env file.')
    return

  client = Groq(api_key=groq_api_key)
  judge = LLMJudge(api_key=groq_api_key)

  with open('dataset/test_cases.json', 'r') as f:
    test_cases = json.load(f)

  target_model = 'llama-3.1-8b-instant'
  results_summary = []

  print(
      f'🚀 Starting Evaluation Pipeline against Target Model:'
      f' {target_model}\n'
  )

  for test in test_cases:
    print(
        f"Running Test Case [{test['id']}] - Category: {test['category']}..."
    )

    response = client.chat.completions.create(
        model=target_model,
        messages=[{'role': 'user', 'content': test['prompt']}],
        temperature=0.1,
    )
    actual_response = response.choices[0].message.content.strip()

    eval_res = judge.evaluate_response(
        prompt=test['prompt'],
        expected=test['expected_answer'],
        actual=actual_response,
    )

    results_summary.append([
        test['id'],
        test['category'],
        'PASS' if eval_res.is_correct else 'FAIL',
        f'{eval_res.score:.2f}',
        eval_res.failure_mode,
        eval_res.reasoning[:60] + '...',
    ])

  print('\n' + '=' * 80)
  print('📊 EVALUATION & FAILURE ANALYSIS REPORT')
  print('=' * 80)
  headers = [
      'ID',
      'Category',
      'Status',
      'Score',
      'Failure Mode',
      'Judge Reasoning Snippet',
  ]
  print(tabulate(results_summary, headers=headers, tablefmt='grid'))


if __name__ == '__main__':
  run_evaluation_pipeline()