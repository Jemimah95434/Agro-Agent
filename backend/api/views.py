
import json
import math
import os
import re
from pathlib import Path

import pandas as pd
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .ml_engine import (
    crop_label,
    get_fertilizer_category,
    predict_crop,
    predict_fertilizer,
    predict_yield,
    supported_fertilizer_categories,
    supported_fertilizer_crops,
)


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate",
)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen:latest")
OLLAMA_TIMEOUT = 120

PROJECT_ROOT = Path(__file__).resolve().parents[2]
YIELD_DATASET_PATH = PROJECT_ROOT / "datasets" / "yield_df.csv"

if not YIELD_DATASET_PATH.is_file():
    docker_dataset_path = (
        Path(__file__).resolve().parent.parent
        / "datasets"
        / "yield_df.csv"
    )
    if docker_dataset_path.is_file():
        YIELD_DATASET_PATH = docker_dataset_path


CROP_FIELDS = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
]

CROP_RANGES = {
    "N": (0.0, 500.0),
    "P": (0.0, 500.0),
    "K": (0.0, 500.0),
    "temperature": (-10.0, 60.0),
    "humidity": (0.0, 100.0),
    "ph": (0.0, 14.0),
    "rainfall": (0.0, 10000.0),
}

CROP_TRAINING_RANGES = {
    "N": (0.0, 140.0),
    "P": (5.0, 145.0),
    "K": (5.0, 205.0),
    "temperature": (8.8, 43.7),
    "humidity": (14.3, 100.0),
    "ph": (3.5, 9.9),
    "rainfall": (20.2, 298.6),
}

FERTILIZER_NUMERIC_FIELDS = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "moisture",
]

FERTILIZER_RANGES = {
    "N": (0.0, 500.0),
    "P": (0.0, 500.0),
    "K": (0.0, 500.0),
    "temperature": (-10.0, 60.0),
    "humidity": (0.0, 100.0),
    "moisture": (0.0, 100.0),
}

FERTILIZER_TRAINING_RANGES = {
    "N": (5.0, 42.0),
    "P": (0.0, 42.0),
    "K": (0.0, 15.0),
    "temperature": (25.0, 38.0),
    "humidity": (50.0, 72.0),
    "moisture": (25.0, 65.0),
}

FERTILIZER_LIMITATIONS = (
    "The bundled fertilizer dataset contains only 92 unique records after "
    "removing duplicates. Its fertilizer labels are almost entirely explained "
    "by the supplied N, P and K values, so the model identifies a matching "
    "fertilizer grade rather than validating an agronomic prescription."
)

FERTILIZER_GUIDANCE = (
    "This result is a fertilizer category only. The bundled data does not "
    "contain crop-specific dosage or application-timing information, so no "
    "quantity or schedule is shown. Confirm nutrient requirements with a soil "
    "test and a local agricultural officer, and follow the product label."
)


def call_ollama(prompt, timeout=OLLAMA_TIMEOUT, json_format=False):
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


def get_crop_advice(crop, data, confidence):
    prompt = f"""
You are AgroAgent, an agricultural advisory assistant.

A trained crop classifier recommends {crop_label(crop)} with
{confidence:.2%} confidence based on these field measurements:
Nitrogen: {data.get('N')}
Phosphorus: {data.get('P')}
Potassium: {data.get('K')}
Temperature: {data.get('temperature')} Celsius
Humidity: {data.get('humidity')} percent
Soil pH: {data.get('ph')}
Rainfall: {data.get('rainfall')} mm

Explain in simple, professional language why this crop may suit the
conditions. Do not recommend a fertilizer quantity or application schedule.
Do not predict or guarantee a yield. Do not claim scientific validation.
Advise the farmer to confirm the choice with a local agricultural officer
and, where possible, a soil test. Use three to five short sentences.
"""
    return call_ollama(prompt)


def crop_tamil(name):
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
    text = response_text.strip()
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
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

        if (
            1900 <= year <= 2100
            and pd.notna(yield_value)
            and yield_value > 0
        ):
            cleaned.append({
                "year": year,
                "yield": yield_value,
            })

    by_year = {
        item["year"]: item
        for item in cleaned
    }

    cleaned = [
        by_year[year]
        for year in sorted(by_year)
    ]

    if not cleaned:
        raise ValueError("No valid year and yield records were returned.")

    return cleaned


