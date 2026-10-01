# backend/agents/safety_agent.py

import re


class SafetyAgent:
    """
    Safety Agent

    Responsibilities:
    - Identify potentially urgent information in medical text
    - Flag concerning symptoms or findings
    - Detect medication instructions that may be unclear
    - Recommend seeking appropriate professional help when needed
    - Prevent unsafe AI-generated medical decisions

    This agent does NOT:
    - Diagnose diseases
    - Prescribe medicines
    - Change medication dosage
    - Tell a patient to stop medication
    - Replace a healthcare professional
    """

    def __init__(self):
        self.name = "Safety Agent"

        # Basic safety keywords for the initial hackathon version.
        # Later this can be replaced/enhanced with a medical
        # knowledge base and LLM-based clinical safety reasoning.
        self.urgent_keywords = [
            "chest pain",
            "severe chest pain",
            "difficulty breathing",
            "shortness of breath",
            "cannot breathe",
            "loss of consciousness",
            "unconscious",
            "fainted",
            "seizure",
            "severe bleeding",
            "heavy bleeding",
            "stroke symptoms",
            "sudden weakness",
            "sudden confusion",
            "slurred speech",
            "severe allergic reaction",
            "anaphylaxis"
        ]

        self.warning_keywords = [
            "high fever",
            "persistent vomiting",
            "severe abdominal pain",
            "severe headache",
            "blood in stool",
            "blood in urine",
            "very high blood pressure",
            "low oxygen",
            "oxygen saturation low",
            "abnormal ecg"
        ]

    def analyze_text(self, text):
        """
        Analyze medical text for potentially concerning information.

        Example:

            agent.analyze_text(
                "Patient reports chest pain and difficulty breathing."
            )
        """

        if not text or not text.strip():
            return {
                "success": False,
                "agent": self.name,
                "message": "No medical text provided."
            }

        text_lower = text.lower()

        urgent_findings = self.find_matches(
            text_lower,
            self.urgent_keywords
        )

        warning_findings = self.find_matches(
            text_lower,
            self.warning_keywords
        )

        if urgent_findings:
            risk_level = "urgent"

        elif warning_findings:
            risk_level = "attention_required"

        else:
            risk_level = "no_obvious_safety_flag"

        return {
            "success": True,
            "agent": self.name,
            "risk_level": risk_level,
            "urgent_findings": urgent_findings,
            "warning_findings": warning_findings,
            "recommendation": self.get_recommendation(
                risk_level
            ),
            "safety_note": (
                "This screening identifies potentially concerning "
                "information from the provided text. It is not a diagnosis."
            )
        }

    def find_matches(self, text, keywords):
        """
        Find safety-related keywords present in the text.
        """

        matches = []

        for keyword in keywords:

            if keyword.lower() in text:

                if keyword not in matches:
                    matches.append(keyword)

        return matches

    def get_recommendation(self, risk_level):
        """
        Generate a safety-oriented recommendation.

        The system does not make a diagnosis.
        """

        if risk_level == "urgent":
            return (
                "Potentially urgent information was detected. "
                "Seek immediate professional medical evaluation "
                "or contact local emergency services, especially "
                "if the symptoms are happening now or are severe."
            )

        if risk_level == "attention_required":
            return (
                "A potentially concerning finding was detected. "
                "Consider contacting a healthcare professional "
                "for appropriate evaluation."
            )

        return (
            "No obvious safety flag was detected from the provided "
            "text. This does not rule out a medical problem."
        )

    def check_medication_safety(self, medicine):
        """
        Check whether medication instructions contain enough
        information to safely organize them.

        This does NOT determine whether a medication is medically
        appropriate.
        """

        if not medicine:
            return {
                "success": False,
                "agent": self.name,
                "message": "No medication information provided."
            }

        name = medicine.get("name")

        dosage = medicine.get("dosage")
        frequency = medicine.get("frequency")
        timing = medicine.get("timing")

        issues = []

        if not name:
            issues.append("Medicine name is missing.")

        if not dosage:
            issues.append("Dosage information is missing.")

        if not frequency:
            issues.append("Frequency information is missing.")

        if not timing:
            issues.append(
                "Timing information is not specified."
            )

        if issues:
            status = "needs_clarification"
        else:
            status = "information_complete"

        return {
            "success": True,
            "agent": self.name,
            "medicine": name,
            "status": status,
            "issues": issues,
            "message": (
                "Do not guess missing medication instructions. "
                "Confirm unclear information with the prescription "
                "or a healthcare professional."
            )
        }

    def validate_ai_response(self, response):
        """
        Basic safety check for AI-generated medical responses.

        This helps prevent the application from presenting
        diagnosis or medication-change instructions as facts.
        """

        if not response:
            return {
                "safe": False,
                "message": "Empty response."
            }

        response_lower = response.lower()

        unsafe_patterns = [
            "you definitely have",
            "you have cancer",
            "stop taking your medicine",
            "start taking",
            "increase your dose",
            "decrease your dose",
            "double your dose",
            "skip your medication"
        ]

        detected = []

        for pattern in unsafe_patterns:

            if pattern in response_lower:
                detected.append(pattern)

        if detected:
            return {
                "safe": False,
                "agent": self.name,
                "detected_issues": detected,
                "message": (
                    "The response may contain unsafe medical "
                    "diagnostic or medication instructions and "
                    "should be reviewed before being shown to the user."
                )
            }

        return {
            "safe": True,
            "agent": self.name,
            "message": "No obvious unsafe instruction detected."
        }


# ---------------------------------------------------------
# Simple test
# ---------------------------------------------------------

if __name__ == "__main__":

    agent = SafetyAgent()

    print("\n--- Urgent Symptom Test ---")

    result = agent.analyze_text(
        "Patient reports chest pain and difficulty breathing."
    )

    print(result)

    print("\n--- Normal Text Test ---")

    result = agent.analyze_text(
        "Patient has mild tiredness."
    )

    print(result)

    print("\n--- Medication Safety Test ---")

    medicine = {
        "name": "Paracetamol",
        "dosage": "500 mg",
        "frequency": "twice daily",
        "timing": "after food"
    }

    result = agent.check_medication_safety(
        medicine
    )

    print(result)

    print("\n--- AI Response Safety Test ---")

    result = agent.validate_ai_response(
        "You definitely have a serious disease. "
        "Stop taking your medicine."
    )

    print(result)