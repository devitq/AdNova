import uuid
from django.test import TestCase, Client, override_settings
from http import HTTPStatus as status
from apps.campaign.models import Advertiser, Campaign


class AdvertiserCampaignTestCase(TestCase):
    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def setUp(self):
        self.client = Client()
        self.advertiser = Advertiser.objects.create(name="Test Advertiser")
        self.campaign = Campaign.objects.create(
            advertiser=self.advertiser,
            impressions_limit=0,
            clicks_limit=0,
            cost_per_impression=0,
            cost_per_click=0,
            ad_title="title",
            ad_text="text",
            start_date=0,
            end_date=0,
        )

        self.campaigns_prefix = "/stats/campaigns"
        self.advertisers_prefix = "/stats/advertisers"

    def test_get_campaign_statistics_invalid_uuid(self):
        response = self.client.get(f"{self.campaigns_prefix}/invalid-uuid")

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_get_campaign_statistics_campaign_not_found(self):
        non_existent_campaign_id = uuid.uuid4()
        response = self.client.get(
            f"{self.campaigns_prefix}/{non_existent_campaign_id}"
        )

        self.assertEqual(response.status_code, status.NOT_FOUND)

    def test_get_campaign_statistics_success(self):
        response = self.client.get(
            f"{self.campaigns_prefix}/{self.campaign.id}"
        )

        self.assertEqual(response.status_code, status.OK)
        self.assertIsInstance(response.json(), dict)

    def test_get_daily_campaign_statistics_invalid_uuid(self):
        response = self.client.get(
            f"{self.campaigns_prefix}/invalid-uuid/daily"
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_get_daily_campaign_statistics_campaign_not_found(self):
        non_existent_campaign_id = uuid.uuid4()
        response = self.client.get(
            f"{self.campaigns_prefix}/{non_existent_campaign_id}/daily"
        )

        self.assertEqual(response.status_code, status.NOT_FOUND)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_get_daily_campaign_statistics_success(self):
        response = self.client.get(
            f"{self.campaigns_prefix}/{self.campaign.id}/daily"
        )

        self.assertEqual(response.status_code, status.OK)
        self.assertIsInstance(response.json(), list)

    def test_get_advertiser_statistics_invalid_uuid(self):
        response = self.client.get(f"{self.advertisers_prefix}/invalid-uuid")

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_get_advertiser_statistics_not_found(self):
        non_existent_advertiser_id = uuid.uuid4()
        response = self.client.get(
            f"{self.advertisers_prefix}/{non_existent_advertiser_id}"
        )

        self.assertEqual(response.status_code, status.NOT_FOUND)

    def test_get_advertiser_statistics_success(self):
        response = self.client.get(
            f"{self.advertisers_prefix}/{self.advertiser.id}"
        )

        self.assertEqual(response.status_code, status.OK)
        self.assertIsInstance(response.json(), dict)

    def test_get_daily_advertiser_statistics_invalid_uuid(self):
        response = self.client.get(
            f"{self.advertisers_prefix}/invalid-uuid/campaigns/daily"
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_get_daily_advertiser_statistics_advertiser_not_found(self):
        non_existent_advertiser_id = uuid.uuid4()
        response = self.client.get(
            f"{self.advertisers_prefix}/{non_existent_advertiser_id}/campaigns/daily"
        )

        self.assertEqual(response.status_code, status.NOT_FOUND)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_get_daily_advertiser_statistics_success(self):
        response = self.client.get(
            f"{self.advertisers_prefix}/{self.advertiser.id}/campaigns/daily"
        )

        self.assertEqual(response.status_code, status.OK)
        self.assertIsInstance(response.json(), list)
