import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from groq import Groq

# Load environment variables from possible locations
for p in [
    os.path.join(os.path.dirname(__file__), ".env"),
    os.path.join(os.path.dirname(__file__), "..", ".env"),
    os.path.join(os.getcwd(), ".env"),
]:
    if os.path.exists(p):
        load_dotenv(p)


class LanguageAgent:
    """
    MediSaathi HealthVault - Language Agent

    Responsibilities:
    - Translate medical explanations into the user's preferred language.
    - Preserve medical values, units, medicine names, dosage, and dates.
    - Preserve uncertainty and doctor-review requirements.
    - Keep explanations simple and patient-friendly.
    """

    SUPPORTED_LANGUAGES = {
        "english": "English",
        "telugu": "Telugu",
        "hindi": "Hindi",
        "tamil": "Tamil",
        "kannada": "Kannada",
        "malayalam": "Malayalam",
        "marathi": "Marathi",
        "bengali": "Bengali",
    }

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Please check your backend/.env file."
            )

        self.client = Groq(api_key=api_key)

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b"
        )

    def translate(self, text, target_language="English"):
        """
        Translate medical information into the requested language.
        """

        if not text:
            return ""

        language_key = target_language.strip().lower()

        if language_key not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {target_language}. "
                f"Supported languages: "
                f"{', '.join(self.SUPPORTED_LANGUAGES.values())}"
            )

        target_language_name = self.SUPPORTED_LANGUAGES[language_key]

        # No API call needed for English
        if target_language_name == "English":
            return text

        prompt = f"""
You are the Language Agent of MediSaathi HealthVault.

Translate the following medical explanation into {target_language_name}.

IMPORTANT RULES:

1. Preserve all medical facts exactly.
2. Do NOT change numbers, dates, units, medicine names,
   dosage, frequency, or reference ranges.
3. Do NOT create a new diagnosis.
4. Do NOT add medical advice that is not present.
5. Preserve uncertainty words such as:
   "may", "possible", "suggests", "could", and
   "doctor review required".
6. Do NOT change the meaning of the medical information.
7. Use simple, natural language that a patient can understand.
8. Keep medicine names in English.
9. Keep important medical terms in English if translating them
   would make the meaning unclear.
10. Do not prescribe, stop, start, or change any medication.
11. Return ONLY the translated explanation.

Medical explanation:

{text}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful multilingual medical "
                        "translation assistant. "
                        "Accuracy and preservation of medical "
                        "information are more important than "
                        "literal translation."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
        )

        return response.choices[0].message.content.strip()

    def process(self, text, target_language="English"):
        """
        Standard interface that will later be used
        by the Orchestrator Agent.
        """

        try:
            language_key = target_language.strip().lower()

            if language_key not in self.SUPPORTED_LANGUAGES:
                raise ValueError(
                    f"Unsupported language: {target_language}"
                )

            translated_text = self.translate(
                text,
                target_language
            )

            return {
                "success": True,
                "language": self.SUPPORTED_LANGUAGES[language_key],
                "translated_text": translated_text,
            }

        except Exception as e:
            return {
                "success": False,
                "language": target_language,
                "translated_text": text,
                "error": str(e),
            }


if __name__ == "__main__":
    print("Starting Language Agent...")
    try:
        agent = LanguageAgent()
        print("Success initializing LanguageAgent.")
    except Exception as e:
        print("Error:", e)