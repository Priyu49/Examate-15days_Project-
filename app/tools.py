import json
import os
import re

RECORDS_PATH = os.path.join("data", "records.json")
THRESHOLD_TABLE = "data/records.json"
DEFAULT_THRESHOLD_STANDARD = "MitraMaati Soil Health Card reference table v1"

# Words a farmer might type for each SHC parameter (used to pull "nitrogen 200" out of free text)
PARAMETER_ALIASES = {
    "Nitrogen (N)": ["nitrogen"],
    "Phosphorus (P)": ["phosphorus", "phosphorous"],
    "Potassium (K)": ["potassium"],
    "Organic Carbon (OC)": ["organic carbon", "oc"],
    "Soil pH": ["soil ph", "ph"],
    "Sulphur (S)": ["sulphur", "sulfur"],
    "Zinc (Zn)": ["zinc", "zn"],
    "Boron (B)": ["boron"],
    "Iron (Fe)": ["iron", "fe"],
    "Manganese (Mn)": ["manganese", "mn"],
    "Copper (Cu)": ["copper", "cu"],
    "Electrical Conductivity (EC)": ["electrical conductivity", "ec"],
}

# Traffic-light colours used by the Day 10 soil card
STATUS_COLORS = {"Low": "red", "Medium": "yellow", "High": "green"}


def parse_soil_query(query: str):
    """
    Pulls (parameter_name, measured_value) out of text such as
    'classify nitrogen 200' or 'my pH is 5.5'. Returns None when the text
    has no parameter + number, so the caller can fall back to RAG.
    """
    text = query.lower()
    number = re.search(r"-?\d+(?:\.\d+)?", text)
    if not number:
        return None
    best = None
    for name, words in PARAMETER_ALIASES.items():
        for w in words:
            m = re.search(rf"\b{re.escape(w)}\b", text)
            if m and (best is None or len(w) > best[1]):
                best = (name, len(w))
    if best is None:
        return None
    return best[0], float(number.group())

def load_records() -> list[dict]:
    if not os.path.exists(RECORDS_PATH):
        return []
    with open(RECORDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def classify_soil_card(parameter_name: str, measured_value: float) -> dict:
    """
    Deterministically compares each entered value with the declared threshold
    standard in data/records.json and labels it Low, Medium, or High.
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

    low_text = f"{low_limit:g}"
    high_text = f"{high_limit:g}"

    # Classification logic (thresholds come from records.json)
    if measured_value < low_limit:
        status = "Low"
        recommendation = (
            f"Low (below {low_text} {matched['unit']}). "
            "Apply the General Recommended Dose (GRD) plus the increase your state recommends."
        )
    elif measured_value <= high_limit:
        status = "Medium"
        recommendation = (
            f"Medium ({low_text}-{high_text} {matched['unit']}). "
            "Apply the standard General Recommended Dose (GRD)."
        )
    else:
        status = "High"
        recommendation = (
            f"High (above {high_text} {matched['unit']}). "
            "Reduce the dose below the GRD or withhold application."
        )
    color = STATUS_COLORS[status]

    return {
        "parameter": matched["parameter_name"],
        "unit": matched["unit"],
        "measured_value": measured_value,
        "status": status,
        "color_code": color,
        "recommendation": recommendation,
        "meaning": matched["what_it_means"],
        "source_url": matched["source_url"],
        "page": matched.get("page"),
        "threshold_standard": matched.get("threshold_standard", DEFAULT_THRESHOLD_STANDARD),
        "measurement_basis": matched.get("measurement_basis", matched["parameter_name"]),
        "threshold_table": THRESHOLD_TABLE,
        "classification_method": "deterministic threshold comparison",
        "low_below": low_limit,
        "high_above": high_limit
    }
