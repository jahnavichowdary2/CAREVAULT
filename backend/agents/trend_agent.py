# backend/agents/trend_agent.py

from datetime import datetime


class TrendAgent:
    """
    Trend Agent

    Responsibilities:
    - Compare medical measurements over time
    - Calculate numerical changes
    - Identify increasing/decreasing/stable patterns
    - Prepare simple trend summaries and baseline recordings
    - Ensure current measurements are represented even when no historical records exist

    This agent does NOT diagnose medical conditions.
    """

    def __init__(self):
        self.name = "Trend Agent"

    def analyze(self, measurements):
        """
        Supports both:

        1. List format:
        [
            {
                "test": "Hemoglobin",
                "value": 10.2,
                "unit": "g/dL",
                "date": "2026-09-28"
            }
        ]

        2. Dictionary format:
        {
            "hemoglobin": [
                {
                    "value": 10.8,
                    "unit": "g/dL",
                    "date": "2026-09-20"
                },
                {
                    "value": 10.2,
                    "unit": "g/dL",
                    "date": "2026-09-28"
                }
            ]
        }
        """
        if not measurements:
            return {
                "success": False,
                "agent": self.name,
                "trends": [],
                "message": "No health measurements provided.",
            }

        # ---------------------------------------------------------
        # Convert dictionary format to list format
        # ---------------------------------------------------------
        if isinstance(measurements, dict):
            normalized = []
            for test_name, records in measurements.items():
                if isinstance(records, list):
                    for record in records:
                        if isinstance(record, dict):
                            normalized_record = record.copy()
                            normalized_record["test"] = test_name
                            normalized.append(normalized_record)
                elif isinstance(records, (int, float, str)):
                    normalized.append({
                        "test": test_name,
                        "value": records,
                    })
            measurements = normalized

        if not isinstance(measurements, list) or not measurements:
            return {
                "success": False,
                "agent": self.name,
                "trends": [],
                "message": "No valid health measurements provided.",
            }

        # ---------------------------------------------------------
        # Group measurements by test
        # ---------------------------------------------------------
        grouped = self.group_by_test(measurements)
        trends = []

        for test_name, records in grouped.items():
            records = self.sort_records(records)

            if len(records) < 2:
                # Baseline measurement from current report
                rec = records[0]
                val = rec.get("value")
                unit = rec.get("unit") or ""
                date_val = rec.get("date") or "Current report"
                curr_display = f"{val} {unit}".strip()

                trends.append({
                    "test": test_name,
                    "status": "baseline_recorded",
                    "unit": unit,
                    "previous": "No previous record",
                    "current": curr_display,
                    "trend": f"Baseline recorded ({date_val})",
                    "change": 0.0,
                    "direction": "baseline",
                    "interpretation": f"Current baseline measurement is {curr_display}.",
                    "records": records,
                })
                continue

            trend = self.calculate_trend(test_name, records)
            trends.append(trend)

        return {
            "success": True,
            "agent": self.name,
            "trends": trends,
            "safety_note": (
                "Trends describe changes in recorded measurements. "
                "They are not a medical diagnosis."
            ),
        }

    def group_by_test(self, measurements):
        grouped = {}
        for measurement in measurements:
            if not isinstance(measurement, dict):
                continue
            test_name = measurement.get("test")
            if not test_name:
                continue

            # Standardize capitalization of test names for grouping
            key = test_name.strip().title()
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(measurement)

        return grouped

    def sort_records(self, records):
        def parse_date(record):
            date_value = record.get("date")
            if not date_value:
                return datetime.max
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
                try:
                    return datetime.strptime(str(date_value).strip(), fmt)
                except (ValueError, TypeError):
                    continue
            return datetime.max

        return sorted(records, key=parse_date)

    def calculate_trend(self, test_name, records):
        first = records[0]
        latest = records[-1]

        first_value = self.to_number(first.get("value"))
        latest_value = self.to_number(latest.get("value"))
        unit = latest.get("unit", first.get("unit", ""))

        if first_value is None or latest_value is None:
            return {
                "test": test_name,
                "status": "unable_to_calculate",
                "unit": unit,
                "previous": str(first.get("value", "Not available")),
                "current": str(latest.get("value", "Not available")),
                "trend": "Unable to calculate numeric difference",
                "message": "Measurement values are not numeric.",
                "records": records,
            }

        change = latest_value - first_value
        percentage_change = (
            (change / abs(first_value)) * 100 if first_value != 0 else None
        )
        direction = self.get_direction(change)

        prev_display = f"{first_value} {unit}".strip()
        curr_display = f"{latest_value} {unit}".strip()
        trend_display = direction.capitalize()

        return {
            "test": test_name,
            "unit": unit,
            "first_record": {
                "date": first.get("date"),
                "value": first_value,
            },
            "latest_record": {
                "date": latest.get("date"),
                "value": latest_value,
            },
            "previous": prev_display,
            "current": curr_display,
            "trend": trend_display,
            "change": round(change, 2),
            "percentage_change": (
                round(percentage_change, 2)
                if percentage_change is not None
                else None
            ),
            "direction": direction,
            "interpretation": self.create_neutral_interpretation(
                direction, change, unit
            ),
            "records": records,
        }

    def to_number(self, value):
        try:
            return float(str(value).strip())
        except (TypeError, ValueError):
            return None

    def get_direction(self, change):
        tolerance = 0.01
        if abs(change) <= tolerance:
            return "stable"
        if change > 0:
            return "increased"
        return "decreased"

    def create_neutral_interpretation(self, direction, change, unit=""):
        u = f" {unit}" if unit else ""
        if direction == "increased":
            return f"The recorded value increased by {round(abs(change), 2)}{u}."
        if direction == "decreased":
            return f"The recorded value decreased by {round(abs(change), 2)}{u}."
        return "The recorded value remained approximately stable."


if __name__ == "__main__":
    agent = TrendAgent()
    m = [{"test": "Hemoglobin", "value": 10.2, "unit": "g/dL", "date": "2026-09-28"}]
    print(agent.analyze(m))