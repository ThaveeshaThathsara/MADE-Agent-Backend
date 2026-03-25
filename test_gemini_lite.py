import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_test = [
    'gemini-flash-lite-latest', 
    'gemini-1.5-flash-lite', 
    'gemini-2.0-flash-lite-preview-02-05',
    'gemini-pro-latest'
]

for model_name in models_to_test:
    print(f"\nTesting model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'OK'")
        print(f"✅ {model_name} Success: {response.text.strip()}")
    except Exception as e:
        print(f"❌ {model_name} Failed: {str(e)}")
