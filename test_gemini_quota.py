import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_test = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-2.0-flash']

for model_name in models_to_test:
    print(f"\nTesting model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'OK'")
        print(f"✅ {model_name} Success: {response.text.strip()}")
    except Exception as e:
        print(f"❌ {model_name} Failed: {str(e)}")
