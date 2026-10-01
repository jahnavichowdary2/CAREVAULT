class ClinicalAgent:
    """
    Clinical Analysis Agent

    Responsibilities:
    - Analyze structured medical findings
    - Compare lab values with reference ranges when available
    - Identify potentially significant findings
    - Explain findings in simple language
    - Identify possible health conditions for discussion with a doctor

    IMPORTANT:
    This agent does NOT provide a confirmed diagnosis.
    It does NOT prescribe, start, stop, or change medicines.
    """

    def __init__(self):
        self.name = "Clinical Analysis Agent"

    def analyze(self, document_data):

        if not document_data:
            return {
                "success": False,
                "agent": self.name,
                "message": "No document data received."
            }

        lab_results = document_data.get("lab_results", [])

        findings = []

        for result in lab_results:
            finding = self.analyze_lab_result(result)
            findings.append(finding)

        return {
            "success": True,
            "agent": self.name,
            "findings": findings,
            "doctor_review_recommended": any(
                finding["doctor_review"]
                for finding in findings
            ),
            "medical_disclaimer": (
                "This information is for educational purposes only. "
                "It is not a confirmed medical diagnosis. "
                "Laboratory results should be interpreted using "
                "the laboratory's reference ranges and the patient's "
                "clinical context. Consult a qualified healthcare "
                "professional for medical decisions."
            )
        }

    # -----------------------------------------
    # ANALYZE LAB RESULT
    # -----------------------------------------

    def analyze_lab_result(self, result):

        test_name = result.get(
            "test",
            "Unknown Test"
        )

        value = result.get("value")

        unit = result.get("unit")

        reference_range = result.get(
            "reference_range"
        )

        # Try to convert the value to a number
        numeric_value = self.to_number(value)

        # Default status
        status = "Reference range unavailable"

        # Compare against reference range if available
        if numeric_value is not None and reference_range:

            lower, upper = self.parse_reference_range(
                reference_range
            )

            if lower is not None and upper is not None:

                if numeric_value < lower:
                    status = "Low"

                elif numeric_value > upper:
                    status = "High"

                else:
                    status = "Within reference range"

        explanation = self.create_explanation(
            test_name,
            value,
            unit,
            status
        )

        possible_conditions = self.get_possible_conditions(
            test_name,
            status
        )

        return {
            "test": test_name,
            "value": value,
            "unit": unit,
            "reference_range": reference_range,
            "status": status,
            "explanation": explanation,
            "possible_conditions": possible_conditions,
            "doctor_review": True
        }

    # -----------------------------------------
    # NUMBER CONVERSION
    # -----------------------------------------

    def to_number(self, value):

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    # -----------------------------------------
    # REFERENCE RANGE
    # -----------------------------------------

    def parse_reference_range(self, reference_range):

        if not reference_range:
            return None, None

        text = str(reference_range)

        # Examples:
        # 12-16
        # 70 - 100
        # 0.5-1.2

        import re

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)",
            text
        )

        if not match:
            return None, None

        lower = float(match.group(1))
        upper = float(match.group(2))

        return lower, upper

    # -----------------------------------------
    # EXPLANATION
    # -----------------------------------------

    def create_explanation(
        self,
        test_name,
        value,
        unit,
        status
    ):

        value_text = f"{value}"

        if unit:
            value_text += f" {unit}"

        if status == "Low":

            return (
                f"{test_name} is reported as "
                f"{value_text}, which is below the "
                "reference range provided in the report. "
                "The result should be discussed with a "
                "qualified healthcare professional."
            )

        elif status == "High":

            return (
                f"{test_name} is reported as "
                f"{value_text}, which is above the "
                "reference range provided in the report. "
                "The result should be discussed with a "
                "qualified healthcare professional."
            )

        elif status == "Within reference range":

            return (
                f"{test_name} is reported as "
                f"{value_text}, which falls within the "
                "reference range provided in the report."
            )

        return (
            f"{test_name} is reported as "
            f"{value_text}. A reference range was not "
            "available, so this result cannot be classified "
            "as high or low by this agent."
        )

    # -----------------------------------------
    # POSSIBLE CONDITIONS
    # -----------------------------------------

    def get_possible_conditions(
        self,
        test_name,
        status
    ):

        if status not in ["Low", "High"]:
            return []

        # These are possibilities for discussion,
        # NOT diagnoses.

        conditions = {

            "Hemoglobin": {
                "Low": [
                    "Anemia or another cause of low hemoglobin "
                    "may be considered by a healthcare professional."
                ],
                "High": [
                    "An elevated hemoglobin level may have "
                    "several possible causes and should be "
                    "interpreted clinically."
                ]
            },

            "Glucose": {
                "High": [
                    "An elevated glucose result may require "
                    "further evaluation depending on the test "
                    "type, timing, and clinical context."
                ],
                "Low": [
                    "A low glucose result may require "
                    "clinical evaluation depending on symptoms "
                    "and circumstances."
                ]
            },

            "Creatinine": {
                "High": [
                    "An elevated creatinine result may be "
                    "associated with reduced kidney function "
                    "among other possible causes."
                ]
            },

            "WBC": {
                "High": [
                    "An elevated white blood cell count can "
                    "occur for several reasons, including "
                    "infection or inflammation."
                ],
                "Low": [
                    "A low white blood cell count can have "
                    "several possible causes and may require "
                    "clinical evaluation."
                ]
            },

            "Platelets": {
                "High": [
                    "An elevated platelet count can have "
                    "multiple possible causes and should be "
                    "interpreted clinically."
                ],
                "Low": [
                    "A low platelet count can have multiple "
                    "possible causes and should be evaluated "
                    "by a healthcare professional."
                ]
            }
        }

        return conditions.get(
            test_name,
            {}
        ).get(
            status,
            []
        )