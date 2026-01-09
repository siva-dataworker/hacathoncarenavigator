from django.db import models
from django.utils import timezone

class Clinic(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    unique_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class ChatSession(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    messages = models.JSONField(default=list)
    symptoms_collected = models.JSONField(default=list)
    triage_state = models.JSONField(default=dict)  # Stores trigger_detected, followup_count, responses
    triage_result = models.CharField(
        max_length=20,
        choices=[('emergency', 'Emergency'), ('clinic', 'Clinic'), ('pending', 'Pending')],
        default='pending'
    )

    def __str__(self):
        return f"Session {self.id} - {self.triage_result}"

class Appointment(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='appointments')
    patient_name = models.CharField(max_length=200)
    patient_phone = models.CharField(max_length=20)
    symptoms_summary = models.TextField()
    urgency_level = models.CharField(
        max_length=20,
        choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')],
        default='medium'
    )
    preferred_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        default='pending'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient_name} - {self.clinic.name}"
