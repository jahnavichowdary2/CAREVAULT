import re


class DocumentAgent:
    """
    Medical Document Agent

    Extracts structured information from medical documents, including
    multiline lab reports and prescriptions from PDF/OCR text.
    Does NOT diagnose, prescribe, or change treatment.
    """

    def __init__(self):
        self.name = "Medical Document Agent"

        # Comprehensive aliases for required common tests
        self.tests = {
            "Hemoglobin": [
                r"\bha?emoglobin\b",
                r"\bhgb\b",
                r"\bhb\b",
            ],
            "HbA1c": [
                r"\bglycosylated\s+ha?emoglobin\b",
                r"\bglycated\s+ha?emoglobin\b",
                r"\bhb\s*a1c\b",
                r"\bhba1c\b",
            ],
            "Glucose": [
                r"\bfasting\s+blood\s+(?:sugar|glucose)\b",
                r"\bpost\s*prandial\s+blood\s+(?:sugar|glucose)\b",
                r"\brandom\s+blood\s+(?:sugar|glucose)\b",
                r"\bblood\s+glucose\b",
                r"\bblood\s+sugar\b",
                r"\bglucose\s*[-–]?\s*fasting\b",
                r"\bfbs\b",
                r"\brbs\b",
                r"\bppbs\b",
                r"\bglucose\b",
            ],
            "WBC": [
                r"\btotal\s+leuco?cyte\s+count\b",
                r"\bwhite\s+blood\s+cell(?:s|\s+count)?\b",
                r"\bwbc\s+count\b",
                r"\btlc\b",
                r"\bwbc\b",
                r"\bleukocytes\b",
            ],
            "RBC": [
                r"\btotal\s+red\s+blood\s+cell(?:s|\s+count)?\b",
                r"\bred\s+blood\s+cell(?:s|\s+count)?\b",
                r"\btotal\s+rbc\b",
                r"\brbc\s+count\b",
                r"\brbc\b",
                r"\berythrocytes\b",
            ],
            "Platelets": [
                r"\btotal\s+platelet(?:s)?(?:\s+count)?\b",
                r"\bplatelet\s+count\b",
                r"\bplatelets?\b",
                r"\bplt\b",
            ],
            "Creatinine": [
                r"\bserum\s+creatinine\b",
                r"\bcreatinine\b",
            ],
            "Urea": [
                r"\bblood\s+urea\s+nitrogen\b",
                r"\bblood\s+urea\b",
                r"\bbun\b",
                r"\burea\b",
            ],
            "Total Cholesterol": [
                r"\bserum\s+cholesterol\b",
                r"\btotal\s+cholesterol\b",
                r"\bcholesterol\s*[-–]?\s*total\b",
                r"\bcholesterol\b",
            ],
            "HDL": [
                r"\bhigh\s+density\s+lipoprotein\b",
                r"\bhdl\s+cholesterol\b",
                r"\bhdl-c\b",
                r"\bhdl\b",
            ],
            "LDL": [
                r"\blow\s+density\s+lipoprotein\b",
                r"\bldl\s+cholesterol\b",
                r"\bldl-c\b",
                r"\bldl\b",
            ],
            "Triglycerides": [
                r"\bserum\s+triglycerides?\b",
                r"\btriglycerides?\b",
                r"\btg\b",
            ],
            "TSH": [
                r"\bthyroid\s+stimulating\s+hormone\b",
                r"\bultra[- ]?sensitive\s+tsh\b",
                r"\btsh\b",
            ],
            "T3": [
                r"\btotal\s+triiodothyronine\b",
                r"\bfree\s+triiodothyronine\b",
                r"\btriiodothyronine\b",
                r"\bft3\b",
                r"\bt3\s+total\b",
                r"\bt3\b",
            ],
            "T4": [
                r"\btotal\s+thyroxine\b",
                r"\bfree\s+thyroxine\b",
                r"\bthyroxine\b",
                r"\bft4\b",
                r"\bt4\s+total\b",
                r"\bt4\b",
            ],
            "ALT": [
                r"\balanine\s+aminotransferase\b",
                r"\balanine\s+transaminase\b",
                r"\bsgpt\b",
                r"\balt\b",
            ],
            "AST": [
                r"\baspartate\s+aminotransferase\b",
                r"\baspartate\s+transaminase\b",
                r"\bsgot\b",
                r"\bast\b",
            ],
            "Vitamin D": [
                r"\b25[- ]?hydroxy\s+vitamin\s*d\b",
                r"\b25[- ]?oh\s+vitamin\s*d\b",
                r"\bvitamin\s*d3?\b",
                r"\bvit\s*d3?\b",
            ],
            "Vitamin B12": [
                r"\bvitamin\s*b12\b",
                r"\bvit\s*b12\b",
                r"\bcyanocobalamin\b",
                r"\bb12\b",
            ],
            "Ferritin": [
                r"\bserum\s+ferritin\b",
                r"\bferritin\b",
            ],
            "CRP": [
                r"\bhigh\s+sensitivity\s+crp\b",
                r"\bhs[- ]?crp\b",
                r"\bc[- ]?reactive\s+protein\b",
                r"\bcrp\b",
            ],
            "ESR": [
                r"\berythrocyte\s+sedimentation\s+rate\b",
                r"\besr\b",
            ],
            "Calcium": [
                r"\bserum\s+calcium\b",
                r"\btotal\s+calcium\b",
                r"\bca\+\+\b",
                r"\bcalcium\b",
            ],
            "Sodium": [
                r"\bserum\s+sodium\b",
                r"\bsodium\b",
                r"\bna\+\b",
            ],
            "Potassium": [
                r"\bserum\s+potassium\b",
                r"\bpotassium\b",
                r"\bk\+\b",
            ],
        }

    # =========================================================
    # MAIN ANALYSIS
    # =========================================================

    def analyze(self, document_text):
        if not document_text or not document_text.strip():
            return {
                "success": False,
                "agent": self.name,
                "message": "No medical document text was provided.",
            }

        text = self.clean_text(document_text)

        lab_results = self.extract_lab_results(text)
        medicines = self.extract_medicines(text)
        findings = self.extract_findings(text, lab_results)
        reference_ranges = self.extract_reference_ranges(text, lab_results)

        return {
            "success": True,
            "agent": self.name,
            "document_type": self.detect_document_type(text),
            "patient_name": self.extract_patient_name(text),
            "dates": self.extract_dates(text),
            "lab_results": lab_results,
            "medicines": medicines,
            "findings": findings,
            "reference_ranges": reference_ranges,
            "original_text": text,
        }

    # =========================================================
    # TEXT CLEANING
    # =========================================================

    def clean_text(self, text):
        if not text:
            return ""

        text = text.replace("\xa0", " ")
        text = text.replace("\r", "\n")

        # Normalize spaces per line while preserving lines
        lines = []
        for line in text.splitlines():
            line = re.sub(r"[ \t]+", " ", line).strip()
            if line:
                lines.append(line)

        return "\n".join(lines)

    # =========================================================
    # DOCUMENT TYPE
    # =========================================================

    def detect_document_type(self, text):
        lower = text.lower()

        laboratory_words = [
            "hemoglobin",
            "haemoglobin",
            "glucose",
            "cholesterol",
            "creatinine",
            "platelet",
            "wbc",
            "rbc",
            "blood test",
            "cbc",
            "lipid profile",
            "thyroid",
            "laboratory",
            "lab report",
            "pathology",
            "complete blood count",
            "investigation report",
        ]

        prescription_words = [
            "prescription",
            "tablet",
            "capsule",
            "syrup",
            "dosage",
            "medication",
            "medicine",
            "prescribed",
            "rx",
        ]

        imaging_words = [
            "x-ray",
            "xray",
            "ct scan",
            "computed tomography",
            "mri",
            "magnetic resonance",
            "ultrasound",
            "sonography",
            "impression",
        ]

        if any(word in lower for word in laboratory_words):
            return "Laboratory Report"

        if any(word in lower for word in imaging_words):
            return "Imaging Report"

        if "discharge summary" in lower:
            return "Discharge Summary"

        if any(word in lower for word in prescription_words):
            return "Prescription"

        return "Medical Document"

    # =========================================================
    # PATIENT NAME
    # =========================================================

    def extract_patient_name(self, text):
        patterns = [
            r"(?:patient\s*name|patient\s*|name)\s*[:\-]\s*([A-Za-z][A-Za-z .'-]{2,60})",
            r"(?:mr\.?|mrs\.?|ms\.?|miss)\s+([A-Za-z][A-Za-z .'-]{2,60})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                name = match.group(1).strip()
                name = re.split(
                    r"\s+(?:age|sex|gender|dob|date|patient\s*id)\b",
                    name,
                    flags=re.IGNORECASE,
                )[0].strip()

                if 2 <= len(name) <= 60:
                    return name

        return None

    # =========================================================
    # DATE EXTRACTION
    # =========================================================

    def extract_dates(self, text):
        patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2}\b",
            r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
            r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",
        ]

        dates = []
        for pattern in patterns:
            for date in re.findall(pattern, text, re.IGNORECASE):
                date = date.strip()
                if date not in dates:
                    dates.append(date)

        return dates

    # =========================================================
    # LAB RESULT EXTRACTION (MULTILINE ROBUST)
    # =========================================================

    def extract_lab_results(self, text):
        """
        Robust multiline lab extraction.
        Handles fields on same line or split across multiple lines, e.g.:
        Hemoglobin
        10.2
        g/dL
        12 - 16
        """
        results = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # Track which tests have been detected to avoid duplicates
        detected_tests = set()

        for idx, line in enumerate(lines):
            # Check if this line or the start of this line matches any test alias
            for test_name, aliases in self.tests.items():
                if test_name in detected_tests:
                    continue

                matched_alias = None
                matched_span = None

                for alias in aliases:
                    m = re.search(alias, line, re.IGNORECASE)
                    if m:
                        matched_alias = alias
                        matched_span = m.span()
                        break

                if not matched_alias:
                    continue

                # We found a potential test. Now inspect a window of lines:
                # from current line up to 6 lines down, or until the next test name.
                window_lines = [line[matched_span[1]:]]  # remainder of current line
                for next_idx in range(idx + 1, min(idx + 7, len(lines))):
                    next_line = lines[next_idx]
                    # Check if next_line starts a different known test name
                    is_other_test = False
                    for other_name, other_aliases in self.tests.items():
                        if other_name != test_name:
                            for o_alias in other_aliases:
                                if re.search(o_alias, next_line, re.IGNORECASE):
                                    is_other_test = True
                                    break
                            if is_other_test:
                                break
                    if is_other_test:
                        break
                    window_lines.append(next_line)

                combined_window = " ".join(window_lines).strip()

                # Extract reference range from window first so its numbers aren't treated as the value
                ref_range, ref_span = self._extract_range_with_span(combined_window)

                # Mask out the reference range from the text when searching for value
                search_text_for_value = combined_window
                if ref_span:
                    search_text_for_value = (
                        combined_window[:ref_span[0]] + " " + combined_window[ref_span[1]:]
                    )

                # Look for explicit labeled value e.g. "Result: 10.2", "Value: 10.2", "Observed: 10.2"
                labeled_val = re.search(
                    r"(?:result|value|observed|finding)\s*[:\-]?\s*([<>]?\s*[-+]?\d+(?:\.\d+)?)",
                    search_text_for_value,
                    re.IGNORECASE,
                )

                value = None
                if labeled_val:
                    value = labeled_val.group(1).strip()
                else:
                    # Look for first standalone numeric value in window
                    val_match = re.search(
                        r"(?<![\w.])([<>]?\s*[-+]?\d+(?:\.\d+)?)(?![\w.])",
                        search_text_for_value,
                    )
                    if val_match:
                        candidate = val_match.group(1).strip()
                        # Avoid taking pure year e.g. 2026 if it looks like a date
                        if not (len(candidate) == 4 and candidate.startswith(("19", "20"))):
                            value = candidate

                if not value:
                    continue

                # Extract unit
                unit = self.extract_unit(combined_window)

                # Determine status / abnormal flag
                flag = self._extract_flag(combined_window, value, ref_range)

                results.append({
                    "test": test_name,
                    "value": value,
                    "unit": unit,
                    "reference_range": ref_range,
                    "status": flag,
                    "source_line": line,
                })
                detected_tests.add(test_name)

        return results

    # =========================================================
    # UNIT EXTRACTION
    # =========================================================

    def extract_unit(self, text):
        units = [
            r"g/dL",
            r"gm/dL",
            r"g/L",
            r"mg/dL",
            r"mg/L",
            r"mmol/L",
            r"µmol/L",
            r"umol/L",
            r"nmol/L",
            r"pmol/L",
            r"mEq/L",
            r"U/L",
            r"IU/L",
            r"mIU/L",
            r"µIU/mL",
            r"uIU/mL",
            r"mIU/mL",
            r"ng/mL",
            r"pg/mL",
            r"µg/dL",
            r"ug/dL",
            r"µg/L",
            r"ug/L",
            r"cells/µL",
            r"cells/uL",
            r"cells/cumm",
            r"lakhs/cumm",
            r"million/µL",
            r"million/uL",
            r"million/cumm",
            r"10\^3/µL",
            r"10\^3/uL",
            r"10\*3/uL",
            r"10\^6/µL",
            r"10\^6/uL",
            r"/cumm",
            r"cumm",
            r"/µL",
            r"/uL",
            r"mm/hr",
            r"mm/1st\s+hr",
            r"mm",
            r"%",
            r"fL",
            r"pg",
        ]

        pattern = r"(?<!\w)(?:" + "|".join(units) + r")(?!\w)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(0).strip()

        return None

    # =========================================================
    # REFERENCE RANGE
    # =========================================================

    def _extract_range_with_span(self, text):
        patterns = [
            r"(?:ref(?:erence)?(?:\s*range|\s*interval)?|biological\s+ref\w*|normal\s*range|range)\s*[:\-]?\s*([<>]?\s*\d+(?:\.\d+)?\s*(?:[-–toTO]+\s*\d+(?:\.\d+)?)?)",
            r"(?:\(|\b)(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)(?:\)|\b)",
            r"(?:\(|\b)(\d+(?:\.\d+)?)\s+to\s+(\d+(?:\.\d+)?)(?:\)|\b)",
            r"(?:<|>|<=|>=)\s*\d+(?:\.\d+)?",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                matched_str = match.group(0).strip()
                # Clean up if matched with "ref range:" prefix
                cleaned = re.sub(
                    r"^(?:ref(?:erence)?(?:\s*range|\s*interval)?|biological\s+ref\w*|normal\s*range|range)\s*[:\-]?\s*",
                    "",
                    matched_str,
                    flags=re.IGNORECASE,
                ).strip()
                cleaned = cleaned.strip("()")
                return cleaned, match.span()

        return None, None

    def _extract_range(self, text):
        ref, _ = self._extract_range_with_span(text)
        return ref

    # =========================================================
    # ABNORMAL FLAG / STATUS
    # =========================================================

    def _extract_flag(self, text, value_str, ref_range):
        """
        Detects High / Low / Abnormal / Normal based on text flags
        or by evaluating numeric value against reference range.
        """
        lower = text.lower()

        # Check explicit flags in text
        if re.search(r"\b(high|elevated|increased|critical\s+high|\bH\b|\*)\b", text):
            return "High"
        if re.search(r"\b(low|decreased|critical\s+low|\bL\b)\b", text):
            return "Low"
        if re.search(r"\b(abnormal|positive|detected)\b", lower):
            return "Abnormal"

        # If reference range is present, compare numerically
        try:
            val_clean = re.sub(r"[^\d.]", "", value_str)
            val_num = float(val_clean)

            if ref_range:
                range_match = re.search(
                    r"(\d+(?:\.\d+)?)\s*[-–toTO]+\s*(\d+(?:\.\d+)?)",
                    ref_range,
                )
                if range_match:
                    lower_limit = float(range_match.group(1))
                    upper_limit = float(range_match.group(2))
                    if val_num < lower_limit:
                        return "Low"
                    elif val_num > upper_limit:
                        return "High"
                    else:
                        return "Normal"

                # Check < or > threshold
                less_match = re.search(r"<\s*(\d+(?:\.\d+)?)", ref_range)
                if less_match:
                    threshold = float(less_match.group(1))
                    if val_num > threshold:
                        return "High"
                    else:
                        return "Normal"

                greater_match = re.search(r">\s*(\d+(?:\.\d+)?)", ref_range)
                if greater_match:
                    threshold = float(greater_match.group(1))
                    if val_num < threshold:
                        return "Low"
                    else:
                        return "Normal"
        except (ValueError, TypeError):
            pass

        if "normal" in lower or "negative" in lower:
            return "Normal"

        return "Reported"

    # =========================================================
    # MEDICINE EXTRACTION (MULTILINE ROBUST)
    # =========================================================

    def extract_medicines(self, text):
        """
        Robust multiline medicine extraction.
        Extracts:
        - name
        - strength/dose (dosage)
        - form (tablet, capsule, syrup, etc.)
        - frequency (once daily, twice daily, 1-0-1, etc.)
        - duration (5 days, 30 days, etc.)
        - timing (after food, before food, etc.)
        """
        medicines = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        ignored_words = {
            "tablet",
            "tablets",
            "tab",
            "tabs",
            "capsule",
            "capsules",
            "cap",
            "caps",
            "syrup",
            "syp",
            "injection",
            "inj",
            "medicine",
            "medicines",
            "medication",
            "medications",
            "prescription",
            "patient",
            "doctor",
            "hospital",
            "clinic",
            "report",
            "blood",
            "test",
            "result",
            "results",
            "normal",
            "abnormal",
            "hemoglobin",
            "glucose",
            "cholesterol",
            "creatinine",
            "platelets",
            "platelet",
            "date",
            "dose",
            "dosage",
            "frequency",
            "duration",
            "timing",
            "advice",
            "instructions",
            "signature",
            "complete",
            "count",
            "reference",
            "range",
            "interval",
            "intervals",
            "ref",
            "biological",
            "observed",
            "value",
            "values",
            "unit",
            "units",
            "method",
            "specimen",
            "sample",
            "flag",
            "flags",
        }

        form_regex = r"\b(tablets?|tabs?|capsules?|caps?|syrups?|syp|injections?|inj|drops?|inhalers?|ointment|cream|suspension)\b"
        dose_regex = r"\b(\d+(?:\.\d+)?\s*(?:mg|mcg|µg|ug|g(?!/[a-zA-Z])|gm(?!/[a-zA-Z])|ml|iu|units?))\b"
        freq_regex = r"\b(once\s+(?:daily|a\s+day)|twice\s+(?:daily|a\s+day)|thrice\s+(?:daily|a\s+day)|three\s+times\s+(?:daily|a\s+day)|four\s+times\s+(?:daily|a\s+day)|\d+\s+times\s+(?:daily|a\s+day)|at\s+bedtime|bedtime|every\s+\d+\s+hours?|1-0-1|1-0-0|0-1-0|0-0-1|1-1-1|1-1-1-1|od|bd|bid|tds|tid|qid|sos|prn)\b"
        duration_regex = r"\b(?:for\s+|x\s*)?(\d+\s*(?:days?|weeks?|months?|d|w|m))\b"
        timing_regex = r"\b(after\s+(?:food|meals?)|before\s+(?:food|meals?|breakfast)|with\s+food|empty\s+stomach|at\s+night|in\s+the\s+morning)\b"

        # Pass 1: Parse block formats or lines containing medicines
        idx = 0
        while idx < len(lines):
            line = lines[idx]
            lower_line = line.lower()

            # Check if this line introduces a medicine or contains medicine keywords
            is_med_header = lower_line in ["medicines:", "medicine", "prescription:", "prescription", "rx:", "rx", "medications:"]

            # If it's a section header, step to the next line
            if is_med_header:
                idx += 1
                continue

            # Look for medicine candidate on current line
            # It could be:
            # - Prefixed: "Tab Paracetamol 500mg" or "1. Paracetamol 500mg"
            # - Standalone name followed by dosage on same or subsequent lines
            # - Has dosage or form on current line
            has_dose = re.search(dose_regex, line, re.IGNORECASE)
            has_form = re.search(form_regex, line, re.IGNORECASE)
            has_rx_prefix = re.match(r"^(?:(?:\d+[\.\)]\s*)?(?:tab|cap|syp|inj|rx)[\.\s:]+)\s*([A-Za-z][A-Za-z0-9-]{2,})", line, re.IGNORECASE)

            # Check if line contains a potential medicine name
            candidate_name = None

            if has_rx_prefix:
                candidate_name = has_rx_prefix.group(1).strip()
            elif has_dose or has_form:
                # Extract words before the dose or form as candidate name
                tokens = re.split(r"[:\-–]", line)[0].strip()
                words = [w for w in re.split(r"\s+", tokens) if w.isalpha() and len(w) >= 3]
                clean_words = [w for w in words if w.lower() not in ignored_words]
                if clean_words:
                    candidate_name = " ".join(clean_words)
            elif idx > 0 and lines[idx - 1].lower() in ["medicine", "medicines:", "rx:", "prescription:", "medications:"]:
                # Line directly following a medicine header
                words = [w for w in re.split(r"\s+", line) if w.isalpha() and len(w) >= 3]
                clean_words = [w for w in words if w.lower() not in ignored_words]
                if clean_words:
                    candidate_name = " ".join(clean_words)

            if candidate_name and candidate_name.lower() not in ignored_words:
                # Gather multiline context: current line + next 5 lines
                window_lines = lines[idx:min(idx + 6, len(lines))]
                combined_window = " ".join(window_lines)

                # Extract dosage
                d_match = re.search(dose_regex, combined_window, re.IGNORECASE)
                dosage = d_match.group(1).strip() if d_match else None

                # Extract form
                f_match = re.search(form_regex, combined_window, re.IGNORECASE)
                form = f_match.group(1).capitalize() if f_match else None

                # Extract frequency
                freq_match = re.search(freq_regex, combined_window, re.IGNORECASE)
                frequency = freq_match.group(1).strip() if freq_match else None

                # Extract duration
                dur_match = re.search(duration_regex, combined_window, re.IGNORECASE)
                duration = dur_match.group(1).strip() if dur_match else None

                # Extract timing
                t_match = re.search(timing_regex, combined_window, re.IGNORECASE)
                timing = t_match.group(1).strip() if t_match else None

                # Clean medicine name
                clean_name = re.sub(
                    r"^(?:\d+[\.\)]\s*)?(?:tab(?:let)?|cap(?:sule)?|syp|syrup|inj(?:ection)?)[\.\s]+",
                    "",
                    candidate_name,
                    flags=re.IGNORECASE,
                ).strip()

                if (
                    clean_name.lower() not in ignored_words
                    and not any(w in ignored_words for w in clean_name.lower().split())
                    and len(clean_name) >= 3
                ):
                    duplicate = any(
                        m["name"].lower() == clean_name.lower() for m in medicines
                    )
                    if not duplicate:
                        medicines.append({
                            "name": clean_name,
                            "dosage": dosage,
                            "dose": dosage,
                            "form": form,
                            "frequency": frequency,
                            "duration": duration,
                            "timing": timing,
                        })

            idx += 1

        # Pass 2: Fallback for standard prescription patterns anywhere in text if none found
        if not medicines:
            # Try matching "Name <dose> <form> <freq> <duration>" in whole text
            inline_matches = re.finditer(
                r"\b([A-Za-z][A-Za-z0-9-]{2,})\s+(\d+(?:\.\d+)?\s*(?:mg|mcg|µg|ug|g|gm|ml|iu))\b",
                text,
                re.IGNORECASE,
            )
            for m in inline_matches:
                med_name = m.group(1).strip()
                if med_name.lower() in ignored_words:
                    continue
                dosage = m.group(2).strip()
                # Look ahead for form, freq, duration
                after = text[m.end():m.end() + 150]
                f_match = re.search(form_regex, after, re.IGNORECASE)
                freq_match = re.search(freq_regex, after, re.IGNORECASE)
                dur_match = re.search(duration_regex, after, re.IGNORECASE)
                timing_match = re.search(timing_regex, after, re.IGNORECASE)

                if not any(item["name"].lower() == med_name.lower() for item in medicines):
                    medicines.append({
                        "name": med_name,
                        "dosage": dosage,
                        "dose": dosage,
                        "form": f_match.group(1).capitalize() if f_match else None,
                        "frequency": freq_match.group(1).strip() if freq_match else None,
                        "duration": dur_match.group(1).strip() if dur_match else None,
                        "timing": timing_match.group(1).strip() if timing_match else None,
                    })

        return medicines

    # =========================================================
    # FINDINGS (COMBINES LAB ABNORMALITIES & TEXT KEYWORDS)
    # =========================================================

    def extract_findings(self, text, lab_results=None):
        findings = []

        # 1. Findings derived from extracted lab results
        if lab_results:
            for item in lab_results:
                test = item.get("test")
                val = item.get("value")
                unit = item.get("unit") or ""
                ref = item.get("reference_range")
                status = item.get("status")

                if status in ["High", "Low", "Abnormal"]:
                    msg = f"{test}: {val} {unit} ({status}"
                    if ref:
                        msg += f", Reference: {ref}"
                    msg += ")"
                    if msg not in findings:
                        findings.append(msg)
                elif val is not None:
                    # Also include normal / reported values as informative findings
                    msg = f"{test}: {val} {unit}"
                    if ref:
                        msg += f" (Reference: {ref})"
                    if msg not in findings:
                        findings.append(msg)

        # 2. Textual findings from report lines
        keywords = [
            "impression",
            "finding",
            "findings:",
            "diagnosis",
            "conclusion",
            "abnormal",
            "elevated",
            "decreased",
            "critical",
            "suggestive of",
            "consistent with",
        ]

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            lower = line.lower()
            if any(keyword in lower for keyword in keywords):
                if line not in findings and len(line) <= 180:
                    findings.append(line)

        return findings

    # =========================================================
    # ALL REFERENCE RANGES
    # =========================================================

    def extract_reference_ranges(self, text, lab_results=None):
        ranges = []

        # 1. Include reference ranges associated with lab results
        if lab_results:
            for item in lab_results:
                ref = item.get("reference_range")
                test = item.get("test")
                if ref:
                    labeled = f"{test}: {ref}"
                    if ref not in ranges and labeled not in ranges:
                        ranges.append(ref)

        # 2. General regex search for ranges
        patterns = [
            r"\b\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?\b",
            r"\b\d+(?:\.\d+)?\s+to\s+\d+(?:\.\d+)?\b",
        ]

        for pattern in patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                value = m.group(0).strip()
                # Skip date patterns like 2026-09-28 or 28-09-2026
                surrounding = text[max(0, m.start() - 5):min(len(text), m.end() + 5)]
                if re.search(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}", surrounding):
                    continue
                if re.match(r"^(?:19|20)\d{2}[-/]\d{1,2}$", value):
                    continue
                if value not in ranges:
                    ranges.append(value)

        return ranges