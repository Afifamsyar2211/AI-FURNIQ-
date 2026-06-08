import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Key is loaded from .env file for security
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")

genai.configure(api_key=api_key)

print("Sedang menyemak senarai model yang tersedia untuk API Key ini...")
print("-" * 50)

try:
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Jumpa model: {m.name}")
            available_models.append(m.name)

    if not available_models:
        print("❌ Tiada model dijumpai! Mungkin API Key salah atau sekatan wilayah.")
    else:
        print("-" * 50)
        print("Sila copy nama model di atas dan berikan kepada saya.")

except Exception as e:
    print(f"❌ Error Besar: {e}")