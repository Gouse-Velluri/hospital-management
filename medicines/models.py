from django.db import models
from django.utils import timezone
from datetime import timedelta
from patients.models import Patient
from doctors.models import Doctor
import random
import string


class Medicine(models.Model):
    TYPE_CHOICES = [
        ('Tablet', 'Tablet'),
        ('Capsule', 'Capsule'),
        ('Syrup', 'Syrup'),
        ('Injection', 'Injection'),
        ('Ointment', 'Ointment'),
        ('Drops', 'Drops'),
        ('Inhaler', 'Inhaler'),
    ]

    CATEGORY_CHOICES = [
        ('General', 'General'),
        ('Dental', 'Dental'),
        ('Cardiology', 'Cardiology'),
        ('Ophthalmology', 'Ophthalmology'),
        ('Dermatology', 'Dermatology'),
        ('Orthopedics', 'Orthopedics'),
        ('Pediatrics', 'Pediatrics'),
        ('Neurology', 'Neurology'),
        ('ENT', 'ENT'),
        ('Psychiatry', 'Psychiatry'),
    ]

    name = models.CharField(max_length=100)
    med_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type")
    dosage = models.CharField(max_length=100, help_text="e.g., 500mg, 10ml")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='General', help_text="Medical category")
    description = models.TextField(blank=True, null=True, help_text="Brief description or usage")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.med_type}) - {self.dosage}"

    class Meta:
        ordering = ['category', 'name']


class Appointment(models.Model):
    SERVICE_CHOICES = [
        ('General Checkup', 'General Checkup'),
        ('Dental Care', 'Dental Care'),
        ('Cardiology Consultation', 'Cardiology Consultation'),
        ('Eye Examination', 'Eye Examination'),
        ('Skin Treatment', 'Skin Treatment'),
        ('Orthopedic Consultation', 'Orthopedic Consultation'),
        ('Pediatric Care', 'Pediatric Care'),
        ('Neurological Assessment', 'Neurological Assessment'),
        ('ENT Consultation', 'ENT Consultation'),
        ('Mental Health Counseling', 'Mental Health Counseling'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    suggested_medicines = models.ManyToManyField(Medicine, blank=True, related_name='appointments')
    created_at = models.DateTimeField(auto_now_add=True)

    SERVICE_TO_CATEGORY = {
        'General Checkup': 'General',
        'Dental Care': 'Dental',
        'Cardiology Consultation': 'Cardiology',
        'Eye Examination': 'Ophthalmology',
        'Skin Treatment': 'Dermatology',
        'Orthopedic Consultation': 'Orthopedics',
        'Pediatric Care': 'Pediatrics',
        'Neurological Assessment': 'Neurology',
        'ENT Consultation': 'ENT',
        'Mental Health Counseling': 'Psychiatry',
    }

    def get_relevant_category(self):
        return self.SERVICE_TO_CATEGORY.get(self.service, 'General')

    def __str__(self):
        return f"{self.patient.name} → Dr. {self.doctor.name} ({self.service})"

    class Meta:
        ordering = ['-date', '-time']


class Prescription(models.Model):
    """Stores dosage instructions for each medicine prescribed in an appointment."""
    FREQUENCY_CHOICES = [
        ('Once daily', 'Once daily'),
        ('Twice daily', 'Twice daily (Morning & Night)'),
        ('Three times daily', 'Three times daily'),
        ('Four times daily', 'Every 6 hours'),
        ('Every 8 hours', 'Every 8 hours'),
        ('Before meals', 'Before meals'),
        ('After meals', 'After meals'),
        ('At bedtime', 'At bedtime only'),
        ('As needed', 'As needed (SOS)'),
        ('Once weekly', 'Once weekly'),
    ]

    DURATION_CHOICES = [
        ('3 days', '3 days'),
        ('5 days', '5 days'),
        ('7 days', '1 week'),
        ('10 days', '10 days'),
        ('14 days', '2 weeks'),
        ('21 days', '3 weeks'),
        ('30 days', '1 month'),
        ('60 days', '2 months'),
        ('90 days', '3 months'),
        ('Ongoing', 'Ongoing'),
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='prescriptions')
    frequency = models.CharField(max_length=30, choices=FREQUENCY_CHOICES, default='Twice daily')
    duration = models.CharField(max_length=30, choices=DURATION_CHOICES, default='5 days')
    instructions = models.CharField(max_length=200, blank=True, null=True, help_text="e.g., Take with water")
    prescribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('appointment', 'medicine')
        ordering = ['medicine__name']

    def __str__(self):
        return f"{self.medicine.name} → {self.frequency} for {self.duration}"


class ConfirmationCode(models.Model):
    """Stores OTP codes for appointment cancellation confirmation."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='confirmation_codes')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='confirmation_codes')
    code = models.CharField(max_length=6, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.digits, k=6))
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP for {self.appointment.id} - {self.patient.name}"

    class Meta:
        ordering = ['-created_at']
