from uuid import uuid4

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from apps.advertiser.models import Advertiser
from apps.campaign.models import Campaign
from apps.client.models import Client


class CampaignModelTest(TestCase):
    @classmethod
    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def setUpTestData(cls) -> None:
        cls.advertiser = Advertiser.objects.create(name="Test Advertiser")
        cls.campaign = Campaign.objects.create(
            advertiser=cls.advertiser,
            impressions_limit=1000,
            clicks_limit=500,
            cost_per_impression=0.05,
            cost_per_click=0.10,
            ad_title="Test Campaign",
            ad_text="This is a test campaign.",
            start_date=1,
            end_date=10,
        )

    def test_campaign_creation(self) -> None:
        self.assertIsInstance(self.campaign, Campaign)
        self.assertEqual(self.campaign.ad_title, "Test Campaign")

    def test_campaign_str_method(self) -> None:
        self.assertEqual(str(self.campaign), "Test Campaign")

    def test_campaign_id_property(self) -> None:
        self.assertEqual(self.campaign.campaign_id, self.campaign.id)
        new_id = uuid4()
        self.campaign.campaign_id = new_id
        self.assertEqual(self.campaign.id, new_id)

    def test_ad_id_property(self) -> None:
        self.assertEqual(self.campaign.ad_id, self.campaign.id)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_started_property(self) -> None:
        cache.set("current_date", 5)
        self.assertTrue(self.campaign.started)
        cache.set("current_date", 0)
        self.assertFalse(self.campaign.started)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_active_property(self) -> None:
        cache.set("current_date", 5)
        self.assertTrue(self.campaign.active)
        cache.set("current_date", 11)
        self.assertFalse(self.campaign.active)
        cache.set("current_date", 5)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_clean_method(self) -> None:
        self.campaign.start_date = -1

        with self.assertRaises(ValidationError):
            self.campaign.clean()

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_view_method(self) -> None:
        client = Client.objects.create(
            login="test_client", age=15, location="Moscow", gender="FEMALE"
        )
        self.campaign.view(client)

        self.assertEqual(self.campaign.impressions.count(), 1)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_click_method(self) -> None:
        client = Client.objects.create(
            login="test_client", age=15, location="Moscow", gender="FEMALE"
        )
        self.campaign.view(client)
        self.campaign.click(client)

        self.assertEqual(self.campaign.clicks.count(), 1)
