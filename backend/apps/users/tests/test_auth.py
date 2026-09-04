from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class RegistrationTests(APITestCase):
    def test_customer_can_self_register(self):
        url = reverse("users:register")
        payload = {
            "email": "customer@example.com",
            "first_name": "Casey",
            "role": User.Role.CUSTOMER,
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="customer@example.com").exists())

    def test_cannot_self_register_as_admin(self):
        url = reverse("users:register")
        payload = {
            "email": "wannabe-admin@example.com",
            "first_name": "Eve",
            "role": User.Role.ADMIN,
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="wannabe-admin@example.com").exists())

    def test_password_mismatch_is_rejected(self):
        url = reverse("users:register")
        payload = {
            "email": "mismatch@example.com",
            "first_name": "Sam",
            "role": User.Role.CUSTOMER,
            "password": "StrongPass123",
            "confirm_password": "DoesNotMatch",
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="login@example.com",
            password="StrongPass123",
            first_name="Lin",
            role=User.Role.CUSTOMER,
        )

    def test_login_returns_tokens_and_role_claim(self):
        url = reverse("users:login")
        response = self.client.post(
            url, {"email": "login@example.com", "password": "StrongPass123"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["role"], User.Role.CUSTOMER)

    def test_login_rejects_wrong_password(self):
        url = reverse("users:login")
        response = self.client.post(
            url, {"email": "login@example.com", "password": "WrongPassword"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminUserManagementTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="StrongPass123", first_name="Ada"
        )
        self.customer = User.objects.create_user(
            email="cust@example.com",
            password="StrongPass123",
            first_name="Cara",
            role=User.Role.CUSTOMER,
        )

    def test_customer_cannot_list_users(self):
        self.client.force_authenticate(self.customer)
        response = self.client.get(reverse("users:admin-users-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_manager_account(self):
        self.client.force_authenticate(self.admin)
        payload = {
            "email": "manager@example.com",
            "first_name": "Max",
            "role": User.Role.MANAGER,
            "password": "StrongPass123",
        }
        response = self.client.post(reverse("users:admin-users-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email="manager@example.com").role, User.Role.MANAGER)
