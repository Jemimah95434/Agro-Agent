from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ml_engine import predict_crop, predict_fertilizer, predict_yield
from .genai_agent import get_prescription, get_chat_reply
import requests

@api_view(['POST'])
def recommend(request):
    data = request.data


    # Validate required numeric fields
    required_fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    missing = [f for f in required_fields if not str(data.get(f, '')).strip()]
    if missing:
        return Response({'error': f'Missing or empty fields: {", ".join(missing)}'}, status=400)

    # Safe conversion
    def safe_float(val, default=0.0):
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    for f in required_fields:
        data[f] = safe_float(data[f])

    crop, confidence, suitability = predict_crop(data)
    fertilizer = predict_fertilizer(data, crop)
    # Add fertilizer quantity and timing (simple rule-based for demo)
    fert_quantity = f"50 kg/acre {fertilizer} (apply during early growth stage)"
    yield_val  = predict_yield(
        data.get('area', 'India'),
        crop,
        int(data.get('year', 2024)),
        float(data['rainfall']),
        float(data.get('pesticides', 100)),
        float(data['temperature'])
    )

    # Get language from request (default to 'en')
    language = data.get('language', 'en')

    # If Tamil, translate all content using Gemini
    if language == 'ta':
        # Fixed Tamil translations for crop names
        crop_tamil_dict = {
            'rice': 'அரிசி',
            'wheat': 'கோதுமை',
            'maize': 'சோளம்',
            'banana': 'வாழைப்பழம்',
            'jute': 'சணல்',
            'coffee': 'காபி',
            'pigeonpeas': 'துவரம் பருப்பு',
            'blackgram': 'உளுந்து',
            'lentil': 'மசூர் பருப்பு',
            'mothbeans': 'மொத்துப்பயறு',
            'mungbean': 'பயத்தம் பருப்பு',
            'kidneybeans': 'ராஜ்மா',
            'chickpea': 'கடலை',
            'coconut': 'தேங்காய்',
            'cotton': 'பருத்தி',
            'grapes': 'திராட்சை',
            'apple': 'ஆப்பிள்',
            'orange': 'ஆரஞ்சு',
            'papaya': 'பப்பாளி',
            'muskmelon': 'முலாம்பழம்',
            'watermelon': 'தர்பூசணி',
            'mango': 'மாம்பழம்',
            'pomegranate': 'மாதுளை',
            'sugarcane': 'கரும்பு',
            'barley': 'பார்லி',
            'groundnuts': 'வேர்க்கடலை',
            'oilseeds': 'எண்ணெய் விதைகள்',
            'millets': 'சிறுதானியங்கள்',
            'soybeans': 'சோயா',
            'plantains': 'வாழை',
        }
        def crop_tamil(name):
            return crop_tamil_dict.get(name.lower(), name)

        from .genai_agent import client
        def translate(text):
            prompt = f"Translate the following to clear, simple, professional Tamil for farmers.\n\nText: {text}\n\nTamil:"
            try:
                response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                return response.text.strip()
            except Exception:
                return text

        prescription_en = get_prescription(crop, fert_quantity, yield_val, data, confidence, language)
        # Force translation to Tamil in case Gemini returns English
        prescription = translate(prescription_en)
        explanation = translate(f"{crop.capitalize()} is recommended because temperature ({data['temperature']}°C), pH ({data['ph']}), and rainfall ({data['rainfall']} mm) are optimal.")
        crop_ta = crop_tamil(crop)
        # Also update suitability list to use Tamil for the main crop if needed
        # (already handled below, but this ensures the main card is always Tamil)
        fertilizer_ta = translate(fert_quantity)
        # Translate suitability crop names using dictionary
        suitability_ta = []
        for s in suitability:
            s_ta = dict(s)
            s_ta['crop'] = crop_tamil(s['crop'])
            suitability_ta.append(s_ta)
        # Cap confidence at 100
        capped_confidence = min(round(confidence * 100, 2), 100.0)
        return Response({
            'crop':         crop_ta,
            'confidence':   capped_confidence,
            'suitability':  suitability_ta,
            'fertilizer':   fertilizer_ta,
            'yield':        yield_val,
            'prescription': prescription,
            'explanation':  explanation
        })
    else:
        try:
            prescription = get_prescription(crop, fert_quantity, yield_val, data, confidence, language)
        except Exception:
            # Gemini failed, use Ollama as fallback
            ollama_prompt = f"You are an expert agricultural advisor. Based on the following data, provide a detailed, professional, and explainable recommendation for the farmer.\nSoil & Weather Data: N={data['N']}, P={data['P']}, K={data['K']}, pH={data['ph']}, Temp={data['temperature']}°C, Humidity={data['humidity']}%, Rainfall={data['rainfall']} mm, Soil Type={data.get('soil_type','')}, Moisture={data.get('moisture','')}.\nML Predictions: Crop={crop}, Fertilizer={fert_quantity}, Expected Yield={yield_val} hg/ha."
            try:
                ollama_response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "qwen:latest", "prompt": ollama_prompt, "stream": False}, timeout=60
                )
                data_ollama = ollama_response.json()
                prescription = data_ollama.get("response", "Sorry, I couldn't answer your question.")
            except Exception as e:
                prescription = f"Ollama error: {e}"
        explanation = (
            f"{crop.capitalize()} is recommended because "
            f"temperature ({data['temperature']}°C), pH ({data['ph']}), and rainfall ({data['rainfall']} mm) are optimal."
        )
        # Cap confidence at 100
        capped_confidence = min(round(confidence * 100, 2), 100.0)
        return Response({
            'crop':         crop,
            'confidence':   capped_confidence,
            'suitability':  suitability,
            'fertilizer':   fert_quantity,
            'yield':        yield_val,
            'prescription': prescription,
            'explanation':  explanation
        })

@api_view(['POST'])
def chat(request):
    message = request.data.get('message', '')
    # Use Ollama with Qwen:latest model for chatbot
    try:
        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen:latest", "prompt": message, "stream": False}, timeout=60
        )
        data = ollama_response.json()
        reply = data.get("response", "Sorry, I couldn't answer your question.")
    except Exception as e:
        reply = f"Ollama error: {e}"
    return Response({'reply': reply})

@api_view(['GET'])
def yield_trend(request):
    crop = request.GET.get('crop', 'rice')
    area = request.GET.get('area', 'India')
    years = request.GET.get('years', '2020-2025')
    # Prompt Qwen for yield trend
    prompt = f"Provide the yield trend for {crop} in {area} from {years} as a JSON list of objects with 'year' and 'yield' (in tons). Example: [{{'year':2020,'yield':3.1}},...] Only output the JSON list."
    try:
        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen:latest", "prompt": prompt, "stream": False}, timeout=60
        )
        data_ollama = ollama_response.json()
        import json
        # Try to extract JSON from response
        import re
        match = re.search(r'(\[.*\])', data_ollama.get('response',''), re.DOTALL)
        if match:
            trend = json.loads(match.group(1).replace("'", '"'))
            return Response({'trend': trend})
        else:
            return Response({'error': 'No trend data found in response.'}, status=500)
    except Exception as e:
        return Response({'error': str(e)}, status=500)