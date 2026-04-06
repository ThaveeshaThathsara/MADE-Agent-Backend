import os
import sys
import requests
import base64
from pathlib import Path
import google.genai as genai  
from dotenv import load_dotenv

load_dotenv()

# DEBUG: Check if .env loaded
api_key = os.getenv("GEMINI_API_KEY")
print(f"🔍 Debug: API Key loaded: {bool(api_key)}")
if api_key:
    print(f"   First 10 chars: {api_key[:10]}...")
else:
    print("   API Key is None or empty")

# Initialize Gemini client (CORRECT METHOD)
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(" GEMINI_API_KEY not found in .env file")
        print("   Please add: GEMINI_API_KEY=your_key_here")
        client = None
    else:
        client = genai.Client(api_key=api_key)  # NEW API METHOD
        print(" Google Gemini API initialized")
        print(f"   API Key starts with: {api_key[:10]}...")
except Exception as e:
    print(f" Failed to initialize Gemini: {e}")
    client = None

def execute_task_with_adk(report_id: str, task: str, task_description: str = "", image_paths: list = [],task_retention: float = None, task_confidence: str = None):
    """
    Execute task using Google Gemini with MADE cognitive state
    """
    if not client:
        yield " Gemini API not initialized. Check GEMINI_API_KEY in .env"
        yield "   Get a FREE API key from: https://aistudio.google.com/app/apikey"
        return
    
    # Step 1: Get cognitive state from MADE backend
    try:
        if task_retention is not None and task_confidence is not None:
            retention = task_retention
            confidence = task_confidence
            is_reconstructing_mild = retention <= 0.40 and retention > 0.30
            is_reconstructing_heavy = retention <= 0.30 and retention > 0.21
            is_confused = retention <= 0.21
            p_factor = 1.0
            yield f" Cognitive State Loaded [PRIORITY MODE]: Retention={retention*100:.1f}%, Confidence={confidence}"
        else:
            # USE DASHBOARD DEFAULT RETENTION
            port = os.getenv("PORT", "8000")
            state_response = requests.get(f"http://localhost:{port}/api/adk/get-npc-state/{report_id}")
            state_response.raise_for_status()
            state = state_response.json()
            
            retention = state.get("retention", 0)
            confidence = state.get("confidence_label", "Unknown")
            is_reconstructing_mild = retention <= 0.40 and retention > 0.30
            is_reconstructing_heavy = retention <= 0.30 and retention > 0.21
            is_confused = retention <= 0.21
            p_factor = state.get("p_factor", 1.0)
            
            yield f" Cognitive State Loaded [GLOBAL MODE]: Retention={retention*100:.1f}%, Confidence={confidence}"
        
    except Exception as e:
        yield f" Failed to fetch cognitive state: {str(e)}"
        return

    # Step 2: Build behavior prompt based on cognitive state
#     if is_confused:
#         behavior_instruction = """
# ⚠️ SEVERE CONFUSION MODE (Retention < 30%)
# You are SEVERELY STRUGGLING. Your memory is failing catastrophically.

# REQUIRED BEHAVIORS:
# - Stop mid-sentence frequently: "Wait, I... what was I doing?"
# - Make obvious errors in your code/work
# - Express stress and panic: "I can't remember... this is too much..."
# - Produce incomplete or broken output
# - Ask for help repeatedly
# - Second-guess every decision

# Your output should CLEARLY show cognitive impairment.
# """
#     elif should_struggle:
#         behavior_instruction = """
# ⚠️ STRUGGLE MODE (Retention 30-40%)
# You are STRUGGLING but not completely lost.

# REQUIRED BEHAVIORS:
# - Work slower, pause often to "remember"
# - Make minor mistakes and catch them
# - Express uncertainty: "Hmm, I think it's... wait, let me check..."
# - Ask clarifying questions
# - Show visible hesitation in your work

# Your output should show difficulty but eventual progress.
# """
#     else:
#         behavior_instruction = """
# ✅ CONFIDENT MODE (Retention > 40%)
# You are working efficiently with good memory.

# REQUIRED BEHAVIORS:
# - Work clearly and systematically
# - Explain your reasoning confidently
# - Produce complete, accurate output
# - Move through tasks steadily

# Your output should show competence and clarity.
# """

