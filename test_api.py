import requests
import json

url = "http://127.0.0.1:5000/api/analyze"

data = {
    "patient_name": "Test Patient",

    "document_text": """
    Complete Blood Count (CBC)

    Patient: Test Patient
    Date: 2026-09-28

    Hemoglobin: 10.2 g/dL
    Reference Range: 12-15 g/dL

    White Blood Cell Count: 7200 /uL
    Reference Range: 4000-11000 /uL

    Platelets: 250000 /uL
    Reference Range: 150000-450000 /uL

    Medicines:
    Example Medicine 500 mg
    Twice daily
    Duration: 30 days
    """,

    "target_language": "English",

    "measurements": {
        "hemoglobin": [
            {
                "date": "2026-09-20",
                "value": 10.8,
                "unit": "g/dL"
            },
            {
                "date": "2026-09-28",
                "value": 10.2,
                "unit": "g/dL"
            }
        ]
    },

    "health_history": [
        "Previous hemoglobin measurement was 10.8 g/dL on 2026-09-20."
    ]
}

print("\nSending request to CareVault Agent...\n")

try:
    response = requests.post(url, json=data)

    print("Status Code:", response.status_code)
    print("\nResponse:")
    print("=" * 60)

    result = response.json()

    print(json.dumps(result, indent=2, ensure_ascii=True))

except Exception as e:
    print("\nERROR:")
    print(e)