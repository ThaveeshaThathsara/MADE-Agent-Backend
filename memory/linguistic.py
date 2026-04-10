import os
import google.genai as genai
from dotenv import load_dotenv
import random

load_dotenv()

# Configure Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f" WARNING: Failed to initialize Gemini Client: {e}")
else:
    print(" WARNING: GEMINI_API_KEY not found in environment.")

def generate_npc_response(base_memory, confidence_label, phase, retention_pct):
   
    if not api_key:
        return f"[Fallback] I remember {base_memory} with {confidence_label} confidence."

    ret_value = min(1.0, retention_pct) * 100
    
    style_guide = ""
    if retention_pct < 0.21:
        style_guide = "Use Gist-only language. Do not provide specific details. Sound vague and focus only on the general idea. Example: 'I don't have the details, but the general idea was...'"
    elif phase == "Phase 2 (Slow)" or retention_pct < 0.40:
        style_guide = "Use Reconstructive language. Sound uncertain and speculative. Use fillers like 'I think', 'maybe', 'if I recall correctly'. Example: 'If I recall correctly, I think it was...'"
    else:
        style_guide = "Use Direct Recall language. Sound clear, precise, and certain about the facts. Example: 'I clearly remember it happened at...'"

    prompt = f"""
    You are an AI NPC in a high-fidelity simulation. 
    Your current cognitive state is:
    - Memory Retention: {ret_value:.1f}%
    - Confidence Level: {confidence_label}
    - Decay Phase: {phase}
    
    Style Guide: {style_guide}
    
    Memory to recall: "{base_memory}"
    
    Response requirements:
    1. Stay in character as a futuristic NPC.
    2. Do NOT mention your retention percentage or confidence level explicitly in the spoken text.
    3. Reflect the required linguistic style perfectly based on the Style Guide.
    4. Keep the response concise (1-2 sentences).
    
    NPC Response:
    """

    model_names = [
        # 'gemini-1.5-flash', 
        # 'gemini-1.5-flash-latest', 
        # 'gemini-1.5-flash-lite-latest',
        # 'gemini-2.0-flash-lite',
        # 'gemini-2.0-flash'
        'gemini-2.5-flash-lite',
        # 'gemini-2.5-flash',
        # 'gemini-2.0-flash',
        # 'gemini-1.5-flash'
    ]
    
    if client:
        for model_name in model_names:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text.strip().replace('"', '')
            except Exception as e:
                last_error = str(e)
                if "429" in last_error:
                    
                    print(f" [Linguistic Engine] Quota Exceeded (429) for {model_name}. Attempting fallback...")
                    break
                continue

    print(f"📡 [Linguistic Engine] API Bypass Active: Simulating neural output for '{confidence_label}' state.")
    
    
    fallbacks = {
        "High Confidence": [
            f"The data for {base_memory} is perfectly synced. I can confirm all parameters are nominal.",
            f"Accessing archived record: {base_memory}. Integrity is 100%. What do you need to know?",
            f"My primary memory core has {base_memory} fully cached and ready for retrieval."
        ],
        "Medium Confidence": [
            f"Scanning neural pathways... {base_memory} is present, but I'm detecting minor trace interference.",
            f"I recall the general framework of {base_memory}, though some specific nodes are currently obscured.",
            f"Uplink unstable, but {base_memory} seems to be part of my recent task sequence."
        ],
        "Low Confidence": [
            f"The record for {base_memory} is highly fragmented. I... I can't quite see the full picture.",
            f"Neural unbinding detected. {base_memory} is fading into my deep archives. It feels distant.",
            f"Warning: Data corruption in Sector 7. {base_memory} is missing critical metadata."
        ],
        "Very Low Confidence": [
            f"I'm searching... but there's only noise where {base_memory} should be. It's almost gone.",
            f"The memory of {base_memory} has lost its anchor. I can only retrieve ghost signals.",
            f"Everything is shifting. {base_memory}? I... I don't think I have that anymore."
        ],
        "Confused": [
            f"Who... what was {base_memory}? My cognitive sync is failing.",
            f"Error: Null reference. {base_memory} is no longer part of my active consciousness.",
            f"I am in standby mode. Memory for {base_memory} is indistinguishable from noise."
        ]
    }
    
    options = fallbacks.get(confidence_label, fallbacks["Confused"])
    return random.choice(options)

if __name__ == "__main__":
    # Test cases
    test_memory = "The security breach in Sector 7 occurred at 04:00 hours."
    
    print("\n--- TEST: HIGH CONFIDENCE / PHASE 1 ---")
    print(generate_npc_response(test_memory, "High Confidence", "Phase 1 (Fast)", 0.85))
    
    print("\n--- TEST: LOW CONFIDENCE / PHASE 2 ---")
    print(generate_npc_response(test_memory, "Low Confidence", "Phase 2 (Slow)", 0.38))
    
    print("\n--- TEST: CONFUSED / GIST ONLY ---")
    print(generate_npc_response(test_memory, "Confused", "Phase 2 (Slow)", 0.21))
