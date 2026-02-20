from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='patient_register'),
    path('login/', views.login_view, name='patient_login'),
    path('dashboard/', views.dashboard, name='patient_dashboard'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('update-appointment/<int:appointment_id>/', views.update_appointment, name='update_appointment'),
    path('delete-appointment/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('update-profile/', views.update_profile, name='patient_update_profile'),
    path('delete-account/', views.delete_account, name='patient_delete_account'),
    path('logout/', views.logout_view, name='patient_logout'),
]
