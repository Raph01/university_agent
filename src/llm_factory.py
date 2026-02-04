from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from src.config import Config

def get_models():
    generator = ChatOpenAI(api_key=Config.OPENAI_API_KEY, model=Config.OPENAI_MODEL, temperature=0)
    validator = ChatGroq(api_key=Config.GROQ_API_KEY, model=Config.GROQ_MODEL, temperature=0)
    return generator, validator