def friendly_error(message, suggestions=None, status=400, **extra):
    result = {
        "success": False,
        "message": message,
    }

    if suggestions:
        result["suggestions"] = suggestions

    result.update(extra)

    return Response(result, status=status)


def missing_fields(data, fields):
    return [
        field
        for field in fields
        if field not in data or data[field] is None or data[field] == ""
    ]


def parse_number(data, field, minimum, maximum):
    try:
        value = float(data[field])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"{field} must be a valid number.")

    if not math.isfinite(value):
        raise ValueError(f"{field} must be a finite number.")

    if value < minimum or value > maximum:
        raise ValueError(
            f"{field} must be between {minimum} and {maximum}."
        )

    return value


def collect_numbers(data, fields, ranges):
    return {
        field: parse_number(
            data,
            field,
            ranges[field][0],
            ranges[field][1],
        )
        for field in fields
    }


def outside_training_ranges(values, training_ranges):
    warnings = []

    for field, (minimum, maximum) in training_ranges.items():
        if field not in values:
            continue

        if values[field] < minimum or values[field] > maximum:
            warnings.append(
                f"{field} is outside the training range "
                f"({minimum} to {maximum}); the prediction may be less reliable."
            )

    return warnings


def language_of(data):
    return str(data.get("language", "en")).strip().lower()


@api_view(["POST"])
def crop_recommendation(request):
    data = request.data
    missing = missing_fields(data, CROP_FIELDS)

    if missing:
        return friendly_error(
            "Please complete all crop recommendation fields.",
            [
                "Provide nitrogen, phosphorus, potassium, temperature, "
                "humidity, pH and rainfall."
            ],
            missing_fields=missing,
        )

    try:
        values = collect_numbers(data, CROP_FIELDS, CROP_RANGES)
        crop, confidence, suitability = predict_crop(values)
        warnings = outside_training_ranges(values, CROP_TRAINING_RANGES)

        explanation = (
            f"{crop_label(crop)} is the model's top crop recommendation "
            f"for the supplied soil and weather values. "
            f"Temperature: {values['temperature']} C, "
            f"pH: {values['ph']}, rainfall: {values['rainfall']} mm."
        )

        try:
            prescription = get_crop_advice(crop, values, confidence)
        except (requests.RequestException, ValueError):
            prescription = explanation

        fertilizer_supported = (
            get_fertilizer_category(crop) is not None
        )

        language = language_of(data)

        if language in ("ta", "tamil"):
            crop_display = crop_tamil(crop)
            suitability_display = [
                {
                    **item,
                    "crop": crop_tamil(item["crop_key"]),
                }
                for item in suitability
            ]
            explanation_display = translate_to_tamil(explanation)
            prescription_display = translate_to_tamil(prescription)
            warnings_display = [
                translate_to_tamil(warning)
                for warning in warnings
            ]
        else:
            crop_display = crop_label(crop)
            suitability_display = suitability
            explanation_display = explanation
            prescription_display = prescription
            warnings_display = warnings

        return Response({
            "success": True,
            "crop_key": crop,
            "crop": crop_display,
            "confidence": min(
                round(float(confidence) * 100, 2),
                100.0,
            ),
            "suitability": suitability_display,
            "explanation": explanation_display,
            "prescription": prescription_display,
            "warnings": warnings_display,
            "fertilizer_supported": fertilizer_supported,
            "caveat": (
                "This model was trained on a benchmark dataset and has not "
                "been validated for local field conditions."
            ),
        })

    except ValueError as exc:
        return friendly_error(
            str(exc),
            [
                "Check that all measurements are valid numbers.",
                "Use field measurements rather than guessed values.",
            ],
        )

    except Exception:
        return friendly_error(
            "We could not generate the crop recommendation right now.",
            [
                "Check the server logs and try again."
            ],
            status=500,
        )


