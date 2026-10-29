import os

import requests
from dotenv import load_dotenv
from google import genai

# Load environment variables from the backend .env file
load_dotenv()

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Ollama configuration
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen:latest")
OLLAMA_TIMEOUT = 60


def get_prescription(
    crop,
    fertilizer,
    yield_val,
    soil_data,
    confidence=None,
    language="en",
):
    """Generate an agricultural recommendation using Gemini or Ollama."""

    lang_instruction = ""
    if language == "ta":
        lang_instruction = (
            "\nRespond ONLY in Tamil. Use clear, simple, professional "
            "Tamil suitable for farmers."
        )

    confidence_instruction = (
        f"- Confidence: {round(confidence * 100, 2)}%"
        if confidence is not None
        else ""
    )

    prompt = f"""
You are an expert agricultural advisor called Agro-Agent.
Based on the following data, provide a detailed, professional,
and explainable recommendation for the farmer.
{lang_instruction}

Soil and Weather Data:
- Nitrogen (N): {soil_data.get('N', 'Not provided')}
- Phosphorus (P): {soil_data.get('P', 'Not provided')}
- Potassium (K): {soil_data.get('K', 'Not provided')}
- pH: {soil_data.get('ph', 'Not provided')}
- Temperature: {soil_data.get('temperature', 'Not provided')}°C
- Humidity: {soil_data.get('humidity', 'Not provided')}%
- Rainfall: {soil_data.get('rainfall', 'Not provided')} mm
- Soil Type: {soil_data.get('soil_type', 'Not provided')}
- Moisture: {soil_data.get('moisture', 'Not provided')}

ML Predictions:
- Crop: {crop}
- Fertilizer: {fertilizer}
- Expected Yield: {yield_val} hg/ha
{confidence_instruction}

Your response must:
1. Start with a sentence recommending {crop} and explain the reasons.
2. Justify the recommendation using the available input values.
3. Provide a fertilizer schedule. Do not invent an exact application
   amount without sufficient crop, soil, and fertilizer information.
4. State the predicted yield as approximately {yield_val} hg/ha.
5. Include the confidence score if provided.
6. Briefly summarize the crop growth stages.
7. Include one practical warning or tip for the farmer.
8. Use clear, non-repetitive, professional language.
9. Write at least 3-5 useful sentences that a farmer can understand.
"""

    # Try Gemini first when an API key is configured
    if client is not None:
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )

            generated_text = (response.text or "").strip()

            if (
                len(generated_text.split()) >= 25
                and "Consult your local agricultural officer"
                not in generated_text
            ):
                return generated_text

        except Exception as gemini_error:
            print(f"Gemini request failed: {gemini_error}")

    # Fall back to Ollama
    ollama_prompt = (
        prompt
        + "\nProvide a detailed, professional answer that is easy "
          "for a farmer to understand."
    )

    try:
        ollama_response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": ollama_prompt,
                "stream": False,
            },
            timeout=OLLAMA_TIMEOUT,
        )
        ollama_response.raise_for_status()

        data_ollama = ollama_response.json()
        generated_text = data_ollama.get("response", "").strip()

        if generated_text:
            return generated_text

    except Exception as ollama_error:
        print(f"Ollama request failed: {ollama_error}")

    # Final fallback if both AI services fail
    return (
        f"{crop.capitalize()} is the recommended crop based on the "
        f"model prediction. The predicted fertilizer is {fertilizer}. "
        f"The estimated yield is {yield_val} hg/ha. "
        "Verify fertilizer quantities using soil-test results and "
        "local agricultural recommendations."
    )


def get_chat_reply(message):
    """Generate an agricultural chat response using Gemini."""

    prompt = f"""
You are Agro-Agent, an AI agricultural assistant for Indian farmers
and students.

Answer the user's question clearly and helpfully in 3-5 sentences.
- Give relevant, practical advice about crops, soil, weather, pests,
  fertilizers, and yield.
- For crop recommendations, explain the reasoning where possible.
- For farming practices, provide clear step-by-step guidance.
- For market prices, government schemes, or weather, explain that
  current information should be verified through official sources.
- Do not invent facts, prices, schemes, or weather conditions.
- If you are unsure, say so politely and suggest consulting a
  local agricultural officer.

Question: {message}
"""

    if client is not None:
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )

            generated_text = (response.text or "").strip()

            if generated_text:
                return generated_text

        except Exception as gemini_error:
            print(f"Gemini chat request failed: {gemini_error}")

    # Use Ollama if Gemini is unavailable
    try:
        ollama_response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=OLLAMA_TIMEOUT,
        )
        ollama_response.raise_for_status()

        generated_text = (
            ollama_response.json().get("response", "").strip()
        )

        if generated_text:
            return generated_text

    except Exception as ollama_error:
        print(f"Ollama chat request failed: {ollama_error}")

    return (
        "I am unable to answer right now. Please try again later "
        "or consult your local agricultural officer."
    )