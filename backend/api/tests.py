import json
from unittest.mock import patch

import requests
from django.test import TestCase, override_settings

from .ml_engine import get_fertilizer_category, predict_yield


CROP_PAYLOAD = {
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 26.5,
    "humidity": 75,
    "ph": 6.5,
    "rainfall": 180,
}

FERTILIZER_PAYLOAD = {
    "crop": "rice",
    "N": 20,
    "P": 20,
    "K": 10,
    "temperature": 30,
    "humidity": 60,
    "moisture": 40,
    "soil_type": "Loamy",
}


@override_settings(ALLOWED_HOSTS=["testserver"])
class CropRecommendationTests(TestCase):
    @patch(
        "api.views.call_ollama",
        side_effect=requests.RequestException("disabled"),
    )
    def test_crop_endpoint_returns_only_crop_outputs(self, _):
        response = self.client.post(
            "/api/crop/",
            data=json.dumps(CROP_PAYLOAD),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertIn("crop", body)
        self.assertIn("confidence", body)
        self.assertIn("suitability", body)
        self.assertNotIn("fertilizer", body)
        self.assertNotIn("yield", body)
        self.assertIn("fertilizer_supported", body)

    def test_crop_endpoint_rejects_missing_fields(self):
        response = self.client.post(
            "/api/crop/",
            data=json.dumps({"N": 90}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertFalse(body["success"])
        self.assertIn("missing_fields", body)
        self.assertIn("P", body["missing_fields"])


@override_settings(ALLOWED_HOSTS=["testserver"])
class FertilizerRecommendationTests(TestCase):
    def test_supported_crop_returns_fertilizer_category(self):
        response = self.client.post(
            "/api/fertilizer/",
            data=json.dumps(FERTILIZER_PAYLOAD),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertTrue(body["supported"])
        self.assertIn(
            body["fertilizer"],
            {"Urea", "DAP", "14-35-14", "17-17-17", "20-20", "28-28"},
        )
        self.assertEqual(body["crop_category"], "Paddy")
        self.assertIn("guidance", body)
        self.assertIn("limitations", body)

    def test_unsupported_crop_does_not_return_fertilizer(self):
        payload = {**FERTILIZER_PAYLOAD, "crop": "banana"}

        response = self.client.post(
            "/api/fertilizer/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertFalse(body["supported"])
        self.assertIsNone(body["fertilizer"])
        self.assertIn("Paddy", body["supported_crops"])

    def test_pulse_crops_map_to_the_pulses_category(self):
        for crop in [
            "chickpea",
            "kidneybeans",
            "pigeonpeas",
            "mothbeans",
            "mungbean",
            "blackgram",
            "lentil",
        ]:
            self.assertEqual(
                get_fertilizer_category(crop),
                "Pulses",
            )


@override_settings(ALLOWED_HOSTS=["testserver"])
class HistoricalYieldTests(TestCase):
    def test_yield_trend_returns_historical_records(self):
        response = self.client.get(
            "/api/yield_trend/",
            {
                "crop": "rice",
                "area": "India",
                "years": "2010-2013",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertTrue(body["is_historical_data"])
        self.assertEqual(body["unit"], "tonnes/ha")
        self.assertEqual(len(body["records"]), 4)
        self.assertEqual(body["records"][0]["year"], 2010)

    def test_yield_trend_rejects_unknown_crop(self):
        response = self.client.get(
            "/api/yield_trend/",
            {"crop": "jute", "area": "India"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["records"], [])

    def test_yield_model_rejects_out_of_range_year(self):
        with self.assertRaises(ValueError):
            predict_yield("India", "rice", 2025, 100, 10, 25)

    def test_yield_model_rejects_unsupported_crop(self):
        with self.assertRaises(ValueError):
            predict_yield("India", "jute", 2013, 100, 10, 25)


@override_settings(ALLOWED_HOSTS=["testserver"])
class HealthCheckTests(TestCase):
    def test_health_endpoint_returns_ok(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
