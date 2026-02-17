from pathlib import Path
import sys
import os
import io

# Add project root to path to import ml, genai, input modules
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import yaml
import numpy as np

def convert_numpy_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(i) for i in obj]
    elif isinstance(obj, tuple):
        return [convert_numpy_types(i) for i in obj]
    else:
        return obj

# Import existing modules
from ml.predict import predict_risk
from ml.explain import (
    explain_prediction, 
    simulate_scenario,
    group_shap_features,
    top_modifiable_factors
)
from genai.gemini_explainer import (
    configure_gemini,
    explain_for_doctor,
    explain_for_patient
)
from genai.drug_info import get_drug_info
from genai.drug_recommendations import get_drug_recommendations_section
from input.pdf_reader import (
    extract_text_from_pdf,
    parse_medical_fields,
    compute_data_quality
)

# Initialize Flask
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configure Gemini
configure_gemini()

# Load thresholds
with open(ROOT_DIR / "config" / "thresholds.yaml", "r") as f:
    THRESHOLDS = yaml.safe_load(f)

# Ensure uploads directory
UPLOAD_FOLDER = ROOT_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)


# --- Helper: PDF Generation (duplicated from ui/app.py to avoid streamlit deps) ---
def generate_pdf_report_bytes(risk_level, risk_score, shap_groups, clinical_summary):
    buffer = io.BytesIO()
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
    # Replace newlines with <br/> for ReportLab
    summary_text = clinical_summary.replace("\n", "<br/>") if clinical_summary else "N/A"
    story.append(Paragraph(summary_text, styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<i>This report is for screening and educational purposes only. "
        "It does not provide diagnosis or treatment.</i>",
        styles["Italic"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


# --- Endpoints ---

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)
        
        # Extract text
        text = extract_text_from_pdf(str(filepath))
        if text.startswith("Error reading PDF"):
             return jsonify({'error': text}), 400
             
        # Parse data
        data = parse_medical_fields(text)
        quality = compute_data_quality(data)
        
        return jsonify({
            'filename': filename,
            'text_preview': text[:500],
            'extracted_data': data,
            'data_quality': quality
        })

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json.get('data')
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    try:
        # Predict Risk
        risk_score = predict_risk(data)
        shap_values = explain_prediction(data)
        
        # Calculate Risk Level
        if risk_score < THRESHOLDS["low"]:
            level = "LOW"
        elif risk_score < THRESHOLDS["medium"]:
            level = "MEDIUM"
        else:
            level = "HIGH"
            
        return jsonify(convert_numpy_types({
            'risk_score': float(risk_score),
            'risk_level': level,
            'shap_values': shap_values, 
            # Helper for frontend: pre-calculate top factors
            'top_factors': top_modifiable_factors(shap_values),
            'grouped_features': group_shap_features(shap_values)
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulate', methods=['POST'])
def simulate():
    req = request.json
    base_data = req.get('base_data')
    feature = req.get('feature')
    value = req.get('value')
    
    if not base_data or not feature or value is None:
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        # We need to convert feature name to snake_case equivalent if needed
        # But simulate_scenario expects strict feature keys. Frontend should send correct keys.
        simulated_data = simulate_scenario(base_data, feature, value)
        if simulated_data:
            new_risk = predict_risk(simulated_data)
            return jsonify({'simulated_risk': float(new_risk)})
        else:
            return jsonify({'error': 'Simulation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/drug-recommendations', methods=['POST'])
def drug_recommendations():
    req = request.json
    data = req.get('data')
    risk_score = req.get('risk_score')
    shap_features = req.get('shap_features') # This might need to be passed back or recalculated
    
    if not data or risk_score is None:
         return jsonify({'error': 'Missing data'}), 400
         
    # Fix: SHAP features might be complex to pass back/forth. 
    # If not provided, we might need to re-calculate, but let's assume frontend stores it.
    if not shap_features:
         shap_features = explain_prediction(data)

    try:
        recs = get_drug_recommendations_section(data, risk_score, shap_features)
        return jsonify(recs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/drug-info', methods=['GET'])
def drug_info():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    try:
        info = get_drug_info(query)
        return jsonify(info)
    except Exception as e:
         return jsonify({'error': str(e)}), 500

@app.route('/api/clinical-summary', methods=['POST'])
def clinical_summary():
    req = request.json
    risk_score = req.get('risk_score')
    shap_features = req.get('shap_features') # Optional, if not sent we recalc
    mode = req.get('mode', 'patient') # 'doctor' or 'patient'
    data = req.get('data') # needed for recalc if shap missing
    
    if risk_score is None:
         return jsonify({'error': 'Risk score required'}), 400
         
    if not shap_features and data:
         shap_features = explain_prediction(data)
    elif not shap_features and not data:
         return jsonify({'error': 'Data or shap features required'}), 400

    try:
        if mode.lower() == 'doctor':
            summary = explain_for_doctor(risk_score, shap_features)
        else:
            summary = explain_for_patient(risk_score, shap_features)
            
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    req = request.json
    risk_level = req.get('risk_level')
    risk_score = req.get('risk_score')
    shap_groups = req.get('grouped_features')
    clinical_summary = req.get('clinical_summary')
    
    if not all([risk_level, risk_score, shap_groups]):
        return jsonify({'error': 'Missing report data'}), 400
        
    try:
        pdf_bytes = generate_pdf_report_bytes(risk_level, risk_score, shap_groups, clinical_summary)
        return send_file(
            pdf_bytes,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='health_report.pdf'
        )
    except Exception as e:
        # print(e) # debug
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
