# tests/test_app.py

import unittest
from unittest.mock import patch
from datetime import datetime

from app.app import app


class AppApiTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_health(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "ok"})

    @patch("app.app.get_latest_row")
    def test_latest_no_data(self, mock_latest):
        mock_latest.return_value = None

        resp = self.client.get("/latest")

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.get_json(), {"message": "no data yet"})

    @patch("app.app.get_latest_row")
    def test_latest_with_data(self, mock_latest):
        mock_latest.return_value = {
            "id": 1,
            "cpu": 50.0,
            "mem": 30.0,
            "disk": 40.0,
            "ts": datetime(2025, 1, 1, 12, 0, 0),
        }

        resp = self.client.get("/latest")

        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertEqual(data["id"], 1)
        self.assertEqual(data["cpu"], 50.0)
        self.assertEqual(data["mem"], 30.0)
        self.assertEqual(data["disk"], 40.0)
        self.assertIn("timestamp", data)

