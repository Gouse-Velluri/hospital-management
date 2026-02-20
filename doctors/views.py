from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from .models import Doctor
from .forms import DoctorRegistrationForm, DoctorLoginForm
from medicines.models import Appointment, Medicine, Prescription


def register(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.password = make_password(form.cleaned_data['password'])
            doctor.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('doctor_login')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'doctors/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                doctor = Doctor.objects.get(email=email)
                if check_password(password, doctor.password):
                    request.session['doctor_id'] = doctor.id
                    request.session['doctor_name'] = doctor.name
                    request.session['user_type'] = 'doctor'
                    messages.success(request, f'Welcome back, Dr. {doctor.name}!')
                    return redirect('doctor_dashboard')
                else:
                    messages.error(request, 'Invalid email or password.')
            except Doctor.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = DoctorLoginForm()
    return render(request, 'doctors/login.html', {'form': form})


def dashboard(request):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        messages.warning(request, 'Please login first.')
        return redirect('doctor_login')

    doctor = Doctor.objects.get(id=doctor_id)
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient').prefetch_related('suggested_medicines', 'prescriptions__medicine')

    # Attach relevant medicines to each appointment based on service category
    for apt in appointments:
        category = apt.get_relevant_category()
        apt.relevant_medicines = Medicine.objects.filter(category=category)

    context = {
        'doctor': doctor,
        'appointments': appointments,
        'frequency_choices': Prescription.FREQUENCY_CHOICES,
        'duration_choices': Prescription.DURATION_CHOICES,
    }
    return render(request, 'doctors/dashboard.html', context)


def add_medicines(request, appointment_id):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login')

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor_id=doctor_id)

    if request.method == 'POST':
        medicine_ids = request.POST.getlist('medicines')
        # Clear old prescriptions for this appointment
        Prescription.objects.filter(appointment=appointment).delete()
        appointment.suggested_medicines.clear()

        for med_id in medicine_ids:
            medicine = Medicine.objects.get(id=med_id)
            frequency = request.POST.get(f'frequency_{med_id}', 'Twice daily')
            duration = request.POST.get(f'duration_{med_id}', '5 days')
            instructions = request.POST.get(f'instructions_{med_id}', '')

            # Create prescription with dosage details
            Prescription.objects.create(
                appointment=appointment,
                medicine=medicine,
                frequency=frequency,
                duration=duration,
                instructions=instructions,
            )
            appointment.suggested_medicines.add(medicine)

        appointment.status = 'Completed'
        appointment.save()
        messages.success(request, f'Medicines prescribed for {appointment.patient.name}!')

    return redirect('doctor_dashboard')


def approve_appointment(request, appointment_id):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login')

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor_id=doctor_id)
    appointment.status = 'Approved'
    appointment.save()
    messages.success(request, f'Appointment for {appointment.patient.name} approved!')
    return redirect('doctor_dashboard')


def reject_appointment(request, appointment_id):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login')

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor_id=doctor_id)
    appointment.status = 'Cancelled'
    appointment.save()
    messages.warning(request, f'Appointment for {appointment.patient.name} rejected.')
    return redirect('doctor_dashboard')


def delete_appointment(request, appointment_id):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login')

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor_id=doctor_id)
    appointment.delete()
    messages.success(request, 'Appointment deleted successfully!')
    return redirect('doctor_dashboard')


def update_profile(request):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login')

    doctor = Doctor.objects.get(id=doctor_id)

    if request.method == 'POST':
        doctor.name = request.POST.get('name', doctor.name)
        doctor.specialization = request.POST.get('specialization', doctor.specialization)
        doctor.experience = request.POST.get('experience', doctor.experience)
        doctor.save()
        request.session['doctor_name'] = doctor.name
        messages.success(request, 'Profile updated successfully!')

    return redirect('doctor_dashboard')


def delete_account(request):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login')

    doctor = Doctor.objects.get(id=doctor_id)
    doctor.delete()
    request.session.flush()
    messages.success(request, 'Your account has been deleted.')
    return redirect('doctor_login')


def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('doctor_login')
