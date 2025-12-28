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
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('mainContent');
            const floatingToggle = document.getElementById('floatingSidebarToggle');

            if (sidebar && mainContent) {
                sidebar.classList.add('collapsed');
                mainContent.classList.add('sidebar-collapsed');

                // Show floating toggle button
                if (floatingToggle) {
                    floatingToggle.style.display = 'flex';
                }
            }
        }

        // Load notifications count
        this.loadNotificationCount();

        // Initialize theme toggle (only if it exists)
        this.initializeThemeToggle();

        // Convert Django messages to modern toasts
        this.convertDjangoMessagesToToasts();
    }

    initializeThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const currentTheme = document.body.getAttribute('data-theme') || 'light';
            const sunIcon = themeToggle.querySelector('.fa-sun');
            const moonIcon = themeToggle.querySelector('.fa-moon');

            if (sunIcon && moonIcon) {
                if (currentTheme === 'dark') {
                    sunIcon.style.opacity = '0.5';
                    sunIcon.style.color = '#B0B0B0';
                    moonIcon.style.opacity = '1';
                    moonIcon.style.color = '#f9fafb';
                } else {
                    sunIcon.style.opacity = '1';
                    sunIcon.style.color = '#374151';
                    moonIcon.style.opacity = '0.5';
                    moonIcon.style.color = '#9ca3af';
                }
            }
        }
    }

    setupEventListeners() {
        // ===== TOPBAR BUTTONS =====
        this.setupTopbarButtons();

        // ===== SIDEBAR CONTROLS =====
        this.setupSidebarControls();

        // ===== SEARCH FUNCTIONALITY =====
        this.setupSearchFunctionality();

        // ===== NOTIFICATION SYSTEM =====
        this.setupNotificationSystem();

        // ===== USER MENU SYSTEM =====
        this.setupUserMenuSystem();

        // ===== GLOBAL EVENT LISTENERS =====
        this.setupGlobalEventListeners();
    }

    // ===== TOPBAR BUTTONS SETUP =====
    setupTopbarButtons() {
        // Mobile Toggle Button
        const mobileToggle = document.getElementById('mobileToggle');
        if (mobileToggle) {
            mobileToggle.addEventListener('click', () => this.toggleMobileMenu());
        }

        // Theme Toggle Button
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Fullscreen Toggle Button
        const fullscreenToggle = document.getElementById('fullscreenToggle');
        if (fullscreenToggle) {
            fullscreenToggle.addEventListener('click', () => this.toggleFullscreen());
        }

        // Search Clear Button
        const searchClear = document.getElementById('searchClear');
        if (searchClear) {
            searchClear.addEventListener('click', () => this.clearSearch());
        }
    }

    // ===== SIDEBAR CONTROLS =====
    setupSidebarControls() {
        console.log('Setting up sidebar controls...');
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const themeToggle = document.getElementById('themeToggle');
        const sidebar = document.getElementById('sidebar');
        const btnTheme = document.getElementById('btnTheme');
        const btnMini = document.getElementById('btnMini');
        const btnMiniOpen = document.getElementById('btnMiniOpen');

        console.log('Sidebar elements found:', {
            mobileMenuToggle: !!mobileMenuToggle,
            sidebarToggle: !!sidebarToggle,
            themeToggle: !!themeToggle,
            sidebar: !!sidebar,
            btnTheme: !!btnTheme,
            btnMini: !!btnMini,
            btnMiniOpen: !!btnMiniOpen
        });

        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => this.toggleMobileMenu());
        }

        // Conectar toggle del topbar con el sidebar
        if (sidebarToggle && sidebar) {
            console.log('Connecting topbar toggle to sidebar');
            sidebarToggle.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Topbar toggle clicked');
                this.toggleSidebar();
            });
        }

        // Conectar themeToggle del topbar con el sistema de temas
        if (themeToggle && sidebar) {
            console.log('Connecting topbar theme toggle to sidebar theme system');
            themeToggle.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Topbar theme toggle clicked');
                this.toggleTheme();
            });
        }

        // Sidebar moderno - solo si existen los elementos
        if (sidebar) {
            console.log('Setting up modern sidebar');
            this.setupModernSidebar(sidebar, btnTheme, btnMini, btnMiniOpen);
        }
    }

    toggleSidebar() {
        console.log('toggleSidebar called');
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('mainContent');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const toggleIcon = sidebarToggle?.querySelector('i');

        console.log('Elements found:', { sidebar, mainContent, sidebarToggle, toggleIcon });

        if (sidebar && mainContent) {
            const isMini = sidebar.classList.contains('mini');
            console.log('Current state - isMini:', isMini);

            // Toggle sidebar state
            sidebar.classList.toggle('mini');
            mainContent.classList.toggle('sidebar-mini');

            const newState = sidebar.classList.contains('mini');
            console.log('New state - isMini:', newState);

            // Update toggle button icon with smooth transition
            if (toggleIcon) {
                toggleIcon.style.transform = 'rotate(180deg)';
                setTimeout(() => {
                    if (isMini) {
                        // Expanding - show hamburger
                        toggleIcon.className = 'fas fa-bars';
                    } else {
                        // Collapsing - show arrow
                        toggleIcon.className = 'fas fa-arrow-left';
                    }
                    toggleIcon.style.transform = 'rotate(0deg)';
                }, 150);
            }

            // Save state to localStorage
            localStorage.setItem('sb-mini', newState ? '1' : '0');

            // Enable/disable tooltips
            this.enableMiniTooltips();

            // Dispatch custom event for other components
            window.dispatchEvent(new CustomEvent('sidebarToggle', {
                detail: { collapsed: newState }
            }));
        } else {
            console.error('Required elements not found');
        }
    }

    enableMiniTooltips() {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        const need = sidebar.classList.contains('mini');
        document.querySelectorAll('.sb-item, #btnMiniOpen').forEach(el => {
            const tip = el.getAttribute('data-bs-title');
            const inst = bootstrap.Tooltip.getInstance(el);
            if (inst) inst.dispose();
            if (need && tip) {
                new bootstrap.Tooltip(el, { placement: 'right', title: tip });
            }
        });
    }

    toggleTheme() {
        console.log('toggleTheme called');
        const sidebar = document.getElementById('sidebar');
        const themeToggle = document.getElementById('themeToggle');
        const btnTheme = document.getElementById('btnTheme');

        if (!sidebar) {
            console.error('Sidebar not found');
            return;
        }

        const isLight = sidebar.classList.contains('light');
        const newTheme = isLight ? 'dark' : 'light';

        console.log('Current theme is light:', isLight, 'Switching to:', newTheme);

        if (newTheme === 'light') {
            // Cambiar a tema claro
            sidebar.classList.add('light');
            document.body.style.background = '#e5e7eb';

            // Actualizar iconos
            if (btnTheme) {
                btnTheme.innerHTML = '<i class="bi bi-brightness-high"></i>';
            }
            if (themeToggle) {
                const icon = themeToggle.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-sun';
                }
            }

            localStorage.setItem('sb-theme', 'light');
        } else {
            // Cambiar a tema oscuro
            sidebar.classList.remove('light');
            document.body.style.background = '#dfe3ea';

            // Actualizar iconos
            if (btnTheme) {
                btnTheme.innerHTML = '<i class="bi bi-moon"></i>';
            }
            if (themeToggle) {
                const icon = themeToggle.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-moon';
                }
            }

            localStorage.setItem('sb-theme', 'dark');
        }

        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themeToggle', {
            detail: { theme: newTheme }
        }));
    }

    setupModernSidebar(sidebar, btnTheme, btnMini, btnMiniOpen) {
        console.log('Setting up modern sidebar with elements:', { btnTheme: !!btnTheme, btnMini: !!btnMini, btnMiniOpen: !!btnMiniOpen });

        // Tema
        if (btnTheme) {
            btnTheme.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Sidebar theme button clicked');
                this.toggleTheme();
            });
        }

        // Aplicar tema guardado al cargar
        const savedTheme = localStorage.getItem('sb-theme') || 'dark';
        if (savedTheme === 'light') {
            sidebar.classList.add('light');
            document.body.style.background = '#e5e7eb';
            if (btnTheme) {
                btnTheme.innerHTML = '<i class="bi bi-brightness-high"></i>';
            }
            const themeToggle = document.getElementById('themeToggle');
            if (themeToggle) {
                const icon = themeToggle.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-sun';
                }
            }
        } else {
            sidebar.classList.remove('light');
            document.body.style.background = '#dfe3ea';
            if (btnTheme) {
                btnTheme.innerHTML = '<i class="bi bi-moon"></i>';
            }
            const themeToggle = document.getElementById('themeToggle');
            if (themeToggle) {
                const icon = themeToggle.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-moon';
                }
            }
        }

        // Botones del sidebar
        if (btnMini) {
            btnMini.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Sidebar mini button clicked');
                this.toggleSidebar();
            });
        }

        if (btnMiniOpen) {
            btnMiniOpen.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Sidebar mini open button clicked');
                this.toggleSidebar();
            });
        }

        // Restaurar estado del sidebar
        const savedState = localStorage.getItem('sb-mini') === '1';
        if (savedState) {
            sidebar.classList.add('mini');
            const mainContent = document.getElementById('mainContent');
            if (mainContent) {
                mainContent.classList.add('sidebar-mini');
            }
        }

        // Configurar estado activo del sidebar
        this.setupActiveSidebarState();

        this.enableMiniTooltips();
    }

    setupActiveSidebarState() {
        // El estado activo ahora se maneja desde Django con context processors
        // Solo necesitamos verificar que los elementos estén correctamente configurados
        console.log('✅ Sidebar active state managed by Django context processor');

        // Verificar elementos activos
        const activeItems = document.querySelectorAll('.sb-item.active, .sb-sub .link.active');
        console.log('📊 Active items found:', activeItems.length);
        activeItems.forEach((item, index) => {
            console.log(`  ${index + 1}.`, item.textContent.trim(), item.className);
        });
    }



    // ===== SEARCH FUNCTIONALITY =====
    setupSearchFunctionality() {
        const searchInput = document.getElementById('searchInput');
        const searchSuggestions = document.getElementById('searchSuggestions');

        if (searchInput) {
            // Search input events
            searchInput.addEventListener('input', (e) => this.handleSearchInput(e.target.value));
            searchInput.addEventListener('focus', () => this.showSearchSuggestions());
            searchInput.addEventListener('blur', () => this.hideSearchSuggestions());
            searchInput.addEventListener('keydown', (e) => this.handleSearchKeydown(e));
        }
    }

    // ===== NOTIFICATION SYSTEM =====
    setupNotificationSystem() {
        const notificationBtn = document.getElementById('notificationsBtn');
        const notificationPanel = document.getElementById('notificationPanel');
        const closeNotifications = document.getElementById('closeNotifications');
        const markAllRead = document.getElementById('markAllRead');

        if (notificationBtn && notificationPanel) {
            notificationBtn.addEventListener('click', () => this.toggleNotifications());
        }

        if (closeNotifications) {
            closeNotifications.addEventListener('click', () => this.closeNotifications());
        }

        if (markAllRead) {
            markAllRead.addEventListener('click', () => this.markAllNotificationsRead());
        }
    }

    // ===== USER MENU SYSTEM =====
    setupUserMenuSystem() {
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userDropdown = document.getElementById('userDropdown');

        if (userMenuBtn && userDropdown) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleUserDropdown();
            });
        }
    }

    // ===== GLOBAL EVENT LISTENERS =====
    setupGlobalEventListeners() {
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            this.handleOutsideClick(e);
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));

        // Window resize
        window.addEventListener('resize', () => this.handleResize());

        // Auto-hide alerts
        this.autoHideAlerts();
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

        // Only proceed if both elements exist
        if (!sidebar || !mainContent) {
            return;
        }

        if (window.innerWidth <= 768) {
            sidebar.classList.remove('collapsed');
            mainContent.classList.remove('sidebar-collapsed');
        }
    }

    autoHideAlerts() {
        // Solo ocultar alerts que no tengan la clase 'alert-persistent' o que estén dentro de formularios
        const alerts = document.querySelectorAll('.alert:not(.alert-persistent):not(.form-container .alert):not(.form-section .alert)');
        alerts.forEach(alert => {
            // Verificar que no esté dentro de un formulario
            if (!alert.closest('form') && !alert.closest('.form-container') && !alert.closest('.form-section')) {
                setTimeout(() => {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }, 5000);
            }
        });
    }

    // Utility methods
    showToast(message, type = 'info', title = null, duration = 5000) {
        // Modern toast notification implementation
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();

        // Generate unique ID for this toast
        const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        // Get icon based on type
        const icons = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle',
            'primary': 'fa-bell'
        };

        const icon = icons[type] || icons['info'];

        // Create toast element
        const toast = document.createElement('div');
        toast.id = toastId;
        let toastClass = `modern-toast toast-${type}`;

        // Add special class for player registration
        if (title && title.includes('Registro') || message.includes('Jugador') && message.includes('registrado')) {
            toastClass += ' player-registered';
        }

        toast.className = toastClass;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon">
                    <i class="fas ${icon}"></i>
                </div>
                <div class="toast-body-wrapper">
                    ${title ? `<div class="toast-title">${title}</div>` : ''}
                    <div class="toast-message">${message}</div>
                </div>
                <button type="button" class="toast-close" aria-label="Cerrar">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="toast-progress">
                <div class="toast-progress-bar"></div>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        // Start progress bar animation
        const progressBar = toast.querySelector('.toast-progress-bar');
        if (progressBar && duration > 0) {
            progressBar.style.animationDuration = `${duration}ms`;
            progressBar.style.animationPlayState = 'running';
        }

        // Auto-remove after duration
        let autoRemoveTimer;
        if (duration > 0) {
            autoRemoveTimer = setTimeout(() => {
                this.hideToast(toast);
            }, duration);
        }

        // Close button handler
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            if (autoRemoveTimer) clearTimeout(autoRemoveTimer);
            this.hideToast(toast);
        });

        // Pause progress on hover
        toast.addEventListener('mouseenter', () => {
            if (progressBar) {
                progressBar.style.animationPlayState = 'paused';
            }
            if (autoRemoveTimer) {
                clearTimeout(autoRemoveTimer);
            }
        });

        // Resume progress on leave
        toast.addEventListener('mouseleave', () => {
            if (progressBar && duration > 0) {
                const toastTimestamp = parseInt(toastId.split('-')[1]);
                const elapsed = Date.now() - toastTimestamp;
                const remaining = duration - elapsed;
                if (remaining > 0) {
                    // Calculate remaining percentage
                    const remainingPercent = (remaining / duration) * 100;
                    progressBar.style.animationPlayState = 'running';
                    progressBar.style.animationDuration = `${remaining}ms`;
                    autoRemoveTimer = setTimeout(() => {
                        this.hideToast(toast);
                    }, remaining);
                }
            }
        });

        return toast;
    }

    hideToast(toast) {
        toast.classList.remove('show');
        toast.classList.add('hide');

        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    createToastContainer() {
        const container = document.getElementById('toastContainer');
        if (container) return container;

        const newContainer = document.createElement('div');
        newContainer.id = 'toastContainer';
        newContainer.className = 'modern-toast-container';
        document.body.appendChild(newContainer);
        return newContainer;
    }

    convertDjangoMessagesToToasts() {
        // Find all Django messages and convert them to toasts
        const messages = document.querySelectorAll('.django-message');
        messages.forEach(msg => {
            const tag = msg.getAttribute('data-tag');
            const message = msg.getAttribute('data-message');
            const extraTags = msg.getAttribute('data-extra-tags') || '';

            // Map Django message tags to toast types
            let toastType = 'info';
            if (tag === 'success') toastType = 'success';
            else if (tag === 'error' || tag === 'danger') toastType = 'error';
            else if (tag === 'warning') toastType = 'warning';
            else if (tag === 'info') toastType = 'info';

            // Special handling for player registration
            let title = null;
            let duration = 5000;
            if (extraTags.includes('player_registered') || message.includes('Jugador') && message.includes('registrado')) {
                toastType = 'success';
                title = '¡Registro Exitoso!';
                duration = 6000; // Show longer for important messages
            }

            // Show toast
            this.showToast(message, toastType, title, duration);
        });
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

// Sidebar enhancements
function initializeSidebarEnhancements() {
    // Add hover effects to navigation items
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        const link = item.querySelector('.nav-link');

        // Add ripple effect on click
        link.addEventListener('click', function (e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });

        // Add subtle animation on hover
        link.addEventListener('mouseenter', function () {
            if (!this.closest('.nav-item').classList.contains('active')) {
                this.style.transform = 'translateX(2px)';
            }
        });

        link.addEventListener('mouseleave', function () {
            if (!this.closest('.nav-item').classList.contains('active')) {
                this.style.transform = 'translateX(0)';
            }
        });
    });

    // Add section collapse/expand functionality
    const sectionTitles = document.querySelectorAll('.nav-section-title');
    sectionTitles.forEach(title => {
        title.style.cursor = 'pointer';
        title.addEventListener('click', function () {
            const section = this.closest('.nav-section');
            const nextSection = section.nextElementSibling;
            let itemsToToggle = [];

            // Find all nav items until next section
            let current = section.nextElementSibling;
            while (current && !current.classList.contains('nav-section')) {
                if (current.classList.contains('nav-item')) {
                    itemsToToggle.push(current);
                }
                current = current.nextElementSibling;
            }

            // Toggle visibility
            itemsToToggle.forEach(item => {
                item.style.display = item.style.display === 'none' ? 'block' : 'none';
            });

            // Add visual indicator
            this.classList.toggle('collapsed');
        });
    });
}