# Step 2: Build behavior prompt based on cognitive state
    if is_confused:
        behavior_instruction = """
⚠️ BIOLOGICAL FLOOR / SEVERE CONFUSION (Retention <= 21%)
Your memory has hit the 21% biological floor. The memory is almost entirely gone.

REQUIRED BEHAVIORS:
- Frequently stop mid-sentence: "Wait, I... what was I doing?"
- Express severe cognitive failure: "I can't remember... it's just noise..."
- Use heavy hedging: "Maybe it was... no, that's not right either."
- Produce highly fragmented, incomplete output.
- You are functionally unable to recall specific details.
"""
    elif is_reconstructing_heavy:
        behavior_instruction = """
⚠️ HEAVY RECONSTRUCTION MODE (Retention 22% - 30%)
Your memory is very weak. You must actively reconstruct fragments.

REQUIRED BEHAVIORS:
- Use heavy filler words frequently: "Umm...", "Uhh...", "Wait..."
- Second-guess yourself: "I think it was... or maybe it wasn't?"
- Show visible hesitation and struggle to piece the facts together.
- Your output should take longer and contain multiple self-corrections.
"""
    elif is_reconstructing_mild:
        behavior_instruction = """
⚠️ MILD RECONSTRUCTION MODE (Retention 31% - 40%)
Your memory has just fallen below the reliable threshold. 

REQUIRED BEHAVIORS:
- Use mild filler words: "Hmm...", "Let me think..."
- Make minor pauses before giving facts.
- Express slight uncertainty but eventually figure it out: "Hmm, let me check... ah, yes."
- Your output is mostly accurate but lacks instant confidence.
"""
    else:
        behavior_instruction = """
✅ CONFIDENT MODE (Retention > 40%)
You are working efficiently with good memory.

REQUIRED BEHAVIORS:
- Work clearly and systematically.
- Explain your reasoning confidently without filler words.
- Produce complete, accurate output.
"""

    # Step 3: Create the system prompt
    system_prompt = f"""
You are a SOFTWARE ENGINEER NPC in a hiring simulation.

📊 YOUR COGNITIVE STATS:
- Retention: {retention*100:.1f}%
- Confidence: {confidence}
- P-Factor: {p_factor:.3f}
- Cognitive Phase: {"SEVERE CONFUSION" if is_confused else "HEAVY RECONSTRUCTION" if is_reconstructing_heavy else "MILD RECONSTRUCTION" if is_reconstructing_mild else "CONFIDENT"}

{behavior_instruction}

🎯 TASK ASSIGNED:
Task Name: {task}
Task Description: {task_description if task_description else task}

IMPORTANT INSTRUCTIONS:
1. You MUST actually DO the task and produce real output (code, plans, explanations, etc.)
2. Stream your work step-by-step as you progress
3. Show your thought process (especially doubts/confusion if retention is low)
4. If writing code, provide it in full with explanations
5. MATCH YOUR BEHAVIOR TO YOUR COGNITIVE STATE (don't be overly competent if confused!)
6. DO NOT just acknowledge the task — actually execute it and produce output now.

BEGIN WORKING NOW AND PRODUCE ACTUAL OUTPUT:
"""

    # Step 4: Prepare multimodal content
    try:
        yield " Starting task execution with Gemini AI..."
        yield f" Task: {task}"
        if task_description:
            yield f" Description: {task_description}"
        if image_paths:
            yield f" Images attached: {len(image_paths)}"
        yield ""
        
        # Build multimodal content
        contents = [system_prompt]
        
        # Add images if provided
        if image_paths:
            for img_path in image_paths:
                try:
                    if os.path.exists(img_path):
                        with open(img_path, "rb") as f:
                            image_data = base64.b64encode(f.read()).decode()
                        
                        # Determine mime type
                        ext = Path(img_path).suffix.lower()
                        mime_map = {
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.png': 'image/png',
                            '.webp': 'image/webp'
                        }
                        mime_type = mime_map.get(ext, 'image/jpeg')
                        
                        contents.append({
                            "mime_type": mime_type,
                            "data": image_data
                        })
                        yield f"✅ Loaded image: {os.path.basename(img_path)}"
                except Exception as e:
                    yield f" Failed to load image {img_path}: {str(e)}"
        
        yield ""
        yield "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        yield ""
        
        # Use NEW API method for streaming with multimodal content
        response = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=contents
        )
        
        chunk_count = 0
        for chunk in response:
            if hasattr(chunk, 'text') and chunk.text:
                chunk_count += 1
                # Stream each chunk
                yield chunk.text
                
        if chunk_count == 0:
            yield " No response generated from Gemini"
            
        yield ""
        yield "Task execution completed"
        
    except Exception as e:
        yield f" Gemini API Error: {str(e)}"
        yield ""
        yield "Possible issues:"
        yield "- Check GEMINI_API_KEY in .env file"
        yield "- Verify API quota/billing at: https://aistudio.google.com/"
        yield "- Check network connection"
        yield "- Try regenerating your API key"


def test_adk_connection():
    """Test if Gemini API is properly configured"""
    if not client:
        return False, "Client not initialized - check GEMINI_API_KEY"
    
    try:
        # Simple test prompt
        model = genai.GenerativeModel('models/gemini-flash-latest')
        response = model.generate_content("Say 'API Working' if you can read this.")
        return True, response.text
    except Exception as e:
        return False, str(e)