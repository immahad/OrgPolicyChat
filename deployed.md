# Deployed Application

## Local Development

The application runs locally at:
**http://localhost:5000**

To start: `python app.py`

## Production Deployment (Render)

Once deployed to Render, the public URL will be:
**https://rag-policybot.onrender.com**


## Deployment Steps

1. Push this repository to GitHub
2. Go to [render.com](https://render.com) and create a new Web Service
3. Connect your GitHub repository
4. Configure:
   - **Build command:** `pip install -r requirements.txt && python rag/ingest.py`
   - **Start command:** `gunicorn app:app --workers 2 --timeout 120`
   - **Environment variable:** `GROQ_API_KEY` = your Groq API key
5. Click "Deploy"

The app will be live at your Render-provided URL within ~5 minutes.
