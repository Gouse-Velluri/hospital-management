from django.db import models


class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('General Medicine', 'General Medicine'),
        ('Cardiology', 'Cardiology'),
        ('Dermatology', 'Dermatology'),
        ('Orthopedics', 'Orthopedics'),
        ('Pediatrics', 'Pediatrics'),
        ('Neurology', 'Neurology'),
        ('Ophthalmology', 'Ophthalmology'),
        ('ENT', 'ENT'),
        ('Dentistry', 'Dentistry'),
        ('Psychiatry', 'Psychiatry'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    experience = models.PositiveIntegerField(help_text="Years of experience")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.name} ({self.specialization})"
