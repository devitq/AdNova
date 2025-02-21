import json
import uuid
from http import HTTPStatus as status

from django.test import TestCase, Client
from apps.advertiser.models import Advertiser
from apps.client.models import Client as ClientModel
from apps.mlscore.models import Mlscore


class TestMlscoreEndpoint(TestCase):
    def setUp(self):
        self.client = Client()
        self.advertiser = Advertiser.objects.create(name="Test Advertiser")
        self.client_obj = ClientModel.objects.create(
            login="test_client",
            age=14,
            location="test_location",
            gender=ClientModel.GenderChoices.FEMALE,
        )

        self.url = "/ml-scores"

    def test_create_mlscore_success(self):
        data = {
            "advertiser_id": str(self.advertiser.id),
            "client_id": str(self.client_obj.id),
            "score": 90,
        }
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )
        mlscore = Mlscore.objects.first()

        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(mlscore.score, 90)

    def test_update_mlscore_success(self):
        mlscore = Mlscore.objects.create(
            advertiser=self.advertiser,
            client=self.client_obj,
            score=80,
        )
        data = {
            "advertiser_id": str(self.advertiser.id),
            "client_id": str(self.client_obj.id),
            "score": 85,
        }
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )
        mlscore.refresh_from_db()

        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(mlscore.score, 85)

    def test_missing_required_field(self):
        data = {"score": 90}
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_invalid_uuid_format(self):
        data = {
            "advertiser_id": "invalid-uuid",
            "client_id": str(self.client_obj.id),
            "score": 90,
        }
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_non_existing_client(self):
        data = {
            "advertiser_id": str(self.advertiser.id),
            "client_id": str(uuid.uuid4()),
            "score": 90,
        }
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_non_existing_advertiser(self):
        data = {
            "advertiser_id": str(uuid.uuid4()),
            "client_id": str(self.client_obj.id),
            "score": 90,
        }
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)


class TestBulkAdvertisersEndpoint(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/advertisers/bulk"
        self.advertiser = Advertiser.objects.create(name="Advertiser 1")

    def test_bulk_create_success(self):
        uuid1 = self.advertiser.id
        uuid2 = uuid.uuid4()
        data = [
            {"advertiser_id": str(uuid1), "name": "Advertiser 4"},
            {"advertiser_id": str(uuid2), "name": "Advertiser 1"},
            {"advertiser_id": str(uuid2), "name": "Advertiser 5"},
            {"advertiser_id": str(uuid2), "name": "Advertiser 2"},
            {"advertiser_id": str(uuid1), "name": "Advertiser 2"},
        ]
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )
        self.advertiser.refresh_from_db()

        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(self.advertiser.name, "Advertiser 2")
        self.assertEqual(Advertiser.objects.count(), 2)

    def test_bulk_update_success(self):
        advertiser = Advertiser.objects.create(name="Old Name")
        data = [{"advertiser_id": str(advertiser.id), "name": "New Name"}]
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )
        advertiser.refresh_from_db()

        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(advertiser.name, "New Name")

    def test_duplicate_advertiser_ids(self):
        adv_id = uuid.uuid4()
        data = [
            {"advertiser_id": str(adv_id), "name": "First"},
            {"advertiser_id": str(adv_id), "name": "Last"},
        ]
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )
        advertiser = Advertiser.objects.get(id=adv_id)

        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(advertiser.name, "Last")

    def test_invalid_advertiser_id_format(self):
        data = [{"advertiser_id": "invalid", "name": "Invalid"}]
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_empty_bulk_request(self):
        response = self.client.post(
            self.url, json.dumps([]), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(len(response.json()), 0)


class TestGetAdvertiserEndpoint(TestCase):
    def setUp(self):
        self.client = Client()
        self.advertiser = Advertiser.objects.create(name="Test Advertiser")
        self.url = "/advertisers"
        self.valid_url = f"{self.url}/{self.advertiser.id}"

    def test_get_advertiser_success(self):
        response = self.client.get(self.valid_url)

        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(
            response.json()["advertiser_id"], str(self.advertiser.id)
        )
        self.assertEqual(response.json()["name"], self.advertiser.name)

    def test_non_existent_advertiser(self):
        non_existent_url = f"{self.url}/{uuid.uuid4()}"
        response = self.client.get(non_existent_url)

        self.assertEqual(response.status_code, status.NOT_FOUND)

    def test_invalid_uuid_format(self):
        response = self.client.get(f"{self.url}/invalid-uuid")

        self.assertEqual(response.status_code, status.BAD_REQUEST)
