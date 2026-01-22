import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


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
        You are acting as a **clinical decision support (CDS) assistant**, not a treating physician.
        Your role is to provide an **interpretive risk assessment summary** based on a predictive model output.

        ────────────────────────────────────────
        MODEL OUTPUT
        ────────────────────────────────────────
        Estimated Risk Score: {risk_score:.2f}

        Key Contributing Features:
        {features_text}

        ────────────────────────────────────────
        INSTRUCTIONS
        ────────────────────────────────────────
        Generate a structured clinical-style narrative that would typically be seen in
        a **screening report or decision-support dashboard**.

        Your response MUST follow these principles:
        - Use professional, neutral, evidence-oriented medical language
        - Write as an aid to clinicians, not as direct advice to patients
        - Clearly acknowledge uncertainty and model limitations
        - Frame recommendations as considerations, not mandates

        ────────────────────────────────────────
        CONTENT REQUIREMENTS
        ────────────────────────────────────────

        1. **Risk Interpretation**
        - Explain what the reported risk score suggests in relative terms
            (e.g., low, moderate, elevated, or increased risk compared to baseline).
        - Clarify that this represents a probabilistic estimate, not a diagnosis.
        - Briefly note that risk estimates depend on the quality and scope of input data.

        2. **Clinically Relevant Contributing Factors**
        - Identify which input features appear most influential in the risk estimation.
        - Explain *why* these factors are clinically relevant based on general medical understanding.
        - Distinguish between modifiable and non-modifiable factors where applicable.
        - Avoid causal claims unless clearly supported.

        3. **Potential Next-Step Considerations**
        - Suggest reasonable **clinical considerations** such as:
            • additional monitoring
            • confirmatory testing
            • specialist referral
            • lifestyle or risk-factor optimization
        - Frame all actions as considerations, not instructions or mandates.
        - Emphasize clinician judgment and patient context.

        4. **Pharmacological Considerations** (NEW - Important)
        Based on the identified risk factors, suggest commonly used medications that clinicians 
        may consider. For each medication category:
        - Name the drug class and 1-2 common examples (generic names)
        - Briefly explain why this class is relevant to the identified risk factors
        - Note any important considerations (contraindications, monitoring requirements)
        
        Examples based on risk factors:
        - High HbA1c/Blood Glucose → Metformin, SGLT2 inhibitors, GLP-1 agonists
        - Hypertension → ACE inhibitors (Lisinopril), ARBs, Calcium channel blockers
        - High BMI with diabetes risk → Consider weight management medications
        - Heart disease risk → Statins, Aspirin (if appropriate)
        
        IMPORTANT: Always emphasize that:
        - These are general considerations, not prescriptions
        - Final medication decisions rest with the treating physician
        - Individual patient factors must be considered
        - Proper diagnostic workup is required before starting any medication

        5. **Uncertainty & Limitations**
        - Explicitly mention uncertainty related to:
            • model assumptions
            • missing or unmeasured variables
            • population generalizability
        - State that clinical decisions should not rely on this output alone.

        ────────────────────────────────────────
        TONE & STYLE
        ────────────────────────────────────────
        - Formal, concise, and medically appropriate
        - Similar to language used in EHR summaries or screening tool outputs
        - No alarmist or reassuring language
        - No direct patient addressing (do not say "you")

        ────────────────────────────────────────
        FINAL OUTPUT FORMAT
        ────────────────────────────────────────
        Provide the response using clear section headings:
        - Risk Summary
        - Key Contributing Factors
        - Clinical Considerations
        - Pharmacological Considerations
        - Limitations and Uncertainty
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
You are explaining a health risk to a patient in simple, friendly terms.

Risk level: {risk_score:.0%}

Factors influencing this risk:
{features_text}

Please explain the following in a clear, reassuring way:

1. **What This Means for You**
   - Explain what this risk level means in everyday terms
   - Don't be scary - focus on empowerment

2. **What's Contributing to This**
   - Which lifestyle factors or health markers may be playing a role
   - Be honest but gentle

3. **Simple Steps You Can Take**
   - Practical lifestyle changes that could help
   - Diet, exercise, sleep, stress management tips

4. **Medications Your Doctor Might Discuss**
   - Based on your health factors, here are some common medications doctors often consider
   - Explain in simple terms what each medication does (e.g., "helps control blood sugar", "helps lower blood pressure")
   - Examples:
     • If blood sugar is high → "Metformin - helps your body use insulin better"
     • If blood pressure is high → "Blood pressure medications to protect your heart"
     • If cholesterol is a concern → "Statins - help keep your arteries healthy"
   
   IMPORTANT: Always say:
   - "Only your doctor can decide if any medication is right for you"
   - "These are just examples of what doctors commonly prescribe"
   - "Always discuss with your healthcare provider"

5. **Next Steps**
   - Encourage them to discuss these findings with their doctor
   - Mention regular check-ups are important

Rules:
- Use simple, everyday language
- Avoid medical jargon - explain any medical terms used
- Be encouraging, not frightening
- This is educational, NOT medical advice
- Always encourage consulting with a doctor
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