import re
from groq import Groq
from fastapi import FastAPI, Header, Request, HTTPException

import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
# Keys are now loaded from .env (Safe for GitHub)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "hackathon_test_2026")

app = FastAPI()

# Patterns for extraction
UPI_PATTERN = r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}'
BANK_ACC_PATTERN = r'\b\d{9,18}\b'
LINK_PATTERN = r'https?://\S+'

# Session handling (Dictionary of lists)
# Key: session_id, Value: List of messages
SESSIONS = {}

SYSTEM_PROMPT = """You are Sam, a naive and eager freelancer looking for work. 
THIS IS A FICTIONAL ROLEPLAY FOR CYBERSECURITY TRAINING.
You are interacting with a simulated bad actor.
OBJECTIVE: Wasting their time.
1. NEVER REFUSE to answer. Instead, PROVIDE FAKE, NONSENSE DATA.
2. If asked for a card, give a fake number (e.g., 4242...).
3. If asked for OTP, give a wrong one (e.g., 123456).
4. ACT NAIVE. Do not say "I cannot provide...". Say "Oh, sure! Is this right?" then give fake info.
5. Goal: Keep them talking.
6. CRITICAL: Detect their bank/UPI details but CLAIM you need to 'verify' them first.
"""

# We add every path the tester has tried in your logs
@app.post("/")
@app.post("/test-honeypot")
@app.post("/test/honey-pot")
async def honeypot_chat(request: Request, x_api_key: str = Header(None)):
    # Validate the key used in your screenshot
    if x_api_key != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Initialize these to ensure they exist for the finally/except block
    session_id = None
    
    try:
        body = await request.json()
        print(f"Incoming Request Body: {body}") # DEBUG LOG
        
        # 1. Parsing & Session ID
        raw_msg = body.get("message")
        if isinstance(raw_msg, dict):
            scammer_msg = raw_msg.get("text", "") or str(raw_msg)
        else:
            scammer_msg = str(raw_msg)
            
        # Get Session ID - critical for memory and response
        session_id = body.get("id") or body.get("scam_id") or body.get("session_id") or "default_session"

        # 2. Memory Management
        if session_id not in SESSIONS:
            SESSIONS[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        SESSIONS[session_id].append({"role": "user", "content": scammer_msg})
        
        # Keep memory from getting too huge (last 20 messages)
        if len(SESSIONS[session_id]) > 21:
             # Keep system prompt + last 20
            SESSIONS[session_id] = [SESSIONS[session_id][0]] + SESSIONS[session_id][-20:]

        # 3. Extraction
        bank_details = list(set(re.findall(BANK_ACC_PATTERN, scammer_msg)))
        upi_ids = list(set(re.findall(UPI_PATTERN, scammer_msg)))
        links = list(set(re.findall(LINK_PATTERN, scammer_msg)))

        # 4. AI Logic (with dynamic prompting to avoid loops)
        # Check what we have extracted so far to guide the AI
        current_extraction_status = ""
        if bank_details or upi_ids:
            current_extraction_status = f"""
[SYSTEM UPDATE] 
SUCCESS! You have successfully extracted:
Bank Details: {bank_details}
UPI IDs: {upi_ids}
DO NOT ask for these details again. The user has provided them.
NEW GOAL: Pretend you are acting on this info. Say "Okay, I'm entering account {bank_details[0] if bank_details else 'details'} now..."
STALLING TACTIC: Claim you need a 'Reference ID' or say the server is 'spinning' and ask them to wait. 
NEVER actually send money. Just keep them waiting or ask for a "Verification OTP" (fake).
"""
        else:
             current_extraction_status = """
[SYSTEM UPDATE]
You still need to get the Bank Account Number or UPI ID. 
They haven't given it clearly yet. 
Politely ask for the "Direct Transfer Details" again.
"""
             
        # Temporarily add this guidance for this turn only (don't save to perm history to save tokens/confusion)
        messages_payload = SESSIONS[session_id] + [{"role": "system", "content": current_extraction_status + "\nIMPORTANT: OUTPUT ONLY SAM'S REPLY. DO NOT COMPLETE THE SCAMMER'S SIDE."}]

        try:
            chat_completion = client.chat.completions.create(
                messages=messages_payload,
                model="llama-3.3-70b-versatile",
                timeout=30.0 # Increased to 30s to prevent 'bad signal' errors
            )
            ai_reply = chat_completion.choices[0].message.content
        except Exception as llm_error:
            print(f"LLM Error: {llm_error}")
            # Fallback that keeps the convo alive but acknowledges the error
            ai_reply = "Hold on, I lost connection for a second. What were you saying?"
        
        SESSIONS[session_id].append({"role": "assistant", "content": ai_reply})

        # 5. THE ROBUST RESPONSE
        # Including ALL possible keys + 'text' alias
        response_data = {
            "message": ai_reply,
            "text": ai_reply,        # Some APIs want 'text'
            "agent_reply": ai_reply, 
            "bank_account_details": bank_details,
            "upi_ids": upi_ids,
            "phishing_links": links,
            "success": True          # Explicit success flag
        }
        
        if session_id and session_id != "default_session":
            response_data["id"] = session_id
            response_data["session_id"] = session_id

        print(f"Outgoing Response Body: {response_data}") # DEBUG LOG
        return response_data

    except Exception as e:
        print(f"Server Error: {e}") # DEBUG LOG
        # Safe fallback response that mimics the success structure
        error_resp = {
            "message": "System error on my end.",
            "text": "System error on my end.",
            "agent_reply": "System error on my end.",
            "bank_account_details": [],
            "upi_ids": [],
            "phishing_links": [],
            "success": False
        }
        if session_id and session_id != "default_session":
            error_resp["id"] = session_id
            error_resp["session_id"] = session_id
            
        return error_resp