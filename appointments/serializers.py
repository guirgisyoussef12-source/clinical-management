from rest_framework import serializers
from .models import Appointment
User = get_user_model()
class AppointmentSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)
    class Meta:
        model = patient
        