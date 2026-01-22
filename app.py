import os
from pathlib import Path
from flask import Flask, request, jsonify, session, render_template
from werkzeug.utils import secure_filename

# Setup paths
ROOT_DIR = Path(__file__).resolve().parent

# Import from input module
from input.pdf_reader import extract_text_from_pdf, parse_medical_fields, compute_data_quality

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
            "upload": "/api/upload (POST)",
            "analyze": "/api/analyze (POST)"
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
