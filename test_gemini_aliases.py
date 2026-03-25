import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Testing the aliases found in list_models.py
models_to_test = ['gemini-flash-latest', 'gemini-pro-latest', 'gemini-1.5-pro']

for model_name in models_to_test:
    print(f"\nTesting model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'OK'")
        print(f"✅ {model_name} Success: {response.text.strip()}")
    except Exception as e:
        print(f"❌ {model_name} Failed: {str(e)}")
