// NSC Admin Dashboard JavaScript

class AdminDashboard {
    constructor() {
        this.init();
        this.setupEventListeners();
    }

    init() {
        // Initialize theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        
        // Initialize sidebar state
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (sidebarCollapsed) {
            this.toggleSidebar();
        }

        // Load notifications count
        this.loadNotificationCount();
    }

    setupEventListeners() {
        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }
        
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => this.toggleMobileMenu());
        }

        // Submenu toggle
        const submenuItems = document.querySelectorAll('.nav-item.has-submenu');
        submenuItems.forEach(item => {
            const link = item.querySelector('.nav-link');
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleSubmenu(item);
            });
        });

        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // User menu
        const userBtn = document.getElementById('userBtn');
        const userDropdown = document.getElementById('userDropdown');
        if (userBtn && userDropdown) {
            userBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleUserDropdown();
            });
        }

        // Notifications
        const notificationBtn = document.getElementById('notificationBtn');
        const notificationPanel = document.getElementById('notificationPanel');
        const closeNotifications = document.getElementById('closeNotifications');
        
        if (notificationBtn && notificationPanel) {
            notificationBtn.addEventListener('click', () => this.toggleNotifications());
        }
        
        if (closeNotifications && notificationPanel) {
            closeNotifications.addEventListener('click', () => this.closeNotifications());
        }

        // Global search
        const globalSearch = document.getElementById('globalSearch');
        if (globalSearch) {
            globalSearch.addEventListener('input', (e) => this.handleGlobalSearch(e.target.value));
        }

        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.user-menu')) {
                this.closeUserDropdown();
            }
            if (!e.target.closest('.notification-panel') && !e.target.closest('.notification-btn')) {
                this.closeNotifications();
            }
        });

        // Window resize
        window.addEventListener('resize', () => this.handleResize());

        // Auto-hide alerts
        this.autoHideAlerts();
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('mainContent');
        
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('sidebar-collapsed');
        
        // Save state
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    }

    toggleMobileMenu() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('show');
    }

    toggleSubmenu(item) {
        item.classList.toggle('open');
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    toggleUserDropdown() {
        const userDropdown = document.getElementById('userDropdown');
        userDropdown.classList.toggle('show');
    }

    closeUserDropdown() {
        const userDropdown = document.getElementById('userDropdown');
        userDropdown.classList.remove('show');
    }

    toggleNotifications() {
        const notificationPanel = document.getElementById('notificationPanel');
        notificationPanel.classList.toggle('show');
        
        if (notificationPanel.classList.contains('show')) {
            this.loadNotifications();
        }
    }

    closeNotifications() {
        const notificationPanel = document.getElementById('notificationPanel');
        notificationPanel.classList.remove('show');
    }

    loadNotificationCount() {
        // Simulate loading notification count
        const notificationCount = document.getElementById('notificationCount');
        if (notificationCount) {
            // In a real app, this would be an AJAX call
            const count = Math.floor(Math.random() * 10);
            notificationCount.textContent = count;
            notificationCount.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    loadNotifications() {
        const notificationList = document.getElementById('notificationList');
        if (!notificationList) return;

        // Simulate loading notifications
        const notifications = [
            {
                id: 1,
                avatar: 'EJ',
                title: 'Emily Johnson comentó en una tarea',
                message: 'Design Sprint',
                time: '12 minutos',
                type: 'comment'
            },
            {
                id: 2,
                avatar: 'ML',
                title: 'Michael Lee subió archivos',
                message: 'Marketing Assets',
                time: '25 minutos',
                type: 'upload'
            },
            {
                id: 3,
                avatar: 'SR',
                title: 'Sophia Ray marcó un problema',
                message: 'Bug Tracker',
                time: '40 minutos',
                type: 'alert'
            },
            {
                id: 4,
                avatar: 'DK',
                title: 'David Kim programó una reunión',
                message: 'UX Review',
                time: '1 hora',
                type: 'event'
            },
            {
                id: 5,
                avatar: 'IW',
                title: 'Isabella White actualizó el documento',
                message: 'Product Specs',
                time: '2 horas',
                type: 'edit'
            }
        ];

        notificationList.innerHTML = notifications.map(notification => `
            <div class="notification-item">
                <div class="notification-avatar">${notification.avatar}</div>
                <div class="notification-content">
                    <h6>${notification.title}</h6>
                    <p>${notification.message}</p>
                </div>
                <div class="notification-time">${notification.time}</div>
            </div>
        `).join('');
    }

    handleGlobalSearch(query) {
        if (query.length < 2) return;
        
        // Simulate search functionality
        console.log('Searching for:', query);
        // In a real app, this would make an AJAX call to search endpoint
    }

    handleResize() {
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('mainContent');
        
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('collapsed');
            mainContent.classList.remove('sidebar-collapsed');
        }
    }

    autoHideAlerts() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    }

    // Utility methods
    showToast(message, type = 'info') {
        // Toast notification implementation
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    confirmDialog(message, callback) {
        if (confirm(message)) {
            callback();
        }
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    formatDate(date) {
        return new Intl.DateTimeFormat('es-ES').format(new Date(date));
    }

    formatNumber(num) {
        return new Intl.NumberFormat('es-ES').format(num);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
});

// Global utility functions
window.AdminUtils = {
    showToast: (message, type = 'info') => {
        if (window.adminDashboard) {
            window.adminDashboard.showToast(message, type);
        }
    },
    
    confirmDialog: (message, callback) => {
        if (window.adminDashboard) {
            window.adminDashboard.confirmDialog(message, callback);
        }
    },
    
    formatCurrency: (amount) => {
        if (window.adminDashboard) {
            return window.adminDashboard.formatCurrency(amount);
        }
        return amount;
    },
    
    formatDate: (date) => {
        if (window.adminDashboard) {
            return window.adminDashboard.formatDate(date);
        }
        return date;
    },
    
    formatNumber: (num) => {
        if (window.adminDashboard) {
            return window.adminDashboard.formatNumber(num);
        }
        return num;
    }
};

// Chart utilities
window.ChartUtils = {
    createLineChart: (canvasId, data, options = {}) => {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        };
        
        return new Chart(ctx, {
            type: 'line',
            data: data,
            options: { ...defaultOptions, ...options }
        });
    },
    
    createDoughnutChart: (canvasId, data, options = {}) => {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        };
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: { ...defaultOptions, ...options }
        });
    }
};
