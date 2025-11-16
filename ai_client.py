from groq import Groq
import json
import os


class AIQuestionGenerator:
    def __init__(self, api_key=None):
        # Get API key from argument or environment
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set GROQ_API_KEY environment variable.")
        self.client = Groq(api_key=self.api_key)

    def generate_questions(self, topic, difficulty="medium", num_questions=10):
        difficulty_map = {
            "easy": "lengvus",
            "medium": "vidutinio sunkumo",
            "hard": "sunkius",
        }

        prompt = f"""Sugeneruok {num_questions} {difficulty_map.get(difficulty, 'vidutinio sunkumo')} klausimus apie "{topic}" lietuvių kalba.

Grąžink TIKTAI JSON formatą be jokio kito teksto:
[
  {{
    "question": "klausimo tekstas",
    "type": "multiple_choice",
    "options": ["A) variantas1", "B) variantas2", "C) variantas3", "D) variantas4"],
    "correct": "A",
    "explanation": "kodėl šis atsakymas teisingas"
  }},
  {{
    "question": "klausimo tekstas",
    "type": "short",
    "correct": "trumpas teisingas atsakymas",
    "explanation": "papildomas paaiškinimas"
  }}
]

Generuok įvairius klausimus - maišyk multiple_choice ir short tipo klausimus."""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
                temperature=1.0,
                max_tokens=1000,
            )

            response_text = chat_completion.choices[0].message.content.strip()
            # Remove possible ```json or ``` wrappers
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            questions = json.loads(response_text)
            return questions

        except Exception as e:
            print(f"Klaida generuojant klausimus: {e}")
            return self._get_fallback_questions(topic)

    def _get_fallback_questions(self, topic):
        return [
            {
                "question": f"Kas yra svarbiausias dalykas apie {topic}?",
                "type": "short",
                "correct": "Bendras atsakymas",
                "explanation": "Tai pavyzdinis klausimas",
            }
        ]
