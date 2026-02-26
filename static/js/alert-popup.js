/**
 * Hospital Management System - Alert Popup Notification System
 * Provides beautiful, animated alert popups and toast notifications
 */

class AlertPopup {
    constructor() {
        this.overlayId = 'alert-popup-overlay-' + Date.now();
        this.toastContainerId = 'toast-container';
        this.initToastContainer();
    }

    /**
     * Initialize the toast container if it doesn't exist
     */
    initToastContainer() {
        if (!document.getElementById(this.toastContainerId)) {
            const container = document.createElement('div');
            container.id = this.toastContainerId;
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
    }

    /**
     * Show an alert popup (modal style)
     * @param {Object} options - Configuration object
     * @param {string} options.type - 'success', 'error', 'warning', 'info'
     * @param {string} options.title - Alert title
     * @param {string} options.message - Alert message
     * @param {Array} options.buttons - Array of button objects {label, callback, type}
     * @param {boolean} options.autoClose - Auto close after delay (default: false)
     * @param {number} options.autoCloseTime - Time to close in ms (default: 5000)
     */
    show(options = {}) {
        const {
            type = 'info',
            title = 'Notification',
            message = '',
            buttons = [],
            autoClose = false,
            autoCloseTime = 5000
        } = options;

        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'alert-popup-overlay';
        overlay.id = this.overlayId;

        // Create popup
        const popup = document.createElement('div');
        popup.className = `alert-popup ${type}`;

        // Get icon based on type
        const icon = this.getIconForType(type);

        // Create content
        popup.innerHTML = `
            <button class="alert-popup-close" aria-label="Close alert">
                <i class="bi bi-x"></i>
            </button>
            <div class="alert-popup-content">
                <div class="alert-popup-icon">
                    <i class="bi ${icon}"></i>
                </div>
                <div class="alert-popup-body">
                    <div class="alert-popup-title">${this.escapeHtml(title)}</div>
                    <div class="alert-popup-message">${this.escapeHtml(message)}</div>
                    ${buttons.length > 0 ? '<div class="alert-popup-actions"></div>' : ''}
                </div>
            </div>
            ${!autoClose ? '<div class="alert-popup-progress"></div>' : ''}
        `;

        // Add buttons if provided
        if (buttons.length > 0) {
            const actionsDiv = popup.querySelector('.alert-popup-actions');
            buttons.forEach(btn => {
                const button = document.createElement('button');
                button.className = `alert-popup-btn ${btn.type === 'secondary' ? 'alert-popup-btn-secondary' : 'alert-popup-btn-primary'}`;
                button.textContent = btn.label;
                button.onclick = () => {
                    if (btn.callback) btn.callback();
                    this.close(overlay);
                };
                actionsDiv.appendChild(button);
            });
        }

        // Close button handler
        popup.querySelector('.alert-popup-close').onclick = () => this.close(overlay);

        // Close on overlay click
        overlay.onclick = (e) => {
            if (e.target === overlay) this.close(overlay);
        };

        // Append to body
        overlay.appendChild(popup);
        document.body.appendChild(overlay);

        // Trigger animation
        setTimeout(() => overlay.classList.add('show'), 10);

        // Auto close
        if (autoClose) {
            setTimeout(() => this.close(overlay), autoCloseTime);
        }

        return overlay;
    }

    /**
     * Show a toast notification (top-right corner)
     * @param {Object} options - Configuration object
     * @param {string} options.type - 'success', 'error', 'warning', 'info'
     * @param {string} options.title - Toast title
     * @param {string} options.message - Toast message
     * @param {number} options.duration - Duration in ms (default: 4000)
     */
    toast(options = {}) {
        const {
            type = 'info',
            title = 'Notification',
            message = '',
            duration = 4000
        } = options;

        const container = document.getElementById(this.toastContainerId);
        const icon = this.getIconForType(type);

        // Create toast
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="bi ${icon}"></i>
            </div>
            <div class="toast-message">
                <div class="toast-title">${this.escapeHtml(title)}</div>
                <div class="toast-text">${this.escapeHtml(message)}</div>
            </div>
            <button class="toast-close" aria-label="Close notification">
                <i class="bi bi-x"></i>
            </button>
        `;

        // Close button
        toast.querySelector('.toast-close').onclick = () => {
            toast.style.animation = 'slideOutLeft 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        };

        container.appendChild(toast);

        // Auto remove
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOutLeft 0.3s ease forwards';
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    }

    /**
     * Show success alert
     */
    success(title, message, buttons = []) {
        return this.show({
            type: 'success',
            title,
            message,
            buttons,
            autoClose: buttons.length === 0
        });
    }

    /**
     * Show error alert
     */
    error(title, message, buttons = []) {
        return this.show({
            type: 'error',
            title,
            message,
            buttons
        });
    }

    /**
     * Show warning alert
     */
    warning(title, message, buttons = []) {
        return this.show({
            type: 'warning',
            title,
            message,
            buttons
        });
    }

    /**
     * Show info alert
     */
    info(title, message, buttons = []) {
        return this.show({
            type: 'info',
            title,
            message,
            buttons
        });
    }

    /**
     * Show success toast
     */
    successToast(title, message) {
        this.toast({
            type: 'success',
            title,
            message
        });
    }

    /**
     * Show error toast
     */
    errorToast(title, message) {
        this.toast({
            type: 'error',
            title,
            message
        });
    }

    /**
     * Show warning toast
     */
    warningToast(title, message) {
        this.toast({
            type: 'warning',
            title,
            message
        });
    }

    /**
     * Show info toast
     */
    infoToast(title, message) {
        this.toast({
            type: 'info',
            title,
            message
        });
    }

    /**
     * Show confirmation dialog
     */
    confirm(title, message, onConfirm, onCancel) {
        return this.show({
            type: 'warning',
            title,
            message,
            buttons: [
                {
                    label: 'Confirm',
                    callback: onConfirm,
                    type: 'primary'
                },
                {
                    label: 'Cancel',
                    callback: onCancel,
                    type: 'secondary'
                }
            ]
        });
    }

    /**
     * Close alert popup
     */
    close(overlay) {
        overlay.classList.remove('show');
        setTimeout(() => overlay.remove(), 300);
    }

    /**
     * Get icon for alert type
     */
    getIconForType(type) {
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };
        return icons[type] || icons.info;
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Create global instance
window.Alert = new AlertPopup();

// Expose methods for easy access
window.showAlert = (options) => window.Alert.show(options);
window.showToast = (options) => window.Alert.toast(options);
window.showSuccess = (title, message, buttons) => window.Alert.success(title, message, buttons);
window.showError = (title, message, buttons) => window.Alert.error(title, message, buttons);
window.showWarning = (title, message, buttons) => window.Alert.warning(title, message, buttons);
window.showInfo = (title, message, buttons) => window.Alert.info(title, message, buttons);
window.showConfirm = (title, message, onConfirm, onCancel) => window.Alert.confirm(title, message, onConfirm, onCancel);
window.showSuccessToast = (title, message) => window.Alert.successToast(title, message);
window.showErrorToast = (title, message) => window.Alert.errorToast(title, message);
window.showWarningToast = (title, message) => window.Alert.warningToast(title, message);
window.showInfoToast = (title, message) => window.Alert.infoToast(title, message);
