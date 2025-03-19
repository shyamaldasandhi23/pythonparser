import spacy
import nltk
import re
import json
import docx
from pdfminer.high_level import extract_text
from nltk.corpus import stopwords

# Download necessary NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))

def extract_text_from_resume(file_path):
    """Extracts text from a resume file (pdf or docx)."""
    try:
        if file_path.endswith('.pdf'):
            return extract_text(file_path)
        elif file_path.endswith('.docx'):
            doc = docx.Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        else:
            raise ValueError("Unsupported file format. Please provide a PDF or DOCX file.")
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

def extract_information(text):
    """Extracts name, email, phone, skills, education, experience, and summary from text."""
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    education = extract_education(text)
    experience = extract_experience(text)
    summary = extract_summary(text)
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education,
        "experience": experience,
        "summary": summary,
    }

def extract_name(text):
    """Extracts name from text."""
    name = ""
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break
    return name

def extract_email(text):
    """Extracts email from text."""
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return email.group(0) if email else ""

def extract_phone(text):
    """Extracts phone number from text."""
    phone = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    return phone.group(0) if phone else ""

def extract_skills(text):
    """Extracts skills from text."""
    skills = ["Python", "Data Analysis", "Machine Learning", "SQL", "Communication", "Project Management", "Java", "C++", "Web Development", "Leadership"] #extend it with more skills as needed
    found_skills = [skill for skill in skills if skill.lower() in text.lower()]
    return found_skills

def extract_education(text):
    """Extracts education from text."""
    education_keywords = ["Bachelor", "Master", "PhD", "University", "College"]
    education = []
    for keyword in education_keywords:
        if keyword.lower() in text.lower():
            education.append(keyword)
    return education

def extract_experience(text):
    """Extracts experience from text (basic keyword matching)."""
    experience_keywords = ["Experience", "Project", "Work History"]
    experience = ""
    for keyword in experience_keywords:
        if keyword.lower() in text.lower():
            experience = text[text.lower().find(keyword.lower()):].split('\n')[0] #just take first line of section
            break

    return experience

def extract_summary(text):
    """Extracts summary from text (very basic)."""
    summary_keywords = ["Summary", "About Me", "Objective"]
    summary = ""
    for keyword in summary_keywords:
        if keyword.lower() in text.lower():
             summary = text[text.lower().find(keyword.lower()):].split('\n')[0] #just take first line of section
             break
    return summary

if __name__ == "__main__":
    file_path = input("Enter the path to your resume file (pdf or docx): ")  # Get file path from user
    resume_text = extract_text_from_resume(file_path)

    if resume_text:
        data = extract_information(resume_text)
        print(json.dumps(data, indent=4))
    else:
        print("Could not process the resume. Please check the file path and format.")