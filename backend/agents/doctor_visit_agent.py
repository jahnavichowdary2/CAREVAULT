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


class DoctorVisitAgent:
    """
    MediSaathi HealthVault - Doctor Visit Agent

    Responsibilities:
    - Prepare a concise summary for a doctor's visit.
    - Organize recent reports, findings, medicines, and trends.
    - Suggest useful questions the patient can ask the doctor.
    - Identify documents that may be useful to carry.

    This agent does NOT:
    - Diagnose diseases
    - Prescribe medicines
    - Change medication dosage
    - Invent missing medical information
    """

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

    def generate_summary(
        self,
        patient_name,
        reports=None,
        medications=None,
        trends=None,
        health_history=None
    ):
        """
        Generate a doctor-visit summary from existing patient information.
        """

        reports = reports or []
        medications = medications or []
        trends = trends or []
        health_history = health_history or []

        prompt = f"""
You are the Doctor Visit Preparation Agent of MediSaathi HealthVault.

Prepare a concise and organized summary that a patient can use
during a doctor's appointment.

PATIENT NAME:
{patient_name}

RECENT REPORTS:
{reports}

CURRENT MEDICATIONS:
{medications}

HEALTH TRENDS:
{trends}

RELEVANT HEALTH HISTORY:
{health_history}

IMPORTANT RULES:

1. Use ONLY the information provided above.
2. Do NOT invent missing medical information.
3. Do NOT diagnose the patient.
4. Do NOT prescribe or recommend starting, stopping,
   or changing any medicine.
5. Clearly distinguish reported findings from interpretations.
6. If information is missing, say "Not available". If no medicines were prescribed in the report, write "None prescribed in this report".
7. Keep the summary simple and easy for a patient to understand.
8. Preserve exact medical values, units, dates, reference ranges, and medicine names, doses, frequencies, and durations.
9. Include useful questions the patient can ask their doctor.
10. Do not present those questions as medical conclusions.

Return the result using exactly this structure:

PATIENT SUMMARY
- Patient name:
- Main reason for visit:

RECENT REPORTS
- Report:
- Date:
- Important findings:

CURRENT MEDICATIONS
- Medicine:
- Dose:
- Frequency:
- Duration:

HEALTH TRENDS
- Test/finding:
- Previous:
- Current:
- Trend:

RELEVANT HISTORY
- Important information:

QUESTIONS TO ASK THE DOCTOR
1.
2.
3.

DOCUMENTS TO CARRY
- 
- 
- 
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful healthcare documentation "
                        "assistant. Your job is to organize provided "
                        "medical information for a doctor's visit. "
                        "Never diagnose, prescribe, or invent information."
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

    def process(
        self,
        patient_name,
        reports=None,
        medications=None,
        trends=None,
        health_history=None
    ):
        """
        Standard interface for the Orchestrator Agent.
        """

        try:
            summary = self.generate_summary(
                patient_name=patient_name,
                reports=reports,
                medications=medications,
                trends=trends,
                health_history=health_history
            )

            return {
                "success": True,
                "patient_name": patient_name,
                "doctor_visit_summary": summary
            }

        except Exception as e:
            return {
                "success": False,
                "patient_name": patient_name,
                "doctor_visit_summary": None,
                "error": str(e)
            }


if __name__ == "__main__":
    print("Starting Doctor Visit Agent...")
    try:
        agent = DoctorVisitAgent()
        print("Success initializing DoctorVisitAgent.")
    except Exception as e:
        print("Error:", e)