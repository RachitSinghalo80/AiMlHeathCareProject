# 🩺 Clinical Risk Insight Tool

Preventive Risk Assessment using Machine Learning, Explainable AI, and Generative AI.

---

## 📌 Description

The **Clinical Risk Insight Tool** is a healthcare-focused web application designed to support **early diabetes risk screening** using structured medical data extracted from PDF reports.

The system combines:
- A **machine learning model** for risk probability estimation
- **Explainable AI (SHAP)** to justify predictions
- **Generative AI** to produce concise clinical summaries
- A **PDF-based workflow** aligned with real OPD / clinical settings

⚠️ This tool is intended for **screening and educational purposes only** and does **not provide diagnosis or treatment recommendations**.

---

## ✨ Key Features

- PDF medical report upload (Chrome-generated & scanned PDFs)
- Automated medical field extraction and normalization
- Data quality scoring before prediction
- Diabetes risk probability & risk tier (Low / Medium / High)
- SHAP-based explainability (feature-level impact)
- Grouped risk drivers:
  - Metabolic factors
  - Lifestyle factors
  - Medical history
- Top modifiable risk factors
- Scenario explorer (what-if analysis)
- Doctor / Patient explanation modes
- Pre-visit clinical report export (PDF)

---


---

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- pip
- Virtual environment (recommended)

### Clone the Repository
```bash
git clone https://github.com/your-username/clinical-risk-insight.git
cd clinical-risk-insight
```

### Create & Activate Virtual Environment
```
python -m venv venv
```
```
source venv/bin/activate        # macOS / Linux
```
```
venv\Scripts\activate           # Windows
```
### Install Dependencies
```
pip install -r requirements.txt
```

### 🔐 Environment Setup

- Create a .env file in the project root:
```
GEMINI_API_KEY=your_api_key_here
```

## ▶️ Usage
- Run the Application
```  
streamlit run ui/app.py
```

## Typical Workflow

1. Upload a medical/lab report (PDF)
2. Review extracted patient data
3. Confirm data accuracy
4. Generate diabetes risk assessment
5. Review explainability and scenario analysis
6. Generate clinical summary
7. Download pre-visit PDF report

## 📊 Model Details

- Algorithm: XGBoost Classifier
- Input Type: Structured tabular data
- Output: Risk probability (0–1)
- Interpretability: SHAP TreeExplainer

## 🧪 Explainability

- SHAP values quantify each feature’s contribution
- Visual bar chart for “Why this risk was predicted”
- Grouped explanations for clinical clarity
- Clear separation of modifiable vs non-modifiable factors

## ⚠️ Assumptions & Limitations

- Uploaded PDFs reflect accurate and recent medical data
- OCR accuracy depends on scan quality
- Model predictions are probabilistic, not diagnostic
- Performance may vary across populations
- GenAI outputs may contain minor inaccuracies

## 🔒 Ethics & Safety

- Explicit disclaimers in UI and reports
- No automated medical advice
- Bias-awareness messaging included
- Human-in-the-loop decision support

##👥 Authors & Acknowledgments

Project Team:
- Check out
  - [RachitSinghalo80](https://github.com/RachitSinghalo80)
  - [RydertHuGlIfE](https://github.com/RydertHuGlIfE)
  - [VinayakTandon199](https://github.com/VinayakTandon199)
  - [KartikeySingh246](https://github.com/KartikeySingh246)

## References

[SHAP]( https://shap.readthedocs.io)
[XGBoost](https://xgboost.readthedocs.io)
[Streamlit](https://docs.streamlit.io)
