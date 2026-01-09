from rest_framework import serializers
from .models import Clinic, ChatSession, Appointment

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = ['id', 'name', 'address', 'unique_code']

class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'messages', 'symptoms_collected', 'triage_result', 'created_at']

class AppointmentSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'clinic', 'clinic_name', 'patient_name', 'patient_phone', 
                  'symptoms_summary', 'urgency_level', 'preferred_time', 'created_at', 'status']
        read_only_fields = ['created_at']
