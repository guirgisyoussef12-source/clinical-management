from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import RegisterView, LoginView, RefreshView, DoctorProfileView, PatientProfileView

router = SimpleRouter()
router.register("doctors", DoctorProfileView, basename="doctor-profile")
router.register("patients", PatientProfileView, basename="patient-profile")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("", include(router.urls)),
]