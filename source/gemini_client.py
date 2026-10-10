import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def get_model():
    api_key = None
    try:
        if hasattr(st, "secrets") and "API_KEY" in st.secrets:
            api_key = st.secrets["API_KEY"]
    except Exception:
        pass

    if not api_key:
        api_key = os.getenv("API_KEY")

    if not api_key or api_key == "your-api-key-here":
        raise ValueError("Please set a valid API_KEY in your Streamlit Secrets or .env file.")

    genai.configure(api_key=api_key)
    
    model_name = "gemini-3.5-flash-lite"
    try:
        if hasattr(st, "secrets") and "MODEL_NAME" in st.secrets and st.secrets["MODEL_NAME"]:
            model_name = st.secrets["MODEL_NAME"]
    except Exception:
        pass
    if not model_name:
        model_name = os.getenv("MODEL_NAME", "gemini-3.5-flash-lite")

    return genai.GenerativeModel(model_name)