// Initialize sidebar enhancements when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeSidebarEnhancements();
});

// ==============================
// Hotel Reservation Modal Helpers
// ==============================
// NOTE: This is intentionally global + DOM-driven so it works even when tab HTML
// is injected dynamically and inline <script> blocks don't execute.
window.NSC_HotelReservation = window.NSC_HotelReservation || (() => {
    const MAX_ADDITIONAL = 10;
    const stateByPk = new Map(); // pk -> { roomId: string, roomLabel: string }

    function q(id) {
        return document.getElementById(id);
    }

    function getPk(fromEl) {
        if (!fromEl) return null;
        const pk = fromEl.getAttribute('data-hotel-pk') || fromEl.getAttribute('data-hotel-id');
        return pk ? String(pk) : null;
    }

    function getSelectedPlayers() {
        return Array.from(document.querySelectorAll('.child-checkbox:checked'));
    }

    function getAdultsCount(pk) {
        const el = q(`adults-total-count${pk}`);
        return el ? Number(el.value || 1) : 1;
    }

    function getAdditionalChildrenCount(pk) {
        const el = q(`additional-children-count${pk}`);
        return el ? Number(el.value || 0) : 0;
    }

    function totalAdults(pk) {
        // Total adults is selected by the user (min 1)
        return Math.max(1, getAdultsCount(pk));
    }

    function totalPeople(pk) {
        return totalAdults(pk) + getSelectedPlayers().length + getAdditionalChildrenCount(pk);
    }

    function escapeHtml(str) {
        return String(str || '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }

    function setCounter(pk, which, value) {
        const id = which === 'adults' ? `adults-total-count${pk}` : `additional-children-count${pk}`;
        const el = q(id);
        if (!el) return;
        const min = which === 'adults' ? 1 : 0;
        const v = Math.max(min, Math.min(MAX_ADDITIONAL, Number(value) || 0));
        el.value = String(v);
    }

    function renderSelectedPlayers(pk) {
        const section = q(`selected-children-section${pk}`);
        const countEl = q(`children-count${pk}`);
        const listEl = q(`children-list${pk}`);

        if (!section || !listEl) return;

        const selected = getSelectedPlayers();
        if (countEl) countEl.textContent = String(selected.length);

        if (selected.length === 0) {
            section.style.display = 'none';
            listEl.innerHTML = '';
            return;
        }

        section.style.display = 'block';
        listEl.innerHTML = '';

        selected.forEach(cb => {
            const childItem = cb.closest('.child-item');
            if (!childItem) return;

            // name
            const nameDiv =
                childItem.querySelector('div[style*=\"font-weight: 700\"][style*=\"color: var(--mlb-blue)\"]') ||
                childItem.querySelector('div[style*=\"font-weight: 700\"]');
            const name = nameDiv ? nameDiv.textContent.trim() : 'Player';

            // photo
            const photoDiv = childItem.querySelector('div[style*=\"border-radius: 50%\"]');
            let avatarHtml = `<div style=\"width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, var(--mlb-red) 0%, #b30029 100%); display:flex; align-items:center; justify-content:center; color:white; font-weight:800;\"><i class=\"fas fa-user\"></i></div>`;
            const img = photoDiv ? photoDiv.querySelector('img') : null;
            if (img && img.src) {
                avatarHtml = `<div style=\"width: 44px; height: 44px; border-radius: 50%; overflow:hidden; border: 2px solid var(--mlb-red);\"><img src=\"${img.src}\" alt=\"${name}\" style=\"width:100%; height:100%; object-fit:cover;\"></div>`;
            }

            const birth = cb.getAttribute('data-birth-date') || '';
            const card = document.createElement('div');
            card.style.cssText = 'display:flex; align-items:center; gap:10px; background:white; padding:10px 12px; border-radius:10px; border:1px solid #e9ecef; flex:1 1 260px;';
            card.innerHTML = `
                ${avatarHtml}
                <div style="min-width:0;">
                    <div style="font-weight:800; color: var(--mlb-blue); line-height:1.1;">${name}</div>
                    ${birth ? `<div style="font-size:0.75rem; color:#6c757d; margin-top:2px;">DOB: ${birth}</div>` : ``}
                </div>
            `;
            listEl.appendChild(card);
        });
    }

    function additionalAdultFormHtml(index) {
        return `
            <div class="adult-form-item" data-adult-index="${index}"
                 style="background: white; border: 2px solid #e9ecef; border-radius: 10px; padding: 15px; margin-bottom: 15px;">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
                    <div style="font-weight:800; color: var(--mlb-blue);">Adult ${index}</div>
                </div>
                <div class="row g-3">
                    <div class="col-md-6">
                        <label class="form-label" style="font-weight:600; color:var(--mlb-blue); font-size:0.85rem;">Full Name <span style="color: var(--mlb-red);">*</span></label>
                        <input type="text" class="form-control adult-name-input" name="adult_name_${index}" data-index="${index}" required style="border:2px solid #e9ecef; border-radius:8px; padding:10px;">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label" style="font-weight:600; color:var(--mlb-blue); font-size:0.85rem;">Email <span style="color: var(--mlb-red);">*</span></label>
                        <input type="email" class="form-control adult-email-input" name="adult_email_${index}" data-index="${index}" required style="border:2px solid #e9ecef; border-radius:8px; padding:10px;">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label" style="font-weight:600; color:var(--mlb-blue); font-size:0.85rem;">Phone <span style="color: var(--mlb-red);">*</span></label>
                        <input type="tel" class="form-control adult-phone-input" name="adult_phone_${index}" data-index="${index}" required style="border:2px solid #e9ecef; border-radius:8px; padding:10px;">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label" style="font-weight:600; color:var(--mlb-blue); font-size:0.85rem;">Date of Birth <span style="color: var(--mlb-red);">*</span></label>
                        <input type="date" class="form-control adult-birthdate-input" name="adult_birthdate_${index}" data-index="${index}" required style="border:2px solid #e9ecef; border-radius:8px; padding:10px;">
                    </div>
                </div>
            </div>
        `;
    }

    function renderAdditionalAdults(pk) {
        const container = q(`additional-adults-forms-container${pk}`);
        if (!container) return;
        const count = getAdditionalAdultsCount(pk);
        container.innerHTML = '';
        for (let i = 0; i < count; i++) {
            const index = 2 + i;
            const wrap = document.createElement('div');
            wrap.innerHTML = additionalAdultFormHtml(index);
            container.appendChild(wrap.firstElementChild);
        }
    }

    function additionalChildFormHtml(index) {
        return `
            <div class="additional-child-form-item" data-child-index="${index}"
                 style="background: white; border: 2px solid #e9ecef; border-radius: 10px; padding: 15px; margin-bottom: 15px;">
                <div style="font-weight:800; color: var(--mlb-blue); margin-bottom:12px;">Child ${index}</div>
                <div class="row g-3">
                    <div class="col-md-6">
                        <label class="form-label" style="font-weight:600; color:var(--mlb-blue); font-size:0.85rem;">Full Name <span style="color: var(--mlb-red);">*</span></label>
                        <input type="text" class="form-control child-name-input" name="additional_child_name_${index}" data-index="${index}" required style="border:2px solid #e9ecef; border-radius:8px; padding:10px;">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label" style="font-weight:600; color:var(--mlb-blue); font-size:0.85rem;">Date of Birth <span style="color: var(--mlb-red);">*</span></label>
                        <input type="date" class="form-control child-birthdate-input" name="additional_child_birthdate_${index}" data-index="${index}" required style="border:2px solid #e9ecef; border-radius:8px; padding:10px;">
                    </div>
                </div>
            </div>
        `;
    }

    function renderAdditionalChildren(pk) {
        const container = q(`additional-children-forms-container${pk}`);
        if (!container) return;
        const count = getAdditionalChildrenCount(pk);
        container.innerHTML = '';
        for (let i = 0; i < count; i++) {
            const index = 1 + i;
            const wrap = document.createElement('div');
            wrap.innerHTML = additionalChildFormHtml(index);
            container.appendChild(wrap.firstElementChild);
        }
    }

    function updateSummary(pk) {
        const adults = totalAdults(pk);
        const addChildren = getAdditionalChildrenCount(pk);
        const players = getSelectedPlayers().length;
        const total = adults + addChildren + players;

        const adultsCountEl = q(`adults-count${pk}`);
        if (adultsCountEl) adultsCountEl.textContent = String(adults);

        const totalPeopleEl = q(`total-people-count${pk}`);
        if (totalPeopleEl) totalPeopleEl.textContent = String(total);

        const hiddenAdults = q(`number_of_adults${pk}`);
        if (hiddenAdults) hiddenAdults.value = String(adults);

        const playersBreakdown = q(`players-breakdown${pk}`);
        const playersCountBreakdown = q(`players-count-breakdown${pk}`);
        if (playersBreakdown) playersBreakdown.style.display = players > 0 ? 'block' : 'none';
        if (playersCountBreakdown) playersCountBreakdown.textContent = String(players);

        const addChildrenBreakdown = q(`additional-children-breakdown${pk}`);
        const addChildrenCountBreakdown = q(`additional-children-count-breakdown${pk}`);
        if (addChildrenBreakdown) addChildrenBreakdown.style.display = addChildren > 0 ? 'block' : 'none';
        if (addChildrenCountBreakdown) addChildrenCountBreakdown.textContent = String(addChildren);

        const noChildrenWarn = q(`no-children-warning${pk}`);
        const hasPlayerOrChild = players > 0 || addChildren > 0;
        if (noChildrenWarn) noChildrenWarn.style.display = (!hasPlayerOrChild) ? 'block' : 'none';

        const showRoomsBtn = q(`show-rooms-btn${pk}`);
        if (showRoomsBtn) {
            const enabled = adults >= 1 && hasPlayerOrChild;
            showRoomsBtn.disabled = !enabled;
            showRoomsBtn.style.opacity = enabled ? '1' : '0.5';
            showRoomsBtn.style.cursor = enabled ? 'pointer' : 'not-allowed';
        }
    }

    function initModal(pk) {
        // Ensure counters exist
        if (!q(`adults-total-count${pk}`)) return;
        if (!q(`additional-children-count${pk}`)) return;

        renderSelectedPlayers(pk);
        updateSummary(pk);
    }

    function showRooms(btnEl) {
        const pk = getPk(btnEl);
        if (!pk) return;
        const adults = totalAdults(pk);
        const addChildren = getAdditionalChildrenCount(pk);
        const players = getSelectedPlayers().length;
        const total = adults + addChildren + players;

        if (adults < 1) return alert('At least one adult is required');
        if (players === 0 && addChildren === 0) return alert('You must select at least one player or add at least one child');

        // Close reservation modal first
        const reservationModalEl = q(`hotelReservationModal${pk}`);
        if (reservationModalEl && window.bootstrap?.Modal) {
            const inst = bootstrap.Modal.getInstance(reservationModalEl);
            if (inst) inst.hide();
        }

        // Open hotel details modal
        const hotelModalEl = q(`hotelModal${pk}`);
        if (hotelModalEl && window.bootstrap?.Modal) {
            const modal = new bootstrap.Modal(hotelModalEl);
            modal.show();

            // Filter room listings (capacity)
            hotelModalEl.addEventListener('shown.bs.modal', function filterRooms() {
                const roomListings = hotelModalEl.querySelectorAll('.room-listing');
                // Clear old recommendation
                roomListings.forEach(r => {
                    r.classList.remove('nsc-room-recommended');
                    const oldBadge = r.querySelector('.nsc-recommended-badge');
                    if (oldBadge) oldBadge.remove();
                });

                const candidates = [];
                roomListings.forEach(roomListing => {
                    const capAttr = roomListing.getAttribute('data-room-capacity');
                    const cap = parseInt(capAttr || '0', 10);
                    const ok = cap >= total;
                    roomListing.style.display = ok ? '' : 'none';

                    if (ok) {
                        const priceAttr = roomListing.getAttribute('data-room-price');
                        const price = parseFloat(String(priceAttr || '0')) || 0;
                        candidates.push({ el: roomListing, cap: cap || 0, price });
                    }
                });

                if (candidates.length) {
                    // Best fit: smallest capacity waste; tie-break by lowest price
                    candidates.sort((a, b) => {
                        const wasteA = Math.max(0, a.cap - total);
                        const wasteB = Math.max(0, b.cap - total);
                        if (wasteA !== wasteB) return wasteA - wasteB;
                        if (a.price !== b.price) return a.price - b.price;
                        return 0;
                    });

                    const best = candidates[0].el;
                    best.classList.add('nsc-room-recommended');

                    const content = best.querySelector('.room-content') || best;
                    const badge = document.createElement('div');
                    badge.className = 'nsc-recommended-badge';
                    badge.textContent = `Recommended for ${total} guests`;
                    content.insertBefore(badge, content.firstChild);

                    // Scroll into view for the user
                    try {
                        best.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    } catch (_) {
                        best.scrollIntoView();
                    }
                }
            }, { once: true });
        }
    }

    function renderGuestDetails(pk) {
        const selected = getSelectedPlayers();

        // Selected players chips
        const selectedWrap = q(`guest-selected-players-wrap${pk}`);
        const selectedEl = q(`guest-selected-players${pk}`);
        if (selectedWrap && selectedEl) {
            if (selected.length === 0) {
                selectedWrap.style.display = 'none';
                selectedEl.innerHTML = '';
            } else {
                selectedWrap.style.display = 'block';
                selectedEl.innerHTML = '';
                selected.forEach(cb => {
                    const childItem = cb.closest('.child-item');
                    const nameDiv =
                        childItem?.querySelector('div[style*="font-weight: 700"][style*="color: var(--mlb-blue)"]') ||
                        childItem?.querySelector('div[style*="font-weight: 700"]');
                    const name = nameDiv ? nameDiv.textContent.trim() : 'Player';
                    const birth = cb.getAttribute('data-birth-date') || '';
                    const chip = document.createElement('div');
                    chip.style.cssText = 'background:#ffffff; border:1px solid #e9ecef; border-radius:999px; padding:8px 12px; font-weight:800; color: var(--mlb-blue); font-size:0.85rem;';
                    chip.textContent = birth ? `${name} (${birth})` : name;
                    selectedEl.appendChild(chip);
                });
            }
        }

        // Additional adults fields
        const addAdults = Math.max(0, totalAdults(pk) - 1);
        const adultsWrap = q(`guest-additional-adults-wrap${pk}`);
        const adultsEl = q(`guest-additional-adults${pk}`);
        if (adultsWrap && adultsEl) {
            if (addAdults <= 0) {
                adultsWrap.style.display = 'none';
                adultsEl.innerHTML = '';
            } else {
                adultsWrap.style.display = 'block';
                adultsEl.innerHTML = '';
                for (let i = 1; i <= addAdults; i++) {
                    const idx = i + 1; // primary is 1
                    const block = document.createElement('div');
                    block.className = 'nsc-guest-adult';
                    block.setAttribute('data-index', String(idx));
                    block.style.cssText = 'background:#ffffff; border:2px solid #e9ecef; border-radius:12px; padding:14px; margin-bottom:12px;';
                    block.innerHTML = `
                        <div style="font-weight:900; color: var(--mlb-blue); margin-bottom:10px;">Adult ${idx}</div>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">Full Name *</label>
                                <input type="text" class="form-control nsc-adult-name" required style="border-radius:10px; border:2px solid #e9ecef; padding:10px;">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">Date of Birth *</label>
                                <input type="date" class="form-control nsc-adult-dob" required style="border-radius:10px; border:2px solid #e9ecef; padding:10px;">
                            </div>
                        </div>
                    `;
                    adultsEl.appendChild(block);
                }
            }
        }

        // Additional children fields
        const addChildren = getAdditionalChildrenCount(pk);
        const childrenWrap = q(`guest-additional-children-wrap${pk}`);
        const childrenEl = q(`guest-additional-children${pk}`);
        if (childrenWrap && childrenEl) {
            if (addChildren <= 0) {
                childrenWrap.style.display = 'none';
                childrenEl.innerHTML = '';
            } else {
                childrenWrap.style.display = 'block';
                childrenEl.innerHTML = '';
                for (let i = 1; i <= addChildren; i++) {
                    const block = document.createElement('div');
                    block.className = 'nsc-guest-child';
                    block.setAttribute('data-index', String(i));
                    block.style.cssText = 'background:#ffffff; border:2px solid #e9ecef; border-radius:12px; padding:14px; margin-bottom:12px;';
                    block.innerHTML = `
                        <div style="font-weight:900; color: var(--mlb-blue); margin-bottom:10px;">Child ${i}</div>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">Full Name *</label>
                                <input type="text" class="form-control nsc-child-name" required style="border-radius:10px; border:2px solid #e9ecef; padding:10px;">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">Date of Birth *</label>
                                <input type="date" class="form-control nsc-child-dob" required style="border-radius:10px; border:2px solid #e9ecef; padding:10px;">
                            </div>
                        </div>
                    `;
                    childrenEl.appendChild(block);
                }
            }
        }

        // Fill number_of_guests
        const guestsEl = q(`guest-number-of-guests${pk}`);
        if (guestsEl) guestsEl.value = String(totalPeople(pk));
    }

    function selectRoom(btnEl) {
        const pk = getPk(btnEl);
        if (!pk) return;

        const roomId = btnEl.getAttribute('data-room-id');
        if (!roomId) return;

        const total = totalPeople(pk);
        const capacity = parseInt(btnEl.getAttribute('data-room-capacity') || '0', 10);
        if (capacity && total > capacity) {
            alert(`This room fits ${capacity} guests, but you selected ${total}. Please adjust guests or choose another room.`);
            return;
        }

        const roomListing = btnEl.closest('.room-listing');
        const roomName = roomListing?.querySelector('.room-name')?.textContent?.trim() || 'Room';
        const roomFeatures = roomListing?.querySelector('.room-features')?.textContent?.trim() || '';
        const roomLabel = `${roomName}${roomFeatures ? ` • ${roomFeatures}` : ''}`;

        stateByPk.set(String(pk), { roomId: String(roomId), roomLabel });

        // Close hotel modal
        const hotelModalEl = q(`hotelModal${pk}`);
        if (hotelModalEl && window.bootstrap?.Modal) {
            const inst = bootstrap.Modal.getInstance(hotelModalEl);
            if (inst) inst.hide();
        }

        // Populate guest modal
        const roomInput = q(`guest-room${pk}`);
        if (roomInput) roomInput.value = String(roomId);

        const labelEl = q(`selected-room-label${pk}`);
        if (labelEl) labelEl.textContent = roomLabel;

        renderGuestDetails(pk);

        const guestModalEl = q(`hotelGuestDetailsModal${pk}`);
        if (guestModalEl && window.bootstrap?.Modal) {
            const guestModal = new bootstrap.Modal(guestModalEl);
            guestModal.show();
        }
    }

    async function openRoomDetail(fromEl) {
        const pk = getPk(fromEl);
        if (!pk) return;
        const roomId = fromEl.getAttribute('data-room-id');
        if (!roomId) return;

        const modalEl = q(`roomDetailModal${pk}`);
        if (!modalEl) return;

        const urlTemplate = modalEl.getAttribute('data-room-detail-url-template');
        if (!urlTemplate) return;
        const url = urlTemplate.replace('999999', String(roomId));

        // Reset UI
        const titleEl = q(`room-detail-title${pk}`);
        const subtitleEl = q(`room-detail-subtitle${pk}`);
        const descEl = q(`room-detail-description${pk}`);
        const capEl = q(`room-detail-capacity${pk}`);
        const priceEl = q(`room-detail-price${pk}`);
        const galleryEl = q(`room-detail-gallery${pk}`);
        const amenitiesEl = q(`room-detail-amenities${pk}`);
        const servicesEl = q(`room-detail-services${pk}`);

        if (titleEl) titleEl.textContent = 'Room';
        if (subtitleEl) subtitleEl.textContent = '';
        if (descEl) descEl.textContent = '';
        if (capEl) capEl.textContent = '-';
        if (priceEl) priceEl.textContent = '-';
        if (amenitiesEl) amenitiesEl.innerHTML = '';
        if (servicesEl) servicesEl.innerHTML = '';
        if (galleryEl) galleryEl.innerHTML = `<div style="padding: 18px; color: #6c757d;">Loading...</div>`;

        // Open modal immediately (loading state)
        if (window.bootstrap?.Modal) {
            const inst = bootstrap.Modal.getInstance(modalEl);
            (inst || new bootstrap.Modal(modalEl)).show();
        }

        try {
            const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            if (!res.ok) throw new Error(`Request failed: ${res.status}`);
            const data = await res.json();

            if (titleEl) titleEl.textContent = `${data.room_type || 'Room'}${data.room_number ? ` • ${data.room_number}` : ''}`;
            if (subtitleEl) subtitleEl.textContent = data.hotel?.name ? data.hotel.name : '';
            if (descEl) descEl.textContent = data.description || '';
            if (capEl) capEl.textContent = String(data.capacity ?? '-');
            if (priceEl) priceEl.textContent = String(data.price_per_night ?? '-');

            // Gallery
            if (galleryEl) {
                const images = Array.isArray(data.images) ? data.images : [];
                if (!images.length) {
                    galleryEl.innerHTML = `<div style="padding: 18px; color: #6c757d;">No images available.</div>`;
                } else if (images.length === 1) {
                    const img = images[0];
                    galleryEl.innerHTML = `
                        <img src="${img.url}" alt="${escapeHtml(img.alt || '')}" style="width:100%; height:420px; object-fit:cover; display:block;">
                    `;
                } else {
                    const carouselId = `roomGalleryCarousel${pk}`;
                    const indicators = images.map((_, idx) =>
                        `<button type="button" data-bs-target="#${carouselId}" data-bs-slide-to="${idx}" ${idx === 0 ? 'class="active" aria-current="true"' : ''} aria-label="Slide ${idx + 1}"></button>`
                    ).join('');
                    const slides = images.map((img, idx) => `
                        <div class="carousel-item ${idx === 0 ? 'active' : ''}">
                            <img src="${img.url}" alt="${escapeHtml(img.alt || '')}" style="width:100%; height:420px; object-fit:cover;">
                        </div>
                    `).join('');
                    galleryEl.innerHTML = `
                        <div id="${carouselId}" class="carousel slide" data-bs-ride="carousel">
                            <div class="carousel-indicators">${indicators}</div>
                            <div class="carousel-inner">${slides}</div>
                            <button class="carousel-control-prev" type="button" data-bs-target="#${carouselId}" data-bs-slide="prev">
                                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                                <span class="visually-hidden">Previous</span>
                            </button>
                            <button class="carousel-control-next" type="button" data-bs-target="#${carouselId}" data-bs-slide="next">
                                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                                <span class="visually-hidden">Next</span>
                            </button>
                        </div>
                    `;
                }
            }

            // Amenities
            if (amenitiesEl) {
                const amenities = Array.isArray(data.amenities) ? data.amenities : [];
                if (!amenities.length) {
                    amenitiesEl.innerHTML = `<div style="color:#6c757d;">No amenities listed.</div>`;
                } else {
                    amenitiesEl.innerHTML = amenities.slice(0, 18).map(a => `
                        <span class="nsc-pill" title="${escapeHtml(a.description || '')}">
                            <i class="fas ${escapeHtml(a.icon || 'fa-check-circle')}" style="color: var(--mlb-red);"></i>
                            ${escapeHtml(a.name || '')}
                        </span>
                    `).join('');
                }
            }

            // Services
            if (servicesEl) {
                const services = Array.isArray(data.services) ? data.services : [];
                if (!services.length) {
                    servicesEl.innerHTML = `<div style="color:#6c757d;">No services listed.</div>`;
                } else {
                    servicesEl.innerHTML = services.slice(0, 10).map(s => `
                        <div style="border:2px solid #e9ecef; border-radius: 12px; padding: 12px; background:#fff;">
                            <div style="font-weight:900; color: var(--mlb-blue);">${escapeHtml(s.name || '')}</div>
                            <div style="font-size:0.85rem; color:#6c757d; margin-top: 2px;">
                                ${escapeHtml(s.type || '')}
                                ${s.price ? ` • $${escapeHtml(s.price)}` : ``}
                                ${s.is_per_night ? ` • /night` : ``}
                                ${s.is_per_person ? ` • /person` : ``}
                            </div>
                            ${s.description ? `<div style="margin-top:6px; color:#333;">${escapeHtml(s.description)}</div>` : ``}
                        </div>
                    `).join('');
                }
            }
        } catch (err) {
            if (galleryEl) {
                galleryEl.innerHTML = `<div style="padding: 18px; color: #b30029; font-weight: 800;">Failed to load room details.</div>`;
            }
        }
    }

    // Stepper actions (adults/children)
    document.addEventListener('click', (e) => {
        const btn = e.target?.closest?.('[data-nsc-action]');
        if (!btn) return;
        const pk = getPk(btn);
        if (!pk) return;
        const action = btn.getAttribute('data-nsc-action');
        if (!action) return;

        e.preventDefault();

        if (action === 'adults-inc' || action === 'adults-dec') {
            const current = getAdultsCount(pk);
            const next = action === 'adults-inc' ? current + 1 : current - 1;
            setCounter(pk, 'adults', next);
            updateSummary(pk);
        }

        if (action === 'children-inc' || action === 'children-dec') {
            const current = getAdditionalChildrenCount(pk);
            const next = action === 'children-inc' ? current + 1 : current - 1;
            setCounter(pk, 'children', next);
            updateSummary(pk);
        }
    });

    // Keep players list + totals synced
    document.addEventListener('change', (e) => {
        if (!e.target?.classList?.contains('child-checkbox')) return;
        // update any open reservation modal(s)
        document.querySelectorAll('[id^=\"hotelReservationModal\"]').forEach(modalEl => {
            const pk = modalEl.getAttribute('data-hotel-pk') || modalEl.id.replace('hotelReservationModal', '');
            if (pk) initModal(String(pk));
        });
    });

    // Bootstrap modal hook
    document.addEventListener('shown.bs.modal', (e) => {
        const modalEl = e.target;
        if (!modalEl || !modalEl.id || !modalEl.id.startsWith('hotelReservationModal')) return;
        const pk = modalEl.getAttribute('data-hotel-pk') || modalEl.id.replace('hotelReservationModal', '');
        if (pk) initModal(String(pk));
    });

    // Guest details form: build notes from extra guests + selected players
    document.addEventListener('submit', (e) => {
        const form = e.target;
        if (!(form instanceof HTMLFormElement)) return;
        if (!form.id || !form.id.startsWith('guest-details-form')) return;

        const pk = form.id.replace('guest-details-form', '');
        if (!pk) return;

        const notesHidden = q(`guest-notes${pk}`);
        const notesHuman = q(`guest-notes-human${pk}`)?.value?.trim() || '';

        const selected = getSelectedPlayers().map(cb => {
            const childItem = cb.closest('.child-item');
            const nameDiv =
                childItem?.querySelector('div[style*="font-weight: 700"][style*="color: var(--mlb-blue)"]') ||
                childItem?.querySelector('div[style*="font-weight: 700"]');
            const name = nameDiv ? nameDiv.textContent.trim() : 'Player';
            const birth = cb.getAttribute('data-birth-date') || '';
            return birth ? `${name} (${birth})` : name;
        });

        const addAdults = Array.from(form.querySelectorAll('.nsc-guest-adult')).map(el => {
            const name = el.querySelector('.nsc-adult-name')?.value?.trim() || '';
            const dob = el.querySelector('.nsc-adult-dob')?.value?.trim() || '';
            return name ? (dob ? `${name} (${dob})` : name) : '';
        }).filter(Boolean);

        const addChildren = Array.from(form.querySelectorAll('.nsc-guest-child')).map(el => {
            const name = el.querySelector('.nsc-child-name')?.value?.trim() || '';
            const dob = el.querySelector('.nsc-child-dob')?.value?.trim() || '';
            return name ? (dob ? `${name} (${dob})` : name) : '';
        }).filter(Boolean);

        const parts = [];
        if (notesHuman) parts.push(notesHuman);
        if (selected.length) parts.push(`Selected players/children: ${selected.join(', ')}`);
        if (addAdults.length) parts.push(`Additional adults: ${addAdults.join(', ')}`);
        if (addChildren.length) parts.push(`Additional children: ${addChildren.join(', ')}`);

        if (notesHidden) notesHidden.value = parts.join(' | ').slice(0, 1900);

        // Ensure number_of_guests is correct at submit time
        const guestsEl = q(`guest-number-of-guests${pk}`);
        if (guestsEl) guestsEl.value = String(totalPeople(pk));
    });

    // Backwards compatibility (old buttons may still exist somewhere)
    function addAdult(btnEl) {
        const pk = getPk(btnEl);
        if (!pk) return;
        const current = getAdultsCount(pk);
        setCounter(pk, 'adults', current + 1);
        updateSummary(pk);
    }

    function addChild(btnEl) {
        const pk = getPk(btnEl);
        if (!pk) return;
        const current = getAdditionalChildrenCount(pk);
        setCounter(pk, 'children', current + 1);
        updateSummary(pk);
    }

    return { initModal, showRooms, selectRoom, openRoomDetail, updateSummary, addAdult, addChild };
})();

// ===== TOPBAR BUTTON FUNCTIONS =====

// Mobile Menu Toggle
AdminDashboard.prototype.toggleMobileMenu = function () {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');

    if (sidebar && mainContent) {
        sidebar.classList.toggle('mobile-open');
        mainContent.classList.toggle('mobile-sidebar-open');

        // Prevent body scroll when mobile menu is open
        if (sidebar.classList.contains('mobile-open')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }
}

// Fullscreen Toggle
AdminDashboard.prototype.toggleFullscreen = function () {
    const fullscreenToggle = document.getElementById('fullscreenToggle');
    const icon = fullscreenToggle.querySelector('i');

    if (!document.fullscreenElement) {
        // Enter fullscreen
        document.documentElement.requestFullscreen().then(() => {
            icon.className = 'fas fa-compress';
            fullscreenToggle.title = 'Salir de pantalla completa';
        }).catch(err => {
            console.log('Error attempting to enable fullscreen:', err);
        });
    } else {
        // Exit fullscreen
        document.exitFullscreen().then(() => {
            icon.className = 'fas fa-expand';
            fullscreenToggle.title = 'Pantalla completa';
        }).catch(err => {
            console.log('Error attempting to exit fullscreen:', err);
        });
    }
}

// Search Functions
AdminDashboard.prototype.handleSearchInput = function (value) {
    const searchClear = document.getElementById('searchClear');
    const searchSuggestions = document.getElementById('searchSuggestions');

    // Show/hide clear button
    if (searchClear) {
        searchClear.style.display = value.length > 0 ? 'block' : 'none';
    }

    // Handle search suggestions
    if (value.length > 2) {
        this.showSearchSuggestions();
        this.loadSearchSuggestions(value);
    } else {
        this.hideSearchSuggestions();
    }
}

AdminDashboard.prototype.showSearchSuggestions = function () {
    const searchSuggestions = document.getElementById('searchSuggestions');
    if (searchSuggestions) {
        searchSuggestions.style.display = 'block';
    }
}

AdminDashboard.prototype.hideSearchSuggestions = function () {
    const searchSuggestions = document.getElementById('searchSuggestions');
    if (searchSuggestions) {
        searchSuggestions.style.display = 'none';
    }
}

AdminDashboard.prototype.loadSearchSuggestions = function (query) {
    const searchSuggestions = document.getElementById('searchSuggestions');
    if (!searchSuggestions) return;

    // Mock search suggestions - replace with real API call
    const suggestions = [
        { type: 'event', title: 'Evento: Conferencia de Tecnología', url: '/events/1' },
        { type: 'user', title: 'Usuario: Juan Pérez', url: '/users/1' },
        { type: 'setting', title: 'Configuración: Notificaciones', url: '/settings/notifications' }
    ].filter(item =>
        item.title.toLowerCase().includes(query.toLowerCase())
    );

    if (suggestions.length > 0) {
        searchSuggestions.innerHTML = suggestions.map(suggestion => `
            <div class="suggestion-item" data-url="${suggestion.url}">
                <i class="fas fa-${this.getSuggestionIcon(suggestion.type)}"></i>
                <span>${suggestion.title}</span>
            </div>
        `).join('');

        // Add click handlers to suggestions
        searchSuggestions.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                window.location.href = item.dataset.url;
            });
        });
    } else {
        searchSuggestions.innerHTML = '<div class="suggestion-item no-results">No se encontraron resultados</div>';
    }
}

