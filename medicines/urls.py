from django.urls import path
from . import views

urlpatterns = [
    path('', views.medicine_list, name='medicine_list'),
    path('add/', views.add_medicine, name='add_medicine'),
    path('update/<int:medicine_id>/', views.update_medicine, name='update_medicine'),
    path('delete/<int:medicine_id>/', views.delete_medicine, name='delete_medicine'),
]
