from pathlib import Path
import sys
from io import BytesIO

#---------Animation------------------
from streamlit_lottie import st_lottie
import json

#-----------Lottie Helper Function---------- 
def load_lottie(path):
    with open(path, "r") as f:
        return json.load(f)
 
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import yaml

# -------- ML & Explainability --------
from ml.predict import predict_risk
from ml.explain import (
    explain_prediction,
    shap_bar_plot,
    group_shap_features,
    top_modifiable_factors,
    simulate_scenario
)

# -------- GenAI --------
from genai.gemini_explainer import (
    configure_gemini,
    explain_for_doctor,
    explain_for_patient
)
from genai.drug_info import get_drug_info
from genai.drug_recommendations import get_drug_recommendations_section

# -------- PDF Reader --------
from input.pdf_reader import (
    extract_text_from_pdf,
    parse_medical_fields,
    compute_data_quality
)

# -------- PDF Report --------
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


# ================= PDF REPORT =================
def generate_pdf_report(risk_level, risk_score, shap_groups, clinical_summary):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>Pre-Visit Clinical Risk Summary</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Risk Level:</b> {risk_level}", styles["Normal"]))
    story.append(Paragraph(f"<b>Risk Probability:</b> {risk_score:.1%}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Key Risk Drivers</b>", styles["Heading2"]))
    for group, items in shap_groups.items():
        if items:
            story.append(Paragraph(f"<b>{group}</b>", styles["Normal"]))
            for name, value in items:
                direction = "Increases risk" if value > 0 else "Reduces risk"
                story.append(
                    Paragraph(
                        f"- {name.replace('_',' ').title()}: {direction}",
                        styles["Normal"]
                    )
                )
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Clinical Summary</b>", styles["Heading2"]))
    story.append(Paragraph(clinical_summary.replace("\n", "<br/>"), styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<i>This report is for screening and educational purposes only. "
        "It does not provide diagnosis or treatment.</i>",
        styles["Italic"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ================= APP SETUP =================
configure_gemini()

st.set_page_config(page_title="Clinical Risk Insight Tool", layout="wide")
st.markdown(
    """
    <style>
    /* ---- Global font tightening ---- */
    html, body, [class*="css"]  {
        font-size: 15px;
        line-height: 1.45;
    }

    /* ---- Section headers ---- */
    h2, h3 {
        margin-bottom: 0.4rem;
    }

    /* ---- Subheaders (e.g., Risk Drivers, Top Modifiable Factors) ---- */
    .block-container h3 {
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
    }

    /* ---- Reduce space between bullet items ---- */
    ul {
        padding-left: 1.2rem;
        margin-top: 0.2rem;
        margin-bottom: 0.4rem;
    }

    li {
        margin-bottom: 0.2rem;
    }

    /* ---- Reduce spacing between Streamlit blocks ---- */
    .element-container {
        margin-bottom: 0.6rem;
    }

    /* ---- Tighten captions ---- */
    .stCaption {
        margin-top: 0.1rem;
        margin-bottom: 0.3rem;
        font-size: 0.85rem;
        color: #9aa0a6;
    }

    /* ---- Buttons slightly tighter ---- */
    button {
        padding: 0.4rem 0.75rem;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🩺 Clinical Risk Insight Tool")
st.caption("Preventive Risk Assessment | ML + GenAI")

with open("config/thresholds.yaml", "r") as f:
    thresholds = yaml.safe_load(f)

# ================= SESSION STATE =================
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None
    st.session_state.data_quality = None
    st.session_state.risk_score = None
    st.session_state.shap_features = None
    st.session_state.clinical_summary = None

left_col, right_col = st.columns([1, 1.4])

# ================= LEFT PANEL =================
with left_col:
    view_mode = st.radio("View Mode", ["Doctor", "Patient"], horizontal=True)

    st.subheader("Upload Medical Report (PDF)")
    st.caption("PDF text extraction. Please review extracted values.")

    # Create uploads folder
    UPLOAD_FOLDER = ROOT_DIR / "uploads"
    UPLOAD_FOLDER.mkdir(exist_ok=True)

    uploaded_pdf = st.file_uploader(
        "Upload lab / medical report",
        type=["pdf"]
    )

    if uploaded_pdf and st.button("Extract Health Data"):
        with st.spinner("Extracting data from report..."):
            # Save uploaded PDF
            from werkzeug.utils import secure_filename
            filename = secure_filename(uploaded_pdf.name)
            filepath = UPLOAD_FOLDER / filename
            
            with open(filepath, "wb") as f:
                f.write(uploaded_pdf.getbuffer())
            
            # Extract text from PDF
            text = extract_text_from_pdf(str(filepath))
            
            # Check for extraction errors
            if text.startswith("Error reading PDF"):
                st.error(text)
                st.stop()
            
            # Save extracted text
            text_path = UPLOAD_FOLDER / (filename + ".txt")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            # Store filename in session
            st.session_state.pdf_filename = filename
            
            # Parse medical fields
            data = parse_medical_fields(text)
            quality = compute_data_quality(data)
            
            st.success(f"✅ PDF uploaded: {filename} ({len(text)} chars extracted)")

            st.session_state.extracted_data = data
            st.session_state.data_quality = quality
            st.session_state.risk_score = None
            st.session_state.shap_features = None
            st.session_state.clinical_summary = None

    if st.session_state.extracted_data:
        
        st.subheader("Patient Snapshot")

        for k, v in st.session_state.extracted_data.items():
            label = k.replace("_", " ").title()
            if k == "blood_glucose_level" and v is not None:
                st.write(f"**{label}**: {v} mg/dL (normalized)")
            elif k == "HbA1c_level" and v is not None:
                st.write(f"**{label}**: {v} %")
            else:
                st.write(f"**{label}**: {v if v is not None else 'Not found'}")

        # ---- Data Quality Badge ----
        dq = st.session_state.data_quality
        if dq == "High":
            st.success("Data Quality: High")
        elif dq == "Medium":
            st.warning("Data Quality: Medium")
        else:
            st.error("Data Quality: Low")
            st.stop()

        confirmed = st.checkbox(
            "I confirm that the extracted values look correct"
        )

        if not confirmed:
            st.info("Please confirm extracted values before risk assessment.")
            st.stop()

        if st.button("Assess Risk"):
            st.session_state.risk_score = predict_risk(
                st.session_state.extracted_data
            )
            st.session_state.shap_features = explain_prediction(
                st.session_state.extracted_data
            )


# ================= RIGHT PANEL =================
with right_col:
    if st.session_state.risk_score is not None:
        risk = st.session_state.risk_score
        shap_feats = st.session_state.shap_features

        if risk < thresholds["low"]:
            level, color, confidence = "LOW", "green", "High confidence (low risk)"
        elif risk < thresholds["medium"]:
            level, color, confidence = "MEDIUM", "orange", "Moderate confidence"
        else:
            level, color, confidence = "HIGH", "red", "High confidence (elevated risk)"

        st.markdown(
            f"<h2 style='color:{color}'>Risk Level: {level}</h2>",
            unsafe_allow_html=True
        )
        st.metric("Estimated Risk Probability", f"{risk:.1%}")
        st.caption(f"Model confidence: {confidence}")
        st.progress(float(min(max(risk, 0.0), 1.0)))
        
            
        st.subheader("Why this risk was predicted")
        st.pyplot(shap_bar_plot(shap_feats))

# ================= Full width result =================    
if st.session_state.risk_score is not None:
        st.markdown("---")
        st.subheader("Risk Drivers (Grouped)")

        left_risk, right_shap = st.columns([1.1, 1])

    # -------- LEFT: Grouped Risk Drivers (Text) --------
        with left_risk:
            grouped = group_shap_features(shap_feats)
            for group, items in grouped.items():
                if items:
                    st.markdown(f"**{group}**")
                    for n, v in items:
                        arrow = "↑" if v > 0 else "↓"
                        st.write(f"- {n.replace('_',' ').title()} {arrow}")
            st.caption(
            "How to read this section:\n"
            "• ↑ indicates a factor increasing estimated risk\n"
            "• ↓ indicates a factor reducing estimated risk\n"
            "• Some factors are non-modifiable (e.g., medical history)\n"
            "• Focus on the 'Top Modifiable Factors' section for actionable insight"
            )

        with right_shap:
            st.caption("Metabolic Risk Overview")
            lottie = load_lottie("assets/diabetes_metabolism.json")
            st_lottie(lottie, height=420, loop=True)
 

# ---------- Top Modifiable + Scenario Explorer (ONE UNIT) ----------
        st.markdown("---")
        st.subheader("Top Modifiable Factors")

        for n, _ in top_modifiable_factors(shap_feats):
            st.write(f"- {n.replace('_',' ').title()}")

        st.caption("What-if Scenario Explorer (Illustrative)")

        base_data = st.session_state.extracted_data.copy()

        scenario_feature = st.selectbox(
            "Adjust factor",
            ["BMI", "Blood Glucose"],
            key="scenario_factor"
        )

        if scenario_feature == "BMI" and base_data.get("bmi") is not None:
            new_val = st.slider(
            "Simulated BMI",
            10.0, 60.0, float(base_data["bmi"]),
            key="bmi_slider"
        )
            simulated = simulate_scenario(base_data, "bmi", new_val)

        elif scenario_feature == "Blood Glucose" and base_data.get("blood_glucose_level") is not None:
            new_val = st.slider(
            "Simulated Blood Glucose (mg/dL)",
            50, 300, int(base_data["blood_glucose_level"]),
            key="glucose_slider"
        )
            simulated = simulate_scenario(
            base_data, "blood_glucose_level", new_val
        )

        if simulated:
            sim_risk = predict_risk(simulated)
            st.write(f"Simulated Risk: **{sim_risk:.1%}**")


        # ================= DRUG RECOMMENDATIONS =================
        st.markdown("---")
        st.subheader("💊 Drug Recommendations")
        st.caption("Based on identified risk factors (consult healthcare provider)")
        
        if "drug_recommendations" not in st.session_state:
            st.session_state.drug_recommendations = None
        
        if st.button("Generate Drug Recommendations"):
            with st.spinner("Analyzing risk factors and fetching drug information..."):
                recommendations = get_drug_recommendations_section(
                    st.session_state.extracted_data,
                    risk,
                    shap_feats
                )
                st.session_state.drug_recommendations = recommendations
        
        if st.session_state.drug_recommendations:
            recs = st.session_state.drug_recommendations
            
            if not recs.get("has_recommendations"):
                st.info(recs.get("message", "No recommendations available"))
            else:
                st.warning(f"⚠️ {recs.get('disclaimer', '')}")
                
                for drug in recs.get("drugs", []):
                    with st.expander(f"📋 {drug.get('name', 'Unknown').title()}", expanded=False):
                        if drug.get("found"):
                            brands = ", ".join(drug.get("brand_names", ["N/A"]))
                            
                            st.markdown(f"**Brand Names:** {brands}")
                            st.markdown(f"**Manufacturer:** {drug.get('manufacturer', 'N/A')}")
                            
                            st.markdown("---")
                            st.markdown("**Purpose / Indications:**")
                            st.write(drug.get("purpose", "Not available")[:400])
                            
                            st.markdown("---")
                            st.markdown("**Dosage:**")
                            st.write(drug.get("dosage", "Consult doctor")[:250])
                            
                            st.markdown("---")
                            st.markdown("**⚠️ Warnings:**")
                            st.write(drug.get("warnings", "See prescribing information")[:300])
                            
                            st.markdown("---")
                            st.markdown("**Side Effects:**")
                            st.write(drug.get("side_effects", "Consult healthcare provider")[:300])
                            
                            st.markdown("---")
                            st.markdown("**Contraindications:**")
                            st.write(drug.get("contraindications", "See prescribing information")[:250])
                            
                            st.markdown("---")
                            st.markdown("**Drug Interactions:**")
                            st.write(drug.get("drug_interactions", "Consult pharmacist")[:250])
                        else:
                            st.info("Detailed FDA information not available for this drug.")

        st.markdown("---")
        
        st.subheader("Clinical Summary")
        if st.button("Generate Clinical Summary"):
            if view_mode == "Doctor":
                st.session_state.clinical_summary = explain_for_doctor(
                    risk, shap_feats
                )
            else:
                st.session_state.clinical_summary = explain_for_patient(
                    risk, shap_feats
                )

        if st.session_state.clinical_summary:
            st.write(st.session_state.clinical_summary)

        st.markdown("---")
        if st.button("Download Pre-Visit Report (PDF)"):
            if not st.session_state.clinical_summary:
                st.session_state.clinical_summary = (
                    explain_for_doctor(risk, shap_feats)
                    if view_mode == "Doctor"
                    else explain_for_patient(risk, shap_feats)
                )

            pdf_buffer = generate_pdf_report(
                risk_level=level,
                risk_score=risk,
                shap_groups=grouped,
                clinical_summary=st.session_state.clinical_summary
            )

            st.download_button(
                label="Click to download PDF",
                data=pdf_buffer,
                file_name="pre_visit_risk_summary.pdf",
                mime="application/pdf"
            )

        st.markdown("---")
        st.caption(
            "⚠️ Screening & educational use only. "
            "Not a diagnostic or treatment tool."
        )

# ================= DRUG INFO SECTION =================
st.markdown("---")
st.subheader("💊 Drug Information Lookup")
st.caption("Search for drug information using name, brand, or condition")

# Initialize session state for drug info
if "drug_info_result" not in st.session_state:
    st.session_state.drug_info_result = None

drug_query = st.text_input(
    "Enter drug name, brand name, or condition",
    placeholder="e.g., Metformin, Crocin, headache, high blood pressure"
)

if st.button("🔍 Search Drug Info"):
    if drug_query:
        with st.spinner("Fetching drug information..."):
            result = get_drug_info(drug_query)
            st.session_state.drug_info_result = result
    else:
        st.warning("Please enter a drug name or condition")

if st.session_state.drug_info_result:
    result = st.session_state.drug_info_result
    if "error" in result:
        st.error(result["error"])
    else:
        st.success(f"✅ Found information for: **{result.get('drug_name', drug_query)}**")
        st.markdown("---")
        st.write(result.get("data", "No information available"))
        
        st.markdown("---")
        st.caption(
            "⚠️ Drug information is for educational purposes only. "
            "Always consult a healthcare professional before taking any medication."
        )
