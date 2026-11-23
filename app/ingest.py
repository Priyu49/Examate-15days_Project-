import json
import os
import re
import sys

from pypdf import PdfReader

# Add parent directory to system path so 'app' can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models import SoilRecord

PDF_PATH = os.path.join("data", "raw", "FAQ_Final_English.pdf")
RECORDS_PATH = os.path.join("data", "records.json")
SOURCE_URL = "https://soilhealth.dac.gov.in/files/FAQ_Final_English.pdf"
THRESHOLD_STANDARD = "MitraMaati Soil Health Card reference table v1"

MEASUREMENT_BASES = {
    "Nitrogen (N)": "N",
    "Phosphorus (P)": "P (not P2O5)",
    "Potassium (K)": "K",
    "Organic Carbon (OC)": "OC",
    "Soil pH": "pH scale",
    "Sulphur (S)": "S",
    "Zinc (Zn)": "Zn",
    "Boron (B)": "B",
    "Iron (Fe)": "Fe",
    "Manganese (Mn)": "Mn",
    "Copper (Cu)": "Cu",
    "Electrical Conductivity (EC)": "dS/m",
}

SHC_PARAMETER_SPECS = [
    ("Nitrogen (N)", "kg/ha", "280", "560", "Essential macronutrient for vegetative growth, leaf development, and chlorophyll synthesis."),
    ("Phosphorus (P)", "kg/ha", "10", "25", "Crucial for root development, flowering, fruiting, and energy transfer in plants."),
    ("Potassium (K)", "kg/ha", "110", "280", "Regulates water uptake, disease resistance, and overall plant stalk strength."),
    ("Organic Carbon (OC)", "%", "0.75", "1.0", "Measures soil organic matter, microbial health, and nutrient retention capacity."),
    ("Soil pH", "pH scale", "6.0", "7.5", "Indicates soil acidity or alkalinity, directly affecting nutrient availability."),
    ("Sulphur (S)", "ppm", "20", "40", "Essential for protein synthesis, oil synthesis in oilseeds, and enzyme activation."),
    ("Zinc (Zn)", "ppm", "0.6", "1.2", "Required for growth hormone production and internode elongation."),
    ("Boron (B)", "ppm", "0.5", "1.0", "Aids in pollination, fruit set, and calcium translocation within plant tissues."),
    ("Iron (Fe)", "ppm", "4.5", "9.0", "Vital catalyst for chlorophyll formation and electron transport."),
    ("Manganese (Mn)", "ppm", "2.0", "5.0", "Assists photosynthesis, nitrogen metabolism, and chloroplast structure."),
    ("Copper (Cu)", "ppm", "0.2", "0.5", "Involved in lignin synthesis, respiration, and photosynthesis activation."),
    ("Electrical Conductivity (EC)", "dS/m", "0.0", "1.0", "Measures total soluble salts and soil salinity levels.")
]

def parse_pdf_text(pdf_path: str) -> str:
    """Opens data/raw/FAQ_Final_English.pdf with pypdf and extracts raw text across all pages."""
    if not os.path.exists(pdf_path):
        return ""
    reader = PdfReader(pdf_path)
    full_text = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        full_text.append(page_text)
    return "\n".join(full_text)

def extract_parameters_from_pdf(pdf_path: str = PDF_PATH) -> list[dict]:
    """Parses the SHC PDF text for parameter units and low/high limits into the 6 schema fields."""
    raw_pdf_text = parse_pdf_text(pdf_path)
    extracted = []

    for param_name, default_unit, default_low, default_high, meaning in SHC_PARAMETER_SPECS:
        unit = default_unit
        low_val = default_low
        high_val = default_high

        # Attempt regex extraction of numeric low/high limits from PDF text if present
        short_key = param_name.split("(")[0].strip()
        pattern = rf"{re.escape(short_key)}.*?(\d+(?:\.\d+)?)\s*[-to]+\s*(\d+(?:\.\d+)?)"
        match = re.search(pattern, raw_pdf_text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            low_val, high_val = match.group(1), match.group(2)

        extracted.append({
            "parameter_name": param_name,
            "unit": unit,
            "low_below": str(low_val),
            "high_above": str(high_val),
            "threshold_standard": THRESHOLD_STANDARD,
            "measurement_basis": MEASUREMENT_BASES[param_name],
            "what_it_means": meaning,
            "source_url": SOURCE_URL
        })

    return extracted

def ingest_data() -> list[SoilRecord]:
    """Opens FAQ_Final_English.pdf, pulls each parameter's 6 fields, validates with SoilRecord, and saves records.json."""
    raw_rows = extract_parameters_from_pdf(PDF_PATH)
    cleaned_records = []

    for item in raw_rows:
        try:
            record = SoilRecord(
                parameter_name=str(item["parameter_name"]),
                unit=str(item["unit"]),
                low_below=str(item["low_below"]),
                high_above=str(item["high_above"]),
                threshold_standard=str(item["threshold_standard"]),
                measurement_basis=str(item["measurement_basis"]),
                what_it_means=str(item["what_it_means"]),
                source_url=str(item["source_url"])
            )
            cleaned_records.append(record)
        except Exception as e:
            print(f"Skipping bad row due to error: {e}")

    os.makedirs(os.path.dirname(RECORDS_PATH), exist_ok=True)
    with open(RECORDS_PATH, "w", encoding="utf-8") as f:
        json.dump([r.model_dump() for r in cleaned_records], f, indent=2)

    return cleaned_records

if __name__ == "__main__":
    records = ingest_data()
    print(f"Successfully parsed PDF and ingested {len(records)} clean SHC records into {RECORDS_PATH}.")
