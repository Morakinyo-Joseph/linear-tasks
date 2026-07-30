from django.db import DatabaseError, OperationalError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Membership, Organization, User
from todos.models import Todo


class AuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_signup_creates_org_and_owner_membership(self):
        response = self.client.post(
            "/api/v1/auth/signup/",
            {
                "email": "owner@linear.test",
                "password": "secret12345",
                "first_name": "Ada",
                "last_name": "Lovelace",
                "organization_name": "Linear HQ",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        user = User.objects.get(email="owner@linear.test")
        self.assertIsNotNone(user.organization_id)
        self.assertEqual(
            Membership.objects.filter(
                user=user,
                organization=user.organization,
                role=Membership.Role.OWNER,
            ).count(),
            1,
        )
        self.assertEqual(Organization.objects.count(), 1)

    def test_login_wrong_password_401(self):
        org = Organization.objects.create(name="Acme", slug="acme-test")
        User.objects.create_user(
            email="user@linear.test",
            password="secret12345",
            organization=org,
        )
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": "user@linear.test", "password": "wrong-password"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_auth(self):
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TodoSchemaDriftTests(TestCase):
    """Documents the intentional migration 0002 model/DB drift (description)."""

    def setUp(self):
        self.org = Organization.objects.create(name="Org A", slug="org-a")
        self.user = User.objects.create_user(
            email="a@linear.test",
            password="secret12345",
            organization=self.org,
        )
        Membership.objects.create(
            user=self.user,
            organization=self.org,
            role=Membership.Role.OWNER,
        )
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.user).access_token}"
        )

    def test_orm_select_description_raises(self):
        with self.assertRaises((OperationalError, DatabaseError)):
            list(
                Todo.objects.filter(organization_id=self.org.id).values(
                    "id", "title", "description"
                )
            )

    def test_create_todo_raises_schema_drift(self):
        with self.assertRaises((OperationalError, DatabaseError)):
            self.client.post(
                "/api/v1/todos/",
                {"title": "Ship API", "description": "Phase 1", "priority": "high"},
                format="json",
            )

    def test_unauthenticated_todos_401(self):
        response = APIClient().get("/api/v1/todos/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DemoErrorEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_boom_raises_when_debug(self):
        with self.settings(DEBUG=True):
            with self.assertRaises(RuntimeError):
                self.client.get("/api/v1/demo/boom/")

    def test_boom_hidden_when_not_debug(self):
        with self.settings(DEBUG=False):
            response = self.client.get("/api/v1/demo/boom/")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
