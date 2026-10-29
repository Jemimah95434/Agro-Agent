import os
import json
import re
from pathlib import Path

import pandas as pd
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .ml_engine import (
    predict_crop,
    predict_fertilizer,
    predict_yield,
)


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)
OLLAMA_MODEL = "qwen:latest"
OLLAMA_TIMEOUT = 120

PROJECT_ROOT = Path(__file__).resolve().parents[2]
YIELD_DATASET_PATH = PROJECT_ROOT / "datasets" / "yield_df.csv"


def call_ollama(prompt, timeout=OLLAMA_TIMEOUT, json_format=False):
    """Send a prompt to the local Ollama model."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    if json_format:
        payload["format"] = "json"
        payload["options"] = {"temperature": 0}

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()

    result = response.json()
    text = result.get("response", "").strip()

    if not text:
        raise ValueError("Ollama returned an empty response.")

    return text


def get_prescription(crop, fertilizer, yield_value, data, confidence):
    """Generate an agricultural recommendation with Qwen."""
    prompt = f"""
You are AgroAgent, an agricultural advisory assistant.

Provide practical guidance based on these model predictions.
Recommended crop: {crop}
Recommended fertilizer: {fertilizer}
Predicted yield: {yield_value}
Crop model confidence: {confidence:.2%}

Farm information:
Nitrogen: {data.get('N')}
Phosphorus: {data.get('P')}
Potassium: {data.get('K')}
Temperature: {data.get('temperature')} Celsius
Humidity: {data.get('humidity')} percent
Soil pH: {data.get('ph')}
Rainfall: {data.get('rainfall')} mm
Soil type: {data.get('soil_type', 'Not provided')}
Moisture: {data.get('moisture', 'Not provided')}

