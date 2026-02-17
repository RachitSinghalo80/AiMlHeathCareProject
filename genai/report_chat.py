"""
Report Chat Module
Handles AI-powered chat and summarization for medical reports
"""
import os
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


def get_report_model():
    """Get Gemini model configured for report analysis"""
    return genai.GenerativeModel(
        "gemini-2.5-flash",
        generation_config={
            "temperature": 1.0,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 4000
        }
    )


def chat_with_report(pdf_text: str, user_message: str) -> str:
    """
    Chat with AI about the uploaded medical report
    
    Args:
        pdf_text: Extracted text from the PDF
        user_message: User's question/message
        
    Returns:
        AI response in HTML format
    """
    prompt = f"""
You are now a medical help bot you are given a report that you need to analyze the report that I have given you and you need to be medically and factually accurate 
you are not trying to overshadow the role of a real doctor but you need to help the user asking 
If the report shows the need of life threatening signs or anything that requires serious medical attention dont be afraid to say so you can recommend that the user needs 
medical attention

IMPORTANT OUTPUT RULES:
- Output valid HTML only (no Markdown, no backslashes) but dont mention html in the text and neither use ```.
- Use <h3> for section titles.
- Use <ol><li> for numbered lists.
- Use <strong> for bold.
- Use <p> for paragraphs.
- Do not include <script> or event handlers.
- Use proper spacing for bullet points

Rules:
- Try to give most answers in bullet points unless asked
- Try to be as concise and give a short answer unless asked in detail 
- Don't use ``` or html words in the response and make it look clean
- Instead of numbers use bullet points

If there are casual responses like hello or thank you in USER QUESTION: 
ignore PDF CONTENT and just respond accordingly, for hi just respond like a normal chatbot

PDF CONTENT:
{pdf_text}

USER QUESTION:
{user_message}
"""

    try:
        model = get_report_model()
        response = model.generate_content(prompt)
        ai_response = "".join([p.text for p in response.candidates[0].content.parts])
        return ai_response
    except Exception as e:
        return f"<p>Error generating response: {str(e)}</p>"


def summarize_report(pdf_text: str) -> str:
    """
    Generate a structured summary of the medical report
    
    Args:
        pdf_text: Extracted text from the PDF
        
    Returns:
        AI-generated summary in HTML format
    """
    prompt = f"""
You are a helpful medical assistant. Provide an HTML-only summary of the following report that has been provided.

STRUCTURE:
<h3>1. Overall Score and Points</h3>
<ul><li>...</li></ul>

<h3>2. Attention Required</h3>
<ul><li>...</li></ul>

<h3>3. Significant Data or Statistics</h3>
<ul><li>...</li></ul>

<h3>4. Recommended Actions or Routines</h3>
<p>...</p>

Rules:
- Try to give most answers in bullet points
- Be concise and give a short summary
- Don't use ``` or html words in the response
- Make it look clean and professional
- Use bullet points instead of numbers

PDF CONTENT:
{pdf_text}
"""

    try:
        model = get_report_model()
        response = model.generate_content(prompt)
        ai_response = "".join([p.text for p in response.candidates[0].content.parts])
        return ai_response
    except Exception as e:
        return f"<p>Error generating summary: {str(e)}</p>"
