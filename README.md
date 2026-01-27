Clinical Risk Insight Tool

Preventive Risk Assessment using ML + Explainable AI + GenAI

1. Overview

Clinical Risk Insight Tool is a preventive screening application designed to estimate diabetes risk from medical reports and present the results in a clinically interpretable, ethical, and actionable manner.

Instead of acting as a diagnostic system, the tool focuses on:

Early risk identification

Transparent explanation of why risk is high

Supporting clinicians and patients with decision insights, not prescriptions

The project combines:

Machine Learning (XGBoost) for risk prediction

SHAP for explainability

PDF-based medical report ingestion

GenAI for human-readable clinical summaries

2. Problem Statement

Many individuals remain undiagnosed or late-diagnosed for diabetes due to:

Fragmented medical data

Lack of interpretability in ML predictions

Overly technical risk tools that are not patient-friendly

Existing tools often output a single risk score without context.

3. Solution Approach

This system reframes risk prediction as a clinical decision support workflow rather than a simple calculator.

Key Design Principles

Explainability-first (no black-box outputs)

Preventive, not diagnostic

Doctor + Patient friendly views

Ethically constrained GenAI usage

4. System Architecture
PDF Medical Report
        ↓
Text Extraction (PyPDF2 / OCR fallback)
        ↓
Structured Field Parsing & Normalization
        ↓
Data Quality Scoring
        ↓
ML Risk Prediction (XGBoost)
        ↓
Explainability Layer (SHAP)
        ↓
Scenario Simulation (What-if analysis)
        ↓
GenAI Summary (Doctor / Patient tone)
        ↓
Pre-Visit PDF Report

5. Input Handling
Supported Inputs

PDF medical / lab reports (Chrome-generated or scanned)

Extracted fields include:

Age

BMI

HbA1c

Blood glucose (unit-normalized)

Hypertension

Heart disease

Data Quality Score

Each upload is assigned a Data Quality level:

High: sufficient clinical fields present

Medium: partial data

Low: insufficient → risk assessment blocked

This prevents unreliable predictions.

6. Machine Learning Core
Model

XGBoost classifier

Trained on structured tabular diabetes datasets

Outputs probability, not diagnosis

Output

Risk probability (0–100%)

Risk tier: Low / Medium / High

Confidence indicator (distance from decision boundary)

7. Explainability (SHAP)

SHAP values are used to explain feature-level contribution.

SHAP Outputs

Bar chart: “Why this risk was predicted”

Grouped risk drivers:

Metabolic factors (HbA1c, glucose, BMI)

Lifestyle factors (smoking, if present)

Medical history (age, hypertension, heart disease)

Interpretation Rules

↑ increases estimated risk

↓ reduces estimated risk

Some factors are non-modifiable

8. Top Modifiable Factors

The system highlights Top 3 modifiable drivers such as:

Blood glucose level

BMI

These are surfaced separately to guide preventive action, not treatment.

9. Scenario Explorer (Illustrative)

A what-if simulation allows adjustment of one variable at a time (e.g., BMI or glucose) to show:

“If this factor improved, estimated risk would decrease.”

⚠️ Clearly labeled as illustrative, not predictive.

10. GenAI Layer

GenAI is used only after ML prediction.

Capabilities

One-click Clinical Summary

Two tones:

Doctor view (technical)

Patient view (empathetic, simple language)

Explains why risk is high using SHAP outputs

Explicitly NOT used for

Diagnosis

Drug prescription

Medical advice

11. Reporting
Pre-Visit PDF Summary

Generated for OPD / clinical workflow:

Risk level & probability

Key drivers

SHAP-based explanation

Clinical summary

Disclaimers

12. UI Design Decisions

Two-panel layout (Input → Output)

Snapshot + explanation aligned side-by-side

Minimal animations, no distracting visuals

Designed to feel hospital-grade, not consumer gimmick

13. Assumptions

Uploaded PDF reflects recent and accurate medical data

Model predictions are screening-level insights

Risk factors are interpreted independently (no causal claims)

GenAI responses may contain minor inaccuracies

14. Limitations

Not a diagnostic system

Performance depends on data quality

OCR accuracy varies for scanned reports

Population bias may exist in training data

15. Ethics & Safety

Explicit disclaimers throughout the app

Bias-awareness messaging

No automated treatment recommendations

Human-in-the-loop design encouraged

16. Intended Use

✔ Preventive screening
✔ Clinical decision support
✔ Patient education

❌ Diagnosis
❌ Treatment planning
❌ Emergency use

17. Tech Stack

Frontend: Streamlit

ML: XGBoost, SHAP

PDF Parsing: PyPDF2 / OCR fallback

GenAI: Gemini API

Reporting: ReportLab

18. Conclusion

This project demonstrates how ML + Explainability + GenAI can be combined responsibly to create a trustworthy healthcare support tool, focusing on clarity, prevention, and ethics rather than automation.
