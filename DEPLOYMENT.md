# Deployment Guide 🚀

## 1. Safety First: GitHub Upload
I have already secured your code.
- Your keys are in `.env` (which is **ignored** by Git).
- Your code uses `os.environ` to read them safely.

### Steps to Upload:
1.  **Create a Repository** on GitHub.
2.  Open your terminal in `a:\honeypot`.
3.  Run these commands:
    ```bash
    git init
    git add .
    git commit -m "Initial honeypot commit"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    git push -u origin main
    ```
    *(Replace the URL with your actual repo link)*

## 2. Deploying to the Internet (Render)
To get a permanent link for the hackathon (instead of Ngrok):

1.  **Sign up** for [Render.com](https://render.com) (Log in with GitHub).
2.  Click **New +** -> **Web Service**.
3.  Select your **Honeypot Repository**.
4.  **Configure**:
    - **Name**: `my-honeypot` (or verified-scam-bait)
    - **Runtime**: `Python 3`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
5.  **Environment Variables** (Crucial!):
    - Scroll down to "Environment Variables".
    - Add Key: `GROQ_API_KEY`, Value: `(Your Key)`
    - Add Key: `SECRET_TOKEN`, Value: `hackathon_test_2026`
6.  Click **Create Web Service**.

Wait 2 minutes. Render will give you a link like `https://my-honeypot.onrender.com`.
**Use that link** in the Mock Scammer API dashboard!
