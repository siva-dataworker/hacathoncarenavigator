from django.contrib import admin
from .models import Clinic, ChatSession, Appointment

@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ['name', 'unique_code', 'address']

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'triage_result', 'created_at']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'clinic', 'urgency_level', 'status', 'created_at']
    list_filter = ['status', 'urgency_level', 'clinic']
