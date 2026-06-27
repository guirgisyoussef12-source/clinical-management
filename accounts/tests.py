from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import DoctorProfile, PatientProfile

User = get_user_model()


# ─── Helpers ────────────────────────────────────────────────────────────────

def create_user(username, password, role, email=None):
    return User.objects.create_user(
        username=username,
        email=email or f"{username}@test.com",
        password=password,
        role=role,
    )


def auth_client(user, password="testpass123"):
    client = APIClient()
    res = client.post("/api/accounts/login/", {"username": user.username, "password": password})
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
    return client


# ─── Register ────────────────────────────────────────────────────────────────

class RegisterTests(TestCase):

    def test_register_as_patient_success(self):
        client = APIClient()
        res = client.post("/api/accounts/register/", {
            "username": "patient1",
            "email": "patient1@test.com",
            "password": "testpass123",
            "role": "PATIENT",
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username="patient1").role, User.Role.PATIENT)

    def test_register_as_doctor_success(self):
        client = APIClient()
        res = client.post("/api/accounts/register/", {
            "username": "doctor1",
            "email": "doctor1@test.com",
            "password": "testpass123",
            "role": "DOCTOR",
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_register_as_receptionist_blocked(self):
        client = APIClient()
        res = client.post("/api/accounts/register/", {
            "username": "recep1",
            "email": "recep1@test.com",
            "password": "testpass123",
            "role": "RECEPTIONIST",
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email_blocked(self):
        create_user("user1", "testpass123", User.Role.PATIENT, email="same@test.com")
        client = APIClient()
        res = client.post("/api/accounts/register/", {
            "username": "user2",
            "email": "same@test.com",
            "password": "testpass123",
            "role": "PATIENT",
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username_blocked(self):
        create_user("sameuser", "testpass123", User.Role.PATIENT)
        client = APIClient()
        res = client.post("/api/accounts/register/", {
            "username": "sameuser",
            "email": "other@test.com",
            "password": "testpass123",
            "role": "PATIENT",
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password_blocked(self):
        client = APIClient()
        res = client.post("/api/accounts/register/", {
            "username": "user3",
            "email": "user3@test.com",
            "password": "123",
            "role": "PATIENT",
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_cannot_access_protected_endpoint(self):
        client = APIClient()
        res = client.get("/api/accounts/doctors/me/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ─── Login ───────────────────────────────────────────────────────────────────

class LoginTests(TestCase):

    def setUp(self):
        self.user = create_user("loginuser", "testpass123", User.Role.PATIENT)

    def test_login_returns_tokens(self):
        client = APIClient()
        res = client.post("/api/accounts/login/", {
            "username": "loginuser",
            "password": "testpass123",
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_login_wrong_password_fails(self):
        client = APIClient()
        res = client.post("/api/accounts/login/", {
            "username": "loginuser",
            "password": "wrongpass",
        })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ─── Doctor Profile ──────────────────────────────────────────────────────────

class DoctorProfileTests(TestCase):

    def setUp(self):
        self.doctor = create_user("doc1", "testpass123", User.Role.DOCTOR)
        self.patient = create_user("pat1", "testpass123", User.Role.PATIENT)
        self.doctor_client = auth_client(self.doctor)
        self.patient_client = auth_client(self.patient)

    def test_doctor_get_profile_no_profile_returns_404(self):
        res = self.doctor_client.get("/api/accounts/doctors/me/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_doctor_create_profile_via_patch(self):
        res = self.doctor_client.patch("/api/accounts/doctors/me/", {
            "phone": "01012345678",
            "date_of_birth": "1985-03-15",
            "specialization": "Cardiology",
            "work_hours": "9am-5pm",
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(DoctorProfile.objects.filter(user=self.doctor).exists())

    def test_doctor_update_profile(self):
        DoctorProfile.objects.create(
            user=self.doctor,
            phone="01012345678",
            date_of_birth="1985-03-15",
            specialization="Cardiology",
            work_hours="9am-5pm",
        )
        res = self.doctor_client.patch("/api/accounts/doctors/me/", {
            "specialization": "Neurology",
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["specialization"], "Neurology")

    def test_patient_cannot_access_doctor_endpoint(self):
        res = self.patient_client.get("/api/accounts/doctors/me/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


# ─── Patient Profile ─────────────────────────────────────────────────────────

class PatientProfileTests(TestCase):

    def setUp(self):
        self.patient = create_user("pat2", "testpass123", User.Role.PATIENT)
        self.doctor = create_user("doc2", "testpass123", User.Role.DOCTOR)
        self.patient_client = auth_client(self.patient)
        self.doctor_client = auth_client(self.doctor)

    def test_patient_get_profile_no_profile_returns_404(self):
        res = self.patient_client.get("/api/accounts/patients/me/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_patient_create_profile_via_patch(self):
        res = self.patient_client.patch("/api/accounts/patients/me/", {
            "phone": "01098765432",
            "date_of_birth": "1995-07-20",
            "address": "123 Main St, Cairo",
            "gender": "MALE",
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(PatientProfile.objects.filter(user=self.patient).exists())

    def test_doctor_cannot_access_patient_endpoint(self):
        res = self.doctor_client.get("/api/accounts/patients/me/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)