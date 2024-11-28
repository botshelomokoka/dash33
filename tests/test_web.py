import unittest
from fastapi.testclient import TestClient
from dash33.web import create_app

class TestWeb(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_health_check(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_wallet_status(self):
        response = self.client.get("/api/v1/wallet/status")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json()) 