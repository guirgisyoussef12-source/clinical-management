from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["id", "doctor", "patient", "appointment_date", "appointment_time", "status"]
    list_filter = ["status", "appointment_date"]
    search_fields = ["doctor__user__username", "patient__user__username"]