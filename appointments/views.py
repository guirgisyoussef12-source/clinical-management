from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from accounts.models import PatientProfile
from .models import Appointment
from .serializers import AppointmentSerializer

User = get_user_model()


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == User.Role.DOCTOR:
            return Appointment.objects.select_related(
                'doctor__user', 'patient__user'
            ).filter(doctor__user=user)

        if user.role == User.Role.PATIENT:
            return Appointment.objects.select_related(
                'doctor__user', 'patient__user'
            ).filter(patient__user=user)

        # Receptionist / admin sees all
        return Appointment.objects.select_related('doctor__user', 'patient__user').all()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == User.Role.PATIENT:
            try:
                patient_profile = PatientProfile.objects.get(user=user)
            except PatientProfile.DoesNotExist:
                from rest_framework.exceptions import ValidationError
                raise ValidationError(
                    {"detail": "You must complete your patient profile before booking an appointment."}
                )
            serializer.save(patient=patient_profile)
        else:
            serializer.save()

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Allows a doctor or receptionist to change appointment status."""
        # Check permission before hitting the DB
        if request.user.role == User.Role.PATIENT:
            return Response(
                {'detail': 'Patients cannot change appointment status.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        appointment = self.get_object()
        new_status = request.data.get('status')

        if new_status not in Appointment.Status.values:
            return Response(
                {'detail': f'Invalid status. Choices: {Appointment.Status.values}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = new_status
        appointment.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(appointment).data)