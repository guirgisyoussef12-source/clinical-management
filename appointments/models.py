from django.db import models
from accounts.models import DoctorProfile, PatientProfile
class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED","scheduled"
        COMPLETED = "COMPLETED","completed"
        CANCELED = "CANCELED","canceled"
        NO_SHOW = "NO_SHOW", "no_show"
    doctor = models.ForeignKey(DoctorProfile,on_delete=models.CASCADE,related_name="doctor_appointments")
    patient = models.ForeignKey(PatientProfile,on_delete=models.CASCADE, related_name="patient_appointments")
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=15 , choices=Status.choices,default=Status.SCHEDULED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=["doctor", "appointment_date", "appointment_time"],
            name="unique_doctor_appointment"
        )
    ]