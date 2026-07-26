import joblib
import numpy as np
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE, '..', 'models')

crop_model  = joblib.load(os.path.join(MODEL_PATH, 'crop_model.pkl'))
fert_model  = joblib.load(os.path.join(MODEL_PATH, 'fert_model.pkl'))
le_soil     = joblib.load(os.path.join(MODEL_PATH, 'le_soil.pkl'))
le_crop     = joblib.load(os.path.join(MODEL_PATH, 'le_crop.pkl'))
le_fert     = joblib.load(os.path.join(MODEL_PATH, 'le_fert.pkl'))
yield_model = joblib.load(os.path.join(MODEL_PATH, 'yield_model.pkl'))
le_area     = joblib.load(os.path.join(MODEL_PATH, 'le_area.pkl'))
le_item     = joblib.load(os.path.join(MODEL_PATH, 'le_item.pkl'))

# Map crop model names → fertilizer dataset crop names
CROP_TO_FERT = {
    'rice': 'Paddy', 'maize': 'Maize', 'cotton': 'Cotton',
    'sugarcane': 'Sugarcane', 'tobacco': 'Tobacco',
    'wheat': 'Wheat', 'barley': 'Barley',
    'millets': 'Millets', 'oilseeds': 'Oil seeds',
    'pulses': 'Pulses', 'groundnuts': 'Ground Nuts'
}

# Map crop model names → yield_df Item names
CROP_TO_YIELD = {
    'rice': 'Rice, paddy',
    'maize': 'Maize',
    'wheat': 'Wheat',
    'banana': 'Plantains and others',
    'chickpea': 'Soybeans',
    'lentil': 'Soybeans',
    'kidneybeans': 'Soybeans',
    'mungbean': 'Soybeans',
    'blackgram': 'Soybeans',
    'mothbeans': 'Soybeans',
    'pigeonpeas': 'Soybeans',
    'cotton': 'Soybeans',
    'jute': 'Soybeans',
    'coffee': 'Soybeans',
    'muskmelon': 'Sweet potatoes',
    'watermelon': 'Sweet potatoes',
    'mango': 'Yams',
    'grapes': 'Yams',
    'apple': 'Yams',
    'orange': 'Yams',
    'papaya': 'Yams',
    'coconut': 'Yams',
    'pomegranate': 'Yams',
    'sugarcane': 'Cassava',
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
    soil_enc = le_soil.transform([data['soil_type']])[0]

    mapped_crop = CROP_TO_FERT.get(crop_name.lower(), crop_name.capitalize())
    if mapped_crop not in le_crop.classes_:
        mapped_crop = le_crop.classes_[0]  # Use first available crop if not found

    crop_enc = le_crop.transform([mapped_crop])[0]
    features = [[
        float(data['temperature']), float(data['humidity']),
        float(data['moisture']), soil_enc, crop_enc,
        float(data['N']), float(data['K']), float(data['P'])
    ]]
    fert_enc = fert_model.predict(features)[0]
    return le_fert.inverse_transform([fert_enc])[0]

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