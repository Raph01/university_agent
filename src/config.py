import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Default Models
    OPENAI_MODEL = "gpt-4o-mini"
    GROQ_MODEL = "llama-3.3-70b-versatile"

    @staticmethod
    def validate_keys():
        if Config.OPENAI_API_KEY:
            print(f"OpenAI API Key exists and begins {Config.OPENAI_API_KEY[:8]}")
        else:
            print("OpenAI API Key not set")
            
        if Config.GROQ_API_KEY:
            print(f"Groq API Key exists and begins {Config.GROQ_API_KEY[:4]}")
        else:
            print("Groq API Key not set (and this is optional)")