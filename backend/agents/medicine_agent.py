# backend/agents/medicine_agent.py

import re


class MedicineAgent:
    """
    Medicine Agent

    Responsibilities:
    - Organize prescribed medicines
    - Extract and preserve dosage, form, frequency, and duration information
    - Explain general medicine purpose
    - Create a schedule from explicit prescription instructions
    - Flag unclear instructions

    This agent does NOT:
    - Diagnose diseases
    - Prescribe medicines
    - Change dosage
    - Recommend starting/stopping medicines
    """

    def __init__(self):
        self.name = "Medicine Agent"

        # Basic examples for demo/hackathon purposes.
        self.medicine_info = {
            "paracetamol": {
                "purpose": "Commonly used to reduce pain and fever.",
                "category": "Pain reliever / fever reducer",
            },
            "acetaminophen": {
                "purpose": "Commonly used to reduce pain and fever.",
                "category": "Pain reliever / fever reducer",
            },
            "ibuprofen": {
                "purpose": "Commonly used to reduce pain, inflammation, and fever.",
                "category": "NSAID",
            },
            "amoxicillin": {
                "purpose": "An antibiotic used for certain bacterial infections.",
                "category": "Antibiotic",
            },
            "metformin": {
                "purpose": "Commonly used to help manage blood glucose in type 2 diabetes.",
                "category": "Antidiabetic medicine",
            },
            "atorvastatin": {
                "purpose": "Used to lower certain types of cholesterol.",
                "category": "Statin",
            },
            "omeprazole": {
                "purpose": "Used to reduce stomach acid production.",
                "category": "Proton pump inhibitor",
            },
            "pantoprazole": {
                "purpose": "Used to reduce stomach acid production.",
                "category": "Proton pump inhibitor",
            },
            "azithromycin": {
                "purpose": "An antibiotic used for certain bacterial infections.",
                "category": "Macrolide antibiotic",
            },
            "cetirizine": {
                "purpose": "Used to relieve allergy symptoms such as runny nose or itching.",
                "category": "Antihistamine",
            },
            "losartan": {
                "purpose": "Used to manage high blood pressure.",
                "category": "Angiotensin II receptor blocker",
            },
            "amlodipine": {
                "purpose": "Used to manage high blood pressure and chest pain.",
                "category": "Calcium channel blocker",
            },
        }

    def analyze(self, medicines):
        """
        Analyze a list of prescribed medicines.

        Expected input:
        [
            {
                "name": "Paracetamol",
                "dosage": "500 mg",
                "form": "Tablet",
                "frequency": "twice daily",
                "duration": "5 days",
                "timing": "after food"
            }
        ]
        """
        if not medicines:
            return {
                "success": False,
                "agent": self.name,
                "medicines": [],
                "message": "No medicine information provided.",
            }

        results = []

        for medicine in medicines:
            if isinstance(medicine, str):
                medicine = {
                    "name": medicine
                }

            name = medicine.get("name", "").strip()

            if not name:
                continue

            dosage = medicine.get("dosage") or medicine.get("dose")
            form = medicine.get("form")
            frequency = medicine.get("frequency")
            duration = medicine.get("duration")
            timing = medicine.get("timing")

            info = self.get_medicine_info(name)

            schedule = self.create_schedule(
                frequency=frequency,
                timing=timing,
            )

            results.append({
                "name": name,
                "medicine": name,
                "dosage": dosage,
                "dose": dosage,
                "form": form,
                "frequency": frequency,
                "duration": duration,
                "timing": timing,
                "purpose": info["purpose"],
                "category": info["category"],
                "schedule": schedule,
                "instruction_status": self.get_instruction_status(
                    frequency,
                    timing,
                ),
            })

        return {
            "success": True,
            "agent": self.name,
            "medicines": results,
            "safety_note": (
                "Medication information is organized from the provided "
                "prescription/document. Do not change the prescribed dose "
                "or stop/start medication without consulting a healthcare professional."
            ),
        }

    def get_medicine_info(self, medicine_name):
        """
        Return general information about a medicine.
        """
        key = medicine_name.lower().strip()

        # Remove common dosage information
        key = re.sub(
            r"\b\d+(?:\.\d+)?\s*(mg|mcg|µg|ug|g|gm|ml|iu)\b",
            "",
            key,
        ).strip()

        for med_key, med_data in self.medicine_info.items():
            if med_key in key or key in med_key:
                return med_data

        return {
            "purpose": "General medicine information is not available in the local knowledge base.",
            "category": "Prescribed medication",
        }

    def get_instruction_status(self, frequency, timing):
        """
        Determine whether enough prescription information exists
        to construct a useful schedule.
        """
        if not frequency:
            return "unclear_frequency"

        if not timing:
            return "frequency_available_timing_unclear"

        return "clear"

    def create_schedule(self, frequency=None, timing=None):
        """
        Create a simple schedule based ONLY on explicit instructions.
        No medical assumptions are made.
        """
        if not frequency:
            return {
                "status": "unclear",
                "message": "Prescription frequency was not provided.",
            }

        frequency_lower = frequency.lower().strip()
        schedule = []

        if (
            "once" in frequency_lower
            or "1 time" in frequency_lower
            or frequency_lower in ["od", "q.d.", "qd", "1-0-0", "0-1-0", "0-0-1"]
        ):
            schedule.append(timing or "Once daily - time not specified")

        elif (
            "twice" in frequency_lower
            or "2 times" in frequency_lower
            or frequency_lower in ["bid", "b.i.d.", "bd", "1-0-1"]
        ):
            schedule.extend([
                timing or "First daily dose - time not specified",
                "Second daily dose - time not specified",
            ])

        elif (
            "three times" in frequency_lower
            or "3 times" in frequency_lower
            or "thrice" in frequency_lower
            or frequency_lower in ["tid", "t.i.d.", "tds", "1-1-1"]
        ):
            schedule.extend([
                timing or "First daily dose - time not specified",
                "Second daily dose - time not specified",
                "Third daily dose - time not specified",
            ])

        elif (
            "four times" in frequency_lower
            or "4 times" in frequency_lower
            or frequency_lower in ["qid", "q.i.d.", "1-1-1-1"]
        ):
            schedule.extend([
                timing or "First daily dose - time not specified",
                "Second daily dose - time not specified",
                "Third daily dose - time not specified",
                "Fourth daily dose - time not specified",
            ])

        elif "bedtime" in frequency_lower or "night" in frequency_lower:
            schedule.append("At bedtime")

        elif "morning" in frequency_lower:
            schedule.append("Morning")

        else:
            return {
                "status": "recorded",
                "items": [f"Take as directed: {frequency}"],
            }

        return {
            "status": "generated_from_prescription",
            "items": schedule,
        }


if __name__ == "__main__":
    agent = MedicineAgent()
    medicines = [
        {
            "name": "Paracetamol",
            "dosage": "500 mg",
            "form": "Tablet",
            "frequency": "Once daily",
            "duration": "5 days",
            "timing": "after food",
        }
    ]
    result = agent.analyze(medicines)
    print("\n--- Medicine Agent Test ---")
    print(result)