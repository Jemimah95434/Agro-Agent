import joblib
import numpy as np
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    os.path.join(BASE, "..", "models"),
)

crop_model = joblib.load(os.path.join(MODEL_PATH, "crop_model.pkl"))
fert_model = joblib.load(os.path.join(MODEL_PATH, "fert_model.pkl"))
le_soil = joblib.load(os.path.join(MODEL_PATH, "le_soil.pkl"))
le_crop = joblib.load(os.path.join(MODEL_PATH, "le_crop.pkl"))
le_fert = joblib.load(os.path.join(MODEL_PATH, "le_fert.pkl"))
le_area = joblib.load(os.path.join(MODEL_PATH, "le_area.pkl"))
le_item = joblib.load(os.path.join(MODEL_PATH, "le_item.pkl"))

_yield_model = None


def get_yield_model():
    global _yield_model
    if _yield_model is None:
        _yield_model = joblib.load(
            os.path.join(MODEL_PATH, "yield_model.pkl"),
            mmap_mode="r",
        )
    return _yield_model


CROP_TO_YIELD = {
    "rice": "Rice, paddy",
    "maize": "Maize",
    "wheat": "Wheat",
    "banana": "Plantains and others",
}

FERTILIZER_CROP_MAP = {
    "rice": "Paddy",
    "paddy": "Paddy",
    "maize": "Maize",
    "cotton": "Cotton",
    "wheat": "Wheat",
    "barley": "Barley",
    "millets": "Millets",
    "oilseeds": "Oil seeds",
    "oil seeds": "Oil seeds",
    "groundnuts": "Ground Nuts",
    "ground nuts": "Ground Nuts",
    "sugarcane": "Sugarcane",
    "tobacco": "Tobacco",
    "pulses": "Pulses",
    "chickpea": "Pulses",
    "kidneybeans": "Pulses",
    "pigeonpeas": "Pulses",
    "mothbeans": "Pulses",
    "mungbean": "Pulses",
    "blackgram": "Pulses",
    "lentil": "Pulses",
}

CROP_LABELS = {
    "apple": "Apple",
    "banana": "Banana",
    "blackgram": "Blackgram",
    "chickpea": "Chickpea",
    "coconut": "Coconut",
    "coffee": "Coffee",
    "cotton": "Cotton",
    "grapes": "Grapes",
    "jute": "Jute",
    "kidneybeans": "Kidney beans",
    "lentil": "Lentil",
    "maize": "Maize",
    "mango": "Mango",
    "mothbeans": "Moth beans",
    "mungbean": "Mung bean",
    "muskmelon": "Muskmelon",
    "orange": "Orange",
    "papaya": "Papaya",
    "pigeonpeas": "Pigeon peas",
    "pomegranate": "Pomegranate",
    "rice": "Rice",
    "watermelon": "Watermelon",
    "wheat": "Wheat",
    "barley": "Barley",
    "millets": "Millets",
    "oilseeds": "Oilseeds",
    "groundnuts": "Groundnuts",
    "sugarcane": "Sugarcane",
    "tobacco": "Tobacco",
    "pulses": "Pulses",
    "soybeans": "Soybeans",
}


def crop_label(crop_name):
    key = str(crop_name).strip().lower()
    return CROP_LABELS.get(key, str(crop_name).strip().title())


def get_fertilizer_category(crop_name):
    key = str(crop_name).strip().lower().replace("_", " ")
    return FERTILIZER_CROP_MAP.get(key)


def supported_fertilizer_crops():
    return sorted(FERTILIZER_CROP_MAP.keys())


def supported_fertilizer_categories():
    return sorted(set(FERTILIZER_CROP_MAP.values()))


def predict_crop(data):
    feature_names = list(crop_model.feature_names_in_)
    features = pd.DataFrame(
        [[
            float(data["N"]),
            float(data["P"]),
            float(data["K"]),
            float(data["temperature"]),
            float(data["humidity"]),
            float(data["ph"]),
            float(data["rainfall"]),
        ]],
        columns=feature_names,
    )
    probabilities = crop_model.predict_proba(features)[0]
    classes = crop_model.classes_
    top_idx = int(np.argmax(probabilities))
    top_crop = str(classes[top_idx])
    confidence = float(probabilities[top_idx])
    suitability = sorted(
        [
            {
                "crop_key": str(crop),
                "crop": crop_label(crop),
                "prob": float(prob),
            }
            for crop, prob in zip(classes, probabilities)
        ],
        key=lambda item: item["prob"],
        reverse=True,
    )
    return top_crop, confidence, suitability


def predict_fertilizer(data, crop_name):
    requested_soil = str(data["soil_type"]).strip()
    soil_lookup = {
        str(value).strip().lower(): value
        for value in le_soil.classes_
    }
    soil_type = soil_lookup.get(requested_soil.lower())
    mapped_crop = get_fertilizer_category(crop_name)

    if mapped_crop is None:
        raise ValueError(
            f"Fertilizer guidance is not available for '{crop_label(crop_name)}'."
        )

    if soil_type is None:
        raise ValueError(f"Unsupported soil type: {requested_soil}")

    if mapped_crop not in le_crop.classes_:
        raise ValueError(
            f"The fertilizer dataset has no crop category '{mapped_crop}'."
        )

    soil_encoded = int(le_soil.transform([soil_type])[0])
    crop_encoded = int(le_crop.transform([mapped_crop])[0])

    features = pd.DataFrame(
        [[
            float(data["temperature"]),
            float(data["humidity"]),
            float(data["moisture"]),
            soil_encoded,
            crop_encoded,
            float(data["N"]),
            float(data["K"]),
            float(data["P"]),
        ]],
        columns=list(fert_model.feature_names_in_),
    )

    probabilities = fert_model.predict_proba(features)[0]
    top_index = int(np.argmax(probabilities))
    encoded_class = int(fert_model.classes_[top_index])
    fertilizer = str(le_fert.inverse_transform([encoded_class])[0])

    return {
        "fertilizer": fertilizer,
        "confidence": float(probabilities[top_index]),
        "crop_category": mapped_crop,
    }


def predict_yield(area, item, year, rainfall, pesticides, temp):
    key = str(item).strip().lower()
    mapped_item = CROP_TO_YIELD.get(key)

    if mapped_item is None:
        raise ValueError(
            f"The yield model has no mapping for crop '{crop_label(item)}'."
        )

    if mapped_item not in le_item.classes_:
        raise ValueError(
            f"The yield dataset has no crop named '{mapped_item}'."
        )

    area_lookup = {
        str(value).strip().lower(): value
        for value in le_area.classes_
    }
    area_name = area_lookup.get(str(area).strip().lower())

    if area_name is None:
        raise ValueError(
            f"The yield dataset has no country/area named '{area}'."
        )

    if not 1990 <= int(year) <= 2013:
        raise ValueError(
            "The yield model only covers historical years from 1990 to 2013."
        )

    area_encoded = int(le_area.transform([area_name])[0])
    item_encoded = int(le_item.transform([mapped_item])[0])
    model = get_yield_model()
    features = pd.DataFrame(
        [[
            area_encoded,
            item_encoded,
            int(year),
            float(rainfall),
            float(pesticides),
            float(temp),
        ]],
        columns=list(model.feature_names_in_),
    )
    return round(float(model.predict(features)[0]), 2)
