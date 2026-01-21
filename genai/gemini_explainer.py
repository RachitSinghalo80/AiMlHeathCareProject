import google.generativeai as genai

import os


def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in environment")
    genai.configure(api_key=api_key)

    return genai 

def explain_for_doctor(risk_score: float, shap_features: list):
    features_text = "\n".join(
        [f"- {name}: {value:.3f}" for name, value in shap_features]
    )

    prompt = f"""
You are a clinical decision support assistant.

Risk score: {risk_score:.2f}

Key contributing factors:
{features_text}

Explain:
1. Why this patient is at this risk level
2. Which factors are most clinically relevant
3. What next-step actions may be considered (tests, follow-ups, lifestyle focus)

Rules:
- Do NOT give a diagnosis
- Mention uncertainty
- Use professional medical language
- Like a screening tool / medical report summary

"""

    model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={
        "max_output_tokens": 5000,   # 👈 controls length
        "temperature": 0.3,         # 👈 reduces verbosity
        "top_p": 0.9
    }
)

    response = model.generate_content(prompt)
    return response.text


def explain_for_patient(risk_score: float, shap_features: list):
    features_text = "\n".join(
        [f"- {name}" for name, _ in shap_features]
    )

    prompt = f"""
You are explaining a health risk to a patient.

Risk level: {risk_score:.0%}

Factors influencing this risk:
{features_text}

Explain:
1. What this risk means in simple terms
2. Which habits or factors may be contributing
3. What general lifestyle improvements could help

Rules:
- Use simple language
- Avoid medical jargon
- Do NOT cause fear
- Do NOT give medical advice
- Like a screening tool / medical report summary
"""

    model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={
        "max_output_tokens": 5000,   # 👈 controls length
        "temperature": 0.3,         # 👈 reduces verbosity
        "top_p": 0.9
    }
)

    response = model.generate_content(prompt)
    return response.text