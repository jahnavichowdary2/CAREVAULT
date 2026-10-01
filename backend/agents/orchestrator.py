"""
CareVault / MediSaathi HealthVault
Orchestrator Agent

The Orchestrator is the central controller of the
multi-agent healthcare system.

Workflow:

Patient / Frontend
        ↓
Document Agent
        ↓
Clinical Agent
        ↓
Medicine Agent
        ↓
Medication Agent
        ↓
Trend Agent
        ↓
Safety Agent
        ↓
Doctor Visit Agent
        ↓
Language Agent
        ↓
Final Response
"""

import sys
import os


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =========================================================
# IMPORT ALL AGENTS
# =========================================================

from backend.agents.patient_agent import PatientInteractionAgent
from backend.agents.consent_agent import ConsentAccessAgent
from backend.agents.document_agent import DocumentAgent
from backend.agents.clinical_agent import ClinicalAgent
from backend.agents.medicine_agent import MedicineAgent
from backend.agents.trend_agent import TrendAgent
from backend.agents.medication_agent import MedicationAgent
from backend.agents.safety_agent import SafetyAgent
from backend.agents.language_agent import LanguageAgent
from backend.agents.doctor_visit_agent import DoctorVisitAgent
from backend.agents.medisaathi_agent import MediSaathiAgent


# =========================================================
# ORCHESTRATOR
# =========================================================

