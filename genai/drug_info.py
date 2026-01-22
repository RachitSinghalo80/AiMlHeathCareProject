"""
Drug Information Module
Fetches drug information from OpenFDA API and enhances with AI
"""
import os
import requests
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


def get_drug_model():
    """Get Gemini model configured for drug information"""
    return genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config={
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 50000,
        }
    )


def process_drug_query(drug_input: str) -> str:
    """
    Process drug/condition query to get standardized drug name for OpenFDA
    
    Args:
        drug_input: Drug name, brand name, or medical condition
        
    Returns:
        Standardized drug name for OpenFDA lookup
    """
    sys_prompt = '''I have given you a condition or a drug/brand name. Here's what you have to do - We are connecting you to OpenFDA, here are the three cases:
    Case 1: If the drug name is given, if the drug is named as another name in OpenFDA return that drug name
    Case 2: If brand name is given - convert to OpenFDA drug name
    Case 3: If a problem is given like headache, high BP - give the appropriate drug name
    
    If an Indian brand is given, find the main drug in it and give output. If a drug exists as another name in FDA db, use that.
    
    Every response should be in a SINGLE WORD. You need to evaluate the cases and select which case fits the query and then give single word responses.
    More than one word responses will not be tolerated.
    
    Here is your query - give me the name of the drug which would be most suitable: '''
    
    try:
        model = get_drug_model()
        result = model.generate_content(sys_prompt + drug_input)
        drug_name = "".join([p.text for p in result.candidates[0].content.parts])
        return drug_name.strip()
    except Exception as e:
        return drug_input  # Fallback to original input


def fetch_from_openfda(drug_name: str) -> dict:
    """
    Fetch drug information from OpenFDA API
    
    Args:
        drug_name: Standardized drug name
        
    Returns:
        OpenFDA API response as dictionary
    """
    url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{drug_name}"+OR+openfda.generic_name:"{drug_name}"&limit=1'
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def format_drug_info_with_ai(fda_data: dict, drug_name: str) -> str:
    """
    Format FDA drug data into readable format using AI
    
    Args:
        fda_data: Raw data from OpenFDA API
        drug_name: The drug name queried
        
    Returns:
        Formatted drug information string
    """
    if 'results' in fda_data and fda_data['results']:
        dinfo = fda_data['results'][0]
        openfda_info = dinfo.get('openfda', {})
        
        generic_name = openfda_info.get('generic_name', ['Not available'])[0]
        brand_name = openfda_info.get('brand_name', [generic_name])[0]
        active_ingredient = dinfo.get('active_ingredient', ['Info not available'])[0]
        purpose_text = dinfo.get('indications_and_usage', ['Not available'])[0]
        dosage_text = dinfo.get('dosage_and_administration', ['Not available'])[0]
        all_ingredients = dinfo.get('spl_product_data_elements', ['Not Available'])[0]

        sys_prompt = f'''You are provided with the following details from FDA about a particular drug. Using this knowledge and your own knowledge which should be medically and factually accurate, give a response formatted as given. It should be easy to understand but should cover all the things that this does. Also make a field for which patients to give this medicine to.

If your knowledge or the data provided conflicts with general use, give the data that doctors widely use, else don't say anything.

- Generic Name: {generic_name}
- Brand Name: {brand_name}
- All Ingredients: {all_ingredients}
- Active Ingredient: {active_ingredient}
- Purpose: {purpose_text}
- Dosage: {dosage_text}

OUTPUT RULES:
- Do NOT use any special symbols like * or #
- Do NOT try to bold things
- Provide the data in short simple headings and paragraphs
- No bullet points, no tables
- Keep everything 70% short and summarized
'''
        try:
            model = get_drug_model()
            result = model.generate_content(sys_prompt)
            return "".join([p.text for p in result.candidates[0].content.parts])
        except Exception as e:
            return f"Error formatting drug info: {str(e)}"
    else:
        # Drug not found in FDA database - use AI knowledge
        return get_non_fda_drug_info(drug_name)


def get_non_fda_drug_info(drug_name: str) -> str:
    """
    Get information for drugs not found in FDA database
    
    Args:
        drug_name: Name of the drug
        
    Returns:
        AI-generated drug information
    """
    sys_prompt = f'''You are given a NON-FDA APPROVED DRUG/cream or anything. Please provide the name, brand, generic name, brand and active ingredient and its use.

If it's an addictive drug, don't provide detailed info. But if it's a genuine used drug like in India (just not FDA listed), then you can give info.

What you have to give:
- Name
- Generic name  
- Brand name
- All ingredients
- Usage

For dosage, say "consult doctor".

Use heading and paragraph format. 
DO NOT use any special characters like * or #
This is a final warning - not obeying this rule WILL NOT BE TOLERATED.
Don't try to make bold or use *.

If highly addictive drugs like Methamphetamine, opiates, cocaine, or heroin are provided, say they are addictive and recommend consulting a doctor.

Here is your drug: {drug_name}
'''
    
    try:
        model = get_drug_model()
        result = model.generate_content(sys_prompt)
        return "".join([p.text for p in result.candidates[0].content.parts])
    except Exception as e:
        return f"Error fetching drug info: {str(e)}"


def get_drug_info(drug_query: str) -> dict:
    """
    Main function to get drug information
    
    Args:
        drug_query: Drug name, brand name, or condition
        
    Returns:
        Dictionary with drug information or error
    """
    if not drug_query or not drug_query.strip():
        return {"error": "Drug name is required!"}
    
    try:
        # Step 1: Process query to get standardized drug name
        drug_name = process_drug_query(drug_query)
        
        # Step 2: Fetch from OpenFDA
        fda_data = fetch_from_openfda(drug_name)
        
        # Step 3: Format the data
        formatted_info = format_drug_info_with_ai(fda_data, drug_name)
        
        return {
            "success": True,
            "drug_name": drug_name,
            "data": formatted_info
        }
    except Exception as e:
        return {"error": str(e)}
