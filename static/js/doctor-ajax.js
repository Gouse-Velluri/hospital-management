/**
 * Hospital Management System - Real-time AJAX Data Processing
 * Doctor Dashboard AJAX Handlers
 */

// Global configuration
const API_ENDPOINTS = {
    approveAppointment: '/doctor/ajax/approve-appointment/',
    completeAppointment: '/doctor/ajax/complete-appointment/',
    rejectAppointment: '/doctor/ajax/reject-appointment/',
    getAppointments: '/doctor/ajax/get-appointments/',
    getStatistics: '/doctor/ajax/get-statistics/'
};

// Utility function to show notifications
function showNotification(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        <i class="bi bi-${type === 'error' ? 'exclamation-circle' : 'check-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    alertDiv.style.animation = 'slideInRight 0.4s ease';

    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(alertDiv, container.firstChild);

    // Auto-close after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Utility function to get CSRF token
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

/**
 * Handle Approve Appointment via AJAX
 */
async function ajaxApproveAppointment(appointmentId) {
    try {
        const formData = new FormData();
        formData.append('appointment_id', appointmentId);
        formData.append('csrfmiddlewaretoken', getCSRFToken());

        const response = await fetch(API_ENDPOINTS.approveAppointment, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            showNotification(data.message, 'success');
            updateAppointmentStatus(appointmentId, 'Approved');
            updateStatistics();
            return true;
        } else {
            showNotification(data.message, 'error');
            return false;
        }
    } catch (error) {
        showNotification('Error approving appointment: ' + error.message, 'error');
        console.error('Error:', error);
        return false;
    }
}

/**
 * Handle Complete Appointment via AJAX
 */
async function ajaxCompleteAppointment(appointmentId) {
    try {
        const formData = new FormData();
        formData.append('appointment_id', appointmentId);
        formData.append('csrfmiddlewaretoken', getCSRFToken());

        const response = await fetch(API_ENDPOINTS.completeAppointment, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            showNotification(data.message, 'success');
            updateAppointmentStatus(appointmentId, 'Completed');
            updateStatistics();
            return true;
        } else {
            showNotification(data.message, 'error');
            return false;
        }
    } catch (error) {
        showNotification('Error completing appointment: ' + error.message, 'error');
        console.error('Error:', error);
        return false;
    }
}

/**
 * Handle Reject Appointment via AJAX
 */
async function ajaxRejectAppointment(appointmentId) {
    try {
        const formData = new FormData();
        formData.append('appointment_id', appointmentId);
        formData.append('csrfmiddlewaretoken', getCSRFToken());

        const response = await fetch(API_ENDPOINTS.rejectAppointment, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            showNotification(data.message, 'warning');
            updateAppointmentStatus(appointmentId, 'Cancelled');
            updateStatistics();
            return true;
        } else {
            showNotification(data.message, 'error');
            return false;
        }
    } catch (error) {
        showNotification('Error rejecting appointment: ' + error.message, 'error');
        console.error('Error:', error);
        return false;
    }
}

/**
 * Update appointment status in real-time
 */
function updateAppointmentStatus(appointmentId, newStatus) {
    const row = document.querySelector(`tr[data-appointment-id="${appointmentId}"]`);
    if (!row) return;

    // Update status badge
    const statusCell = row.querySelector('.appointment-status');
    if (statusCell) {
        statusCell.innerHTML = `<span class="badge-status badge-${newStatus.toLowerCase()}">${newStatus}</span>`;
    }

    // Animate the update
    row.style.animation = 'none';
    setTimeout(() => {
        row.style.animation = 'glow 0.6s ease-in-out';
    }, 10);
}

/**
 * Fetch and update statistics in real-time
 */
async function updateStatistics() {
    try {
        const response = await fetch(API_ENDPOINTS.getStatistics, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            const stats = data.statistics;

            // Update stat cards
            document.getElementById('totalCount').textContent = stats.total;
            document.getElementById('pendingCount').textContent = stats.pending;
            document.getElementById('approvedCount').textContent = stats.approved;
            document.getElementById('completedCount').textContent = stats.completed;
            document.getElementById('cancelledCount').textContent = stats.cancelled;

            // Animate updates
            document.querySelectorAll('.stat-value').forEach(el => {
                el.style.animation = 'popIn 0.3s ease';
            });
        }
    } catch (error) {
        console.error('Error fetching statistics:', error);
    }
}

/**
 * Fetch all appointments data in real-time
 */
async function fetchAppointmentsData() {
    try {
        const response = await fetch(API_ENDPOINTS.getAppointments, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            return data.appointments;
        } else {
            showNotification('Error fetching appointments', 'error');
            return [];
        }
    } catch (error) {
        showNotification('Error fetching appointments: ' + error.message, 'error');
        console.error('Error:', error);
        return [];
    }
}

/**
 * Initialize auto-refresh for statistics every 10 seconds
 */
function initAutoRefresh(intervalSeconds = 10) {
    setInterval(() => {
        updateStatistics();
    }, intervalSeconds * 1000);
}

/**
 * Initialize AJAX handlers on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('AJAX handlers initialized');

    // Add AJAX handlers to action buttons
    document.querySelectorAll('[data-action="approve"]').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const appointmentId = this.getAttribute('data-appointment-id');
            await ajaxApproveAppointment(appointmentId);
        });
    });

    document.querySelectorAll('[data-action="complete"]').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const appointmentId = this.getAttribute('data-appointment-id');
            await ajaxCompleteAppointment(appointmentId);
        });
    });

    document.querySelectorAll('[data-action="reject"]').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const appointmentId = this.getAttribute('data-appointment-id');
            if (confirm('Are you sure you want to reject this appointment?')) {
                await ajaxRejectAppointment(appointmentId);
            }
        });
    });

    // Initialize auto-refresh
    initAutoRefresh(10);

    // Initial stats load
    updateStatistics();
});

// Export functions for external use
window.DoctorAJAX = {
    approveAppointment: ajaxApproveAppointment,
    completeAppointment: ajaxCompleteAppointment,
    rejectAppointment: ajaxRejectAppointment,
    fetchAppointments: fetchAppointmentsData,
    updateStatistics: updateStatistics,
    showNotification: showNotification
};