class OrchestratorAgent:

    def __init__(self):

        print("Initializing CareVault Orchestrator...")

        # -------------------------------------------------
        # Initialize all agents
        # -------------------------------------------------

        self.patient_agent = PatientInteractionAgent()
        self.consent_agent = ConsentAccessAgent()
        self.document_agent = DocumentAgent()
        self.clinical_agent = ClinicalAgent()
        self.medicine_agent = MedicineAgent()
        self.trend_agent = TrendAgent()
        self.medication_agent = MedicationAgent()
        self.safety_agent = SafetyAgent()
        self.language_agent = LanguageAgent()
        self.doctor_visit_agent = DoctorVisitAgent()
        self.medisaathi_agent = MediSaathiAgent(self)

        print("All agents initialized successfully.")


    # =====================================================
    # MEDISAATHI CENTRAL AGENT
    # =====================================================

    def process_agent_message(
        self,
        message,
        language="English",
        patient_name="User",
        measurements=None,
        health_history=None
    ):
        """Process a message through the MediSaathi central agent."""

        return self.medisaathi_agent.process(
            message=message,
            language=language,
            patient_name=patient_name,
            measurements=measurements,
            health_history=health_history
        )


    # =====================================================
    # 1. PATIENT CHAT / INTENT
    # =====================================================

    def process_patient_message(
        self,
        message,
        language="English"
    ):
        """
        Process a patient's question and identify
        which specialist agent should handle it.
        """

        return self.patient_agent.process_message(
            message=message,
            language=language
        )


    # =====================================================
    # 2. DOCUMENT ANALYSIS
    # =====================================================

    def analyze_document(
        self,
        document_text
    ):
        """
        Send medical document text to Document Agent.
        """

        return self.document_agent.analyze(
            document_text
        )


    # =====================================================
    # 3. CLINICAL ANALYSIS
    # =====================================================

    def analyze_clinical_findings(
        self,
        document_data
    ):
        """
        Analyze extracted laboratory findings.
        """

        return self.clinical_agent.analyze(
            document_data
        )


    # =====================================================
    # 4. MEDICINE ANALYSIS
    # =====================================================

    def analyze_medicines(
        self,
        medicines
    ):
        """
        Analyze medicines extracted from the document.
        """

        if not medicines:
            return {
                "success": True,
                "agent": "Medicine Agent",
                "medicines": [],
                "message": "No medicines were detected."
            }

        return self.medicine_agent.analyze(
            medicines
        )


    # =====================================================
    # 5. MEDICATION SCHEDULE
    # =====================================================

    def create_medication_schedule(
        self,
        medicines
    ):
        """
        Organize prescribed medicines into a schedule.

        The Medication Agent does not invent timings.
        """

        if not medicines:
            return {
                "success": True,
                "agent": "Medication Schedule Agent",
                "schedules": [],
                "message": "No medicines were detected."
            }

        return self.medication_agent.create_schedule(
            medicines
        )


    # =====================================================
    # 6. TREND ANALYSIS
    # =====================================================

    def analyze_health_trends(
        self,
        measurements
    ):
        """
        Compare medical measurements over time.

        Example:

        [
            {
                "test": "Hemoglobin",
                "value": 10.2,
                "unit": "g/dL",
                "date": "2026-09-28"
            },
            {
                "test": "Hemoglobin",
                "value": 10.8,
                "unit": "g/dL",
                "date": "2026-08-28"
            }
        ]
        """

        if not measurements:
            return {
                "success": True,
                "agent": "Trend Agent",
                "trends": [],
                "message": (
                    "No historical measurements were provided "
                    "for trend analysis."
                )
            }

        return self.trend_agent.analyze(
            measurements
        )


    # =====================================================
    # 7. SAFETY ANALYSIS
    # =====================================================

    def analyze_safety(
        self,
        text
    ):
        """
        Check provided medical text for potential
        safety-related concerns.
        """

        return self.safety_agent.analyze_text(
            text
        )


    # =====================================================
    # 8. MEDICATION SAFETY
    # =====================================================

    def check_medication_safety(
        self,
        medicine
    ):
        """
        Check whether medication instructions contain
        enough information to organize safely.
        """

        return self.safety_agent.check_medication_safety(
            medicine
        )


    # =====================================================
    # 9. DOCTOR VISIT SUMMARY
    # =====================================================

    def prepare_doctor_visit(
        self,
        patient_name,
        reports=None,
        medications=None,
        trends=None,
        health_history=None
    ):
        """
        Generate a doctor-visit summary.
        """

        return self.doctor_visit_agent.process(
            patient_name=patient_name,
            reports=reports,
            medications=medications,
            trends=trends,
            health_history=health_history
        )


    # =====================================================
    # 10. LANGUAGE PROCESSING
    # =====================================================

    def process_language(
        self,
        text,
        target_language="English"
    ):
        """
        Translate medical information into the
        patient's preferred language.
        """

        return self.language_agent.process(
            text=text,
            target_language=target_language
        )


    # =====================================================
    # 11. CONSENT FUNCTIONS
    # =====================================================

    def request_access(
        self,
        requester_id,
        owner_id,
        scope,
        reason=None
    ):
        """
        Request access to another user's health records.
        """

        return self.consent_agent.request_access(
            requester_id=requester_id,
            owner_id=owner_id,
            scope=scope,
            reason=reason
        )


    def grant_access(
        self,
        request_id,
        owner_id
    ):
        """
        Grant a pending consent request.
        """

        return self.consent_agent.grant_access(
            request_id=request_id,
            owner_id=owner_id
        )


    def deny_access(
        self,
        request_id,
        owner_id
    ):
        """
        Deny a pending consent request.
        """

        return self.consent_agent.deny_access(
            request_id=request_id,
            owner_id=owner_id
        )


    def revoke_access(
        self,
        request_id,
        owner_id
    ):
        """
        Revoke previously granted access.
        """

        return self.consent_agent.revoke_access(
            request_id=request_id,
            owner_id=owner_id
        )


    def check_access(
        self,
        requester_id,
        owner_id,
        scope
    ):
        """
        Check whether access is allowed.
        """

        return self.consent_agent.check_access(
            requester_id=requester_id,
            owner_id=owner_id,
            scope=scope
        )


    # =====================================================
    # 12. COMPLETE MEDICAL DOCUMENT WORKFLOW
    # =====================================================

    def process_health_document(
        self,
        patient_name,
        document_text,
        target_language="English",
        measurements=None,
        health_history=None
    ):
        """
        MAIN MULTI-AGENT WORKFLOW

        Document
            ↓
        Document Agent
            ↓
        Clinical Agent
            ↓
        Medicine Agent
            ↓
        Medication Agent
            ↓
        Trend Agent
            ↓
        Safety Agent
            ↓
        Doctor Visit Agent
            ↓
        Language Agent
            ↓
        Final Result
        """

        # -------------------------------------------------
        # Validate input
        # -------------------------------------------------

        if not document_text or not document_text.strip():

            return {
                "success": False,
                "error": "No medical document text was provided."
            }


        # =================================================
        # STEP 1 — DOCUMENT AGENT
        # =================================================

        print("\n[1/8] Running Document Agent...")

        document_result = self.document_agent.analyze(
            document_text
        )

        if not document_result.get("success"):

            return {
                "success": False,
                "stage": "document",
                "error": document_result.get(
                    "message",
                    "Document Agent failed."
                )
            }

        print("Document Agent: SUCCESS")


        # =================================================
        # STEP 2 — CLINICAL AGENT
        # =================================================

        print("\n[2/8] Running Clinical Agent...")

        clinical_result = self.clinical_agent.analyze(
            document_result
        )

        print("Clinical Agent: SUCCESS")


        # =================================================
        # STEP 3 — MEDICINE AGENT
        # =================================================

        print("\n[3/8] Running Medicine Agent...")

        extracted_medicines = document_result.get(
            "medicines",
            []
        )

        medicine_result = self.analyze_medicines(
            extracted_medicines
        )

        print("Medicine Agent: SUCCESS")


        # =================================================
        # STEP 4 — MEDICATION AGENT
        # =================================================

        print("\n[4/8] Running Medication Agent...")

        medication_result = self.create_medication_schedule(
            extracted_medicines
        )

        print("Medication Agent: SUCCESS")


        # =================================================
        # STEP 5 — TREND AGENT
        # =================================================

        print("\n[5/8] Running Trend Agent...")

        # Extract current report measurements
        report_date = (
            document_result.get("dates", [None])[0]
            if document_result.get("dates")
            else "Current report"
        )

        current_measurements = []
        for lab in document_result.get("lab_results", []):
            test_val = lab.get("value")
            test_name = lab.get("test")
            test_unit = lab.get("unit")
            if test_val is not None and test_name:
                current_measurements.append({
                    "test": test_name,
                    "value": test_val,
                    "unit": test_unit,
                    "date": report_date,
                })

        # Combine historical measurements with current document measurements
        all_measurements = []
        if measurements:
            if isinstance(measurements, list):
                all_measurements.extend(measurements)
            elif isinstance(measurements, dict):
                for t_name, recs in measurements.items():
                    if isinstance(recs, list):
                        for r in recs:
                            if isinstance(r, dict):
                                rc = r.copy()
                                rc["test"] = t_name
                                all_measurements.append(rc)

        for cm in current_measurements:
            if not any(
                m.get("test") == cm["test"]
                and str(m.get("value")) == str(cm["value"])
                and m.get("date") == cm["date"]
                for m in all_measurements
            ):
                all_measurements.append(cm)

        trend_result = self.analyze_health_trends(
            all_measurements
        )

        print("Trend Agent: SUCCESS")


        # =================================================
        # STEP 6 — SAFETY AGENT
        # =================================================

        print("\n[6/8] Running Safety Agent...")

        safety_text = document_text

        # Add clinical explanations to the safety input
        clinical_findings = clinical_result.get(
            "findings",
            []
        )

        for finding in clinical_findings:

            explanation = finding.get(
                "explanation"
            )

            if explanation:
                safety_text += "\n" + explanation

        safety_result = self.safety_agent.analyze_text(
            safety_text
        )

        print("Safety Agent: SUCCESS")


        # =================================================
        # STEP 7 — DOCTOR VISIT AGENT
        # =================================================

        print("\n[7/8] Running Doctor Visit Agent...")

        # Compile rich findings from clinical agent and document agent
        detailed_findings = []
        for cf in clinical_result.get("findings", []):
            t = cf.get("test", "Test")
            v = cf.get("value", "")
            u = cf.get("unit") or ""
            s = cf.get("status", "")
            r = cf.get("reference_range")
            f_str = f"{t}: {v} {u} ({s}"
            if r:
                f_str += f", Reference: {r}"
            f_str += ")"
            if f_str not in detailed_findings:
                detailed_findings.append(f_str)

        for df in document_result.get("findings", []):
            if df not in detailed_findings:
                detailed_findings.append(df)

        if not detailed_findings:
            for lr in document_result.get("lab_results", []):
                detailed_findings.append(
                    f"{lr.get('test')}: {lr.get('value')} {lr.get('unit') or ''}"
                )

        reports = [
            {
                "report": document_result.get(
                    "document_type",
                    "Medical Document"
                ),
                "date": (
                    document_result.get("dates", [None])[0]
                    if document_result.get("dates")
                    else None
                ),
                "findings": detailed_findings if detailed_findings else ["No specific abnormalities noted in report."],
            }
        ]

        # Use Medicine Agent output for doctor summary
        doctor_medications = medicine_result.get(
            "medicines",
            []
        )

        doctor_trends = trend_result.get(
            "trends",
            []
        )

        doctor_result = self.prepare_doctor_visit(
            patient_name=patient_name,
            reports=reports,
            medications=doctor_medications,
            trends=doctor_trends,
            health_history=health_history
        )

        if not doctor_result.get("success"):

            print("Doctor Visit Agent: FAILED")

            doctor_summary = None

        else:

            print("Doctor Visit Agent: SUCCESS")

            doctor_summary = doctor_result.get(
                "doctor_visit_summary"
            )


        # =================================================
        # SAFETY VALIDATION OF AI SUMMARY
        # =================================================

        summary_safety = None

        if doctor_summary:

            summary_safety = (
                self.safety_agent.validate_ai_response(
                    doctor_summary
                )
            )


        # =================================================
        # STEP 8 — LANGUAGE AGENT
        # =================================================

        print("\n[8/8] Running Language Agent...")

        translated_summary = None
        language_result = None

        if doctor_summary:

            language_result = self.process_language(
                text=doctor_summary,
                target_language=target_language
            )

            if language_result.get("success"):

                translated_summary = language_result.get(
                    "translated_text"
                )

                print("Language Agent: SUCCESS")

            else:

                print("Language Agent: FAILED")


        # =================================================
        # FINAL RESULT
        # =================================================

        return {
            "success": True,

            "patient_name": patient_name,

            "document": document_result,

            "clinical_analysis": clinical_result,

            "medicine_analysis": medicine_result,

            "medication_schedule": medication_result,

            "health_trends": trend_result,

            "measurements": current_measurements,

            "safety_analysis": safety_result,

            "doctor_visit": doctor_result,

            "doctor_summary_safety": summary_safety,

            "language": language_result,

            "final_summary": translated_summary
        }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("\n")
    print("==============================================")
    print("      CAREVAULT MULTI-AGENT TEST")
    print("==============================================")


    try:

        # -------------------------------------------------
        # Create Orchestrator
        # -------------------------------------------------

        orchestrator = OrchestratorAgent()


        # -------------------------------------------------
        # Sample medical document
        # -------------------------------------------------

        sample_document = """
        Complete Blood Count

        Date: 28/09/2026

        Hemoglobin: 10.2 g/dL
        Glucose: 96 mg/dL

        Prescription:
        Paracetamol tablet
        """


        # -------------------------------------------------
        # Historical measurements
        # -------------------------------------------------

        measurements = [

            {
                "test": "Hemoglobin",
                "value": 10.8,
                "unit": "g/dL",
                "date": "2026-08-28"
            },

            {
                "test": "Hemoglobin",
                "value": 10.2,
                "unit": "g/dL",
                "date": "2026-09-28"
            }
        ]


        # -------------------------------------------------
        # Run complete workflow
        # -------------------------------------------------

        result = orchestrator.process_health_document(

            patient_name="Test Patient",

            document_text=sample_document,

            target_language="English",

            measurements=measurements,

            health_history=[
                "Previous blood report available."
            ]
        )


        # -------------------------------------------------
        # Display result
        # -------------------------------------------------

        print("\n")
        print("==============================================")
        print("              FINAL RESULT")
        print("==============================================")


        if result.get("success"):

            print("\nOVERALL STATUS: SUCCESS")


            print("\n--- DOCUMENT ---")

            print(
                result["document"].get(
                    "document_type"
                )
            )


            print("\n--- CLINICAL ANALYSIS ---")

            print(
                result["clinical_analysis"].get(
                    "findings"
                )
            )


            print("\n--- MEDICINES ---")

            print(
                result["medicine_analysis"].get(
                    "medicines"
                )
            )


            print("\n--- MEDICATION SCHEDULE ---")

            print(
                result["medication_schedule"].get(
                    "schedules"
                )
            )


            print("\n--- HEALTH TRENDS ---")

            print(
                result["health_trends"].get(
                    "trends"
                )
            )


            print("\n--- SAFETY ---")

            print(
                result["safety_analysis"].get(
                    "risk_level"
                )
            )


            print("\n--- DOCTOR SUMMARY ---")

            print(
                result["doctor_visit"].get(
                    "doctor_visit_summary"
                )
            )


            print("\n--- FINAL SUMMARY ---")

            print(
                result.get(
                    "final_summary"
                )
            )


        else:

            print("\nWORKFLOW FAILED")

            print(
                result.get(
                    "error"
                )
            )


    except Exception as e:

        print("\n==============================================")
        print("ERROR")
        print("==============================================")

        print(str(e))