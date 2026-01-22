from flask import Flask, render_template, request, send_file, session, redirect, url_for, jsonify
import os
import google.generativeai as genai
import PyPDF2
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import webbrowser
import json 
import random
import requests

app = Flask(__name__)
script_dir = os.path.dirname(os.path.abspath(__file__))
uploads_dir = os.path.join(script_dir, "uploads")
os.makedirs(uploads_dir, exist_ok=True)

app.config['UPLOAD_FOLDER'] = uploads_dir
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'pdf'}
app.secret_key = "nullisgreat"   

genai.configure(api_key="AIzaSyD9c5s3ecOwNTwgRqZSCxWj3pCKfrSH2xY")

# report model 
model1 = genai.GenerativeModel("models/gemini-flash-lite-latest", generation_config={
    "temperature": 1.0,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 4000
})

# Model for drug info
model2 = genai.GenerativeModel(
    "models/gemini-flash-lite-latest",
    generation_config={
        "temperature": 0.7,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 50000,
    },
)


#report analyuzer

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/pdf-test')
def pdfinput():
    return render_template("input.html")

@app.route('/viewer')
def viewer():
    if 'pdf_filename' not in session:
        return redirect(url_for('index'))
    return render_template("analyzer.html")

@app.route('/get-pdf-info')
def get_pdf_info():
    filename = session.get('pdf_filename')
    if not filename:
        return jsonify({"error": "No PDF loaded"}), 400
    return jsonify({"filename": filename})

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
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
        
        extracted_text = extract_text_from_pdf(filepath)
        if extracted_text.startswith("Error reading PDF"):
            return jsonify({"error": extracted_text}), 400
        
        text_path = os.path.join(app.config['UPLOAD_FOLDER'], filename + ".txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        
        session['pdf_filename'] = filename
        
        return jsonify({
            "success": True,
            "filename": filename,
            "message": "PDF uploaded successfully",
            "text_length": len(extracted_text)
        })
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

# for pdf 
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    filename = session.get('pdf_filename', '')

    if not filename:
        return jsonify({"error": "No PDF loaded"}), 400
    
    text_path = os.path.join(app.config['UPLOAD_FOLDER'], filename + ".txt")
    if not os.path.exists(text_path):
        return jsonify({"error": "Extracted text not found"}), 400
    
    with open(text_path, "r", encoding="utf-8") as f:
        pdf_text = f.read()

    prompt = f"""
You are now a medical help bot you are given a report that you need to analyze  the report thhat I have given you and you need to be medically and factually accurate 
you are not trying to overshadow the role of a real doctor but you need to help the user asking 
If the report shows the need of life threatning signs or anything that requires serious medical attendtion dont be afraid to say so you can recommend that the user needs 
medical attention

IMPORTANT OUTPUT RULES:
- Output valid HTML only (no Markdown, no backslashes) but dont mention html in the text and neither use ```.
- Use <h3> for section titles.
- Use <ol><li> for numbered lists.
- Use <strong> for bold.
- Use <p> for paragraphs.
- Do not include <script> or event handlers.
- use "  " this spacing for the bullet points and = this for subpoints
While Making bullet points give a space after heading eg 
try to give most answers in bullet points unless asked...
try to be as consice and give a short answer as well unless asked in detail 
and dont use ``` or html words in the response and make it look clean
instead of numbers use bullet points

if there is casual responses like hello or thank you in USER QUESTION: 
ignore PDF CONTENT and just respond accordingly for hi jsut respond like a normal chatbot

topic 
   1: h1
   2: h2 

PDF CONTENT:
{pdf_text}

USER QUESTION:
{user_message}
"""

    if user_message.startswith("search youtube for:"):
        topic = user_message.replace("search youtube for:", "").strip()
        search_url = f"https://www.google.com/search?q={topic.replace(' ', '+')}"
        webbrowser.open(search_url)
        return jsonify({"response": f"<p>Opened Google search for <strong>{topic}</strong> in your browser! 🎥</p>", "is_html": True})

    try:
        response = model1.generate_content(prompt)
        ai_response = "".join([p.text for p in response.candidates[0].content.parts])
        return jsonify({"response": ai_response, "is_html": True})
    except Exception as e:
        return jsonify({"error": f"Error generating response: {str(e)}"}), 500


# for pdf
@app.route('/summarize', methods=['POST'])
def summarize():
    filename = session.get('pdf_filename', '')

    if not filename:
        return jsonify({"error": "No PDF loaded"}), 400
    
    text_path = os.path.join(app.config['UPLOAD_FOLDER'], filename + ".txt")
    if not os.path.exists(text_path):
        return jsonify({"error": "Extracted text not found"}), 400
    
    with open(text_path, "r", encoding="utf-8") as f:
        pdf_text = f.read()

    prompt = f"""
You are a helpful medical assistant. Provide an HTML-only summary of the following report that has been provided.

STRUCTURE:
<h3>1. Overall Score and Points</h3>
<ol><li>...</li></ol>

<h3>2. Attention required</h3>
<ol><li>...</li></ol>

<h3>3. Significant data or statistics</h3>
<ol><li>...</li></ol>

<h3>4. Recommended Medicine or Routines</h3>
<p>...</p>

try to give most answers in bullet points unless asked...
try to be as consice and give a short answer as well unless asked in detail 
and dont use ``` or html words in the response and make it look clean
instead of numbers use bullet pts

PDF CONTENT:
{pdf_text}
"""

    try:
        response = model1.generate_content(prompt)
        ai_response = "".join([p.text for p in response.candidates[0].content.parts])
        return jsonify({"response": ai_response, "is_html": True})
    except Exception as e:
        return jsonify({"error": f"Error generating summary: {str(e)}"}), 500


#druginforoutes
@app.route('/drug-info')
def drug_info_page():
    return render_template("drug_index.html")

def process_query(dinput):
    sysprompt = '''I have given you My Condiiton or a drug/brand name herers What you have to do We are connecting you to OpenFDA here are the three cases:
    Case 1: If the drug name is given if the drug is named as another name in OpenFDA reutrn the drug name
    Case 2: If brand name is given - convert to openFDA drug
    Case 3: Problem is given like headache high bp give drug name
    If indian brand is given find the main drug in them and give output but if a drug exists as another name in fda db use that
    Every response should be in a single word You need to eval ther cases and select which case fits the query and then give single word responses more than one word responses will not be tolerated
    here is your query you need to give me the name of the drug in all cases which would be most suitable for this cause : '''
    result = model2.generate_content(sysprompt + dinput)
    resn = "".join([p.text for p in result.candidates[0].content.parts])
    return resn

@app.route('/webredirect/<resn>')
def webdi(resn):
    l = f"https://www.1mg.com/search/all?name={resn}"
    return redirect(l)

def fetch_data_from_openfda(resn):
    url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{resn}"+OR+openfda.generic_name:"{resn}"&limit=1'
    response = requests.get(url)
    return response.json()

@app.route('/api/get-drug-info', methods=['POST'])
def get_drug_info():
    data = request.json
    drug_name = data.get('drugName', '').strip()
    
    if not drug_name:
        return jsonify({"error": "Drug name is required!"}), 400
    
    try:
        resn = process_query(drug_name)
        fda_data = fetch_data_from_openfda(resn)
        
        if 'results' in fda_data and fda_data['results']:
            dinfo = fda_data['results'][0]
            openfda_info = dinfo.get('openfda', {})
            generic_name = openfda_info.get('generic_name', ['Not available'])[0]
            brand_name = openfda_info.get('brand_name', [generic_name])[0]
            active_ingredient = dinfo.get('active_ingredient', ['Info not available'])[0]
            purpose_text = dinfo.get('indications_and_usage', ['Not available'])[0]
            dosage_text = dinfo.get('dosage_and_administration', ['Not available'])[0]
            alling = dinfo.get('spl_product_data_elements', ['Not Available'])[0]
            

            sysp = f''' You are provided with the following details from FDA about a particular drug using this knwoledge and your own knowledge which should me medically and factually
                        accruate Give a response formatted as given and it should be easy to understand but should cover all the things that this does also make a field for which patients to give this medicine too
                        If your knowledge or the data provided the the openFDA data conflitcs from the general use give the data that doctors widely used else dont say anything
                        - Generic Name: {generic_name}
                        
                        - Brand Name: {brand_name}
                        - All Ingridients: {alling}
                        - Active Ingredient: {active_ingredient}
                        - Purpose: {purpose_text}
                        - Dosage: {dosage_text}
                        
                        

                        Do not Use any special Symbols like * [NOT OBEYING THIS RULE WILL NOT BE TOLERATED DONT TRY TO BOLD THINGS 
                        output_warning: Provide the data in short simble heading and paragpraph no bullet points dont make tables and anything and keep everything 70% short and summarized

                        '''
            drugi = model2.generate_content(sysp)
            drug_info = "".join([p.text for p in drugi.candidates[0].content.parts])

            return jsonify({"data": drug_info})
        else:
            sys2 = '''You are given a NON FDA APPROVED DRUG/cream or anything please provide the name brand and generic name brand and active ingrident and its use: 
                      if its a addictrive drug dont give it but if its a geniune used drug like in india just not listed then you can give info here what you have to give: 
                      Name, generic name, brand name, all ingirdients and usage for dosage give use doctor advise use heading and paragraph format to give asnwers and DO NOT use any special characters like * 
                      hereis your drug: 
                      keep everything short and DO NOT USE SPECIAL SYMBOLS LIKE * or # this is final warning [not obeying this rule WILL NOT BE TOLDERATED dont try to make bold and use*]
                      if highly addictive drugs like Methamphetamine, opiates and cocaine. heroin are provided say they are addictive and consult doctor'''
            r = model2.generate_content(sys2 + resn)
            rsp = "".join([p.text for p in r.candidates[0].content.parts])
            return jsonify({"data": rsp})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#helper
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file with improved error handling"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            if pdf_reader.is_encrypted:
                try:
                    pdf_reader.decrypt("")  
                except:
                    return "Error reading PDF: Document is password protected"
            
            num_pages = len(pdf_reader.pages)
            if num_pages == 0:
                return "Error reading PDF: No pages found in document"
            
            text = ""
            for i, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    text += page_text + "\n"
                except Exception:
                    continue
            
            extracted_text = text.strip()
            if not extracted_text:
                return "Error reading PDF: No text could be extracted. Might be scanned/images only."
            return extracted_text
            
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# eroorcheck
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"error": "File too large. Maximum size is 50MB."}), 413

@app.errorhandler(413)
def handle_413(e):
    return jsonify({"error": "File too large. Maximum size is 50MB."}), 413


if __name__ == '__main__':
    app.run(debug=True)