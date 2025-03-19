import re
import json
from datetime import datetime
import io

try:
    from pypdf import PdfReader  # For PDF parsing (install with pip install pypdf)
except ImportError:
    print("pypdf is not installed. Please install it with: pip install pypdf")
    PdfReader = None

try:
    import docx  # For DOCX parsing (install with pip install python-docx)
except ImportError:
    print("python-docx is not installed. Please install it with: pip install python-docx")
    docx = None


try:
    import spacy  # For NLP (install with pip install spacy)
    nlp = spacy.load("en_core_web_lg")  # Load a  English model.  Other options: en_core_web_md, en_core_web_lg
except ImportError:
    print("spaCy is not installed. Please install it with: pip install spacy")
    spacy = None
    nlp = None
    print("Also, download the English language model: python -m spacy download en_core_web_lg")
except OSError:
    print("Error: The spaCy model 'en_core_web_lg' is not downloaded. Please download it using: python -m spacy download en_core_web_lg")
    spacy = None
    nlp = None


def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    if PdfReader is None:
        print("PDF parsing is disabled because pypdf is not installed.")
        return ""

    text = ""
    try:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


def extract_text_from_docx(docx_file):
    """Extracts text from a DOCX file."""
    if docx is None:
        print("DOCX parsing is disabled because python-docx is not installed.")
        return ""
    try:
        doc = docx.Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""


def parse_job_description(job_description):
    """
    Parses a job description to extract key information using NLP.

    Args:
        job_description (str): The job description text.

    Returns:
        str: A JSON string containing the extracted information.  Returns an empty JSON string if parsing fails.
    """

    try:
        if nlp is None:
            print("NLP (spaCy) is not available. Using basic keyword extraction.")
            job_role = extract_job_role_keywords(job_description)
            responsibilities = extract_responsibilities_keywords(job_description)
            location = extract_location_keywords(job_description)
            organization = extract_organization_keywords(job_description)
            domain = extract_domain_keywords(job_description)
            date_posted = extract_date_posted(job_description)
        else:
            doc = nlp(job_description)
            job_role = extract_job_role_nlp(doc)
            responsibilities = extract_responsibilities_nlp(doc)
            location = extract_location_nlp(doc)
            organization = extract_organization_nlp(doc)
            domain = extract_domain_nlp(doc)
            date_posted = extract_date_posted(job_description)  # Date extraction doesn't always benefit from NLP

        parsed_data = {
            "job_role": job_role,
            "responsibilities": responsibilities,
            "location": location,
            "organization": organization,
            "domain": domain,
            "date_posted": date_posted
        }

        return json.dumps(parsed_data, indent=4)

    except Exception as e:
        print(f"Error parsing job description: {e}")
        return json.dumps({})  # Return an empty JSON object on error.

