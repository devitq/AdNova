from http import HTTPStatus as status
from django.test import TestCase, override_settings
from django.core.cache import cache
import json


class AdvanceTimeTests(TestCase):
    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def setUp(self):
        cache.clear()
        cache.set("current_date", 10)

        self.url = "/time/advance"

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_advance_time_success(self):
        self.assertEqual(cache.get("current_date"), 10)

        response = self.client.post(
            self.url,
            data=json.dumps({"current_date": 15}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(response.json()["current_date"], 15)
        self.assertEqual(cache.get("current_date"), 15)

    # unittest & django pobeda so i can't use override_settings and parametrized at the same time, sorry
    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_advance_time_failure_invalid_value1(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"current_date": list()}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_advance_time_failure_invalid_value2(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"current_date": -1241}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_advance_time_failure_invalid_value3(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"current_date": "lol"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_advance_time_failure_invalid_value4(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"current_date": dict()}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_advance_time_failure_less_than_actual(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"current_date": 5}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)
