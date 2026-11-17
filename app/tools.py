import json
import os

RECORDS_PATH = os.path.join("data", "records.json")

def load_records() -> list[dict]:
    if not os.path.exists(RECORDS_PATH):
        return []
    with open(RECORDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def classify_soil_card(parameter_name: str, measured_value: float) -> dict:
    """
    Compares each entered value with the low and high thresholds in records.json 
    and labels it Low, Medium, or High. Applies SHC color-code rules.
    """
    records = load_records()
    matched = None
    for rec in records:
        if rec["parameter_name"].lower() == parameter_name.lower() or rec["parameter_name"].lower().startswith(parameter_name.lower()):
            matched = rec
            break

    if not matched:
        return {
            "parameter": parameter_name,
            "measured_value": measured_value,
            "status": "Unknown",
            "recommendation": "Parameter not found in official records."
        }

    try:
        low_limit = float(matched["low_below"])
        high_limit = float(matched["high_above"])
    except ValueError:
        low_limit, high_limit = 0.0, 1.0

    # Classification logic
    if measured_value < low_limit:
        status = "Low"
        color = "Red / Orange"
        # Low means GRD plus state-specified increase (e.g. +25%)
        recommendation = f"Status is Low (below {low_limit} {matched['unit']}). Apply General Recommended Dose (GRD) + 30% increase."
    elif low_limit <= measured_value <= high_limit:
        status = "Medium (Moderate)"
        color = "Green (Sufficient)"
        # Moderate means general recommended dose
        recommendation = f"Status is Moderate/Sufficient (within {low_limit}-{high_limit} {matched['unit']}). Apply standard GRD."
    else:
        status = "High"
        color = "Blue"
        # High means general recommended dose minus 30% or restricted application
        recommendation = f"Status is High (above {high_limit} {matched['unit']}). Apply GRD minus 30% or withhold application."

    return {
        "parameter": matched["parameter_name"],
        "unit": matched["unit"],
        "measured_value": measured_value,
        "status": status,
        "color_code": color,
        "recommendation": recommendation,
        "meaning": matched["what_it_means"],
        "source_url": matched["source_url"]
    }