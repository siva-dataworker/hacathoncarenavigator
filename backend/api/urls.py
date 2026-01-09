from django.urls import path
from . import views

urlpatterns = [
    # Chat API endpoints
    path('chat/start', views.start_chat, name='start_chat'),
    path('chat/continue', views.send_message, name='send_message'),
    
    # Clinic endpoints
    path('clinics', views.list_clinics, name='list_clinics'),
    path('clinics/<int:clinic_id>/', views.get_clinic_by_id, name='get_clinic_by_id'),
    
    # Booking endpoints
    path('book-appointment', views.book_appointment, name='book_appointment'),
    path('clinic/<int:clinic_id>/bookings', views.get_clinic_bookings, name='get_clinic_bookings'),
]