@api_view(["POST"])
def fertilizer_recommendation(request):
    data = request.data
    crop_name = str(data.get("crop", "")).strip()

    if not crop_name:
        return friendly_error(
            "Please select the crop you want fertilizer guidance for.",
            ["Choose a crop before requesting fertilizer guidance."],
            missing_fields=["crop"],
        )

    required = ["N", "P", "K", "temperature", "humidity", "moisture", "soil_type"]
    missing = missing_fields(data, required)

    if missing:
        return friendly_error(
            "Please complete all fertilizer advisor fields.",
            [
                "Provide N, P, K, temperature, humidity, soil moisture "
                "and soil type."
            ],
            missing_fields=missing,
        )

    soil_type = str(data["soil_type"]).strip()
    crop_key = crop_name.lower()
    crop_display = crop_label(crop_key)
    language = language_of(data)
    display_name = (
        crop_tamil(crop_key)
        if language in ("ta", "tamil")
        else crop_display
    )

    try:
        values = collect_numbers(
            data,
            FERTILIZER_NUMERIC_FIELDS,
            FERTILIZER_RANGES,
        )
        values["soil_type"] = soil_type

        category = get_fertilizer_category(crop_key)

        if category is None:
            message = (
                f"Fertilizer guidance is not available for {crop_display}. "
                "The bundled fertilizer model only supports these crop "
                "categories: "
                f"{', '.join(supported_fertilizer_categories())}. "
                "No fertilizer was predicted rather than returning a "
                "misleading result."
            )

            if language in ("ta", "tamil"):
                message = translate_to_tamil(message)

            return Response({
                "success": True,
                "supported": False,
                "crop_key": crop_key,
                "crop": display_name,
                "selected_crop": display_name,
                "fertilizer": None,
                "message": message,
                "supported_crops": supported_fertilizer_categories(),
                "supported_crop_keys": supported_fertilizer_crops(),
                "guidance": FERTILIZER_GUIDANCE,
                "limitations": FERTILIZER_LIMITATIONS,
                "warnings": [],
            })

        result = predict_fertilizer(values, crop_key)
        warnings = outside_training_ranges(
            values,
            FERTILIZER_TRAINING_RANGES,
        )

        guidance = FERTILIZER_GUIDANCE
        limitations = FERTILIZER_LIMITATIONS
        warnings_display = warnings

        if language in ("ta", "tamil"):
            guidance = translate_to_tamil(guidance)
            limitations = translate_to_tamil(limitations)
            warnings_display = [
                translate_to_tamil(warning)
                for warning in warnings
            ]

        return Response({
            "success": True,
            "supported": True,
            "crop_key": crop_key,
            "crop": display_name,
            "selected_crop": display_name,
            "fertilizer": result["fertilizer"],
            "confidence": min(
                round(float(result["confidence"]) * 100, 2),
                100.0,
            ),
            "crop_category": result["crop_category"],
            "guidance": guidance,
            "limitations": limitations,
            "warnings": warnings_display,
            "data_quality": {
                "raw_records": 198,
                "raw_duplicate_records": 99,
                "raw_unique_records": 99,
                "records_after_date_label_exclusion": 184,
                "unique_records_used": 92,
                "note": (
                    "The training notebook removes duplicate rows and also "
                    "excludes a date-corrupted label before training, leaving "
                    "92 unique records."
                ),
            },
        })

    except ValueError as exc:
        return friendly_error(
            str(exc),
            [
                "Confirm that the selected crop and soil type are supported.",
                "Check that all measurements are valid numbers.",
            ],
        )

    except Exception:
        return friendly_error(
            "We could not generate fertilizer guidance right now.",
            [
                "Check the server logs and try again."
            ],
            status=500,
        )


