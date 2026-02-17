"""
Drug Recommendations Module
Generates drug recommendations based on risk factors and fetches detailed info from OpenFDA
"""
import os
import requests
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


def get_model():
    """Get Gemini model"""
    return genai.GenerativeModel(
        "gemini-2.5-flash",
        generation_config={
            "temperature": 0.5,
            "top_p": 0.9,
            "max_output_tokens": 3000
        }
    )


def get_recommended_drugs_for_risk(extracted_data: dict, risk_score: float, shap_features: list) -> list:
    """
    Get recommended drug classes based on patient's risk factors
    
    Args:
        extracted_data: Patient's extracted medical data
        risk_score: The computed risk score
        shap_features: SHAP features showing risk contributors
        
    Returns:
        List of recommended drug names
    """
    # Build context from data
    factors = []
    if extracted_data.get("HbA1c_level") and extracted_data["HbA1c_level"] > 6.5:
        factors.append("elevated HbA1c (diabetes indicator)")
    if extracted_data.get("blood_glucose_level") and extracted_data["blood_glucose_level"] > 126:
        factors.append("high blood glucose")
    if extracted_data.get("hypertension"):
        factors.append("hypertension")
    if extracted_data.get("heart_disease"):
        factors.append("heart disease history")
    if extracted_data.get("bmi") and extracted_data["bmi"] > 30:
        factors.append("obesity (high BMI)")
    
    if not factors:
        return []
    
    prompt = f"""Based on these health risk factors: {', '.join(factors)}
    
    List exactly 3-4 commonly prescribed drug GENERIC names (not brand names) that doctors typically consider.
    Return ONLY the drug names, one per line, nothing else.
    Example format:
    Metformin
    Lisinopril
    Atorvastatin
    """
    
    try:
        model = get_model()
        response = model.generate_content(prompt)
        drugs = [d.strip() for d in response.text.strip().split('\n') if d.strip()]
        return drugs[:4]  # Limit to 4 drugs
    except Exception:
        # Fallback based on factors
        fallback_drugs = []
        if "HbA1c" in str(factors) or "glucose" in str(factors):
            fallback_drugs.append("Metformin")
        if "hypertension" in str(factors):
            fallback_drugs.append("Lisinopril")
        if "heart" in str(factors):
            fallback_drugs.append("Atorvastatin")
        return fallback_drugs


def fetch_detailed_drug_info(drug_name: str) -> dict:
    """
    Fetch detailed drug information from OpenFDA
    
    Args:
        drug_name: Generic drug name
        
    Returns:
        Dictionary with detailed drug info
    """
    url = f'https://api.fda.gov/drug/label.json?search=openfda.generic_name:"{drug_name}"&limit=1'
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'results' not in data or not data['results']:
            return {"name": drug_name, "found": False}
        
        result = data['results'][0]
        openfda = result.get('openfda', {})
        
        return {
            "name": drug_name,
            "found": True,
            "brand_names": openfda.get('brand_name', ['N/A'])[:3],
            "manufacturer": openfda.get('manufacturer_name', ['N/A'])[0],
            "purpose": result.get('indications_and_usage', ['Not available'])[0][:500],
            "dosage": result.get('dosage_and_administration', ['Consult doctor'])[0][:300],
            "warnings": result.get('warnings', ['No specific warnings listed'])[0][:400],
            "side_effects": result.get('adverse_reactions', ['Consult healthcare provider'])[0][:400],
            "contraindications": result.get('contraindications', ['See prescribing information'])[0][:300],
            "drug_interactions": result.get('drug_interactions', ['Consult pharmacist'])[0][:300],
        }
    except Exception as e:
        return {"name": drug_name, "found": False, "error": str(e)}


def format_drug_for_display(drug_info: dict) -> str:
    """Format drug info for Streamlit display"""
    if not drug_info.get("found"):
        return f"**{drug_info['name']}** - Information not available in FDA database"
    
    brands = ", ".join(drug_info.get("brand_names", ["N/A"]))
    
    formatted = f"""
**{drug_info['name'].title()}**
- **Brand Names:** {brands}
- **Purpose:** {drug_info.get('purpose', 'N/A')[:200]}...
- **Dosage:** {drug_info.get('dosage', 'Consult doctor')[:150]}...
- **Warnings:** {drug_info.get('warnings', 'N/A')[:150]}...
- **Side Effects:** {drug_info.get('side_effects', 'N/A')[:150]}...
"""
    return formatted


def get_drug_recommendations_section(extracted_data: dict, risk_score: float, shap_features: list) -> dict:
    """
    Main function to get drug recommendations with detailed info
    
    Args:
        extracted_data: Patient's medical data
        risk_score: Computed risk score
        shap_features: SHAP feature importance
        
    Returns:
        Dictionary with recommendations and detailed info
    """
    # Get recommended drugs based on risk factors
    recommended_drugs = get_recommended_drugs_for_risk(extracted_data, risk_score, shap_features)
    
    if not recommended_drugs:
        return {
            "has_recommendations": False,
            "message": "No specific drug recommendations based on current risk factors."
        }
    
    # Fetch detailed info for each drug
    drug_details = []
    for drug in recommended_drugs:
        info = fetch_detailed_drug_info(drug)
        drug_details.append(info)
    
    return {
        "has_recommendations": True,
        "drugs": drug_details,
        "disclaimer": "These are commonly prescribed medications for the identified risk factors. Always consult a healthcare professional before starting any medication."
    }
