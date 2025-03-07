from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.client.models import Client


class ClientModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            login="test_client",
            age=25,
            location="Test City",
            gender=Client.GenderChoices.MALE,
        )

    def test_client_creation_success(self):
        self.assertEqual(self.client.login, "test_client")
        self.assertEqual(self.client.age, 25)
        self.assertEqual(self.client.location, "Test City")
        self.assertEqual(self.client.gender, Client.GenderChoices.MALE)

    def test_client_string_representation(self):
        self.assertEqual(str(self.client), "test_client")

    def test_client_id_property(self):
        new_id = self.client.id
        self.client.client_id = new_id

        self.assertEqual(self.client.client_id, new_id)

    def test_age_cannot_exceed_max_value(self):
        self.client.age = 120

        with self.assertRaises(ValidationError):
            self.client.full_clean()

    def test_valid_gender_choices(self):
        self.client.gender = "MALE"
        self.client.full_clean()

        self.client.gender = "FEMALE"
        self.client.full_clean()

    def test_invalid_gender_choice(self):
        self.client.gender = "OTHER"

        with self.assertRaises(ValidationError):
            self.client.full_clean()

    def test_blank_login(self):
        self.client.login = ""

        with self.assertRaises(ValidationError):
            self.client.full_clean()
