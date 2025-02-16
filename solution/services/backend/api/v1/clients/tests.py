from http import HTTPStatus as status
from django.test import TestCase
from django.urls import reverse
import json
from uuid import uuid4
from apps.client.models import Client


class ClientTests(TestCase):
    def setUp(self):
        self.client_1 = Client.objects.create(
            login="testuser1", age=25, location="City1", gender="MALE"
        )
        self.client_2 = Client.objects.create(
            login="testuser2", age=30, location="City2", gender="FEMALE"
        )

        self.bulk_url = "/clients/bulk"
        self.get_url = "/clients"

    def test_bulk_create_or_update(self):
        client_3_id = str(uuid4())
        client_data = [
            {
                "client_id": client_3_id,
                "login": "newusers",
                "age": 21,
                "location": "City1",
                "gender": "FEMALE",
            },
            {
                "client_id": str(self.client_1.id),
                "login": "updateduser",
                "age": 26,
                "location": "City1",
                "gender": "MALE",
            },
            {
                "client_id": client_3_id,
                "login": "newusersa",
                "age": 25,
                "location": "City1",
                "gender": "FEMALE",
            },
            {
                "client_id": client_3_id,
                "login": "newuser",
                "age": 22,
                "location": "City3",
                "gender": "MALE",
            },
        ]
        response = self.client.post(
            self.bulk_url,
            data=json.dumps(client_data),
            content_type="application/json",
        )
        client_3 = Client.objects.get(id=client_3_id)
        self.client_1.refresh_from_db()

        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(Client.objects.count(), 3)
        self.assertEqual(self.client_1.login, "updateduser")
        self.assertEqual(client_3.location, "City3")
        self.assertEqual(client_3.login, "newuser")
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()[1]["client_id"], str(client_3.id))
        self.assertEqual(response.json()[1]["login"], client_3.login)

    def test_bulk_create_invalid_data(self):
        client_data = [
            {
                "client_id": "invalid_uuid",
                "login": "baduser",
                "age": 150,
                "location": "City4",
                "gender": "UNKNOWN",
            }
        ]
        response = self.client.post(
            self.bulk_url,
            data=json.dumps(client_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_duplicate_advertiser_ids(self):
        adv_id = uuid4()
        data = [
            {
                "client_id": str(adv_id),
                "login": "baduser",
                "age": 10,
                "location": "City4",
                "gender": "FEMALE",
            },
            {
                "client_id": str(adv_id),
                "login": "Last",
                "age": 14,
                "location": "City4",
                "gender": "MALE",
            },
        ]
        response = self.client.post(
            self.bulk_url, json.dumps(data), content_type="application/json"
        )
        client = Client.objects.get(id=adv_id)

        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(client.login, "Last")
        self.assertEqual(client.age, 14)
        self.assertEqual(client.gender, "MALE")

    def test_invalid_client_id_format(self):
        client_data = [
            {
                "client_id": "invalid_uuid",
                "login": "baduser",
                "age": 150,
                "location": "City4",
                "gender": "UNKNOWN",
            }
        ]
        response = self.client.post(
            self.bulk_url,
            json.dumps(client_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_empty_bulk_request(self):
        response = self.client.post(
            self.bulk_url, json.dumps([]), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(len(response.json()), 0)

    def test_get_client_success(self):
        response = self.client.get(f"{self.get_url}/{self.client_1.id}")

        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(response.json()["login"], self.client_1.login)

    def test_get_client_not_found(self):
        response = self.client.get(f"{self.get_url}/{uuid4()}")

        self.assertEqual(response.status_code, status.NOT_FOUND)

    def test_get_client_invalid_uuid(self):
        response = self.client.get(f"{self.get_url}/invalid_uuid")

        self.assertEqual(response.status_code, status.BAD_REQUEST)
