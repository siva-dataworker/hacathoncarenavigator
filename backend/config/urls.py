from django.contrib import admin
from django.urls import path, include
from api import template_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Template views
    path('', template_views.index, name='index'),
    path('clinics/', template_views.clinics_list, name='clinics_list'),
    path('clinic/<int:clinic_id>/', template_views.clinic_detail, name='clinic_detail'),
    path('clinic/<int:clinic_id>/chat', template_views.clinic_chat, name='clinic_chat'),
    path('booking', template_views.booking, name='booking'),
    path('dashboard/', template_views.dashboard, name='dashboard'),
]
