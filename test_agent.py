import json
from backend.app import app

client = app.test_client()

sample_multiline = """
Complete Blood Count (CBC)

Patient: Test Patient
Date: 2026-09-28

Hemoglobin
10.2
g/dL
12 - 16

WBC
7200
/uL
4000 - 11000

Platelets
250000
/uL
150000 - 450000

Medicine
Paracetamol
500 mg
Tablet
Once daily
5 days
"""

payload = {
    "patient_name": "Test Patient",
    "document_text": sample_multiline,
    "target_language": "English",
}

print("\nSending request to /api/analyze...\n")

response = client.post("/api/analyze", json=payload)
data = response.get_json()

print("Status Code:", response.status_code)
print("Success:", data.get("success"))

doc = data.get("document", {})
lab_results = doc.get("lab_results", [])
medicines = doc.get("medicines", [])
findings = doc.get("findings", [])
ref_ranges = doc.get("reference_ranges", [])
trends = data.get("health_trends", {}).get("trends", [])

print("\n" + "=" * 50)
print("VERIFICATION OF REQUIREMENT 11")
print("=" * 50)
print(f"1. lab_results non-empty: {len(lab_results) > 0} (count: {len(lab_results)})")
print(f"2. medicines non-empty: {len(medicines) > 0} (count: {len(medicines)})")
print(f"3. findings non-empty: {len(findings) > 0} (count: {len(findings)})")
print(f"4. reference_ranges non-empty: {len(ref_ranges) > 0} (count: {len(ref_ranges)})")
print(f"5. health_trends non-empty: {len(trends) > 0} (count: {len(trends)})")

print("\n" + "=" * 50)
print("EXTRACTED LAB RESULTS:")
print("=" * 50)
print(json.dumps(lab_results, indent=2))

print("\n" + "=" * 50)
print("EXTRACTED MEDICINES:")
print("=" * 50)
print(json.dumps(medicines, indent=2))

print("\n" + "=" * 50)
print("EXTRACTED FINDINGS:")
print("=" * 50)
print(json.dumps(findings, indent=2))

print("\n" + "=" * 50)
print("EXTRACTED REFERENCE RANGES:")
print("=" * 50)
print(json.dumps(ref_ranges, indent=2))

print("\n" + "=" * 50)
print("FINAL SUMMARY:")
print("=" * 50)
summary = data.get("final_summary", "")
# Safe print for Windows console
print(summary.encode("ascii", errors="replace").decode("ascii"))