AdminDashboard.prototype.getSuggestionIcon = function (type) {
    const icons = {
        'event': 'calendar',
        'user': 'user',
        'setting': 'cog'
    };
    return icons[type] || 'search';
}

AdminDashboard.prototype.handleSearchKeydown = function (e) {
    const searchSuggestions = document.getElementById('searchSuggestions');
    const suggestions = searchSuggestions?.querySelectorAll('.suggestion-item');

    if (e.key === 'Escape') {
        this.hideSearchSuggestions();
        document.getElementById('searchInput').blur();
    } else if (e.key === 'Enter') {
        if (suggestions && suggestions.length > 0) {
            suggestions[0].click();
        }
    }
}

AdminDashboard.prototype.clearSearch = function () {
    const searchInput = document.getElementById('searchInput');
    const searchClear = document.getElementById('searchClear');
    const searchSuggestions = document.getElementById('searchSuggestions');

    if (searchInput) {
        searchInput.value = '';
        searchInput.focus();
    }

    if (searchClear) {
        searchClear.style.display = 'none';
    }

    if (searchSuggestions) {
        searchSuggestions.style.display = 'none';
    }
}

// Notification Functions
AdminDashboard.prototype.toggleNotifications = function () {
    const notificationPanel = document.getElementById('notificationPanel');
    const notificationBtn = document.getElementById('notificationsBtn');

    if (notificationPanel) {
        notificationPanel.classList.toggle('show');

        // Update button state
        if (notificationBtn) {
            notificationBtn.classList.toggle('active');
        }

        // Load notifications when opening
        if (notificationPanel.classList.contains('show')) {
            this.loadNotifications();
        }
    }
}

