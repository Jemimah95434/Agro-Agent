from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_prescription(crop, fertilizer, yield_val, soil_data, confidence=None, language='en'):
    # If language is Tamil, ask Gemini to reply in Tamil
    lang_instruction = ''
    if language == 'ta':
        lang_instruction = '\nRespond ONLY in Tamil. Use clear, simple, professional Tamil suitable for farmers.'

    prompt = f"""
You are an expert agricultural advisor called Agro-Agent.
Based on the following data, provide a detailed, professional, and explainable recommendation for the farmer.{lang_instruction}

Soil & Weather Data:
- Nitrogen (N): {soil_data['N']}
- Phosphorus (P): {soil_data['P']}
- Potassium (K): {soil_data['K']}
- pH: {soil_data['ph']}
- Temperature: {soil_data['temperature']}°C
- Humidity: {soil_data['humidity']}%
- Rainfall: {soil_data['rainfall']} mm
- Soil Type: {soil_data.get('soil_type', '')}
- Moisture: {soil_data.get('moisture', '')}

ML Predictions:
- Crop: {crop}
- Fertilizer: {fertilizer}
- Expected Yield: {yield_val} hg/ha
{f'- Confidence: {round(confidence*100,2)}%' if confidence is not None else ''}

Your response must:
1. Start with: "{crop.capitalize()} is recommended due to [reasons: rainfall, humidity, soil, etc.]."
2. Clearly justify the recommendation using the input values (rainfall, soil, etc.).
3. Give a fertilizer schedule: "Apply [amount] of [fertilizer] during [stage] to enhance [benefit]."
4. State the expected yield: "Expected yield is approximately [yield] hg/ha."
5. Add a confidence score if provided: "Confidence: [confidence]%"
6. Add a brief crop growth stage summary.
7. Add one warning or tip for the farmer.
8. Use clear, non-repetitive, professional language.
9. Make the explanation at least 3-5 sentences and easy for a farmer to understand.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # Free Gemini model
            contents=prompt
        )
        text = response.text.strip()
        # If Gemini returns a short or generic answer, fallback to Qwen
        if len(text.split()) < 25 or 'Consult your local agricultural officer' in text:
            raise Exception('Gemini response too short or generic')
        return text
    except Exception as e:
        # Fallback to Ollama Qwen
        import requests
        ollama_prompt = prompt + "\nYour response must be detailed, professional, and easy for a farmer to understand."
        try:
            ollama_response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "qwen:latest", "prompt": ollama_prompt, "stream": False}, timeout=60
            )
            data_ollama = ollama_response.json()
            return data_ollama.get("response", f"{crop.capitalize()} is recommended. Apply {fertilizer}. Expected yield is {yield_val} hg/ha. Consult your local agricultural officer for detailed guidance.")
        except Exception as ollama_e:
            return f"{crop.capitalize()} is recommended. Apply {fertilizer}. Expected yield is {yield_val} hg/ha. Consult your local agricultural officer for detailed guidance."

def get_chat_reply(message):
    prompt = f"""
You are Agro-Agent, an expert AI agricultural assistant for farmers and students.
Answer the user's question in a clear, helpful, and detailed way (3-5 sentences).
Always:
- Give relevant, practical advice for Indian agriculture (crops, soil, weather, pests, fertilizer, yield, etc.).
- If the question is about crop recommendation, explain your reasoning (rainfall, soil, etc.).
- If the question is about farming practices, give step-by-step guidance.
- If the question is about market price, government schemes, or weather, answer with the latest general advice and suggest checking official sources for updates.
- If you don't know, say so politely and suggest consulting a local agricultural officer.
Question: {message}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return "I am unable to answer right now. Please try again in a moment or consult your local agricultural officer."