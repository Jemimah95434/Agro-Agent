import joblib
import numpy as np
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    os.path.join(BASE, "..", "models"),
)

crop_model  = joblib.load(os.path.join(MODEL_PATH, 'crop_model.pkl'))
fert_model  = joblib.load(os.path.join(MODEL_PATH, 'fert_model.pkl'))
le_soil     = joblib.load(os.path.join(MODEL_PATH, 'le_soil.pkl'))
le_crop     = joblib.load(os.path.join(MODEL_PATH, 'le_crop.pkl'))
le_fert     = joblib.load(os.path.join(MODEL_PATH, 'le_fert.pkl'))
yield_model = joblib.load(os.path.join(MODEL_PATH, 'yield_model.pkl'))
le_area     = joblib.load(os.path.join(MODEL_PATH, 'le_area.pkl'))
le_item     = joblib.load(os.path.join(MODEL_PATH, 'le_item.pkl'))

CROP_TO_FERT = {
    "rice": "Paddy",
    "maize": "Maize",
    "cotton": "Cotton",
    "sugarcane": "Sugarcane",
    "tobacco": "Tobacco",
    "wheat": "Wheat",
    "barley": "Barley",
    "millets": "Millets",
    "oilseeds": "Oil seeds",
    "pulses": "Pulses",
    "groundnuts": "Ground Nuts",
}

CROP_TO_YIELD = {
    "rice": "Rice, paddy",
    "maize": "Maize",
    "wheat": "Wheat",
    "banana": "Plantains and others",
}

def predict_crop(data):
    features = [[
        float(data['N']), float(data['P']), float(data['K']),
        float(data['temperature']), float(data['humidity']),
        float(data['ph']), float(data['rainfall'])
    ]]
    # Get probabilities for all crops
    probs = crop_model.predict_proba(features)[0]
    classes = crop_model.classes_
    # Find top crop and its probability
    top_idx = np.argmax(probs)
    top_crop = classes[top_idx]
    confidence = float(probs[top_idx])
    # Build sorted suitability list
    suitability = sorted([
        {'crop': str(c), 'prob': float(p)} for c, p in zip(classes, probs)
    ], key=lambda x: x['prob'], reverse=True)
    return top_crop, confidence, suitability

def predict_fertilizer(data, crop_name):
    soil_type = str(data["soil_type"]).strip()
    crop_key = str(crop_name).strip().lower()

    mapped_crop = CROP_TO_FERT.get(crop_key)

    if mapped_crop is None:
        raise ValueError(
            f"Fertilizer model does not support the recommended crop "
            f"'{crop_name}'. Supported crop categories are: "
            f"{', '.join(CROP_TO_FERT.keys())}."
        )

    if soil_type not in le_soil.classes_:
        raise ValueError(f"Unsupported soil type: {soil_type}")

    if mapped_crop not in le_crop.classes_:
        raise ValueError(
            f"Fertilizer dataset does not contain crop category "
            f"'{mapped_crop}'."
        )

    soil_enc = int(le_soil.transform([soil_type])[0])
    crop_enc = int(le_crop.transform([mapped_crop])[0])

    features = [[
        float(data["temperature"]),
        float(data["humidity"]),
        float(data["moisture"]),
        soil_enc,
        crop_enc,
        float(data["N"]),
        float(data["K"]),
        float(data["P"]),
    ]]

    prediction = int(fert_model.predict(features)[0])
    return str(le_fert.inverse_transform([prediction])[0])

def predict_yield(area, item, year, rainfall, pesticides, temp):
    mapped_item = CROP_TO_YIELD.get(item.lower(), 'Maize')
    if mapped_item not in le_item.classes_:
        mapped_item = 'Maize'

    if area not in le_area.classes_:
        area = 'India'

    area_enc = le_area.transform([area])[0]
    item_enc = le_item.transform([mapped_item])[0]
    features = [[area_enc, item_enc, year, rainfall, pesticides, temp]]
    return round(float(yield_model.predict(features)[0]), 2)