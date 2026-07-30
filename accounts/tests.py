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


class TodoTenancyTests(TestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(name="Org A", slug="org-a")
        self.org_b = Organization.objects.create(name="Org B", slug="org-b")
        self.user_a = User.objects.create_user(
            email="a@linear.test",
            password="secret12345",
            organization=self.org_a,
        )
        Membership.objects.create(
            user=self.user_a,
            organization=self.org_a,
            role=Membership.Role.OWNER,
        )
        self.user_b = User.objects.create_user(
            email="b@linear.test",
            password="secret12345",
            organization=self.org_b,
        )
        Membership.objects.create(
            user=self.user_b,
            organization=self.org_b,
            role=Membership.Role.OWNER,
        )
        self.todo_a = Todo.objects.create(
            organization=self.org_a,
            created_by=self.user_a,
            title="A only",
        )
        self.todo_b = Todo.objects.create(
            organization=self.org_b,
            created_by=self.user_b,
            title="B only",
        )
        self.client_a = APIClient()
        self.client_a.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.user_a).access_token}"
        )
        self.client_b = APIClient()
        self.client_b.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.user_b).access_token}"
        )

    def test_unauthenticated_todos_401(self):
        client = APIClient()
        response = client.get("/api/v1/todos/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_own_org(self):
        response = self.client_a.get("/api/v1/todos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row["id"] for row in response.data["results"]}
        self.assertIn(str(self.todo_a.public_id), ids)
        self.assertNotIn(str(self.todo_b.public_id), ids)

    def test_cannot_get_other_org_todo(self):
        response = self.client_a.get(f"/api/v1/todos/{self.todo_b.public_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_patch_other_org_todo(self):
        response = self.client_a.patch(
            f"/api/v1/todos/{self.todo_b.public_id}/",
            {"title": "hacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.todo_b.refresh_from_db()
        self.assertEqual(self.todo_b.title, "B only")

    def test_cannot_delete_other_org_todo(self):
        response = self.client_a.delete(f"/api/v1/todos/{self.todo_b.public_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Todo.objects.filter(pk=self.todo_b.pk).exists())

    def test_create_and_complete(self):
        create = self.client_a.post(
            "/api/v1/todos/",
            {"title": "Ship API", "description": "Phase 1"},
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        todo_id = create.data["id"]
        complete = self.client_a.post(f"/api/v1/todos/{todo_id}/complete/")
        self.assertEqual(complete.status_code, status.HTTP_200_OK)
        self.assertEqual(complete.data["status"], "done")