Explain why the crop was recommended and give sensible next steps.
Advise the farmer to verify fertilizer dosage with local agricultural
guidance. Do not invent laboratory results. Clearly state that yield
is a model prediction, not a guarantee.
Use simple, professional language.
"""
    return call_ollama(prompt)


def crop_tamil(name):
    """Translate supported crop names into Tamil."""
    crop_tamil_dict = {
        "rice": "நெல்",
        "maize": "மக்காச்சோளம்",
        "chickpea": "கொண்டைக்கடலை",
        "kidneybeans": "சிறுநீரக அவரை",
        "pigeonpeas": "துவரை",
        "mothbeans": "மொச்சை",
        "mungbean": "பாசிப்பயறு",
        "blackgram": "உளுந்து",
        "lentil": "மசூர் பருப்பு",
        "pomegranate": "மாதுளை",
        "banana": "வாழை",
        "mango": "மாம்பழம்",
        "grapes": "திராட்சை",
        "watermelon": "தர்பூசணி",
        "muskmelon": "முலாம்பழம்",
        "apple": "ஆப்பிள்",
        "orange": "ஆரஞ்சு",
        "papaya": "பப்பாளி",
        "coconut": "தேங்காய்",
        "cotton": "பருத்தி",
        "jute": "சணல்",
        "coffee": "காபி",
        "sugarcane": "கரும்பு",
        "wheat": "கோதுமை",
        "barley": "பார்லி",
        "groundnuts": "நிலக்கடலை",
        "ground nuts": "நிலக்கடலை",
        "oilseeds": "எண்ணெய் வித்துக்கள்",
        "oil seeds": "எண்ணெய் வித்துக்கள்",
        "millets": "சிறுதானியங்கள்",
        "soybeans": "சோயாபீன்ஸ்",
        "plantains": "வாழை",
        "paddy": "நெல்",
    }
    key = str(name).strip().lower()
    return crop_tamil_dict.get(key, str(name))


def translate_to_tamil(text):
    """Translate text with Qwen; preserve the original if translation fails."""
    prompt = (
        "Translate the following text into clear, simple, professional "
        "Tamil for farmers. Preserve numbers and measurements. "
        "Return only the Tamil translation.\n\n"
        f"Text: {text}"
    )

    try:
        return call_ollama(prompt, timeout=60)
    except (requests.RequestException, ValueError):
        return text


def parse_trend_response(response_text):
    """Parse and validate a JSON trend response."""
    text = response_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    parsed = json.loads(text)

    if isinstance(parsed, dict):
        trend = parsed.get("trend", [])
    elif isinstance(parsed, list):
        trend = parsed
    else:
        raise ValueError("The response must be a JSON array or object.")

    if not isinstance(trend, list):
        raise ValueError("The trend field must be a list.")

    cleaned = []

    for item in trend:
        if not isinstance(item, dict):
            continue

        try:
            year = int(item["year"])
            yield_value = float(item["yield"])
        except (KeyError, TypeError, ValueError, OverflowError):
            continue

        if 1900 <= year <= 2100 and yield_value > 0:
            cleaned.append({
                "year": year,
                "yield": yield_value,
            })

    by_year = {item["year"]: item for item in cleaned}
    cleaned = [by_year[year] for year in sorted(by_year)]

    if not cleaned:
        raise ValueError("No valid year and yield records were returned.")

    return cleaned


def friendly_error(message, suggestions=None, status=400):
    """Return a user-friendly API error response."""
    result = {
        "success": False,
        "message": message,
    }

    if suggestions:
        result["suggestions"] = suggestions

    return Response(result, status=status)


@api_view(["POST"])
def recommend(request):
    """Predict crop, fertilizer, and yield from farm inputs."""
    data = request.data

    required_fields = [
        "N", "P", "K", "temperature", "humidity",
        "ph", "rainfall", "soil_type", "moisture",
    ]

    missing = [
        field for field in required_fields
        if field not in data or data[field] in (None, "")
    ]

    if missing:
        return friendly_error(
            "Please complete all required farm details.",
            ["Fill in the missing fields and try again."],
        )

    try:
        # Validate numeric farm inputs before model prediction.
        numeric_fields = [
            "N", "P", "K", "temperature", "humidity",
            "ph", "rainfall", "moisture",
        ]

        for field in numeric_fields:
            value = float(data[field])
            if not pd.notna(value):
                raise ValueError(f"{field} must be a valid number.")

        crop, confidence, suitability = predict_crop(data)

        fertilizer = None
        fertilizer_note = ""

        try:
            fertilizer = predict_fertilizer(data, crop)
        except (ValueError, KeyError):
            # The fertilizer model supports fewer crops than the crop
            # model. Keep the crop and yield results instead of failing
            # the whole recommendation.
            fertilizer_note = (
                f"A fertilizer recommendation is not available for the "
                f"predicted crop '{crop}'. Consult a local agricultural "
                f"officer for crop-specific fertilizer guidance."
            )

        area = str(data.get("area", "India")).strip() or "India"
        year = int(data.get("year", 2025))
        pesticides = float(data.get("pesticides", 0))
        rainfall = float(data["rainfall"])
        temperature = float(data["temperature"])

        yield_value = predict_yield(
            area,
            crop,
            year,
            rainfall,
            pesticides,
            temperature,
        )

        try:
            prescription = get_prescription(
                crop,
                fertilizer or "Not available for this crop",
                yield_value,
                data,
                confidence,
            )
        except (requests.RequestException, ValueError):
            prescription = (
                "The model recommendation is available, but the AI "
                "advice could not be generated. Please try again later "
                "and verify fertilizer dosage with local agricultural "
                "guidance."
            )

        language = str(data.get("language", "en")).strip().lower()

        if language in ("ta", "tamil"):
            crop_display = crop_tamil(crop)
            fertilizer_display = (
                translate_to_tamil(fertilizer) if fertilizer else None
            )
            prescription_display = translate_to_tamil(prescription)
            fertilizer_note_display = (
                translate_to_tamil(fertilizer_note)
                if fertilizer_note
                else ""
            )

            explanation = translate_to_tamil(
                f"{crop} is the model's top crop recommendation based "
                f"on the supplied inputs. Temperature: {temperature} C, "
                f"pH: {data['ph']}, rainfall: {rainfall} mm."
            )

            suitability_display = [
                {
                    **item,
                    "crop": crop_tamil(item.get("crop", "")),
                }
                for item in suitability
            ]
        else:
            crop_display = crop
            fertilizer_display = fertilizer
            prescription_display = prescription
            fertilizer_note_display = fertilizer_note
            explanation = (
                f"{crop.capitalize()} is the model's top crop "
                f"recommendation based on the supplied inputs. "
                f"Temperature: {temperature} C, pH: {data['ph']}, "
                f"rainfall: {rainfall} mm."
            )
            suitability_display = suitability

        return Response({
            "success": True,
            "crop": crop_display,
            "confidence": min(round(float(confidence) * 100, 2), 100.0),
            "suitability": suitability_display,
            "fertilizer": fertilizer_display,
            "fertilizer_note": fertilizer_note_display,
            "yield": yield_value,
            "prescription": prescription_display,
            "explanation": explanation,
        })

    except (KeyError, TypeError, ValueError, OverflowError):
        return friendly_error(
            "Some farm details are invalid or incomplete.",
            [
                "Check that all measurements are valid numbers.",
                "Check the soil type and selected crop.",
            ],
        )
    except Exception:
        return friendly_error(
            "We could not generate your recommendation right now.",
            [
                "Check your farm details and try again.",
                "If the problem continues, check the server logs.",
            ],
            status=500,
        )


@api_view(["POST"])
def chat(request):
    """Answer agricultural questions using Qwen through Ollama."""
    message = str(request.data.get("message", "")).strip()

    if not message:
        return friendly_error("Please enter a question before sending it.")

    prompt = f"""
