import os
from pathlib import Path
from flask import Flask, request, jsonify, session, render_template
from werkzeug.utils import secure_filename

# Setup paths
ROOT_DIR = Path(__file__).resolve().parent

# Import from input module
from input.pdf_reader import extract_text_from_pdf, parse_medical_fields, compute_data_quality
from genai.report_chat import chat_with_report, summarize_report
from genai.drug_info import get_drug_info
from genai.gemini_explainer import configure_gemini

# Configure Gemini API
configure_gemini()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Upload configuration
UPLOAD_FOLDER = os.path.join(ROOT_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return jsonify({
        "message": "Clinical Risk Insight Tool API",
        "endpoints": {
            "upload": "/api/upload (POST) - Upload PDF and extract data",
            "analyze": "/api/analyze (POST) - Analyze health risk from extracted data",
            "chat": "/api/chat (POST) - Chat with AI about the uploaded report",
            "summarize": "/api/summarize (POST) - Get AI summary of the uploaded report",
            "drug_info": "/api/drug-info (POST) - Get drug information from OpenFDA"
        }
    })


@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Upload and extract text from a PDF file"""
    try:
        if 'pdf_file' not in request.files:
            return jsonify({"error": "No file selected"}), 400
        
        file = request.files['pdf_file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Please upload a PDF file."}), 400
            
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(filepath)
        if extracted_text.startswith("Error reading PDF"):
            return jsonify({"error": extracted_text}), 400
        
        # Save extracted text to file
        text_path = os.path.join(app.config['UPLOAD_FOLDER'], filename + ".txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        
        # Store filename in session
        session['pdf_filename'] = filename
        
        # Parse medical fields from extracted text
        parsed_data = parse_medical_fields(extracted_text)
        data_quality = compute_data_quality(parsed_data)
        
        return jsonify({
            "success": True,
            "filename": filename,
            "message": "PDF uploaded successfully",
            "text_length": len(extracted_text),
            "extracted_data": parsed_data,
            "data_quality": data_quality
        })
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_risk():
    """Analyze risk based on extracted or provided data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Import ML modules here to avoid circular imports
        from ml.predict import predict_risk
        from ml.explain import explain_prediction, group_shap_features, top_modifiable_factors
        
        # Predict risk
        risk_score = predict_risk(data)
        shap_features = explain_prediction(data)
        grouped_features = group_shap_features(shap_features)
        modifiable = top_modifiable_factors(shap_features)
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "LOW"
        elif risk_score < 0.6:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        return jsonify({
            "success": True,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_percentage": f"{risk_score:.1%}",
            "grouped_features": grouped_features,
            "modifiable_factors": modifiable
        })
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


# ================= REPORT CHAT =================
@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with AI about the uploaded medical report"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        filename = session.get('pdf_filename', '')

        if not filename:
            return jsonify({"error": "No PDF loaded. Please upload a PDF first."}), 400
        
        text_path = os.path.join(app.config['UPLOAD_FOLDER'], filename + ".txt")
        if not os.path.exists(text_path):
            return jsonify({"error": "Extracted text not found. Please re-upload the PDF."}), 400
        
        with open(text_path, "r", encoding="utf-8") as f:
            pdf_text = f.read()

        response = chat_with_report(pdf_text, user_message)
        return jsonify({"response": response, "is_html": True})
        
    except Exception as e:
        return jsonify({"error": f"Chat failed: {str(e)}"}), 500


@app.route('/api/summarize', methods=['POST'])
def summarize():
    """Generate a summary of the uploaded medical report"""
    try:
        filename = session.get('pdf_filename', '')

        if not filename:
            return jsonify({"error": "No PDF loaded. Please upload a PDF first."}), 400
        
        text_path = os.path.join(app.config['UPLOAD_FOLDER'], filename + ".txt")
        if not os.path.exists(text_path):
            return jsonify({"error": "Extracted text not found. Please re-upload the PDF."}), 400
        
        with open(text_path, "r", encoding="utf-8") as f:
            pdf_text = f.read()

        response = summarize_report(pdf_text)
        return jsonify({"response": response, "is_html": True})
        
    except Exception as e:
        return jsonify({"error": f"Summarization failed: {str(e)}"}), 500


# ================= DRUG INFO =================
@app.route('/api/drug-info', methods=['POST'])
def drug_info():
    """Get drug information from OpenFDA and AI"""
    try:
        data = request.get_json()
        drug_name = data.get('drugName', '').strip()
        
        if not drug_name:
            return jsonify({"error": "Drug name is required!"}), 400
        
        result = get_drug_info(drug_name)
        
        if "error" in result:
            return jsonify(result), 400
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Drug info failed: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