AdminDashboard.prototype.closeNotifications = function () {
    const notificationPanel = document.getElementById('notificationPanel');
    const notificationBtn = document.getElementById('notificationsBtn');

    if (notificationPanel) {
        notificationPanel.classList.remove('show');
    }

    if (notificationBtn) {
        notificationBtn.classList.remove('active');
    }
}

AdminDashboard.prototype.loadNotifications = function () {
    const notificationList = document.getElementById('notificationList');
    if (!notificationList) return;

    // Mock notifications - replace with real API call
    const notifications = [
        {
            id: 1,
            title: 'Nuevo evento creado',
            message: 'Se ha creado el evento "Conferencia de Tecnología"',
            time: 'Hace 5 minutos',
            read: false,
            type: 'success'
        },
        {
            id: 2,
            title: 'Usuario registrado',
            message: 'Juan Pérez se ha registrado en el sistema',
            time: 'Hace 1 hora',
            read: false,
            type: 'info'
        },
        {
            id: 3,
            title: 'Sistema actualizado',
            message: 'El sistema se ha actualizado a la versión 2.1.0',
            time: 'Hace 2 horas',
            read: true,
            type: 'warning'
        }
    ];

    if (notifications.length > 0) {
        notificationList.innerHTML = notifications.map(notification => `
            <div class="notification-item ${notification.read ? 'read' : 'unread'}" data-id="${notification.id}">
                <div class="notification-icon ${notification.type}">
                    <i class="fas fa-${this.getNotificationIcon(notification.type)}"></i>
                </div>
                <div class="notification-content">
                    <h6>${notification.title}</h6>
                    <p>${notification.message}</p>
                    <small>${notification.time}</small>
                </div>
                <button class="notification-mark-read" data-id="${notification.id}">
                    <i class="fas fa-check"></i>
                </button>
            </div>
        `).join('');

        // Add click handlers
        notificationList.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.notification-mark-read')) {
                    this.markNotificationAsRead(item.dataset.id);
                }
            });
        });

        notificationList.querySelectorAll('.notification-mark-read').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.markNotificationAsRead(btn.dataset.id);
            });
        });
    } else {
        notificationList.innerHTML = `
            <div class="notification-empty">
                <i class="fas fa-bell-slash"></i>
                <p>No hay notificaciones</p>
            </div>
        `;
    }
}