You are AgroAgent, a helpful agricultural assistant.
Answer the farmer's question clearly and practically.
Do not claim certainty when information is insufficient.
Question: {message}
"""

    try:
        return Response({"reply": call_ollama(prompt)})
    except requests.RequestException:
        return friendly_error(
            "The agricultural assistant is temporarily unavailable.",
            ["Check that Ollama is running and try again."],
            status=502,
        )
    except ValueError:
        return friendly_error(
            "The assistant could not generate a response.",
            ["Please try asking your question again."],
            status=502,
        )


@api_view(["GET"])
def yield_trend(request):
    """
    Return historical crop yields from yield_df.csv.
    Dataset yield is converted from hg/ha to tonnes/ha.
    """
    crop = str(request.query_params.get("crop", "rice")).strip()
    area = str(request.query_params.get("area", "India")).strip()
    years = str(request.query_params.get("years", "")).strip()

    if not crop or not area:
        return friendly_error(
            "Please provide both a crop and an area."
        )

    if not YIELD_DATASET_PATH.exists():
        return friendly_error(
            "Historical yield data is currently unavailable.",
            ["Check that datasets/yield_df.csv exists in the project folder."],
            status=503,
        )

    try:
        df = pd.read_csv(YIELD_DATASET_PATH)
        df.columns = df.columns.str.strip()

        required_columns = ["Area", "Item", "Year", "hg/ha_yield"]
        missing_columns = [
            column for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            return friendly_error(
                "The historical yield dataset has an unexpected format.",
                ["Check the dataset column names."],
                status=500,
            )

        crop_mapping = {
            "rice": "Rice, paddy",
            "rice, paddy": "Rice, paddy",
            "maize": "Maize",
            "wheat": "Wheat",
            "cassava": "Cassava",
            "potatoes": "Potatoes",
            "sorghum": "Sorghum",
            "soybeans": "Soybeans",
            "sweet potatoes": "Sweet potatoes",
            "yams": "Yams",
            "plantains and others": "Plantains and others",
        }

        dataset_crop = crop_mapping.get(crop.lower())

        if dataset_crop is None:
            return Response({
                "success": False,
                "message": (
                    f"Historical yield data is not available for "
                    f"'{crop}'."
                ),
                "suggestions": [
                    "Choose a crop available in the historical dataset."
                ],
                "available_crops": sorted(
                    df["Item"].dropna().astype(str).unique().tolist()
                ),
                "records": [],
            })

        filtered = df[
            (df["Item"].astype(str).str.strip().str.lower()
             == dataset_crop.lower())
            &
            (df["Area"].astype(str).str.strip().str.lower()
             == area.lower())
        ].copy()

        if years:
            match = re.fullmatch(r"\s*(\d{4})(?:\s*-\s*(\d{4}))?\s*", years)

            if not match:
                return friendly_error(
                    "The year range is invalid.",
                    ["Use a format such as 2010-2020 or 2013."],
                )

            start_year = int(match.group(1))
            end_year = int(match.group(2) or start_year)

            if start_year > end_year:
                return friendly_error(
                    "The start year must not be later than the end year."
                )

            filtered["Year"] = pd.to_numeric(
                filtered["Year"], errors="coerce"
            )
            filtered = filtered[
                filtered["Year"].between(start_year, end_year)
            ]

        if filtered.empty:
            return Response({
                "success": False,
                "message": (
                    f"No historical records were found for "
                    f"{dataset_crop} in {area} for the requested period."
                ),
                "suggestions": [
                    "Try a different crop, area, or year range."
                ],
                "records": [],
            })

        filtered["Year"] = pd.to_numeric(
            filtered["Year"], errors="coerce"
        )
        filtered["hg/ha_yield"] = pd.to_numeric(
            filtered["hg/ha_yield"], errors="coerce"
        )

        filtered = filtered.dropna(subset=["Year", "hg/ha_yield"])
        filtered = filtered[filtered["hg/ha_yield"] >= 0]

        grouped = (
            filtered.groupby("Year")["hg/ha_yield"]
            .mean()
            .sort_index()
        )

        records = [
            {
                "year": int(year),
                "yield": round(float(value) / 10000, 3),
            }
            for year, value in grouped.items()
        ]

        if not records:
            return Response({
                "success": False,
                "message": "No usable historical yield records were found.",
                "records": [],
            })

        return Response({
            "success": True,
            "crop": dataset_crop,
            "area": area,
            "unit": "tonnes/ha",
            "source": "Historical dataset: yield_df.csv",
            "is_historical_data": True,
            "records": records,
        })

    except (OSError, pd.errors.ParserError):
        return friendly_error(
            "The historical yield dataset could not be read.",
            ["Check that yield_df.csv is valid and accessible."],
            status=500,
        )
