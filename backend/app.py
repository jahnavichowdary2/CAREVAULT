"""
CareVault / MediSaathi HealthVault
Backend API

Frontend
   ↓
Flask API
   ↓
Orchestrator
   ↓
All Healthcare Agents
"""

import sys
import os

# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify
from flask_cors import CORS
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load environment variables
for p in [
    os.path.join(os.path.dirname(__file__), ".env"),
    os.path.join(os.path.dirname(__file__), "agents", ".env"),
    os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), ".env"),
]:
    if os.path.exists(p):
        load_dotenv(p)


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =========================================================
# IMPORT ORCHESTRATOR
# =========================================================

from backend.agents.orchestrator import OrchestratorAgent


# =========================================================
# CREATE FLASK APP
# =========================================================

app = Flask(__name__)

# Allow React/frontend to communicate with Flask
CORS(app)


# =========================================================
# INITIALIZE ORCHESTRATOR
# =========================================================

print("Starting CareVault backend...")

orchestrator = OrchestratorAgent()

print("CareVault backend initialized successfully.")


# =========================================================
# HOME / HEALTH CHECK
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "project": "CareVault / MediSaathi HealthVault",
        "message": "CareVault backend is running.",
        "status": "online"
    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/api/health", methods=["GET"])
def health_check():

    return jsonify({
        "success": True,
        "status": "healthy",
        "service": "CareVault Backend"
    })


# =========================================================
# MAIN MEDICAL DOCUMENT ANALYSIS API
# =========================================================

@app.route("/api/analyze", methods=["POST"])
def analyze_document():

    try:

        # -------------------------------------------------
        # Get JSON request
        # -------------------------------------------------

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "Request body must contain JSON data."
            }), 400


        # -------------------------------------------------
        # Required information
        # -------------------------------------------------

        patient_name = data.get(
            "patient_name",
            "Unknown Patient"
        )

        document_text = data.get(
            "document_text"
        )


        # -------------------------------------------------
        # Validate document
        # -------------------------------------------------

        if not document_text:

            return jsonify({
                "success": False,
                "error": "document_text is required."
            }), 400


        # -------------------------------------------------
        # Optional information
        # -------------------------------------------------

        target_language = data.get(
            "target_language",
            "English"
        )

        measurements = data.get(
            "measurements",
            []
        )

        health_history = data.get(
            "health_history",
            []
        )


        # -------------------------------------------------
        # Run complete multi-agent workflow
        # -------------------------------------------------

        print("\n========================================")
        print("NEW MEDICAL DOCUMENT REQUEST")
        print("========================================")

        print("Patient:", patient_name)
        print("Language:", target_language)

        result = orchestrator.process_health_document(

            patient_name=patient_name,

            document_text=document_text,

            target_language=target_language,

            measurements=measurements,

            health_history=health_history
        )


        # -------------------------------------------------
        # Return result
        # -------------------------------------------------

        return jsonify(result), 200


    except Exception as e:

        print("\nERROR:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    # =========================================================
# MEDISAATHI CENTRAL AGENT API
# =========================================================

@app.route("/api/agent/chat", methods=["POST"])
def agent_chat():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "Request body must contain JSON data."
            }), 400


        # -------------------------------------------------
        # User message
        # -------------------------------------------------

        message = data.get("message")

        if not message:

            return jsonify({
                "success": False,
                "error": "message is required."
            }), 400


        # -------------------------------------------------
        # Optional information
        # -------------------------------------------------

        language = data.get(
            "language",
            "English"
        )

        patient_name = data.get(
            "patient_name",
            "User"
        )

        measurements = data.get(
            "measurements",
            []
        )

        health_history = data.get(
            "health_history",
            []
        )


        # -------------------------------------------------
        # Run MediSaathi Central Agent
        # -------------------------------------------------

        print("\n========================================")
        print("NEW MEDISAATHI AGENT REQUEST")
        print("========================================")

        print("Message:", message)
        print("Language:", language)


        result = orchestrator.process_agent_message(

            message=message,

            language=language,

            patient_name=patient_name,

            measurements=measurements,

            health_history=health_history
        )


        # -------------------------------------------------
        # Return result
        # -------------------------------------------------

        return jsonify(result), 200


    except Exception as e:

        print("\nMEDISAATHI AGENT ERROR:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# LANGUAGE / TRANSLATION API
# =========================================================

@app.route("/api/translate", methods=["POST"])
def translate_text():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "Request body must contain JSON data."
            }), 400


        text = data.get("text")

        target_language = data.get(
            "target_language",
            "English"
        )


        if not text:

            return jsonify({
                "success": False,
                "error": "text is required."
            }), 400


        result = orchestrator.process_language(

            text=text,

            target_language=target_language
        )


        return jsonify(result), 200


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# DOCTOR VISIT SUMMARY API
# =========================================================

@app.route("/api/doctor-summary", methods=["POST"])
def doctor_summary():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "Request body must contain JSON data."
            }), 400


        patient_name = data.get(
            "patient_name",
            "Unknown Patient"
        )

        reports = data.get(
            "reports",
            []
        )

        medications = data.get(
            "medications",
            []
        )

        trends = data.get(
            "trends",
            []
        )

        health_history = data.get(
            "health_history",
            []
        )


        result = orchestrator.prepare_doctor_visit(

            patient_name=patient_name,

            reports=reports,

            medications=medications,

            trends=trends,

            health_history=health_history
        )


        return jsonify(result), 200


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    print("\n========================================")
    print("       CAREVAULT BACKEND")
    print("========================================")
    print("Server: http://127.0.0.1:5000")
    print("Health: http://127.0.0.1:5000/api/health")
    print("========================================\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )