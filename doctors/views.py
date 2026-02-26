from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from .models import Doctor
from .forms import DoctorRegistrationForm, DoctorLoginForm
from medicines.models import Appointment, Medicine, Prescription
from django.views.decorators.http import require_http_methods
import secrets


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


def complete_appointment(request, appointment_id):
    """Mark appointment as completed without medicine prescription."""
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login')

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor_id=doctor_id)
    appointment.status = 'Completed'
    appointment.save()
    messages.success(request, f'Appointment for {appointment.patient.name} marked as completed!')
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


def forgot_password(request):
    """Handle forgot password page and AJAX requests for doctors."""
    if request.method == 'GET':
        # Display the forgot password form
        return render(request, 'doctors/forgot_password.html')

    elif request.method == 'POST':
        # Handle AJAX POST request
        email = request.POST.get('email', '').strip()

        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)

        try:
            doctor = Doctor.objects.get(email=email)
            reset_token = secrets.token_urlsafe(32)

            request.session[f'reset_token_{email}'] = reset_token
            request.session[f'reset_token_time_{email}'] = str(__import__('datetime').datetime.now())

            reset_url = request.build_absolute_uri(f'/doctor/reset-password/?token={reset_token}&email={email}')

            return JsonResponse({
                'status': 'success',
                'message': f'Password reset link has been sent to {email}',
                'reset_url': reset_url
            })

        except Doctor.DoesNotExist:
            return JsonResponse({
                'status': 'success',
                'message': 'If an account exists with this email, you will receive a password reset link'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def reset_password(request):
    """Handle password reset page and submission for doctors."""
    if request.method == 'GET':
        token = request.GET.get('token', '')
        email = request.GET.get('email', '')

        return render(request, 'doctors/reset_password.html', {
            'token': token,
            'email': email
        })

    elif request.method == 'POST':
        token = request.POST.get('token', '').strip()
        email = request.POST.get('email', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect(f'/doctor/reset-password/?token={token}&email={email}')

        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long')
            return redirect(f'/doctor/reset-password/?token={token}&email={email}')

        stored_token = request.session.get(f'reset_token_{email}', '')

        if token != stored_token:
            messages.error(request, 'Invalid or expired reset token')
            return redirect('doctor_login')

        try:
            doctor = Doctor.objects.get(email=email)
            doctor.password = make_password(new_password)
            doctor.save()

            request.session.pop(f'reset_token_{email}', None)
            request.session.pop(f'reset_token_time_{email}', None)

            messages.success(request, 'Your password has been reset successfully! Please login with your new password.')
            return redirect('doctor_login')

        except Doctor.DoesNotExist:
            messages.error(request, 'Doctor not found')
            return redirect('doctor_login')


# === AJAX ENDPOINTS FOR REAL-TIME DATA PROCESSING ===

@require_http_methods(["POST"])
def ajax_approve_appointment(request):
    """AJAX endpoint to approve an appointment in real-time."""
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    appointment_id = request.POST.get('appointment_id')

    try:
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor_id=doctor_id)
        appointment.status = 'Approved'
        appointment.save()

        return JsonResponse({
            'status': 'success',
            'message': f'Appointment for {appointment.patient.name} approved!',
            'appointment_id': appointment_id,
            'new_status': 'Approved'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["POST"])
def ajax_complete_appointment(request):
    """AJAX endpoint to complete an appointment without medicines."""
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    appointment_id = request.POST.get('appointment_id')

    try:
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor_id=doctor_id)
        appointment.status = 'Completed'
        appointment.save()

        return JsonResponse({
            'status': 'success',
            'message': f'Appointment for {appointment.patient.name} marked as completed!',
            'appointment_id': appointment_id,
            'new_status': 'Completed'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["POST"])
def ajax_reject_appointment(request):
    """AJAX endpoint to reject/cancel an appointment."""
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    appointment_id = request.POST.get('appointment_id')

    try:
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor_id=doctor_id)
        appointment.status = 'Cancelled'
        appointment.save()

        return JsonResponse({
            'status': 'success',
            'message': f'Appointment for {appointment.patient.name} rejected.',
            'appointment_id': appointment_id,
            'new_status': 'Cancelled'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def ajax_get_appointments(request):
    """AJAX endpoint to get all appointments with real-time data."""
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    try:
        appointments = Appointment.objects.filter(doctor_id=doctor_id).select_related('patient').prefetch_related('prescriptions__medicine')

        appointments_data = []
        for apt in appointments:
            prescriptions = []
            for rx in apt.prescriptions.all():
                prescriptions.append({
                    'medicine': rx.medicine.name,
                    'frequency': rx.frequency,
                    'duration': rx.duration,
                    'dosage': rx.medicine.dosage
                })

            appointments_data.append({
                'id': apt.id,
                'patient_name': apt.patient.name,
                'service': apt.service,
                'date': apt.date.strftime('%b %d, %Y'),
                'time': apt.time.strftime('%H:%M'),
                'status': apt.status,
                'prescriptions': prescriptions,
                'patient_email': apt.patient.email,
                'patient_phone': apt.patient.phone
            })

        return JsonResponse({
            'status': 'success',
            'appointments': appointments_data,
            'total': len(appointments_data)
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def ajax_get_statistics(request):
    """AJAX endpoint to get real-time appointment statistics."""
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    try:
        appointments = Appointment.objects.filter(doctor_id=doctor_id)

        stats = {
            'total': appointments.count(),
            'pending': appointments.filter(status='Pending').count(),
            'approved': appointments.filter(status='Approved').count(),
            'completed': appointments.filter(status='Completed').count(),
            'cancelled': appointments.filter(status='Cancelled').count()
        }

        return JsonResponse({
            'status': 'success',
            'statistics': stats
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
