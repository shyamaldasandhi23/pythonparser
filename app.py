import streamlit as st
import pandas as pd
import os
import getpass
import json
import pandas as pd
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from llama_cloud_services import LlamaParse
import nest_asyncio
nest_asyncio.apply()

st.title("RESUME PARSER APP")  # Sets the app title
#st.header("This is a header")  # Displays a header
#st.subheader("This is a subheader")  # Displays a subheader
loadfile=st.file_uploader("Upload your resume", type=['pdf','docx','doc'])
Save_button = st.button("Save Resume")
if Save_button:
    if loadfile is not None:
        with open(os.path.join("./streamlit_app","Resume_client.pdf"), 'wb') as f:
            f.write(loadfile.getbuffer())
        st.success("Resume saved successfully")

class Person(BaseModel):
    """Information about a person."""

    # ^ Doc-string for the entity Person.
    # This doc-string is sent to the LLM as the description of the schema Person,# and it can help to improve extraction results.

    # Note that:
    # 1. Each field is an `optional` -- this allows the model to decline to extract it!
    # 2. Each field has a `description` -- this description is used by the LLM.
    name: Optional[str] = Field(default=None, description="The name of the person")
    contact: Optional[str] = Field(default=None, description="The mobile number of the person")
    email: Optional[str] = Field(default=None, description="The Email of the person")
    dob: Optional[str] = Field(default=None, description="The date of birth of the person")
    address: Optional[str] = Field(default=None, description="The address of the person")
    job_role: Optional[str] = Field(default=None, description="The designation of the person in company")
    skills: List[str] = Field(default=None, description="The skills of the person.list of skills, programming languages, IT tools, software skills")
    years_of_experience: Optional[str] = Field(default=None, description="The years of experience of the person")
    company: Optional[str] = Field(default=None, description="The company of the person")
    education: Optional[str] = Field(default=None, description="The education of the person.university or high-school education qualification or degree")
    education_institute: Optional[str] = Field(default=None, description="The institute of the education")
    education_year: Optional[str] = Field(default=None, description="The year of education")
    education_degree: Optional[str] = Field(default=None, description="The degree of education")
    course_startdate: Optional[str] = Field(default=None, description="The start date of the course")
    course_enddate: Optional[str] = Field(default=None, description="The end date of the course")
    certification: Optional[str] = Field(default=None, description="The certification of the person")
    number_of_certifications: Optional[str] = Field(default=None, description="The number of certifications of the person")
    #awards: List[str] = Field(default=None, description="The awards or achivements of the person")
    awards: Optional[str] = Field(default=None, description="The awards or achivements of the person")
    refernces: Optional[str] = Field(default=None, description="The refernces of the perso")
    mislenious: Optional[str] = Field(default=None, description="The mislenious information of the person")
    summary: Optional[str] = Field(default=None, description="summary of resme or cv docment in 100 words maximum")

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text extracted from resume. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value.",
        ),
        # Please see the how-to about improving performance with
        # reference examples.
        # MessagesPlaceholder('examples'),
        ("human", "{text}"),
    ]
)

Groq_apikey = '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'

if not os.environ.get("GROQ_API_KEY"):
  #os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")
  os.environ["GROQ_API_KEY"] = Groq_apikey

from langchain.chat_models import init_chat_model

llm = init_chat_model("llama-3.3-70b-specdec", model_provider="groq") #llama-3.3-70b-specdec #llama-3.3-70b-versatile
structured_llm = llm.with_structured_output(schema=Person)

# Set the directory containing the resumes
resume_directory = "streamlit_app"

# Initialize the LlamaParse object
llama_parser = LlamaParse(api_key="llx-GZjnxDnYiKnmMfh1Smw6vo3YeHIuI8GNtT6lAvopIWLBvLoT",result_type="text",num_workers=4)

new_df = pd.DataFrame()
df = pd.DataFrame()

# Iterate through each file in the resume directory
for filename in os.listdir(resume_directory):
    if filename.endswith(".pdf"):
        file_path = os.path.join(resume_directory, filename)
        documents = llama_parser.load_data(file_path)
        all_text = ""
        for doc in documents:
            all_text += doc.text
            #print(all_text)
        prompt = prompt_template.invoke({"text": all_text})
        result = structured_llm.invoke(prompt)
        #print(result)
        result_dict = result.dict()
        result_json = json.dumps(result_dict, indent=4)
        #print(result_json)
        result_dict = json.loads(result_json)
        df = pd.DataFrame([result_dict])
    new_df = pd.concat([new_df, df], ignore_index=True)
    st.write(new_df)