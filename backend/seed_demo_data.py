#!/usr/bin/env python
"""
Demo Seed Data Script for Care Navigator Application

This script creates comprehensive demo data including:
- 2 Clinics with detailed information
- 2 Doctors per clinic (as metadata)
- Sample appointments with various statuses
- Time slot information (as reference data)

Usage:
    python seed_demo_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Clinic, Appointment, ChatSession
from django.utils import timezone


def clear_existing_data():
    """Clear existing demo data"""
    print("🗑️  Clearing existing data...")
    Appointment.objects.all().delete()
    ChatSession.objects.all().delete()
    Clinic.objects.all().delete()
    print("✅ Existing data cleared")


def create_clinics():
    """Create demo clinics with detailed information"""
    print("\n🏥 Creating clinics...")
    
    clinics_data = [
        {
            'id': 4,  # Fixed ID for consistency
            'name': 'Apollo Health Center - Anna Nagar',
            'address': 'No. 45, 2nd Avenue, Anna Nagar West, Chennai - 600040, Tamil Nadu',
            'unique_code': 'apollo-anna-nagar',
            'phone': '+91 44 2626 2626',
            'email': 'apollo.annanagar@apollohospitals.com',
            'timings': 'Mon-Sat: 9:00 AM - 8:00 PM, Sun: 9:00 AM - 2:00 PM',
            'specialties': ['General Medicine', 'Family Medicine', 'Pediatrics', 'Cardiology'],
            'facilities': ['24/7 Pharmacy', 'Diagnostic Lab', 'X-Ray', 'ECG', 'Ambulance Service'],
            'doctors': [
                {
                    'name': 'Dr. Ramesh Kumar',
                    'specialization': 'General Physician',
                    'experience': '15 years',
                    'qualification': 'MBBS, MD (Internal Medicine)',
                    'available_slots': ['09:00 AM', '02:00 PM', '05:00 PM'],
                    'languages': ['English', 'Tamil', 'Hindi']
                },
                {
                    'name': 'Dr. Priya Menon',
                    'specialization': 'Family Medicine',
                    'experience': '12 years',
                    'qualification': 'MBBS, DNB (Family Medicine)',
                    'available_slots': ['10:00 AM', '03:00 PM', '06:00 PM'],
                    'languages': ['English', 'Tamil', 'Malayalam']
                }
            ],
            'about': 'Apollo Health Center in Anna Nagar is a multi-specialty clinic offering comprehensive healthcare services. With experienced doctors and modern facilities, we provide quality medical care to the community.',
            'insurance_accepted': ['Star Health', 'ICICI Lombard', 'HDFC Ergo', 'New India Assurance']
        },
        {
            'id': 5,  # Fixed ID for consistency
            'name': 'Fortis Malar Hospital - Adyar',
            'address': 'No. 52, Gandhi Nagar, 1st Main Road, Adyar, Chennai - 600020, Tamil Nadu',
            'unique_code': 'fortis-adyar',
            'phone': '+91 44 4289 2222',
            'email': 'info.malar@fortishealthcare.com',
            'timings': 'Mon-Sun: 8:00 AM - 10:00 PM (24/7 Emergency)',
            'specialties': ['General Medicine', 'Internal Medicine', 'Cardiology', 'Orthopedics', 'Emergency Care'],
            'facilities': ['24/7 Emergency', 'ICU', 'Diagnostic Lab', 'CT Scan', 'MRI', 'Ambulance Service', 'Blood Bank'],
            'doctors': [
                {
                    'name': 'Dr. Suresh Babu',
                    'specialization': 'General Physician',
                    'experience': '18 years',
                    'qualification': 'MBBS, MD (General Medicine)',
                    'available_slots': ['09:30 AM', '02:30 PM', '06:30 PM'],
                    'languages': ['English', 'Tamil', 'Telugu']
                },
                {
                    'name': 'Dr. Anjali Reddy',
                    'specialization': 'Internal Medicine',
                    'experience': '10 years',
                    'qualification': 'MBBS, MD (Internal Medicine), MRCP',
                    'available_slots': ['11:00 AM', '04:00 PM', '07:00 PM'],
                    'languages': ['English', 'Tamil', 'Telugu', 'Hindi']
                }
            ],
            'about': 'Fortis Malar Hospital in Adyar is a leading multi-specialty hospital with state-of-the-art facilities and 24/7 emergency services. Our team of expert doctors provides world-class healthcare.',
            'insurance_accepted': ['Star Health', 'ICICI Lombard', 'HDFC Ergo', 'Max Bupa', 'Religare', 'United India Insurance']
        }
    ]
    
    clinics = []
    for clinic_data in clinics_data:
        # Remove fields that aren't in the model
        clinic_id = clinic_data.pop('id')
        phone = clinic_data.pop('phone')
        email = clinic_data.pop('email')
        timings = clinic_data.pop('timings')
        specialties = clinic_data.pop('specialties')
        facilities = clinic_data.pop('facilities')
        doctors = clinic_data.pop('doctors')
        about = clinic_data.pop('about')
        insurance = clinic_data.pop('insurance_accepted')
        
        clinic = Clinic.objects.create(**clinic_data)
        clinics.append(clinic)
        
        # Store additional data in a JSON file for frontend use
        clinic_details = {
            'id': clinic.id,
            'name': clinic.name,
            'address': clinic.address,
            'unique_code': clinic.unique_code,
            'phone': phone,
            'email': email,
            'timings': timings,
            'specialties': specialties,
            'facilities': facilities,
            'doctors': doctors,
            'about': about,
            'insurance_accepted': insurance
        }
        
        print(f"\n✅ Created: {clinic.name} (ID: {clinic.id})")
        print(f"   📍 Address: {clinic.address}")
        print(f"   📞 Phone: {phone}")
        print(f"   📧 Email: {email}")
        print(f"   🕐 Timings: {timings}")
        print(f"   🏥 Specialties: {', '.join(specialties)}")
        print(f"   👨‍⚕️ Doctors:")
        
        for doctor in doctors:
            print(f"      • {doctor['name']} - {doctor['specialization']}")
            print(f"        {doctor['qualification']} | {doctor['experience']} experience")
            print(f"        Languages: {', '.join(doctor['languages'])}")
            print(f"        Available: {', '.join(doctor['available_slots'])}")
    
    return clinics


def create_appointments(clinics):
    """Create sample appointments"""
    print("\n📅 Creating sample appointments...")
    
    # Get dates for next few days
    today = timezone.now()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)
    
    appointments_data = [
        # Apollo Anna Nagar Appointments
        {
            'clinic': clinics[0],
            'patient_name': 'Rajesh Kumar',
            'patient_phone': '9876543210',
            'symptoms_summary': 'Persistent headache for 3 days, mild fever (99.5°F), feeling tired',
            'urgency_level': 'medium',
            'preferred_time': tomorrow.replace(hour=10, minute=0, second=0, microsecond=0),
            'status': 'confirmed',
            'doctor': 'Dr. Ramesh Kumar'
        },
        {
            'clinic': clinics[0],
            'patient_name': 'Priya Sharma',
            'patient_phone': '9876543211',
            'symptoms_summary': 'Cough and cold for 5 days, throat pain, runny nose',
            'urgency_level': 'low',
            'preferred_time': tomorrow.replace(hour=14, minute=30, second=0, microsecond=0),
            'status': 'pending',
            'doctor': 'Dr. Ramesh Kumar'
        },
        {
            'clinic': clinics[0],
            'patient_name': 'Mohammed Farhan',
            'patient_phone': '9876543214',
            'symptoms_summary': 'Skin rash on arms and legs, itching, appeared 2 days ago',
            'urgency_level': 'low',
            'preferred_time': day_after.replace(hour=16, minute=0, second=0, microsecond=0),
            'status': 'pending',
            'doctor': 'Dr. Priya Menon'
        },
        {
            'clinic': clinics[0],
            'patient_name': 'Kavitha Ramesh',
            'patient_phone': '9876543215',
            'symptoms_summary': 'Joint pain in knees, difficulty walking, swelling',
            'urgency_level': 'medium',
            'preferred_time': day_after.replace(hour=10, minute=0, second=0, microsecond=0),
            'status': 'confirmed',
            'doctor': 'Dr. Priya Menon'
        },
        
        # Fortis Adyar Appointments
        {
            'clinic': clinics[1],
            'patient_name': 'Arun Venkatesh',
            'patient_phone': '9876543212',
            'symptoms_summary': 'Lower back pain after lifting heavy objects, difficulty in movement, pain radiating to legs',
            'urgency_level': 'medium',
            'preferred_time': tomorrow.replace(hour=9, minute=30, second=0, microsecond=0),
            'status': 'confirmed',
            'doctor': 'Dr. Suresh Babu'
        },
        {
            'clinic': clinics[1],
            'patient_name': 'Lakshmi Iyer',
            'patient_phone': '9876543213',
            'symptoms_summary': 'Stomach pain and nausea since morning, loss of appetite',
            'urgency_level': 'medium',
            'preferred_time': tomorrow.replace(hour=11, minute=0, second=0, microsecond=0),
            'status': 'pending',
            'doctor': 'Dr. Suresh Babu'
        },
        {
            'clinic': clinics[1],
            'patient_name': 'Vikram Singh',
            'patient_phone': '9876543216',
            'symptoms_summary': 'Persistent cough for 2 weeks, chest discomfort, shortness of breath',
            'urgency_level': 'high',
            'preferred_time': today.replace(hour=16, minute=0, second=0, microsecond=0),
            'status': 'confirmed',
            'doctor': 'Dr. Anjali Reddy'
        },
        {
            'clinic': clinics[1],
            'patient_name': 'Deepa Krishnan',
            'patient_phone': '9876543217',
            'symptoms_summary': 'Migraine headaches, sensitivity to light, occurring 3-4 times per week',
            'urgency_level': 'medium',
            'preferred_time': day_after.replace(hour=14, minute=0, second=0, microsecond=0),
            'status': 'pending',
            'doctor': 'Dr. Anjali Reddy'
        }
    ]
    
    appointments = []
    for apt_data in appointments_data:
        doctor = apt_data.pop('doctor')
        appointment = Appointment.objects.create(**apt_data)
        appointments.append(appointment)
        
        status_emoji = '✅' if appointment.status == 'confirmed' else '⏳'
        urgency_emoji = '🔴' if appointment.urgency_level == 'high' else '🟡' if appointment.urgency_level == 'medium' else '🟢'
        
        print(f"\n{status_emoji} {appointment.patient_name} - {appointment.clinic.name}")
        print(f"   {urgency_emoji} Urgency: {appointment.urgency_level.upper()}")
        print(f"   📞 Phone: {appointment.patient_phone}")
        print(f"   👨‍⚕️ Doctor: {doctor}")
        print(f"   🕐 Time: {appointment.preferred_time.strftime('%b %d, %Y at %I:%M %p')}")
        print(f"   💬 Symptoms: {appointment.symptoms_summary[:60]}...")
        print(f"   📊 Status: {appointment.status.upper()}")
    
    return appointments


def create_sample_chat_sessions():
    """Create sample chat sessions for demo"""
    print("\n💬 Creating sample chat sessions...")
    
    sessions_data = [
        {
            'messages': [
                {'role': 'assistant', 'content': 'Hi! I\'m here to help assess your symptoms. Please describe what you\'re experiencing.'},
                {'role': 'user', 'content': 'I have been having headaches for the past 3 days'},
                {'role': 'assistant', 'content': 'I understand you\'ve been experiencing headaches for 3 days. Can you tell me more about the headache? Is it constant or does it come and go?'},
                {'role': 'user', 'content': 'It comes and goes, mostly in the evening'},
                {'role': 'assistant', 'content': 'Thank you for that information. Do you have any other symptoms like fever, nausea, or sensitivity to light?'},
                {'role': 'user', 'content': 'Yes, I have a mild fever around 99 degrees'}
            ],
            'symptoms_collected': [
                'headaches for 3 days',
                'comes and goes, mostly in evening',
                'mild fever around 99 degrees'
            ],
            'triage_result': 'clinic'
        },
        {
            'messages': [
                {'role': 'assistant', 'content': 'Hi! I\'m here to help assess your symptoms. Please describe what you\'re experiencing.'},
                {'role': 'user', 'content': 'I have back pain after lifting something heavy'},
                {'role': 'assistant', 'content': 'I see you have back pain from lifting. How severe is the pain on a scale of 1-10?'},
                {'role': 'user', 'content': 'Around 6 or 7, it hurts when I move'}
            ],
            'symptoms_collected': [
                'back pain after lifting',
                'pain level 6-7',
                'hurts when moving'
            ],
            'triage_result': 'clinic'
        }
    ]
    
    sessions = []
    for session_data in sessions_data:
        session = ChatSession.objects.create(**session_data)
        sessions.append(session)
        print(f"✅ Created chat session #{session.id} - {len(session.messages)} messages")
    
    return sessions


def print_summary(clinics, appointments):
    """Print summary of created data"""
    print("\n" + "="*70)
    print("📊 DEMO DATA CREATION SUMMARY")
    print("="*70)
    
    print(f"\n🏥 Clinics Created: {len(clinics)}")
    for clinic in clinics:
        print(f"   • {clinic.name} (ID: {clinic.id})")
        print(f"     Code: {clinic.unique_code}")
        print(f"     Link: http://localhost:5173/clinic/{clinic.id}")
    
    print(f"\n📅 Appointments Created: {len(appointments)}")
    print(f"   • Confirmed: {len([a for a in appointments if a.status == 'confirmed'])}")
    print(f"   • Pending: {len([a for a in appointments if a.status == 'pending'])}")
    print(f"   • High Urgency: {len([a for a in appointments if a.urgency_level == 'high'])}")
    print(f"   • Medium Urgency: {len([a for a in appointments if a.urgency_level == 'medium'])}")
    print(f"   • Low Urgency: {len([a for a in appointments if a.urgency_level == 'low'])}")
    
    print("\n🔗 Quick Access Links:")
    print(f"   • Patient Portal: http://localhost:5173/")
    print(f"   • Clinic Dashboard: http://localhost:5173/clinic-dashboard")
    for clinic in clinics:
        print(f"   • {clinic.name}: http://localhost:5173/clinic/{clinic.id}")
    
    print("\n📋 API Endpoints to Test:")
    print(f"   • GET  http://localhost:8000/api/clinics/")
    print(f"   • GET  http://localhost:8000/api/clinics/1")
    print(f"   • GET  http://localhost:8000/api/clinic/apollo-anna-nagar/appointments/")
    print(f"   • POST http://localhost:8000/api/chat/start/")
    print(f"   • POST http://localhost:8000/api/booking/")
    
    print("\n" + "="*70)
    print("✅ Demo data created successfully!")
    print("="*70 + "\n")


def main():
    """Main function to run the seed script"""
    print("\n" + "="*70)
    print("🌱 CARE NAVIGATOR - DEMO DATA SEEDER")
    print("="*70)
    
    try:
        # Clear existing data
        clear_existing_data()
        
        # Create clinics
        clinics = create_clinics()
        
        # Create appointments
        appointments = create_appointments(clinics)
        
        # Create sample chat sessions
        create_sample_chat_sessions()
        
        # Print summary
        print_summary(clinics, appointments)
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
