from pathlib import Path
import sys

# --- Ensure project root is on Python path ---
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import yaml

from ml.predict import predict_risk
from ml.explain import explain_prediction
from genai.gemini_explainer import (
    configure_gemini,
    explain_for_doctor,
    explain_for_patient
)

# ---------- Configure Gemini (from environment variable) ----------
configure_gemini()

# ---------- Page Config ----------
st.set_page_config(
    page_title="Clinical Risk Insight Tool",
    layout="wide"
)

st.title("🩺 Clinical Risk Insight Tool")
st.caption("Preventive Risk Assessment | ML + GenAI")

# ---------- Load Risk Thresholds ----------
with open("config/thresholds.yaml", "r") as f:
    thresholds = yaml.safe_load(f)

# ---------- Session State Initialization ----------
if "risk_score" not in st.session_state:
    st.session_state.risk_score = None
    st.session_state.shap_features = None
    st.session_state.input_data = None

# ---------- View Mode ----------
view_mode = st.radio(
    "View Mode",
    ["Doctor", "Patient"],
    horizontal=True
)

# ---------- Input Form ----------
st.subheader("Patient Information")

with st.form("patient_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Age", min_value=1, max_value=120)
        bmi = st.number_input("BMI", min_value=10.0, max_value=60.0)
        hba1c = st.number_input("HbA1c Level", min_value=3.0, max_value=15.0)

    with col2:
        blood_glucose = st.number_input(
            "Blood Glucose Level", min_value=50, max_value=300
        )

        hypertension = st.selectbox(
            "Hypertension (High Blood Pressure)",
            ["No", "Yes"]
        )
        

        heart_disease = st.selectbox(
            "Heart Disease",
            ["No", "Yes"]
    )
    

    with col3:
        gender = st.selectbox("Gender", ["Female", "Male", "Other"])
        smoking = st.selectbox(
            "Smoking History",
            ["Never", "Former", "Current", "Ever", "Not current"]
        )

    submitted = st.form_submit_button("Assess Risk")

# ---------- Inference ----------
if submitted:
    st.session_state.input_data = {
        "age": age,
        "bmi": bmi,
        "HbA1c_level": hba1c,
        "blood_glucose_level": blood_glucose,
        "hypertension": 1 if hypertension == "Yes" else 0,
        "heart_disease": 1 if heart_disease == "Yes" else 0,


        # Gender one-hot
        "gender_Male": 1 if gender == "Male" else 0,
        "gender_Other": 1 if gender == "Other" else 0,

        # Smoking history one-hot
        "smoking_history_never": 1 if smoking == "never" else 0,
        "smoking_history_former": 1 if smoking == "former" else 0,
        "smoking_history_current": 1 if smoking == "current" else 0,
        "smoking_history_ever": 1 if smoking == "ever" else 0,
        "smoking_history_not current": 1 if smoking == "not current" else 0,
    }

    st.session_state.risk_score = predict_risk(
        st.session_state.input_data
    )
    st.session_state.shap_features = explain_prediction(
        st.session_state.input_data
    )

# ---------- Display Results ----------
if st.session_state.risk_score is not None:
    risk_score = st.session_state.risk_score
    shap_features = st.session_state.shap_features

    if risk_score < thresholds["low"]:
        risk_level = "LOW"
        color = "green"
    elif risk_score < thresholds["medium"]:
        risk_level = "MEDIUM"
        color = "orange"
    else:
        risk_level = "HIGH"
        color = "red"

    st.markdown("---")
    st.subheader("Risk Assessment Result")

    st.markdown(
        f"<h3 style='color:{color}'>Risk Level: {risk_level}</h3>",
        unsafe_allow_html=True
    )
    st.metric("Risk Probability", f"{risk_score:.2%}")

    # ---------- SHAP Explanation ----------
    if view_mode == "Doctor":
        st.subheader("Why this risk was predicted")
        for name, value in shap_features:
            st.write(f"- **{name}** → impact: `{value:.3f}`")

    # ---------- GenAI Explanation ----------
    st.markdown("---")
    st.subheader("Explanation")

    if st.button("Explain"):
        with st.spinner("Generating explanation..."):
            if view_mode == "Doctor":
                explanation = explain_for_doctor(
                    st.session_state.risk_score,
                    st.session_state.shap_features
                )
            else:
                explanation = explain_for_patient(
                    st.session_state.risk_score,
                    st.session_state.shap_features
                )

        st.write(explanation)

    # ---------- Disclaimer ----------
    st.markdown("---")
    st.caption(
        "⚠️ This tool is for screening and educational purposes only. "
        "It does not provide a medical diagnosis or treatment."
    )

    # ---------- Reset ----------
    st.markdown("---")
    if st.button("Reset"):
        st.session_state.risk_score = None
        st.session_state.shap_features = None