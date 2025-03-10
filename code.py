import re
import os
import io
import docx
import pdfminer.high_level
import spacy
from typing import List, Optional

# Install spaCy's English model (large model recommended for accuracy)
# python -m spacy download en_core_web_lg
# Requires: pip install pdfminer.six python-docx spacy

def extract_information_from_resume(resume_path: str, use_spacy: bool = True) -> dict:
    """
    Extracts information from a resume file (PDF or DOCX).

    Args:
        resume_path (str): The path to the resume file.
        use_spacy (bool, optional): Whether to use spaCy for NER. Defaults to True.

    Returns:
        dict: A dictionary containing extracted information.
    """

    extracted_data = {
        'name': None,
        'email': None,
        'phone': None,
        'skills': [],
        'certifications': [],
        'qualifications': [],
        'projects': [],
        'summary': None,
        'filepath': resume_path
    }

    try:
        text = extract_text_from_resume(resume_path)
        if text:
            extracted_data['email'] = extract_email(text)
            extracted_data['phone'] = extract_phone_number(text)

            if use_spacy:
                extracted_data['name'] = extract_name_spacy(text)
            else:
                extracted_data['name'] = extract_name_regex(text)

            extracted_data['skills'] = extract_skills(text)
            extracted_data['certifications'] = extract_certifications(text)
            extracted_data['qualifications'] = extract_qualifications(text)
            extracted_data['projects'] = extract_projects(text)
            extracted_data['summary'] = extract_summary(text)
        else:
            print(f"Warning: Could not extract text from resume at {resume_path}")

    except Exception as e:
        print(f"Error processing {resume_path}: {e}")

    return extracted_data


