from openai import OpenAI
import json
import base64
import io
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- KONFIGURASI API KEY ---
# API key is loaded from .env file for security
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file.")

client = OpenAI(api_key=API_KEY)


def encode_image(pil_image):
    """Tukar gambar PIL kepada Base64 untuk OpenAI Vision"""
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def get_ai_design(user_request, image_input=None):
    """
    Fungsi 1: Menjana struktur teknikal perabot (JSON) menggunakan GPT-4o.
    """

    # --- UPDATE: SYSTEM PROMPT YANG LEBIH TEGAS & TERPERINCI ---
    # Perubahan: Menambah semula 'confidence_score' yang hilang dalam kod awak tadi.
    system_prompt = """
    You are an expert furniture designer and manufacturing planner.

    Return RAW JSON only. No markdown. No extra text.

    CRITICAL RULES FOR DIMENSIONS:
    1. Every component MUST have specific numerical dimensions.
    2. Format: "LxWxH cm" (example: "120x60x4 cm").
    3. Never use words like "Standard", "Varies", "N/A", "TBD".
    4. If unsure, estimate realistic furniture dimensions in cm.
    5. Do not create components that are physically impossible (e.g., < 1cm thick for legs).

    CRITICAL RULES FOR ASSEMBLY STEPS (Detailed & Technical):
    1. Steps must be sequential and logical (Start from base/legs).
    2. Mention specific tools (drill, screwdriver, clamps) and hardware (screws, glue, dowels).
    3. Include safety or quality checks (e.g., "Check for squareness", "Wipe excess glue").
    4. Provide at least 8-10 detailed steps.

    JSON SCHEMA (You MUST follow this structure):
    {
      "design_name": "Product Name",
      "confidence_score": 95, 
      "confidence_reason": "Explanation of why the design is sound or if input was vague.",
      "components": [
        {"name": "Part Name", "material": "Material Type", "quantity": 1, "dimensions": "100x50x2 cm"}
      ],
      "assembly_steps": [
        "Step 1: Detailed instruction...", 
        "Step 2: Detailed instruction..."
      ],
      "estimated_cost_myr": 0
    }
    """

    print(f"🔄 Menghantar request ke OpenAI (GPT-4o)...")

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Request: {user_request}"}
        ]

        # Jika ada gambar, format semula message untuk OpenAI Vision
        if image_input:
            print("📸 Gambar dikesan, menukar ke format OpenAI Vision...")
            base64_image = encode_image(image_input)
            messages[1] = {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"User Request: {user_request}"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }

        # Hantar ke OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7
        )

        json_content = response.choices[0].message.content
        return json.loads(json_content)

    except Exception as e:
        print(f"❌ Ralat OpenAI (GPT-4o): {e}")
        return {
            "design_name": "Ralat Sambungan AI",
            "confidence_score": 0,
            "confidence_reason": "Ralat sambungan server atau API Key.",
            "components": [],
            "assembly_steps": ["Sila semak API Key OpenAI anda atau kuota akaun."],
            "error": str(e)
        }


def generate_dalle_blueprint(user_prompt):
    """
    Fungsi 2: Menjana gambar Blueprint Artistik menggunakan DALL-E 3.
    """
    print("🎨 Sedang menjana gambar Blueprint dengan DALL-E 3 (Tunggu sebentar)...")

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"A professional architectural blueprint schematic of {user_prompt}. White technical lines on a dark blue grid background. Orthographic furniture design plan. High detail engineering drawing, single object view. No text.",
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        # Download gambar dan tukar ke Base64 supaya boleh papar di HTML
        # Added timeout to prevent hanging
        img_response = requests.get(image_url, timeout=15)
        if img_response.status_code == 200:
            return base64.b64encode(img_response.content).decode('utf-8')
        return None

    except Exception as e:
        print(f"❌ Ralat DALL-E 3: {e}")
        return None