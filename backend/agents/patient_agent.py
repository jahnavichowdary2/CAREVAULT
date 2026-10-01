"""
CareVault - Patient Interaction / Voice Agent

This is the patient-facing conversational agent.

Responsibilities:
- Understand the patient's message
- Maintain a natural conversation
- Identify the patient's intent
- Route the request to the correct specialist agent
- Generate a simple, patient-friendly response
- Support multilingual conversations
- Provide text that can be converted to speech by the frontend

Important:
This agent does NOT diagnose, prescribe, or change treatment.
It explains available health information and coordinates
with specialist CareVault agents.
"""


class PatientInteractionAgent:

    def __init__(self):
        self.name = "CareVault Patient Voice Agent"

        self.supported_languages = {
            "English": "en-IN",
            "Telugu": "te-IN",
            "Hindi": "hi-IN",
            "Tamil": "ta-IN",
            "Kannada": "kn-IN",
            "Malayalam": "ml-IN"
        }

        self.intents = {
            "document": [
                "report",
                "blood report",
                "medical report",
                "test result",
                "scan",
                "prescription"
            ],

            "clinical": [
                "problem",
                "abnormal",
                "finding",
                "condition",
                "what does this mean",
                "health issue"
            ],

            "medicine": [
                "medicine",
                "tablet",
                "capsule",
                "drug",
                "medication"
            ],

            "trend": [
                "compare",
                "previous report",
                "old report",
                "improved",
                "worse",
                "change",
                "trend"
            ],

            "medication_schedule": [
                "when should i take",
                "medicine timing",
                "morning",
                "afternoon",
                "night",
                "before food",
                "after food"
            ],

            "doctor_visit": [
                "doctor",
                "appointment",
                "doctor visit",
                "what should i ask",
                "questions for doctor"
            ],

            "safety": [
                "emergency",
                "danger",
                "urgent",
                "serious",
                "should i worry"
            ],

            "general": [
                "hello",
                "hi",
                "hey",
                "help"
            ]
        }

    # ---------------------------------------------------------
    # MAIN CONVERSATION
    # ---------------------------------------------------------

    def chat(self, message, language="English", context=None):

        if not message or not message.strip():
            return {
                "success": False,
                "agent": self.name,
                "response": self.get_empty_message(language)
            }

        message = message.strip()

        intent = self.detect_intent(message)

        next_agent = self.get_next_agent(intent)

        response = self.generate_response(
            message=message,
            intent=intent,
            language=language,
            context=context
        )

        return {
            "success": True,
            "agent": self.name,
            "patient_message": message,
            "language": language,
            "intent": intent,
            "next_agent": next_agent,
            "response": response,
            "voice_enabled": True
        }

    # ---------------------------------------------------------
    # INTENT DETECTION
    # ---------------------------------------------------------

    def detect_intent(self, message):

        text = message.lower()

        priority = [
            "safety",
            "medication_schedule",
            "medicine",
            "trend",
            "doctor_visit",
            "clinical",
            "document",
            "general"
        ]

        for intent in priority:

            for keyword in self.intents[intent]:

                if keyword in text:
                    return intent

        return "general"

    # ---------------------------------------------------------
    # ROUTING
    # ---------------------------------------------------------

    def get_next_agent(self, intent):

        mapping = {

            "document":
                "Medical Document Agent",

            "clinical":
                "Clinical Analysis Agent",

            "medicine":
                "Medicine Agent",

            "trend":
                "Health Trend Agent",

            "medication_schedule":
                "Medication Schedule Agent",

            "doctor_visit":
                "Doctor Visit Agent",

            "safety":
                "Safety Agent",

            "general":
                "AI Orchestrator"
        }

        return mapping.get(
            intent,
            "AI Orchestrator"
        )

    # ---------------------------------------------------------
    # NATURAL CONVERSATION
    # ---------------------------------------------------------

    def generate_response(
        self,
        message,
        intent,
        language,
        context=None
    ):

        if language == "Telugu":

            return self.generate_telugu_response(
                message,
                intent
            )

        if language == "Hindi":

            return self.generate_hindi_response(
                message,
                intent
            )

        return self.generate_english_response(
            message,
            intent
        )

    # ---------------------------------------------------------
    # ENGLISH
    # ---------------------------------------------------------

    def generate_english_response(
        self,
        message,
        intent
    ):

        if intent == "general":

            if any(
                word in message.lower()
                for word in ["hi", "hello", "hey"]
            ):
                return (
                    "Hi! I'm CareVault. "
                    "I'm here to help you understand your "
                    "health information. "
                    "You can ask me about your reports, "
                    "medicines, health trends, or doctor visits."
                )

            return (
                "Sure, I'm here to help. "
                "You can ask me about your medical reports, "
                "medicines, health information, or questions "
                "you want to discuss with your doctor."
            )

        if intent == "document":

            return (
                "Sure. I can help you understand your medical "
                "report. I'll first look at the information in "
                "the report and explain the important findings "
                "in simple words."
            )

        if intent == "clinical":

            return (
                "I can help explain the health finding in simple "
                "terms. I'll separate what is actually shown in "
                "your records from possible explanations, and "
                "I'll let you know what should be discussed "
                "with your doctor."
            )

        if intent == "medicine":

            return (
                "Sure. I can explain the information available "
                "about your medicine, including its recorded "
                "purpose. I won't change your prescription or "
                "dosage."
            )

        if intent == "trend":

            return (
                "Sure. I can compare your current health records "
                "with your previous records and explain the "
                "changes in simple terms."
            )

        if intent == "medication_schedule":

            return (
                "I can check the medication information available "
                "in your records. If the timing or instructions "
                "are unclear, please confirm them with your doctor "
                "or pharmacist rather than guessing."
            )

        if intent == "doctor_visit":

            return (
                "Absolutely. I can help you prepare for your "
                "doctor visit and create a list of useful "
                "questions based on your health records."
            )

        if intent == "safety":

            return (
                "I'll treat this as a safety-related question. "
                "I'll check the available health information "
                "and highlight anything that may need urgent "
                "medical attention. If you believe you are "
                "having a medical emergency, contact emergency "
                "medical services immediately."
            )

        return (
            "I understand. Let me help you with that."
        )

    # ---------------------------------------------------------
    # TELUGU
    # ---------------------------------------------------------

    def generate_telugu_response(
        self,
        message,
        intent
    ):

        if intent == "general":

            return (
                "హాయ్! నేను CareVault. "
                "మీ ఆరోగ్య సమాచారాన్ని సులభంగా అర్థం చేసుకోవడానికి "
                "నేను మీకు సహాయం చేస్తాను. "
                "మీరు మీ రిపోర్ట్స్, మందులు లేదా ఆరోగ్య పరిస్థితి "
                "గురించి నన్ను అడగవచ్చు."
            )

        if intent == "document":

            return (
                "తప్పకుండా. మీ మెడికల్ రిపోర్ట్‌ను చూసి, "
                "అందులో ఉన్న ముఖ్యమైన విషయాలను సులభమైన "
                "మాటల్లో మీకు వివరిస్తాను."
            )

        if intent == "clinical":

            return (
                "మీ రిపోర్ట్‌లో కనిపిస్తున్న ఆరోగ్య సంబంధిత "
                "విషయాన్ని సులభంగా అర్థమయ్యేలా వివరిస్తాను. "
                "రిపోర్ట్‌లో నిజంగా ఉన్న సమాచారం మరియు "
                "సంభావ్య కారణాలను వేరుగా చెబుతాను."
            )

        if intent == "medicine":

            return (
                "మీ మందుల గురించి అందుబాటులో ఉన్న సమాచారాన్ని "
                "సులభంగా వివరిస్తాను. "
                "కానీ మీ మందుల మోతాదు లేదా ప్రిస్క్రిప్షన్‌ను "
                "నేను మార్చను."
            )

        if intent == "trend":

            return (
                "మీ పాత మరియు కొత్త రిపోర్టులను పోల్చి, "
                "ఏ మార్పులు కనిపిస్తున్నాయో సులభంగా వివరిస్తాను."
            )

        if intent == "doctor_visit":

            return (
                "మీ డాక్టర్ అపాయింట్‌మెంట్ కోసం సిద్ధం కావడానికి "
                "నేను సహాయం చేస్తాను. "
                "డాక్టర్‌ను అడగాల్సిన ముఖ్యమైన ప్రశ్నలను "
                "తయారు చేయగలను."
            )

        if intent == "safety":

            return (
                "ఇది ఆరోగ్య భద్రతకు సంబంధించిన ప్రశ్న. "
                "మీ దగ్గర ఉన్న సమాచారాన్ని పరిశీలించి, "
                "డాక్టర్‌ను త్వరగా సంప్రదించాల్సిన పరిస్థితి "
                "ఉందా అనేది అర్థం చేసుకోవడానికి సహాయం చేస్తాను. "
                "అత్యవసర పరిస్థితి అనిపిస్తే వెంటనే "
                "ఎమర్జెన్సీ మెడికల్ సహాయం తీసుకోండి."
            )

        return (
            "సరే. దీనికి సంబంధించి నేను మీకు సహాయం చేస్తాను."
        )

    # ---------------------------------------------------------
    # HINDI
    # ---------------------------------------------------------

    def generate_hindi_response(
        self,
        message,
        intent
    ):

        if intent == "general":

            return (
                "नमस्ते! मैं CareVault हूँ। "
                "मैं आपकी स्वास्थ्य जानकारी को आसान भाषा में "
                "समझने में आपकी मदद कर सकता हूँ।"
            )

        if intent == "document":

            return (
                "ज़रूर। मैं आपकी मेडिकल रिपोर्ट में दी गई "
                "महत्वपूर्ण जानकारी को आसान भाषा में समझाने "
                "में आपकी मदद करूँगा।"
            )

        if intent == "medicine":

            return (
                "ज़रूर। मैं आपकी दवा के बारे में उपलब्ध "
                "जानकारी समझा सकता हूँ। "
                "लेकिन मैं आपकी दवा की खुराक या prescription "
                "को नहीं बदलूँगा।"
            )

        if intent == "trend":

            return (
                "मैं आपकी पुरानी और नई रिपोर्ट की तुलना करके "
                "उनमें हुए बदलावों को आसान भाषा में समझा सकता हूँ।"
            )

        if intent == "doctor_visit":

            return (
                "मैं आपकी डॉक्टर की appointment के लिए तैयारी "
                "करने और डॉक्टर से पूछे जाने वाले सवाल तैयार "
                "करने में मदद कर सकता हूँ।"
            )

        if intent == "safety":

            return (
                "मैं इस सवाल को safety-related request की तरह "
                "देखूँगा और उपलब्ध जानकारी के आधार पर "
                "महत्वपूर्ण बातों को समझाने में मदद करूँगा।"
            )

        return (
            "ठीक है। मैं इसमें आपकी मदद करता हूँ।"
        )

    # ---------------------------------------------------------
    # EMPTY MESSAGE
    # ---------------------------------------------------------

    def get_empty_message(self, language):

        if language == "Telugu":
            return "దయచేసి మీ ప్రశ్న చెప్పండి."

        if language == "Hindi":
            return "कृपया अपना सवाल बताइए।"

        return "Please tell me what you would like help with."