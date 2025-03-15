from dotenv import load_dotenv
from langchain_groq import ChatGroq

from langchain_core.prompts import PromptTemplate


import os
load_dotenv()
llm=ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"),model_name="llama3-8b-8192")

