import io
import json
import pypdf
from typing import Any, Dict, Optional, Tuple
from services.llm_service import llm_service
from utils.logger import get_logger

logger = get_logger("service.resume_parser")

def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF or plain text bytes."""
    if filename.lower().endswith(".pdf"):
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading PDF {filename}: {e}", exc_info=True)
            # Fallback to decode
            return file_bytes.decode("utf-8", errors="ignore")
    else:
        try:
            return file_bytes.decode("utf-8", errors="ignore").strip()
        except Exception as e:
            logger.error(f"Error decoding text file {filename}: {e}", exc_info=True)
            return ""

async def parse_resume_text(text: str) -> Dict[str, Any]:
    """Use LLM to extract structured fields from resume text."""
    if not text:
        return _get_empty_resume()

    system_prompt = """You are the Resume Parser for CommuneOS.
Your job is to read the text of a resume and extract structured information from it.
You MUST return ONLY valid JSON in this exact structure:
{
  "skills": ["Skill1", "Skill2"],
  "technologies": ["Tech1", "Tech2"],
  "frameworks": ["Framework1", "Framework2"],
  "languages": ["Language1", "Language2"],
  "education": [
    {
      "school": "School Name",
      "degree": "Degree (e.g. BS, MS, PhD)",
      "field_of_study": "Field of Study",
      "start_year": 2018,
      "end_year": 2022
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "description": "Project description",
      "technologies": ["Tech1", "Tech2"]
    }
  ],
  "experience": [
    {
      "company": "Company Name",
      "role": "Role Title",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM",
      "description": "Role description"
    }
  ],
  "certifications": ["Certification Name"]
}

Rules:
- Do NOT generate paragraphs, comments, or intro/outro text. Only return the requested JSON fields.
- Make lists of skills, technologies, frameworks, languages, certifications simple strings.
- If some parts cannot be found or are missing, return empty lists.
"""

    prompt = f"Resume text:\n\n{text}\n\nParse this resume into the structured JSON representation."
    
    result_json, is_fallback = await llm_service.complete_json(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.1,
    )
    
    if is_fallback or not result_json:
        logger.warning("LLM resume parsing failed or fell back. Returning empty structured schema.")
        return _get_empty_resume()
        
    # Ensure all required keys exist
    expected_keys = ["skills", "technologies", "frameworks", "languages", "education", "projects", "experience", "certifications"]
    for key in expected_keys:
        if key not in result_json:
            result_json[key] = []
            
    return result_json

def _get_empty_resume() -> Dict[str, Any]:
    return {
        "skills": [],
        "technologies": [],
        "frameworks": [],
        "languages": [],
        "education": [],
        "projects": [],
        "experience": [],
        "certifications": []
    }
