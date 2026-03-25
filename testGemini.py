import os
from dotenv import load_dotenv
import google.genai as genai

# Load .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Initialize client
client = genai.Client(api_key=api_key)

# List available models
for m in client.models.list():
    print(m.name)

# Use a valid model (check the list above for exact names)
response = client.models.generate_content(
    model="models/gemini-flash-latest",   # or gemini-2.0-pro depending on availability
    contents="Say 'Working!' if you can read this"
)

print(response.text)