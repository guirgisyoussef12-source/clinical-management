from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import AppointmentViewSet

router = SimpleRouter()
router.register("", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("", include(router.urls)),
]