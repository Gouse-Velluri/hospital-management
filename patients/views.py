from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Patient
from .forms import PatientRegistrationForm, PatientLoginForm
from doctors.models import Doctor
from medicines.models import Appointment


def register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.password = make_password(form.cleaned_data['password'])
            patient.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('patient_login')
    else:
        form = PatientRegistrationForm()
    return render(request, 'patients/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = PatientLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                patient = Patient.objects.get(email=email)
                if check_password(password, patient.password):
                    request.session['patient_id'] = patient.id
                    request.session['patient_name'] = patient.name
                    request.session['user_type'] = 'patient'
                    messages.success(request, f'Welcome back, {patient.name}!')
                    return redirect('patient_dashboard')
                else:
                    messages.error(request, 'Invalid email or password.')
            except Patient.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = PatientLoginForm()
    return render(request, 'patients/login.html', {'form': form})


def dashboard(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        messages.warning(request, 'Please login first.')
        return redirect('patient_login')

    patient = Patient.objects.get(id=patient_id)
    doctors = Doctor.objects.all()
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor').prefetch_related('prescriptions__medicine')
    service_choices = Appointment.SERVICE_CHOICES

    context = {
        'patient': patient,
        'doctors': doctors,
        'appointments': appointments,
        'service_choices': service_choices,
    }
    return render(request, 'patients/dashboard.html', context)


def book_appointment(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        service = request.POST.get('service')
        date = request.POST.get('date')
        time = request.POST.get('time')
        notes = request.POST.get('notes', '')

        try:
            doctor = Doctor.objects.get(id=doctor_id)
            patient = Patient.objects.get(id=patient_id)
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                service=service,
                date=date,
                time=time,
                notes=notes,
            )
            messages.success(request, 'Appointment booked successfully!')
        except Exception as e:
            messages.error(request, f'Error booking appointment: {str(e)}')

    return redirect('patient_dashboard')


def update_appointment(request, appointment_id):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')

    appointment = get_object_or_404(Appointment, id=appointment_id, patient_id=patient_id)

    if request.method == 'POST':
        appointment.doctor_id = request.POST.get('doctor')
        appointment.service = request.POST.get('service')
        appointment.date = request.POST.get('date')
        appointment.time = request.POST.get('time')
        appointment.notes = request.POST.get('notes', '')
        appointment.save()
        messages.success(request, 'Appointment updated successfully!')

    return redirect('patient_dashboard')


def delete_appointment(request, appointment_id):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')

    appointment = get_object_or_404(Appointment, id=appointment_id, patient_id=patient_id)
    appointment.delete()
    messages.success(request, 'Appointment deleted successfully!')
    return redirect('patient_dashboard')


def update_profile(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')

    patient = Patient.objects.get(id=patient_id)

    if request.method == 'POST':
        patient.name = request.POST.get('name', patient.name)
        patient.phone = request.POST.get('phone', patient.phone)
        patient.save()
        request.session['patient_name'] = patient.name
        messages.success(request, 'Profile updated successfully!')

    return redirect('patient_dashboard')


def delete_account(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')

    patient = Patient.objects.get(id=patient_id)
    patient.delete()
    request.session.flush()
    messages.success(request, 'Your account has been deleted.')
    return redirect('patient_login')


def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('patient_login')
