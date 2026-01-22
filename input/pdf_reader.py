import re
from PyPDF2 import PdfReader


# ---------- PDF Text Extraction ----------
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyPDF2 (works for text-based PDFs)"""
    try:
        reader = PdfReader(pdf_path)
        full_text = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
        
        return "\n".join(full_text)
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# ---------- Structured Medical Extraction ----------
def parse_medical_fields(text: str) -> dict:
    data = {
        "age": None,
        "bmi": None,
        "HbA1c_level": None,
        "blood_glucose_level": None,  # normalized to mg/dL
        "hypertension": None,
        "heart_disease": None,
    }

    text_lower = text.lower()

    # ---------- AGE ----------
    m = re.search(r"age\s*[:\-]?\s*(\d{1,3})", text_lower)
    if m:
        data["age"] = int(m.group(1))

    # ---------- BMI ----------
    m = re.search(r"bmi\s*[:\-]?\s*(\d+\.?\d*)", text_lower)
    if m:
        data["bmi"] = float(m.group(1))

    # ---------- HbA1c ----------
    m = re.search(r"hba1c\s*[:\-]?\s*(\d+\.?\d*)\s*%?", text_lower)
    if m:
        data["HbA1c_level"] = float(m.group(1))

    # ---------- BLOOD GLUCOSE (UNIT AWARE) ----------
    # mg/dL
    m_mg = re.search(
        r"(glucose|blood glucose|fasting glucose).*?(\d+\.?\d*)\s*mg/dl",
        text_lower
    )

    # mmol/L
    m_mmol = re.search(
        r"(glucose|blood glucose|fasting glucose).*?(\d+\.?\d*)\s*mmol/l",
        text_lower
    )

    if m_mg:
        data["blood_glucose_level"] = float(m_mg.group(2))
    elif m_mmol:
        # Convert mmol/L → mg/dL
        data["blood_glucose_level"] = round(float(m_mmol.group(2)) * 18.0, 1)

    # ---------- HYPERTENSION ----------
    if re.search(r"hypertension\s*[:\-]?\s*no", text_lower):
        data["hypertension"] = False
    elif re.search(r"\bno\s+hypertension\b|\bnormotensive\b", text_lower):
        data["hypertension"] = False
    elif re.search(r"\bhypertension\b|\bhigh blood pressure\b", text_lower):
        data["hypertension"] = True


    # ---------- HEART DISEASE ----------
    if re.search(r"heart disease\s*[:\-]?\s*no", text_lower):
        data["heart_disease"] = False
    elif re.search(r"\bno\s+heart disease\b|\bnormal heart\b", text_lower):
        data["heart_disease"] = False
    elif re.search(r"\bheart disease\b|\bcardiac\b|\bcoronary\b", text_lower):
        data["heart_disease"] = True

    return data

# ---------- Data Quality ----------
def compute_data_quality(data: dict) -> str:
    filled = sum(1 for v in data.values() if v is not None)

    if filled >= 5:
        return "High"
    elif filled >= 3:
        return "Medium"
    else:
        return "Low"