@api_view(["POST"])
def recommend(request):
    """Legacy combined endpoint retained for existing API clients."""
    data = request.data

    required_fields = [
        "N",
        "P",
        "K",
        "temperature",
        "humidity",
        "ph",
        "rainfall",
        "soil_type",
        "moisture",
    ]

    missing = missing_fields(data, required_fields)

    if missing:
        return friendly_error(
            "Please complete all required farm details.",
            [
                "Check that all measurements are valid numbers.",
                "Check the soil type and selected crop.",
            ],
            missing_fields=missing,
        )

    try:
        values = collect_numbers(data, CROP_FIELDS, CROP_RANGES)
        values["moisture"] = parse_number(
            data,
            "moisture",
            FERTILIZER_RANGES["moisture"][0],
            FERTILIZER_RANGES["moisture"][1],
        )
        values["soil_type"] = str(data["soil_type"]).strip()

        crop, confidence, suitability = predict_crop(values)

        fertilizer = None
        fertilizer_note = ""

        try:
            fertilizer_result = predict_fertilizer(values, crop)
            fertilizer = fertilizer_result["fertilizer"]
        except (ValueError, KeyError):
            fertilizer_note = (
                "A fertilizer recommendation is not available for "
                f"the predicted crop '{crop_label(crop)}'. Consult a local "
                "agricultural officer for crop-specific guidance."
            )

        area = str(data.get("area", "India")).strip() or "India"
        year = int(data.get("year", 2013))
        pesticides = float(data.get("pesticides", 0))
        yield_value = None
        yield_note = ""

        try:
            yield_value = predict_yield(
                area,
                crop,
                year,
                values["rainfall"],
                pesticides,
                values["temperature"],
            )
        except ValueError as exc:
            yield_note = str(exc)

        prescription = (
            "The combined endpoint is retained for compatibility. "
            "Use /api/crop/ for crop recommendations and /api/fertilizer/ "
            "for crop-specific fertilizer guidance."
        )

        language = language_of(data)

        if language in ("ta", "tamil"):
            crop_display = crop_tamil(crop)
            fertilizer_display = (
                translate_to_tamil(fertilizer)
                if fertilizer
                else None
            )
            prescription_display = translate_to_tamil(prescription)
            fertilizer_note_display = (
                translate_to_tamil(fertilizer_note)
                if fertilizer_note
                else ""
            )
            explanation = translate_to_tamil(
                f"{crop_label(crop)} is the model's top crop recommendation "
                f"based on the supplied inputs."
            )
            suitability_display = [
                {
                    **item,
                    "crop": crop_tamil(item["crop_key"]),
                }
                for item in suitability
            ]
        else:
            crop_display = crop_label(crop)
            fertilizer_display = fertilizer
            prescription_display = prescription
            fertilizer_note_display = fertilizer_note
            explanation = (
                f"{crop_label(crop)} is the model's top crop recommendation "
                f"based on the supplied inputs."
            )
            suitability_display = suitability

        return Response({
            "success": True,
            "crop_key": crop,
            "crop": crop_display,
            "confidence": min(
                round(float(confidence) * 100, 2),
                100.0,
            ),
            "suitability": suitability_display,
            "fertilizer": fertilizer_display,
            "fertilizer_note": fertilizer_note_display,
            "yield": yield_value,
            "yield_note": yield_note,
            "prescription": prescription_display,
            "explanation": explanation,
        })

    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        return friendly_error(
            str(exc),
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
    message = str(request.data.get("message", "")).strip()

    if not message:
        return friendly_error(
            "Please enter a question before sending it."
        )

    prompt = f"""
You are AgroAgent, a helpful agricultural assistant.
Answer the farmer's question clearly and practically.
Do not claim certainty when information is insufficient.
Do not invent fertilizer dosage or application schedules.
Question: {message}
"""

    try:
        return Response({
            "reply": call_ollama(prompt),
        })

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
            [
                "Check that datasets/yield_df.csv exists and is included "
                "in the backend deployment."
            ],
            status=503,
        )

    try:
        df = pd.read_csv(YIELD_DATASET_PATH)
        df.columns = df.columns.str.strip()

        required_columns = [
            "Area",
            "Item",
            "Year",
            "hg/ha_yield",
        ]

        missing_columns = [
            column
            for column in required_columns
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
            "banana": "Plantains and others",
        }

        dataset_crop = crop_mapping.get(crop.lower())

        if dataset_crop is None:
            return Response({
                "success": False,
                "message": (
                    f"Historical yield data is not available for '{crop}'."
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
            (
                df["Item"].astype(str).str.strip().str.lower()
                == dataset_crop.lower()
            )
            &
            (
                df["Area"].astype(str).str.strip().str.lower()
                == area.lower()
            )
        ].copy()

        if years:
            match = re.fullmatch(
                r"\s*(\d{4})(?:\s*-\s*(\d{4}))?\s*",
                years,
            )

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
                filtered["Year"],
                errors="coerce",
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
            filtered["Year"],
            errors="coerce",
        )

        filtered["hg/ha_yield"] = pd.to_numeric(
            filtered["hg/ha_yield"],
            errors="coerce",
        )

        filtered = filtered.dropna(
            subset=["Year", "hg/ha_yield"]
        )

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
