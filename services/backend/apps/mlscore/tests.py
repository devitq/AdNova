from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from config.errors import ConflictError
from apps.advertiser.models import Advertiser
from apps.client.models import Client
from apps.mlscore.models import Mlscore


class MlscoreModelTest(TestCase):
    def setUp(self):
        self.advertiser = Advertiser.objects.create(name="Test Advertiser")
        self.client_obj = Client.objects.create(
            login="test_client",
            age=25,
            location="test_location",
            gender=Client.GenderChoices.MALE,
        )

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_create_mlscore(self):
        mlscore = Mlscore.objects.create(
            advertiser=self.advertiser,
            client=self.client_obj,
            score=95,
        )

        self.assertEqual(mlscore.score, 95)
        self.assertEqual(str(mlscore), "Test Advertiser | test_client")

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_mlscore_unique_together_constraint(self):
        Mlscore.objects.create(
            advertiser=self.advertiser,
            client=self.client_obj,
            score=80,
        )

        with self.assertRaises(ConflictError):
            Mlscore.objects.create(
                advertiser=self.advertiser,
                client=self.client_obj,
                score=85,
            )

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_delete_advertiser_cascades(self):
        mlscore = Mlscore.objects.create(
            advertiser=self.advertiser,
            client=self.client_obj,
            score=90,
        )
        self.advertiser.delete()

        self.assertFalse(Mlscore.objects.filter(id=mlscore.id).exists())

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_delete_client_cascades(self):
        mlscore = Mlscore.objects.create(
            advertiser=self.advertiser,
            client=self.client_obj,
            score=90,
        )
        self.client_obj.delete()

        self.assertFalse(Mlscore.objects.filter(id=mlscore.id).exists())

    def test_score_positive_integer_constraint(self):
        with self.assertRaises(ValidationError):
            Mlscore.objects.create(
                advertiser=self.advertiser,
                client=self.client_obj,
                score=-5,
            )
