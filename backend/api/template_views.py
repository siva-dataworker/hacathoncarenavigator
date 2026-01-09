from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Clinic, Appointment, ChatSession

def index(request):
    """Landing page"""
    return render(request, 'index.html')

def assistant(request):
    """General chat assistant page"""
    return render(request, 'assistant.html')

def clinics_list(request):
    """List all clinics"""
    clinics = Clinic.objects.all()
    return render(request, 'clinics_list.html', {'clinics': clinics})

def clinic_detail(request, clinic_id):
    """Clinic-specific landing page"""
    clinic = get_object_or_404(Clinic, id=clinic_id)
    return render(request, 'clinic_detail.html', {'clinic': clinic})

def clinic_chat(request, clinic_id):
    """Clinic-specific chat interface"""
    clinic = get_object_or_404(Clinic, id=clinic_id)
    return render(request, 'clinic_chat.html', {'clinic': clinic})

def booking(request):
    """Booking page"""
    clinics = Clinic.objects.all()
    selected_clinic_id = request.GET.get('clinic')
    if selected_clinic_id:
        selected_clinic_id = int(selected_clinic_id)
    return render(request, 'booking.html', {
        'clinics': clinics,
        'selected_clinic_id': selected_clinic_id
    })

def dashboard(request):
    """Clinic dashboard (demo)"""
    # For demo, show all appointments
    appointments = Appointment.objects.all().order_by('-created_at')[:50]
    clinics = Clinic.objects.all()
    return render(request, 'dashboard.html', {
        'appointments': appointments,
        'clinics': clinics
    })
