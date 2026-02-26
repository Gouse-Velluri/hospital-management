from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Patient
from .forms import PatientRegistrationForm, PatientLoginForm
from doctors.models import Doctor
from medicines.models import Appointment
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import secrets
import string


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
        doctor_id = request.POST.get('doctor_id')
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


def cancel_appointment(request, appointment_id):
    """Directly cancel an appointment without OTP verification."""
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')

    appointment = get_object_or_404(Appointment, id=appointment_id, patient_id=patient_id)

    if appointment.status == 'Cancelled':
        messages.info(request, 'This appointment is already cancelled.')
        return redirect('patient_dashboard')

    if request.method == 'POST':
        appointment.status = 'Cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully!')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('patient_dashboard')


def delete_appointment(request, appointment_id):
    """Delete an appointment permanently."""
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')

    appointment = get_object_or_404(Appointment, id=appointment_id, patient_id=patient_id)
    patient_name = appointment.patient.name

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


def forgot_password(request):
    """Handle forgot password page and AJAX requests."""
    if request.method == 'GET':
        # Display the forgot password form
        return render(request, 'patients/forgot_password.html')

    elif request.method == 'POST':
        # Handle AJAX POST request
        email = request.POST.get('email', '').strip()

        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)

        try:
            patient = Patient.objects.get(email=email)
            # Generate a unique reset token
            reset_token = secrets.token_urlsafe(32)

            # Store token in session with email (in production, use a database model)
            request.session[f'reset_token_{email}'] = reset_token
            request.session[f'reset_token_time_{email}'] = str(__import__('datetime').datetime.now())

            # In a real application, send email with reset link
            # For now, we'll return the token and URL for testing
            reset_url = request.build_absolute_uri(f'/patient/reset-password/?token={reset_token}&email={email}')

            return JsonResponse({
                'status': 'success',
                'message': f'Password reset link has been sent to {email}',
                'reset_url': reset_url  # For demo purposes
            })

        except Patient.DoesNotExist:
            # Don't reveal if email exists (security best practice)
            return JsonResponse({
                'status': 'success',
                'message': 'If an account exists with this email, you will receive a password reset link'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def reset_password(request):
    """Handle password reset page and submission."""
    if request.method == 'GET':
        token = request.GET.get('token', '')
        email = request.GET.get('email', '')

        return render(request, 'patients/reset_password.html', {
            'token': token,
            'email': email
        })

    elif request.method == 'POST':
        token = request.POST.get('token', '').strip()
        email = request.POST.get('email', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # Validate passwords match
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect(f'/patient/reset-password/?token={token}&email={email}')

        # Validate password strength
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long')
            return redirect(f'/patient/reset-password/?token={token}&email={email}')

        # Verify token (check session)
        stored_token = request.session.get(f'reset_token_{email}', '')

        if token != stored_token:
            messages.error(request, 'Invalid or expired reset token')
            return redirect('patient_login')

        try:
            patient = Patient.objects.get(email=email)
            patient.password = make_password(new_password)
            patient.save()

            # Clear reset token from session
            request.session.pop(f'reset_token_{email}', None)
            request.session.pop(f'reset_token_time_{email}', None)

            messages.success(request, 'Your password has been reset successfully! Please login with your new password.')
            return redirect('patient_login')

        except Patient.DoesNotExist:
            messages.error(request, 'Patient not found')
            return redirect('patient_login')