# Keyword-based extraction functions (fallback if NLP is not available)
def extract_job_role_keywords(job_description):
    """Extracts the job role using keywords."""
    role_keywords = ["Role:", "Title:", "Position:", "Job Title:"]
    for keyword in role_keywords:
        match = re.search(rf"{keyword}\s*([A-Za-z\s-]+)", job_description, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    first_line_match = re.match(r"([A-Za-z\s-]+)", job_description)
    if first_line_match:
        return first_line_match.group(1).strip()
    return None

def extract_responsibilities_keywords(job_description):
    """Extracts responsibilities using keywords."""
    responsibilities = []
    bullet_point_regex = r"[\-\u2022\u2023\u25E6\u2043]\s*([A-Za-z0-9\s.,();:-]+)(?=\n|$)"
    numbered_list_regex = r"\d+\.\s*([A-Za-z0-9\s.,();:-]+)(?=\n|$)"
    bullet_matches = re.findall(bullet_point_regex, job_description)
    numbered_matches = re.findall(numbered_list_regex, job_description)
    responsibilities.extend(bullet_matches)
    responsibilities.extend(numbered_matches)
    return [resp.strip() for resp in responsibilities]

def extract_location_keywords(job_description):
    """Extracts the location using keywords."""
    location_keywords = ["Location:", "City:", "Based in:", "Work Location:"]
    for keyword in location_keywords:
        match = re.search(rf"{keyword}\s*([A-Za-z\s,]+)", job_description, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_organization_keywords(job_description):
    """Extracts the organization name using keywords."""
    org_keywords = ["Company:", "Organization:", "Hiring at:", "Posted by:"]
    for keyword in org_keywords:
        match = re.search(rf"{keyword}\s*([A-Za-z\s&.]+)", job_description, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_domain_keywords(job_description):
    """Extracts the domain using keywords."""
    domains = ["Technology", "Finance", "Healthcare", "Education", "Marketing", "Sales", "Engineering", "Science", "Arts", "Retail"]
    found_domains = []
    for domain in domains:
        if re.search(r"\b" + domain + r"\b", job_description, re.IGNORECASE):
            found_domains.append(domain)
    return found_domains


# NLP-based extraction functions
def extract_job_role_nlp(doc):
    """Extracts the job role using NLP."""
    # This is a simplified example.  More sophisticated techniques might be needed.
    for ent in doc.ents:
        if ent.label_ == "JOB_TITLE":  # You'd need to train or use a model with JOB_TITLE entity recognition
            return ent.text.strip()
    # Fallback: Try extracting nouns that appear at the beginning of the description
    for token in doc:
        if token.pos_ == "NOUN" and token.dep_ == "ROOT":
            return token.text.strip()
    return None


def extract_responsibilities_nlp(doc):
    """Extracts responsibilities using NLP."""
    responsibilities = []
    for sent in doc.sents:
        # This is a very basic example.  You'll likely need to refine this based on your data.
        if "responsible" in sent.text.lower() or "required" in sent.text.lower() or "duties" in sent.text.lower():
            responsibilities.append(sent.text.strip())
    return responsibilities


def extract_location_nlp(doc):
    """Extracts the location using NLP."""
    for ent in doc.ents:
        if ent.label_ == "GPE":  # Geopolitical entity (city, country, etc.)
            return ent.text.strip()
    return None


def extract_organization_nlp(doc):
    """Extracts the organization name using NLP."""
    for ent in doc.ents:
        if ent.label_ == "ORG":
            return ent.text.strip()
    return None


def extract_domain_nlp(doc):
    """Extracts the domain using NLP.  More advanced techniques are needed for this."""
    domains = ["Technology", "Finance", "Healthcare", "Education", "Marketing", "Sales", "Engineering", "Science", "Arts", "Retail"]
    found_domains = []
    text = doc.text.lower()
    for domain in domains:
        if domain.lower() in text:
            found_domains.append(domain)
    return found_domains


def extract_date_posted(job_description):
    """Extracts the date the job was posted."""
    date_patterns = [
        r"Posted on:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        r"Date Posted:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\s*ago",
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}"
    ]

    for pattern in date_patterns:
        match = re.search(pattern, job_description, re.IGNORECASE)
        if match:
            date_string = match.group(1)
            try:
                date_obj = datetime.strptime(date_string, "%m/%d/%Y")
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
                except ValueError:
                    try:
                        date_obj = datetime.strptime(date_string, "%B %d, %Y")
                    except ValueError:
                        try:
                            date_obj = datetime.strptime(date_string, "%m-%d-%Y")
                        except ValueError:
                            try:
                                date_obj = datetime.strptime(date_string, "%d-%m-%Y")
                            except ValueError:
                                return None
            return date_obj.strftime("%Y-%m-%d")

    return None


def process_job_description_file(file_path):
    """
    Processes a job description file (PDF or DOCX) to extract information.

    Args:
        file_path (str): The path to the job description file.

    Returns:
        str: A JSON string containing the extracted information. Returns an empty JSON string on error.
    """
    try:
        if file_path.lower().endswith(".pdf"):
            with open(file_path, 'rb') as file:
                job_description_text = extract_text_from_pdf(file)
        elif file_path.lower().endswith(".docx"):
            job_description_text = extract_text_from_docx(file_path)
        else:
            print("Unsupported file format. Only PDF and DOCX files are supported.")
            return json.dumps({})

        if not job_description_text:
            print("Could not extract text from the file.")
            return json.dumps({})

        parsed_json = parse_job_description(job_description_text)
        return parsed_json

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return json.dumps({})
    except Exception as e:
        print(f"Error processing file: {e}")
        return json.dumps({})


# Example Usage:
file_path = "path/to/your/job_description.pdf"  # or .docx # Replaced dummy pdf file generation with file path

parsed_json_from_file = process_job_description_file(file_path)
print(parsed_json_from_file)