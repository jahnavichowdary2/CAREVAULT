"""
CareVault / MediSaathi
Central AI Healthcare Agent

MediSaathi:
1. Understands the user's request
2. Creates an action plan
3. Selects relevant healthcare tools
4. Executes the tools
5. Performs a safety check
6. Generates a concise multilingual response
"""

import os
import json

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from groq import Groq


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

for p in [
    os.path.join(os.path.dirname(__file__), ".env"),
    os.path.join(os.path.dirname(__file__), "..", ".env"),
    os.path.join(os.getcwd(), ".env"),
]:
    if os.path.exists(p):
        load_dotenv(p)


# =========================================================
# MEDISAATHI AGENT
# =========================================================

class MediSaathiAgent:

    def __init__(self, orchestrator):

        print("Initializing MediSaathi Agent...")

        self.orchestrator = orchestrator

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b"
        )

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is missing from the .env file."
            )

        self.client = Groq(
            api_key=api_key
        )

        self.supported_languages = [
            "English",
            "Telugu",
            "Hindi",
            "Tamil",
            "Kannada",
            "Malayalam"
        ]

        print("MediSaathi Agent initialized successfully.")


    # =====================================================
    # MAIN PROCESS
    # =====================================================

    def process(
        self,
        message,
        language="English",
        patient_name="User",
        measurements=None,
        health_history=None
    ):

        if not message:
            return {
                "success": False,
                "error": "Message is required."
            }

        if not language:
            language = "English"

        if language not in self.supported_languages:
            language = "English"

        measurements = measurements or []
        health_history = health_history or []

        print("\n========================================")
        print("MEDISAATHI CENTRAL AGENT")
        print("========================================")
        print("Message:", message)
        print("Language:", language)
        print("Patient:", patient_name)

        try:

            # -------------------------------------------------
            # STEP 1 — UNDERSTAND AND PLAN
            # -------------------------------------------------

            plan = self.create_plan(
                message=message,
                language=language
            )

            print("\nMediSaathi Plan:")
            print(plan)

            intent = plan.get(
                "intent",
                "general_health"
            )

            selected_tools = plan.get(
                "tools",
                []
            )

            # -------------------------------------------------
            # STEP 2 — EXECUTE SELECTED TOOLS
            # -------------------------------------------------

            tool_results = self.execute_tools(
                selected_tools=selected_tools,
                message=message,
                measurements=measurements,
                health_history=health_history,
                patient_name=patient_name
            )

            # -------------------------------------------------
            # STEP 3 — SAFETY CHECK
            # -------------------------------------------------

            safety_result = self.orchestrator.analyze_safety(
                message
            )

            # -------------------------------------------------
            # STEP 4 — FINAL RESPONSE
            # -------------------------------------------------

            response = self.generate_response(
                message=message,
                language=language,
                intent=intent,
                tool_results=tool_results,
                safety_result=safety_result
            )

            # -------------------------------------------------
            # FINAL RESULT
            # -------------------------------------------------

            return {
                "success": True,
                "agent": "MediSaathi",
                "patient_name": patient_name,

                "understanding": {
                    "message": message,
                    "language": language,
                    "intent": intent
                },

                "plan": plan,

                "tool_results": tool_results,

                "safety": safety_result,

                "response": response,

                "voice_enabled": True
            }

        except Exception as e:

            print("\nMEDISAATHI ERROR:")
            print(str(e))

            return {
                "success": False,
                "agent": "MediSaathi",
                "error": str(e),
                "response": (
                    "I could not process your request right now. "
                    "Please try again."
                ),
                "voice_enabled": True
            }


    # =====================================================
    # CREATE PLAN
    # =====================================================

    def create_plan(
        self,
        message,
        language="English"
    ):

        prompt = f"""
You are the planning brain of MediSaathi,
a safe multilingual healthcare information assistant.

USER MESSAGE:
{message}

REQUESTED LANGUAGE:
{language}

AVAILABLE TOOLS:

1. document_analysis
   Analyze medical reports and extracted information.

2. clinical_information
   Explain recorded clinical findings in simple language.

3. medicine_information
   Explain information about medicines already present
   in the user's records.

4. health_trends
   Compare health measurements over time.

5. safety_check
   Check whether the request contains an urgent
   or safety-related concern.

6. doctor_visit_preparation
   Help prepare questions and information for a doctor visit.

INTENTS:

- document_analysis
- clinical_information
- medicine_information
- health_trends
- doctor_visit
- emergency
- general_health

RULES:

- Select only the tools actually needed.
- Do not select every tool for every request.
- Emergency or safety concerns should prioritize safety_check.
- Never diagnose.
- Never prescribe.
- Never change medicine dosage.
- Never invent medical values.
- Preserve dates, values, units and medicine names.
- Use the minimum number of tools necessary.

Return ONLY valid JSON.

JSON FORMAT:

{{
    "intent": "one intent from the list",
    "tools": [
        "tool_name"
    ],
    "reason": "short explanation"
}}
"""

        try:

            response = self.client.chat.completions.create(

                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are MediSaathi's planning agent. "
                            "Return valid JSON only."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.1
            )

            content = response.choices[0].message.content

            if not content:
                return {
                    "intent": "general_health",
                    "tools": ["safety_check"],
                    "reason": "Fallback plan."
                }

            content = content.strip()

            # Remove accidental markdown fences
            if content.startswith("```"):
                content = content.replace(
                    "```json",
                    ""
                ).replace(
                    "```",
                    ""
                ).strip()

            plan = json.loads(content)

            if not isinstance(plan, dict):
                raise ValueError(
                    "Planning response was not a JSON object."
                )

            if "intent" not in plan:
                plan["intent"] = "general_health"

            if "tools" not in plan:
                plan["tools"] = []

            if not isinstance(plan["tools"], list):
                plan["tools"] = []

            return plan

        except Exception as e:

            print(
                "Planning error:",
                str(e)
            )

            return {
                "intent": "general_health",
                "tools": ["safety_check"],
                "reason": "Fallback safety-first plan."
            }


    # =====================================================
    # EXECUTE TOOLS
    # =====================================================

    def execute_tools(
        self,
        selected_tools,
        message,
        measurements=None,
        health_history=None,
        patient_name="User"
    ):

        measurements = measurements or []
        health_history = health_history or []

        results = {}

        # -------------------------------------------------
        # DOCUMENT ANALYSIS
        # -------------------------------------------------

        if "document_analysis" in selected_tools:

            try:

                document_result = (
                    self.orchestrator.analyze_document(
                        message
                    )
                )

                results["document_analysis"] = document_result

            except Exception as e:

                results["document_analysis"] = {
                    "success": False,
                    "error": str(e)
                }


        # -------------------------------------------------
        # CLINICAL INFORMATION
        # -------------------------------------------------

        if "clinical_information" in selected_tools:

            try:

                # If document analysis already exists,
                # use its result as the clinical input.

                document_data = results.get(
                    "document_analysis"
                )

                if not document_data and health_history:
                    for item in health_history:
                        if isinstance(item, dict):
                            if "document" in item and item["document"].get("lab_results"):
                                document_data = item["document"]
                                break
                            elif "lab_results" in item:
                                document_data = item
                                break

                if document_data:

                    clinical_result = (
                        self.orchestrator
                        .analyze_clinical_findings(
                            document_data
                        )
                    )

                else:

                    clinical_result = {
                        "success": True,
                        "message": (
                            "No structured medical document "
                            "was provided."
                        )
                    }

                results["clinical_information"] = (
                    clinical_result
                )

            except Exception as e:

                results["clinical_information"] = {
                    "success": False,
                    "error": str(e)
                }


        # -------------------------------------------------
        # MEDICINE INFORMATION
        # -------------------------------------------------

        if "medicine_information" in selected_tools:

            try:

                medicines = []

                document_data = results.get(
                    "document_analysis"
                )

                if isinstance(document_data, dict):

                    medicines = document_data.get(
                        "medicines",
                        []
                    )

                if not medicines and health_history:
                    for item in health_history:
                        if isinstance(item, dict):
                            if "medicine_analysis" in item and item["medicine_analysis"].get("medicines"):
                                medicines = item["medicine_analysis"]["medicines"]
                                break
                            elif "document" in item and item["document"].get("medicines"):
                                medicines = item["document"]["medicines"]
                                break

                if medicines:

                    medicine_result = (
                        self.orchestrator
                        .analyze_medicines(
                            medicines
                        )
                    )

                else:

                    medicine_result = {
                        "success": True,
                        "medicines": [],
                        "message": (
                            "No medicines were detected "
                            "in the available information."
                        )
                    }

                results["medicine_information"] = (
                    medicine_result
                )

            except Exception as e:

                results["medicine_information"] = {
                    "success": False,
                    "error": str(e)
                }


        # -------------------------------------------------
        # HEALTH TRENDS
        # -------------------------------------------------

        if "health_trends" in selected_tools:

            try:

                trend_measurements = measurements
                if not trend_measurements and health_history:
                    for item in health_history:
                        if isinstance(item, dict):
                            if "measurements" in item and item["measurements"]:
                                trend_measurements = item["measurements"]
                                break
                            elif "document" in item and item["document"].get("lab_results"):
                                trend_measurements = item["document"]["lab_results"]
                                break

                trend_result = (
                    self.orchestrator
                    .analyze_health_trends(
                        trend_measurements
                    )
                )

                results["health_trends"] = trend_result

            except Exception as e:

                results["health_trends"] = {
                    "success": False,
                    "error": str(e)
                }


        # -------------------------------------------------
        # SAFETY CHECK
        # -------------------------------------------------

        if "safety_check" in selected_tools:

            try:

                safety_result = (
                    self.orchestrator
                    .analyze_safety(
                        message
                    )
                )

                results["safety_check"] = safety_result

            except Exception as e:

                results["safety_check"] = {
                    "success": False,
                    "error": str(e)
                }


        # -------------------------------------------------
        # DOCTOR VISIT PREPARATION
        # -------------------------------------------------

        if "doctor_visit_preparation" in selected_tools:

            try:

                doctor_result = {
                    "success": True,
                    "agent": "Doctor Visit Agent",
                    "patient_name": patient_name,
                    "message": (
                        "Prepare your recent reports, "
                        "current medicines, symptoms, "
                        "and questions for your doctor."
                    )
                }

                results[
                    "doctor_visit_preparation"
                ] = doctor_result

            except Exception as e:

                results[
                    "doctor_visit_preparation"
                ] = {
                    "success": False,
                    "error": str(e)
                }


        # -------------------------------------------------
        # EMERGENCY
        # -------------------------------------------------

        if "emergency" in selected_tools:

            try:

                safety_result = (
                    self.orchestrator
                    .analyze_safety(
                        message
                    )
                )

                results["emergency"] = {
                    "success": True,
                    "safety": safety_result,
                    "guidance": (
                        "If this is an emergency, "
                        "contact local emergency services "
                        "or seek immediate medical attention."
                    )
                }

            except Exception as e:

                results["emergency"] = {
                    "success": False,
                    "error": str(e)
                }


        return results


    # =====================================================
    # GENERATE FINAL RESPONSE
    # =====================================================

    def generate_response(
        self,
        message,
        language,
        intent,
        tool_results,
        safety_result
    ):

        prompt = f"""
You are MediSaathi, a safe multilingual healthcare information assistant.

Your job is to answer the user's question using the relevant information
provided by the healthcare tools.

USER QUESTION:
{message}

LANGUAGE:
{language}

INTENT:
{intent}

RELEVANT TOOL RESULTS:
{json.dumps(tool_results, ensure_ascii=False, default=str)}

SAFETY RESULT:
{json.dumps(safety_result, ensure_ascii=False, default=str)}


RESPONSE INSTRUCTIONS:

1. Answer the user's question directly.

2. Return ONLY the natural-language answer that should be shown
   to the user and spoken by the voice assistant.

3. DO NOT return JSON.

4. DO NOT return a Python dictionary.

5. DO NOT return a list or structured object.

6. DO NOT return tool results.

7. DO NOT return internal agent information.

8. DO NOT mention:
   - tools
   - agents
   - prompts
   - JSON
   - planning
   - internal reasoning
   - workflow

9. DO NOT output numbers alone.

10. Numbers are allowed ONLY when they are part of the actual
    answer, such as:
    - blood test values
    - dates
    - medicine names with dosage information already present
    - percentages
    - temperatures

11. Preserve medical values, dates, medicine names and units exactly
    as provided in the available information.

12. Do not invent medical information.

13. Clearly distinguish recorded information from general explanation.

14. Keep the response concise.

15. Normally use 1 to 4 short sentences.

16. Use short bullet points only when they genuinely make the answer
    easier to understand.

17. Do not repeat the user's question.

18. Do not add unnecessary introductions such as:
    "Sure!"
    "Absolutely!"
    "Of course!"
    "I'd be happy to help!"

19. If the user asks a simple question, give a simple answer.

20. If the user asks for an explanation, explain only what is necessary.

21. Respond in the requested language:
    {language}

SAFETY RULES:

- Never diagnose the user.
- Never prescribe medication.
- Never tell the user to start, stop, increase, or decrease medication.
- Never invent dosage instructions.
- If doctor review is appropriate, mention it briefly.
- If the request appears urgent, prioritize appropriate emergency guidance.
- For emergencies, give clear immediate safety guidance.

IMPORTANT:

The final output must be plain, human-readable language.

The final output must be suitable for BOTH:
1. displaying inside the MediSaathi chat
2. reading aloud using text-to-speech

Return ONLY the final natural-language answer.
"""

        try:

            response = self.client.chat.completions.create(

                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are MediSaathi, a safe multilingual "
                            "healthcare information assistant. "
                            "Always return only natural-language text "
                            "that can be displayed and spoken to the user."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.2
            )

            result = response.choices[0].message.content

            if not result:
                return (
                    "I could not generate a response."
                )

            result = result.strip()

            # Remove accidental markdown code fences
            if (
                result.startswith("```")
                and result.endswith("```")
            ):
                result = result[3:-3].strip()

            return result

        except Exception as e:

            print(
                "Response generation error:",
                str(e)
            )

            return (
                "I could not generate the response right now. "
                "Please try again."
            )


# =========================================================
# SIMPLE TEST
# =========================================================

if __name__ == "__main__":

    print("\n========================================")
    print("       MEDISAATHI AGENT TEST")
    print("========================================")

    try:

        # This test requires an orchestrator.
        print(
            "MediSaathi module loaded successfully."
        )

        print(
            "Use backend/app.py to run the complete system."
        )

    except Exception as e:

        print(
            "Test error:",
            str(e)
        )