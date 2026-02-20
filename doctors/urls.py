from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='doctor_register'),
    path('login/', views.login_view, name='doctor_login'),
    path('dashboard/', views.dashboard, name='doctor_dashboard'),
    path('add-medicines/<int:appointment_id>/', views.add_medicines, name='add_medicines'),
    path('approve/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('reject/<int:appointment_id>/', views.reject_appointment, name='reject_appointment'),
    path('delete-appointment/<int:appointment_id>/', views.delete_appointment, name='doctor_delete_appointment'),
    path('update-profile/', views.update_profile, name='doctor_update_profile'),
    path('delete-account/', views.delete_account, name='doctor_delete_account'),
    path('logout/', views.logout_view, name='doctor_logout'),
]
