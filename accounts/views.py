from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model

from .models import DoctorProfile, PatientProfile
from .serializers import (
    RegisterSerializer,
    DoctorProfileSerializer,
    PatientProfileSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class DoctorProfileView(viewsets.GenericViewSet):
    """
    Only exposes /me/ — doctors manage their own profile only.
    """
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        if request.user.role != User.Role.DOCTOR:
            return Response(
                {"detail": "Only doctors can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN,
            )

        profile = DoctorProfile.objects.select_related("user").filter(user=request.user).first()

        if request.method == "PATCH":
            if profile is None:
                # Create on first PATCH only if all required fields are provided
                serializer = self.get_serializer(data=request.data)
            else:
                serializer = self.get_serializer(profile, data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # GET
        if profile is None:
            return Response(
                {"detail": "Profile not set up yet. Send a PATCH request to create it."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(self.get_serializer(profile).data)


class PatientProfileView(viewsets.GenericViewSet):
    """
    Only exposes /me/ — patients manage their own profile only.
    """
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        if request.user.role != User.Role.PATIENT:
            return Response(
                {"detail": "Only patients can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN,
            )

        profile = PatientProfile.objects.select_related("user").filter(user=request.user).first()

        if request.method == "PATCH":
            if profile is None:
                serializer = self.get_serializer(data=request.data)
            else:
                serializer = self.get_serializer(profile, data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # GET
        if profile is None:
            return Response(
                {"detail": "Profile not set up yet. Send a PATCH request to create it."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(self.get_serializer(profile).data)