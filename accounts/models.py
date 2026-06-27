from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    class Role(models.TextChoices):
        DOCTOR = "DOCTOR", "Doctor"
        PATIENT = "PATIENT", "Patient"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)

    def __str__(self):
        return f"{self.username} ({self.role})"


class DoctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile")
    phone = models.CharField(max_length=11)
    date_of_birth = models.DateField()
    specialization = models.CharField(max_length=40)
    work_hours = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr. {self.user.username} — {self.specialization}"


class PatientProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_profile")
    phone = models.CharField(max_length=11)
    date_of_birth = models.DateField()
    address = models.TextField()
    gender = models.CharField(max_length=6, choices=Gender.choices)

    def __str__(self):
        return f"{self.user.username} ({self.gender})"