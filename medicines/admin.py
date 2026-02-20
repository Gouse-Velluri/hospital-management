from django.contrib import admin
from .models import Medicine, Appointment

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'med_type', 'dosage', 'created_at')
    search_fields = ('name',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'service', 'date', 'time', 'status')
    list_filter = ('status', 'service', 'date')
    search_fields = ('patient__name', 'doctor__name')