def extract_text_from_resume(resume_path: str) -> Optional[str]:
    """Extracts text from a resume file (PDF or DOCX)."""
    try:
        if resume_path.endswith('.pdf'):
            return extract_text_from_pdf(resume_path)
        elif resume_path.endswith('.docx'):
            return extract_text_from_docx(resume_path)
        else:
            print(f"Unsupported file format: {resume_path}")
            return None
    except Exception as e:
        print(f"Error extracting text from {resume_path}: {e}")
        return None

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """Extracts text from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            text = pdfminer.high_level.extract_text(file)
            return text
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return None


def extract_text_from_docx(docx_path: str) -> Optional[str]:
    """Extracts text from a DOCX file."""
    try:
        doc = docx.Document(docx_path)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error extracting text from DOCX {docx_path}: {e}")
        return None


def extract_name_regex(text: str) -> Optional[str]:
    """Extracts a name from text using regular expressions."""
    name = None
    name_pattern = r"([A-Z][a-z]+)\s+([A-Z][a-z]+)"
    match = re.search(name_pattern, text)
    if match:
        name = match.group()
    return name


def extract_name_spacy(text: str) -> Optional[str]:
    """Extracts a name from text using spaCy."""
    try:
        nlp = spacy.load("en_core_web_lg")
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return None
    except OSError:
        print("Error: spaCy model (en_core_web_lg) not found. Please download it.")
        return None
    except Exception as e:
        print(f"Error using spaCy for name extraction: {e}")
        return None


def extract_email(text: str) -> Optional[str]:
    """Extracts an email address from text."""
    email = None
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(email_pattern, text)
    if match:
        email = match.group()
    return email


def extract_phone_number(text: str) -> Optional[str]:
    """Extracts a phone number from text."""
    phone = None
    phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    match = re.search(phone_pattern, text)
    if match:
        phone = match.group()
    return phone

def extract_skills(text: str) -> List[str]:
    """Extracts skills from text.  This is a VERY basic example and needs improvement."""
    # This is a placeholder and needs a MUCH better implementation.
    # Ideally, use a list of known skills, or a more sophisticated NLP technique.
    skills = []
    skill_keywords = ["Python", "Java", "SQL", "communication", "leadership", "management", "C++", "JavaScript", "React", "AWS", "Azure"] # Example list
    for skill in skill_keywords:
        if skill.lower() in text.lower():
            skills.append(skill)

    return skills

def extract_certifications(text: str) -> List[str]:
    """Extracts certifications from text. Needs significant improvement."""
    # This is a placeholder.  Realistically, you'd need a much more sophisticated approach,
    # perhaps involving regular expressions with known certification patterns.
    certifications = []
    certification_keywords = ["AWS Certified", "Microsoft Certified", "PMP", "CCNA", "CompTIA"] # Example list
    for cert in certification_keywords:
      if cert.lower() in text.lower():
        certifications.append(cert)
    return certifications

def extract_qualifications(text: str) -> List[str]:
    """Extracts qualifications (education) from text. Needs improvement."""
    # This is a placeholder.  You'd need more complex regex or NLP to identify degrees, etc.
    qualifications = []
    qualification_keywords = ["Bachelor's Degree", "Master's Degree", "PhD", "MBA"] # Example list
    for qual in qualification_keywords:
      if qual.lower() in text.lower():
        qualifications.append(qual)
    return qualifications

def extract_projects(text: str) -> List[str]:
    """Extracts project descriptions from text. Needs major improvement."""
    # This is a very basic placeholder.  Identifying projects accurately is difficult
    # without more context or structure in the resume.  Consider using section headings.
    projects = []
    # Very simple regex to find lines starting with "Project"
    project_matches = re.findall(r"Project\s*[:\-]?\s*(.+)", text, re.IGNORECASE)
    projects.extend(project_matches)
    return projects

def extract_summary(text: str) -> Optional[str]:
    """Extracts the summary/objective from text.  Needs improvement."""
    # This is a simplified approach.  It looks for "Summary" or "Objective" headings
    # and extracts the following paragraph.  Resumes vary *widely* in structure.
    summary = None
    summary_match = re.search(r"(Summary|Objective)\s*[:\-]?\s*(.+)", text, re.DOTALL | re.IGNORECASE)
    if summary_match:
      summary = summary_match.group(2).strip() # Extract everything after the heading

    return summary



def process_directory(directory_path: str, use_spacy: bool = True) -> List[dict]:
    """Processes all PDF and DOCX files in a directory."""
    results = []
    for filename in os.listdir(directory_path):
        if filename.endswith(('.pdf', '.docx')):
            filepath = os.path.join(directory_path, filename)
            data = extract_information_from_resume(filepath, use_spacy)
            results.append(data)
    return results


if __name__ == '__main__':

    # Example usage:
    resume_file = "example_resume.pdf"  # Replace with your file

    # Create a dummy PDF file for testing purposes
    with open(resume_file, "w") as f:
        f.write("""John Doe
john.doe@example.com
(123) 456-7890

Summary:
Highly motivated software engineer with experience in Python and Java.

Skills:
Python, Java, SQL, Communication, Leadership

Certifications:
AWS Certified Cloud Practitioner

Qualifications:
Bachelor's Degree in Computer Science

Projects:
Project 1: Developed a web application using Python and Flask.

Experience:
Software Engineer at ABC Company
""")


    extracted_info = extract_information_from_resume(resume_file)
    print("Extracted information from single file:", extracted_info)

    # Process all resumes in a directory:
    resume_directory = "resumes"  # Replace with your directory
    if not os.path.exists(resume_directory):
        os.makedirs(resume_directory) # create the directory if it doesn't exist.

    resume_file_2 = "resumes/example_resume2.pdf"
    with open(resume_file_2, "w") as f:
        f.write("""Jane Smith
jane.smith@example.com
(987) 654-3210

Objective:
To obtain a challenging position in a dynamic organization.

Skills:
JavaScript, React, AWS, Azure

Certifications:
Microsoft Certified Azure Fundamentals

Qualifications:
Master's Degree in Data Science

Projects:
Project 2: Created a data analysis dashboard using React and AWS.
""")


    extracted_info_list = process_directory(resume_directory)
    print("Extracted information from directory:")
    for info in extracted_info_list:
        print(info)