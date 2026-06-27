from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import DoctorProfile, PatientProfile
from accounts.serializers import DoctorProfileSerializer, PatientProfileSerializer
from .models import Appointment

User = get_user_model()


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileSerializer(read_only=True)
    patient = PatientProfileSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.all(),
        source='doctor',
        write_only=True,
    )
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=PatientProfile.objects.all(),
        source='patient',
        write_only=True,
    )

    class Meta:
        model = Appointment
        fields = [
            'id',
            'doctor',
            'doctor_id',
            'patient',
            'patient_id',
            'appointment_date',
            'appointment_time',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        doctor = attrs.get('doctor')
        appointment_date = attrs.get('appointment_date')
        appointment_time = attrs.get('appointment_time')

        qs = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                'This doctor already has an appointment scheduled at that date and time.'
            )
        return attrs