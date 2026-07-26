# Agro-Agent

An AI-powered agricultural advisory system that provides crop recommendations, fertilizer suggestions, yield predictions, and an intelligent chatbot for farmers.

## Summary

Agro-Agent combines **machine learning** and **generative AI** to help farmers make data-driven decisions. The system analyzes soil composition, weather conditions, and environmental factors to recommend the most suitable crop, the right fertilizer, and expected yield. It also features an AI chatbot that answers farming queries in both **English** and **Tamil**.

### Key Features

- **Crop Recommendation** — Predicts the best crop based on N, P, K, pH, temperature, humidity, and rainfall using a trained ML classifier.
- **Fertilizer Prediction** — Suggests the appropriate fertilizer based on soil type, crop, and nutrient levels.
- **Yield Estimation** — Forecasts expected yield (hg/ha) using historical data, area, rainfall, and pesticide usage.
- **AI Prescription** — Generates detailed, explainable farming prescriptions using Google Gemini (with Ollama fallback).
- **AI Chatbot** — Allows farmers to ask farming questions and get instant answers powered by Ollama (Qwen model).
- **Bilingual Support** — Full English and Tamil language support with real-time translation.
- **Voice Output** — Text-to-speech for prescription text in the browser.

### Tech Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Frontend | React 19, Axios, i18next, Material UI           |
| Backend  | Django 5.2, Django REST Framework, CORS         |
| ML       | Scikit-learn, Joblib, NumPy                     |
| GenAI    | Google Gemini 2.0 Flash, Ollama (Qwen)          |
| Database | SQLite                                          |

---

## How to Run

### Prerequisites

- Python 3.10+
- Node.js 16+ and npm
- Ollama installed and running locally (for chatbot and fallback features)

### 1. Backend Setup

```bash
cd backend

# Activate the virtual environment (already included)
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install any missing dependencies (if needed)
pip install django djangorestframework django-cors-headers python-dotenv google-genai joblib numpy scikit-learn requests

# Run database migrations
python manage.py migrate

# Start the Django server
python manage.py runserver
```

The backend will start at **http://localhost:8000**.

### 2. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the React dev server
npm start
```

The frontend will start at **http://localhost:3000** and connect to the backend automatically.

### 3. Ollama Setup (for Chatbot & Fallback)

Make sure Ollama is installed and running, then pull the required model:

```bash
ollama pull qwen
```

Ollama must be accessible at **http://localhost:11434**.

### 4. Environment Variables

Copy the example env file and add your keys:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and add your keys:

```
GEMINI_API_KEY=your_gemini_api_key_here
DJANGO_SECRET_KEY=your_django_secret_key_here
```

- **GEMINI_API_KEY** — Get from [Google AI Studio](https://aistudio.google.com/)
- **DJANGO_SECRET_KEY** — Generate a random secret key for production

> **Note:** The `.env` file is gitignored and will NOT be pushed to GitHub. Never commit API keys or secrets.

---

## API Endpoints

| Method | Endpoint              | Description                              |
|--------|-----------------------|------------------------------------------|
| POST   | `/api/recommend/`     | Get crop, fertilizer, yield, and prescription |
| POST   | `/api/chat/`          | Chat with the AI assistant               |
| GET    | `/api/yield_trend/`   | Get yield trend data for a crop          |

---

## Project Structure

```
agro-agent/
├── backend/
│   ├── agro_backend/       # Django project settings
│   ├── api/
│   │   ├── views.py        # API view logic
│   │   ├── ml_engine.py    # ML prediction functions
│   │   ├── genai_agent.py  # Gemini AI integration
│   │   └── urls.py         # API routing
│   ├── manage.py
│   ├── .env                # API keys (gitignored)
│   └── .env.example        # Template for .env
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React application
│   │   ├── i18n.js         # Internationalization config
│   │   └── locales/        # Translation files (en, ta)
│   └── package.json
├── models/                 # Trained ML model files (.pkl)
├── datasets/               # Training datasets (CSV)
└── ml_notebooks/           # Jupyter notebooks for model training
```
