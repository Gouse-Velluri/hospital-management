from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Medicine


def medicine_list(request):
    """Only doctors can access the medicines directory."""
    if request.session.get('user_type') != 'doctor':
        messages.error(request, 'Access denied. Only authorized doctors can view the medicines directory.')
        return redirect('home')

    categories = Medicine.CATEGORY_CHOICES
    medicines_by_category = {}
    for cat_value, cat_label in categories:
        meds = Medicine.objects.filter(category=cat_value)
        if meds.exists():
            medicines_by_category[cat_label] = meds

    context = {
        'medicines_by_category': medicines_by_category,
        'total_count': Medicine.objects.count(),
        'categories': categories,
    }
    return render(request, 'medicines/medicine_list.html', context)


def add_medicine(request):
    """Only logged-in doctors can add medicines."""
    if request.session.get('user_type') != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name')
        med_type = request.POST.get('med_type')
        dosage = request.POST.get('dosage')
        category = request.POST.get('category', 'General')
        description = request.POST.get('description', '')

        if name and med_type and dosage:
            Medicine.objects.create(
                name=name, med_type=med_type, dosage=dosage,
                category=category, description=description,
            )
            messages.success(request, 'Medicine added successfully!')
        else:
            messages.error(request, 'All fields are required.')

    return redirect('medicine_list')


def update_medicine(request, medicine_id):
    if request.session.get('user_type') != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('home')

    medicine = get_object_or_404(Medicine, id=medicine_id)
    if request.method == 'POST':
        medicine.name = request.POST.get('name', medicine.name)
        medicine.med_type = request.POST.get('med_type', medicine.med_type)
        medicine.dosage = request.POST.get('dosage', medicine.dosage)
        medicine.category = request.POST.get('category', medicine.category)
        medicine.description = request.POST.get('description', medicine.description)
        medicine.save()
        messages.success(request, 'Medicine updated successfully!')
    return redirect('medicine_list')


def delete_medicine(request, medicine_id):
    if request.session.get('user_type') != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('home')

    medicine = get_object_or_404(Medicine, id=medicine_id)
    medicine.delete()
    messages.success(request, 'Medicine deleted successfully!')
    return redirect('medicine_list')
