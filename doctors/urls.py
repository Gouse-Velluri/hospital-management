from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='doctor_register'),
    path('login/', views.login_view, name='doctor_login'),
    path('forgot-password/', views.forgot_password, name='doctor_forgot_password'),
    path('reset-password/', views.reset_password, name='doctor_reset_password'),
    path('dashboard/', views.dashboard, name='doctor_dashboard'),
    path('add-medicines/<int:appointment_id>/', views.add_medicines, name='add_medicines'),
    path('approve/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('complete/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    path('reject/<int:appointment_id>/', views.reject_appointment, name='reject_appointment'),
    path('delete-appointment/<int:appointment_id>/', views.delete_appointment, name='doctor_delete_appointment'),
    path('update-profile/', views.update_profile, name='doctor_update_profile'),
    path('delete-account/', views.delete_account, name='doctor_delete_account'),
    path('logout/', views.logout_view, name='doctor_logout'),
    # AJAX Endpoints
    path('ajax/approve-appointment/', views.ajax_approve_appointment, name='ajax_approve_appointment'),
    path('ajax/complete-appointment/', views.ajax_complete_appointment, name='ajax_complete_appointment'),
    path('ajax/reject-appointment/', views.ajax_reject_appointment, name='ajax_reject_appointment'),
    path('ajax/get-appointments/', views.ajax_get_appointments, name='ajax_get_appointments'),
    path('ajax/get-statistics/', views.ajax_get_statistics, name='ajax_get_statistics'),
]
