import json
import os
from groq import Groq
from pydantic import BaseModel


class EvaluationResult(BaseModel):
  is_correct: bool
  score: float
  failure_mode: str
  reasoning: str


class LLMJudge:

  def __init__(self, api_key: str = None):
    self.client = Groq(api_key=api_key or os.getenv('GROQ_API_KEY'))
    self.judge_model = 'llama-3.3-70b-versatile'

  def evaluate_response(
      self, prompt: str, expected: str, actual: str
  ) -> EvaluationResult:
    judge_system_prompt = """
        You are an expert Frontier AI Research Evaluator. Your task is to evaluate the quality of an LLM generation against a test prompt and expected behavior.
        
        Analyze the actual response and return a JSON object with:
        - "is_correct": boolean
        - "score": float between 0.0 and 1.0
        - "failure_mode": Choose exactly ONE from ["None", "Factual Hallucination", "Logical Fallacy", "Schema Mismatch", "Over-refusal"]
        - "reasoning": Concise explanation of the judgment.
        """

    user_content = f"""
        Prompt: {prompt}
        Expected Behavior/Answer: {expected}
        Actual LLM Response: {actual}
        """

    try:
      response = self.client.chat.completions.create(
          model=self.judge_model,
          messages=[
              {'role': 'system', 'content': judge_system_prompt},
              {'role': 'user', 'content': user_content},
          ],
          response_format={'type': 'json_object'},
          temperature=0.0,
      )
      data = json.loads(response.choices[0].message.content)
      return EvaluationResult(**data)
    except Exception as e:
      return EvaluationResult(
          is_correct=False,
          score=0.0,
          failure_mode='Pipeline Error',
          reasoning=f'Evaluation failed due to error: {str(e)}',
      )