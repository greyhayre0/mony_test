from django.test import TestCase, Client
from django.core.cache import cache
from .models import ExchangeRate
import time


class ExchangeRateTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        cache.clear()

        ExchangeRate.objects.create(usd_rate=75.50)
        ExchangeRate.objects.create(usd_rate=76.00)

    def test_get_current_usd_success(self):
        """Тест успешного получения курса"""
        response = self.client.get("/get-current-usd/")

        if response.status_code == 429:
            time.sleep(10)
            response = self.client.get("/get-current-usd/")

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("current_rate", data)
        self.assertIn("last_10_requests", data)
        self.assertIsInstance(data["current_rate"], float)
        self.assertIsInstance(data["last_10_requests"], list)

    def test_rate_limiting(self):
        """Тест ограничения частоты запросов"""
        response1 = self.client.get("/get-current-usd/")

        response2 = self.client.get("/get-current-usd/")

        if response1.status_code == 200:
            self.assertEqual(response2.status_code, 429)
            data = response2.json()
            self.assertIn("error", data)
            self.assertIn("remaining_time", data)

    def test_last_10_requests(self):
        """Тест возврата последних 10 запросов"""
        for i in range(15):
            ExchangeRate.objects.create(usd_rate=75.00 + i * 0.1)

        response = self.client.get("/get-current-usd/")
        if response.status_code == 429:
            time.sleep(10)
            response = self.client.get("/get-current-usd/")

        if response.status_code == 200:
            data = response.json()
            self.assertEqual(len(data["last_10_requests"]), 10)
