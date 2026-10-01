from agents.patient_agent import PatientInteractionAgent

agent = PatientInteractionAgent()

tests = [
    ("Hello", "English"),
    ("Analyze my blood report", "English"),
    ("Tell me about my medicines", "English"),
    ("Compare my previous report", "English"),
    ("I need to prepare for my doctor visit", "English"),
    ("I have an emergency", "English"),
    ("నా మెడికల్ రిపోర్ట్ గురించి చెప్పండి", "Telugu"),
    ("मेरी दवाइयों के बारे में बताइए", "Hindi"),
]

for message, language in tests:
    print("\n" + "=" * 60)
    print("USER:", message)
    print("LANGUAGE:", language)

    result = agent.chat(
        message=message,
        language=language
    )

    print("SUCCESS:", result["success"])
    print("INTENT:", result.get("intent"))
    print("NEXT AGENT:", result.get("next_agent"))
    print("RESPONSE:", result.get("response"))
    print("VOICE ENABLED:", result.get("voice_enabled"))