AdminDashboard.prototype.getNotificationIcon = function (type) {
    const icons = {
        'success': 'check-circle',
        'info': 'info-circle',
        'warning': 'exclamation-triangle',
        'error': 'times-circle'
    };
    return icons[type] || 'bell';
}

AdminDashboard.prototype.markNotificationAsRead = function (notificationId) {
    // Update UI
    const notificationItem = document.querySelector(`[data-id="${notificationId}"]`);
    if (notificationItem) {
        notificationItem.classList.remove('unread');
        notificationItem.classList.add('read');
    }

    // Update badge count
    this.updateNotificationBadge();

    // Here you would make an API call to mark as read
    console.log(`Marking notification ${notificationId} as read`);
}

AdminDashboard.prototype.markAllNotificationsRead = function () {
    const notificationItems = document.querySelectorAll('.notification-item.unread');
    notificationItems.forEach(item => {
        item.classList.remove('unread');
        item.classList.add('read');
    });

    this.updateNotificationBadge();
    console.log('All notifications marked as read');
}

AdminDashboard.prototype.updateNotificationBadge = function () {
    const badge = document.getElementById('notificationBadge');
    const unreadCount = document.querySelectorAll('.notification-item.unread').length;

    if (badge) {
        badge.textContent = unreadCount;
        badge.style.display = unreadCount > 0 ? 'flex' : 'none';
    }
}

