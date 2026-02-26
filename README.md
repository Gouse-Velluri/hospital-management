



# 🏥 MedCare — Hospital Management System

A full-stack **Django** hospital management system with patient appointments, doctor dashboards, and a comprehensive medicine directory with **1000+ medicines** across 10 medical specialties.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-green?logo=django)
![License](https://img.shields.io/badge/License-MIT-yellow)
---

## ✨ Features

### 👨‍⚕️ Doctor Portal

- Register / Login with secure authentication
- Dashboard with appointment management
- **Prescribe medicines** with dosage details (frequency, duration, instructions)
- Full CRUD access to the medicine directory

### 👤 Patient Portal

- Register / Login
- Book appointments with preferred doctors & services
- View prescribed medicines with complete dosage information
- Edit profile

### 💊 Medicine Management

- **1000 medicines** across **10 categories** (General, Dental, Cardiology, Ophthalmology, Dermatology, Orthopedics, Pediatrics, Neurology, ENT, Psychiatry)
- **Doctor-only access** — patients cannot view the medicine directory
- Add, Edit, Delete medicines (authorized doctors only)
- Search & filter by category
- **iOS Glassmorphism UI** with frosted glass effects

### 📋 Prescription System

- Detailed dosage: Frequency, Duration, Special Instructions
- Category-based medicine suggestions for appointments
- Prescription history visible on patient dashboard

---

## 🛠️ Tech Stack

| Layer      | Technology                         |
| ---------- | ---------------------------------- |
| Backend    | Django 5.2, Python 3.12            |
| Frontend   | HTML5, CSS3, Bootstrap 5           |
| Database   | SQLite (dev) / PostgreSQL (prod)   |
| UI Design  | iOS Glassmorphism, Bootstrap Icons |
| Deployment | Gunicorn, WhiteNoise               |

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/hospital-management.git
cd hospital-management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## 📸 Screenshots

### Home Page

Modern landing page with quick access to Patient & Doctor portals.

### Medicine Directory (Doctor View)

iOS glassmorphism-styled medicine directory with 1000 medicines categorized into 10 specialties. Only accessible by authorized doctors.

### Doctor Dashboard

Appointment management with prescription modals featuring dosage fields.

### Patient Dashboard

View appointments and prescribed medicines with full dosage details.

---

## 📁 Project Structure

```
hospital-management/
├── doctors/          # Doctor app (views, models, forms)
├── patients/         # Patient app (views, models, forms)
├── medicines/        # Medicine & Prescription models
├── hospital_management/  # Django project settings
├── templates/        # HTML templates
│   ├── doctors/      # Doctor dashboard, login, register
│   ├── patients/     # Patient dashboard, login, register
│   ├── medicines/    # Medicine list (glassmorphism)
│   └── home.html     # Landing page
├── static/css/       # Custom styling
├── requirements.txt
├── Procfile          # Deployment config
└── manage.py
```

---

## 🔐 Access Control

| Feature                  | Patient | Doctor |
| ------------------------ | ------- | ------ |
| View Home Page           | ✅      | ✅     |
| Book Appointment         | ✅      | ❌     |
| View Prescriptions       | ✅      | ✅     |
| Medicine Directory       | ❌      | ✅     |
| Add/Edit/Delete Medicine | ❌      | ✅     |
| Prescribe Medicines      | ❌      | ✅     |

---

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using Django**
"# Hospital-Management" 
