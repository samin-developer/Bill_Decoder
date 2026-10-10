import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def get_model():
    api_key = os.getenv("API_KEY")
    if not api_key or api_key == "your-api-key-here":
        raise ValueError("Please set a valid API_KEY in your .env file.")
    genai.configure(api_key=api_key)
    model_name = os.getenv("MODEL_NAME", "gemini-3.5-flash-lite")
    return genai.GenerativeModel(model_name)
