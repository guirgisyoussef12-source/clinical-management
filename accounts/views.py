from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import DoctorProfile , PatientProfile
from .serializers import DoctorProfileSerializer , PatientProfileSerializer
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .serializers import RegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class DoctorProfileView(viewsets.ModelViewSet):
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DoctorProfile.objects.select_related("user").filter(
            user=self.request.user
        )

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):

        if request.user.role != User.Role.DOCTOR:
            return Response(
                {"detail": "Only doctors can access this endpoint."},
                status=403
            )

        profile, _ = DoctorProfile.objects.get_or_create(
            user=request.user
        )

        if request.method == "PATCH":
            serializer = self.get_serializer(
                profile,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return Response(self.get_serializer(profile).data)
class PatientProfileView(viewsets.ModelViewSet):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PatientProfile.objects.select_related("user").filter(
            user=self.request.user
        )

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):

        if request.user.role != User.Role.PATIENT:
            return Response(
                {"detail": "Only patients can access this endpoint."},
                status=403
            )

        profile, _ = PatientProfile.objects.get_or_create(
            user=request.user
        )

        if request.method == "PATCH":
            serializer = self.get_serializer(
                profile,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return Response(self.get_serializer(profile).data)