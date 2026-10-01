# backend/agents/medication_agent.py


class MedicationAgent:
    """
    Medication Schedule Agent

    Responsibilities:
    - Organize medication schedules
    - Convert prescription frequency into a simple schedule
    - Identify missing or unclear medication instructions

    This agent does NOT:
    - Prescribe medicines
    - Change dosage
    - Recommend stopping medication
    - Recommend starting medication
    """

    def __init__(self):
        self.name = "Medication Schedule Agent"

    def create_schedule(self, medicines):
        """
        Create a medication schedule from prescription instructions.

        Expected input:

        [
            {
                "name": "Paracetamol",
                "dosage": "500 mg",
                "frequency": "twice daily",
                "timing": "after food"
            }
        ]
        """

        if not medicines:
            return {
                "success": False,
                "agent": self.name,
                "message": "No medication information provided."
            }

        schedules = []

        for medicine in medicines:

            if isinstance(medicine, str):
                medicine = {
                    "name": medicine
                }

            name = medicine.get("name", "").strip()

            if not name:
                continue

            dosage = medicine.get("dosage")
            frequency = medicine.get("frequency")
            timing = medicine.get("timing")

            schedule = self.interpret_frequency(
                frequency,
                timing
            )

            schedules.append({
                "medicine": name,
                "dosage": dosage,
                "frequency": frequency,
                "prescribed_timing": timing,
                "schedule": schedule,
                "status": self.get_status(
                    frequency,
                    timing
                )
            })

        return {
            "success": True,
            "agent": self.name,
            "schedules": schedules,
            "safety_note": (
                "This schedule only organizes the instructions "
                "provided in the prescription. Do not change "
                "medication dosage or timing without consulting "
                "a healthcare professional."
            )
        }

    def interpret_frequency(self, frequency, timing):
        """
        Convert common prescription frequency descriptions
        into a simple schedule.

        The agent does not invent exact clock times.
        """

        if not frequency:
            return {
                "status": "unclear",
                "times": [],
                "message": "Medication frequency was not provided."
            }

        frequency_lower = frequency.lower().strip()

        if (
            "once daily" in frequency_lower
            or "once a day" in frequency_lower
            or "1 time" in frequency_lower
        ):
            return {
                "status": "ready",
                "times": [
                    timing if timing else "Time not specified"
                ]
            }

        if (
            "twice daily" in frequency_lower
            or "twice a day" in frequency_lower
            or "2 times" in frequency_lower
        ):
            return {
                "status": "ready",
                "times": [
                    "First dose - " + (
                        timing if timing else "time not specified"
                    ),
                    "Second dose - " + (
                        timing if timing else "time not specified"
                    )
                ]
            }

        if (
            "three times daily" in frequency_lower
            or "three times a day" in frequency_lower
            or "3 times" in frequency_lower
        ):
            return {
                "status": "ready",
                "times": [
                    "First dose - " + (
                        timing if timing else "time not specified"
                    ),
                    "Second dose - " + (
                        timing if timing else "time not specified"
                    ),
                    "Third dose - " + (
                        timing if timing else "time not specified"
                    )
                ]
            }

        if (
            "four times daily" in frequency_lower
            or "four times a day" in frequency_lower
            or "4 times" in frequency_lower
        ):
            return {
                "status": "ready",
                "times": [
                    "First dose - " + (
                        timing if timing else "time not specified"
                    ),
                    "Second dose - " + (
                        timing if timing else "time not specified"
                    ),
                    "Third dose - " + (
                        timing if timing else "time not specified"
                    ),
                    "Fourth dose - " + (
                        timing if timing else "time not specified"
                    )
                ]
            }

        if "morning" in frequency_lower:
            return {
                "status": "ready",
                "times": ["Morning"]
            }

        if "afternoon" in frequency_lower:
            return {
                "status": "ready",
                "times": ["Afternoon"]
            }

        if "evening" in frequency_lower:
            return {
                "status": "ready",
                "times": ["Evening"]
            }

        if "night" in frequency_lower:
            return {
                "status": "ready",
                "times": ["Night"]
            }

        if "bedtime" in frequency_lower:
            return {
                "status": "ready",
                "times": ["Bedtime"]
            }

        return {
            "status": "unclear",
            "times": [],
            "message": (
                "The medication frequency could not be safely "
                "interpreted. Please follow the prescription "
                "or confirm with a healthcare professional."
            )
        }

    def get_status(self, frequency, timing):
        """
        Determine whether enough information exists
        to create a schedule.
        """

        if not frequency:
            return "missing_frequency"

        if not timing:
            return "timing_not_specified"

        return "complete"

    def get_upcoming_doses(self, medicines):
        """
        Generate a simple list of medication instructions.

        This only organizes the provided prescription.
        It does not create medical recommendations.
        """

        schedules = self.create_schedule(medicines)

        if not schedules.get("success"):
            return schedules

        upcoming = []

        for item in schedules["schedules"]:

            for dose in item["schedule"].get("times", []):

                upcoming.append({
                    "medicine": item["medicine"],
                    "dosage": item["dosage"],
                    "instruction": dose
                })

        return {
            "success": True,
            "agent": self.name,
            "upcoming_doses": upcoming
        }


# ---------------------------------------------------------
# Simple test
# ---------------------------------------------------------

if __name__ == "__main__":

    agent = MedicationAgent()

    medicines = [
        {
            "name": "Paracetamol",
            "dosage": "500 mg",
            "frequency": "twice daily",
            "timing": "after food"
        },
        {
            "name": "Metformin",
            "dosage": "500 mg",
            "frequency": "once daily",
            "timing": "after dinner"
        }
    ]

    print("\n--- Medication Agent Test ---")

    result = agent.create_schedule(medicines)

    print(result)

    print("\n--- Upcoming Doses ---")

    upcoming = agent.get_upcoming_doses(medicines)

    print(upcoming)