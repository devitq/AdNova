from django.core.cache import cache
from django.test import TestCase, override_settings

from apps.advertiser.models import Advertiser
from apps.campaign.models import Campaign, CampaignClick, CampaignImpression
from apps.client.models import Client


class CampaignStatisticsTest(TestCase):
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
        cls.client_instance = Client.objects.create(
            login="test_client",
            age=30,
            gender="MALE",
            location="Test Location",
        )

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def setUp(self) -> None:
        cache.clear()
        cache.set("current_date", 5)

    def test_get_statistics_no_data(self) -> None:
        stats = self.campaign.get_statistics()
        expected_stats = {
            "impressions_count": 0,
            "clicks_count": 0,
            "conversion": 0,
            "spent_impressions": 0,
            "spent_clicks": 0,
            "spent_total": 0,
        }

        self.assertEqual(stats, expected_stats)

    def test_get_statistics_with_data(self) -> None:
        CampaignImpression.objects.create(
            campaign=self.campaign,
            client=self.client_instance,
            price=self.campaign.cost_per_impression,
            date=5,
        )
        CampaignClick.objects.create(
            campaign=self.campaign,
            client=self.client_instance,
            price=self.campaign.cost_per_click,
            date=5,
        )
        stats = self.campaign.get_statistics()
        expected_stats = {
            "impressions_count": 1,
            "clicks_count": 1,
            "conversion": 100.0,
            "spent_impressions": 0.05,
            "spent_clicks": 0.10,
            "spent_total": 0.15,
        }

        self.assertEqual(stats, expected_stats)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_get_daily_statistics_no_data(self) -> None:
        daily_stats = self.campaign.get_daily_statistics()
        expected_stats = [
            {
                "date": day,
                "impressions_count": 0,
                "clicks_count": 0,
                "conversion": 0,
                "spent_impressions": 0,
                "spent_clicks": 0,
                "spent_total": 0,
            }
            for day in range(
                self.campaign.start_date, cache.get("current_date") + 1
            )
        ]

        self.assertEqual(daily_stats, expected_stats)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_get_daily_statistics_with_data(self) -> None:
        CampaignImpression.objects.create(
            campaign=self.campaign,
            client=self.client_instance,
            price=self.campaign.cost_per_impression,
            date=5,
        )
        CampaignClick.objects.create(
            campaign=self.campaign,
            client=self.client_instance,
            price=self.campaign.cost_per_click,
            date=5,
        )
        daily_stats = self.campaign.get_daily_statistics()
        expected_stats = [
            {
                "date": day,
                "impressions_count": 1 if day == 5 else 0,
                "clicks_count": 1 if day == 5 else 0,
                "conversion": 100.0 if day == 5 else 0,
                "spent_impressions": 0.05 if day == 5 else 0,
                "spent_clicks": 0.10 if day == 5 else 0,
                "spent_total": 0.15 if day == 5 else 0,
            }
            for day in range(
                self.campaign.start_date, cache.get("current_date") + 1
            )
        ]

        self.assertEqual(daily_stats, expected_stats)
