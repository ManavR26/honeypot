# Agentic Honey-Pot for Scam Detection 🍯

This project implements an autonomous AI honeypot "Sam" that interacts with scammers to waste their time and extract banking details.

## Prerequisites

1.  **Python 3.8+** installed.
2.  **Groq API Key**: Get one from [console.groq.com](https://console.groq.com).
3.  **Ngrok Account**: Get a free account at [ngrok.com](https://ngrok.com).

## Setup Instructions

### 1. Install Dependencies
Open your terminal and run:
```bash
pip install fastapi uvicorn groq
```

### 2. Configure API Keys
Open `main.py` and replace the placeholder API key with your own:
```python
client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")
```

### 3. Run the Server
In your terminal, navigate to the folder containing `main.py` and run:
```bash
uvicorn main:app --reload
```
You should see: `Uvicorn running on http://127.0.0.1:8000`

### 4. Expose to Internet (Ngrok)
Open a **new** terminal window and run:
```bash
ngrok http 8000
```
Copy the `Forwarding` URL (e.g., `https://random-name.ngrok-free.app`).

### 5. Connect to Honeypot
1.  Go to the Hackathon Submission/Testing Dashboard.
2.  Enter your **Ngrok URL** followed by `/` (e.g., `https://random-name.ngrok-free.app/`).
3.  Enter the secret token found in `main.py` (`hackathon_test_2026`).

## Troubleshooting
- **Invalid Body Error**: Check the terminal running `uvicorn`. It will print the request/response logs.
- **500 Error**: Ensure your Groq API key is valid.

---
*Built for the Agentic Scam Detection Buildathon*