// User Menu Functions
AdminDashboard.prototype.toggleUserDropdown = function () {
    const userDropdown = document.getElementById('userDropdown');
    const userMenuBtn = document.getElementById('userMenuBtn');

    if (userDropdown) {
        userDropdown.classList.toggle('show');

        // Update button state
        if (userMenuBtn) {
            userMenuBtn.classList.toggle('active');
        }
    }
}

AdminDashboard.prototype.closeUserDropdown = function () {
    const userDropdown = document.getElementById('userDropdown');
    const userMenuBtn = document.getElementById('userMenuBtn');

    if (userDropdown) {
        userDropdown.classList.remove('show');
    }

    if (userMenuBtn) {
        userMenuBtn.classList.remove('active');
    }
}

// Global Event Handlers
AdminDashboard.prototype.handleOutsideClick = function (e) {
    if (!e.target.closest('.user-menu')) {
        this.closeUserDropdown();
    }
    if (!e.target.closest('.notification-panel') && !e.target.closest('#notificationsBtn')) {
        this.closeNotifications();
    }
    if (!e.target.closest('.search-container')) {
        this.hideSearchSuggestions();
    }
}

AdminDashboard.prototype.handleKeyboardShortcuts = function (e) {
    // Ctrl + K for search focus
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape to close dropdowns
    if (e.key === 'Escape') {
        this.closeUserDropdown();
        this.closeNotifications();
        this.hideSearchSuggestions();
    }

    // Ctrl + B for sidebar toggle
    if (e.ctrlKey && e.key === 'b') {
        e.preventDefault();
        this.toggleSidebar();
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + B to toggle sidebar
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        if (window.adminDashboard) {
            window.adminDashboard.toggleSidebar();
        }
    }

    // Escape to close sidebar on mobile
    if (e.key === 'Escape') {
        const sidebar = document.getElementById('sidebar');
        if (sidebar && sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
        }
    }
});
