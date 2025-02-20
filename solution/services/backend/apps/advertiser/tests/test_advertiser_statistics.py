from django.core.cache import cache
from django.test import TestCase, override_settings
from apps.advertiser.models import Advertiser
from apps.campaign.models import Campaign, CampaignImpression, CampaignClick
from apps.client.models import Client


class AdvertiserStatisticsTest(TestCase):
    @classmethod
    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def setUpTestData(cls):
        cache.set("current_date", 1)

        cls.advertiser = Advertiser.objects.create(name="Test Advertiser")
        cls.campaign1 = Campaign.objects.create(
            advertiser=cls.advertiser,
            impressions_limit=1000,
            clicks_limit=500,
            cost_per_impression=0.05,
            cost_per_click=0.10,
            ad_title="Campaign 1",
            ad_text="This is the first test campaign.",
            start_date=1,
            end_date=10,
        )
        cls.campaign2 = Campaign.objects.create(
            advertiser=cls.advertiser,
            impressions_limit=2000,
            clicks_limit=1000,
            cost_per_impression=0.04,
            cost_per_click=0.08,
            ad_title="Campaign 2",
            ad_text="This is the second test campaign.",
            start_date=2,
            end_date=12,
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
    def setUp(self):
        cache.clear()
        cache.set("current_date", 5)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_get_statistics_no_data(self):
        stats = self.advertiser.get_statistics()
        expected_stats = {
            "impressions_count": 0,
            "clicks_count": 0,
            "conversion": 0,
            "spent_impressions": 0.0,
            "spent_clicks": 0.0,
            "spent_total": 0.0,
        }

        self.assertEqual(stats, expected_stats)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_get_statistics_with_data(self):
        CampaignImpression.objects.create(
            campaign=self.campaign1,
            client=self.client_instance,
            price=self.campaign1.cost_per_impression,
            date=3,
        )
        CampaignClick.objects.create(
            campaign=self.campaign1,
            client=self.client_instance,
            price=self.campaign1.cost_per_click,
            date=3,
        )
        CampaignImpression.objects.create(
            campaign=self.campaign2,
            client=self.client_instance,
            price=self.campaign2.cost_per_impression,
            date=4,
        )

        stats = self.advertiser.get_statistics()
        expected_stats = {
            "impressions_count": 2,
            "clicks_count": 1,
            "conversion": 50.0,
            "spent_impressions": 0.09,
            "spent_clicks": 0.10,
            "spent_total": 0.19,
        }

        self.assertEqual(stats, expected_stats)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_get_daily_statistics_no_data(self):
        daily_stats = self.advertiser.get_daily_statistics()
        expected_stats = [
            {
                "impressions_count": 0,
                "clicks_count": 0,
                "conversion": 0,
                "spent_impressions": 0.0,
                "spent_clicks": 0.0,
                "spent_total": 0.0,
                "date": day,
            }
            for day in range(cache.get("current_date", 0) + 1)
        ]

        self.assertEqual(daily_stats, expected_stats)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_get_daily_statistics_with_data(self):
        CampaignImpression.objects.create(
            campaign=self.campaign1,
            client=self.client_instance,
            price=self.campaign1.cost_per_impression,
            date=3,
        )
        CampaignClick.objects.create(
            campaign=self.campaign1,
            client=self.client_instance,
            price=self.campaign1.cost_per_click,
            date=3,
        )
        CampaignImpression.objects.create(
            campaign=self.campaign2,
            client=self.client_instance,
            price=self.campaign2.cost_per_impression,
            date=4,
        )

        daily_stats = self.advertiser.get_daily_statistics()
        expected_stats = [
            {
                "impressions_count": 1 if day == 3 else 1 if day == 4 else 0,
                "clicks_count": 1 if day == 3 else 0,
                "conversion": 100.0 if day == 3 else 0.0,
                "spent_impressions": 0.05
                if day == 3
                else 0.04
                if day == 4
                else 0.0,
                "spent_clicks": 0.10 if day == 3 else 0.0,
                "spent_total": 0.15 if day == 3 else 0.04 if day == 4 else 0.0,
                "date": day,
            }
            for day in range(cache.get("current_date") + 1)
        ]

        self.assertEqual(daily_stats, expected_stats)
