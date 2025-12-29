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
    showToast(message, type = 'info', title = null, duration = 5000, imageUrl = null) {
        // Modern toast notification implementation
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();

        // Generate unique ID for this toast
        const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        // Get icon based on type (only if no image provided)
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

        // Icon or image section
        const iconOrImage = imageUrl
            ? `<div class="toast-icon toast-image" style="width: 48px; height: 48px; border-radius: 8px; overflow: hidden; flex-shrink: 0; background: #f8f9fa;">
                <img src="${imageUrl}" alt="Room image" style="width: 100%; height: 100%; object-fit: cover;">
               </div>`
            : `<div class="toast-icon">
                <i class="fas ${icon}"></i>
               </div>`;

        toast.innerHTML = `
            <div class="toast-content">
                ${iconOrImage}
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
    showToast: (message, type = 'info', title = null, duration = 5000, imageUrl = null) => {
        if (window.adminDashboard) {
            window.adminDashboard.showToast(message, type, title, duration, imageUrl);
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

    // Helper function to show toast notifications
    function showToast(message, type = 'warning', duration = 6000, imageUrl = null) {
        if (window.AdminUtils && window.AdminUtils.showToast) {
            // AdminUtils.showToast doesn't support imageUrl, so we'll call adminDashboard directly
            if (window.adminDashboard && window.adminDashboard.showToast) {
                window.adminDashboard.showToast(message, type, null, duration, imageUrl);
            } else {
                window.AdminUtils.showToast(message, type);
            }
        } else if (window.adminDashboard && window.adminDashboard.showToast) {
            window.adminDashboard.showToast(message, type, null, duration, imageUrl);
        } else {
            // Fallback to alert if toast system is not available
            alert(message);
        }
    }

    // Helper function to setup focus management for modals
    function setupModalFocusHandling(modalEl) {
        if (!modalEl) return modalEl;

        // Check if listeners are already added (use a data attribute as flag)
        if (modalEl.dataset.focusHandlingSetup === 'true') {
            return modalEl;
        }

        // Mark as setup
        modalEl.dataset.focusHandlingSetup = 'true';

        // Add event listeners to handle focus when modal is hidden
        modalEl.addEventListener('hide.bs.modal', function(e) {
            // Remove focus from any element inside the modal before hiding
            const activeEl = document.activeElement;
            if (activeEl && modalEl.contains(activeEl)) {
                try {
                    activeEl.blur();
                } catch (err) {
                    // Ignore errors if blur fails
                }
            }
        }, { once: false });

        modalEl.addEventListener('hidden.bs.modal', function(e) {
            // Ensure focus is moved away after modal is hidden
            const activeEl = document.activeElement;
            if (activeEl && modalEl.contains(activeEl)) {
                try {
                    activeEl.blur();
                } catch (err) {
                    // Ignore errors
                }
            }
            // Try to focus body or remove focus completely
            try {
                // Use requestAnimationFrame to ensure this happens after Bootstrap's cleanup
                requestAnimationFrame(() => {
                    const stillActive = document.activeElement;
                    if (stillActive && modalEl.contains(stillActive)) {
                        stillActive.blur();
                    }
                });
            } catch (err) {
                // Ignore errors
            }
        }, { once: false });

        return modalEl;
    }

    function setCounter(pk, which, value) {
        const id = which === 'adults' ? `adults-total-count${pk}` : `additional-children-count${pk}`;
        const el = q(id);
        if (!el) return;
        const min = which === 'adults' ? 1 : 0;
        const v = Math.max(min, Math.min(MAX_ADDITIONAL, Number(value) || 0));
        el.value = String(v);
    }

    // Direct stepper API (used by inline onclicks in the template)
    function stepper(pk, action) {
        const p = String(pk || '');
        if (!p) return;

        if (action === 'adults-inc') setCounter(p, 'adults', getAdultsCount(p) + 1);
        if (action === 'adults-dec') setCounter(p, 'adults', getAdultsCount(p) - 1);
        if (action === 'children-inc') setCounter(p, 'children', getAdditionalChildrenCount(p) + 1);
        if (action === 'children-dec') setCounter(p, 'children', getAdditionalChildrenCount(p) - 1);

        updateSummary(p);
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
        console.log('initModal called with pk:', pk);

        // First, try to find the modal (may need to wait for DOM)
        let reservationModalEl = q(`hotelReservationModal${pk}`);

        // If not found, try with document.querySelector as fallback
        if (!reservationModalEl) {
            reservationModalEl = document.getElementById(`hotelReservationModal${pk}`);
        }

        // If still not found, try searching in all modals
        if (!reservationModalEl) {
            console.log('Trying to find modal in DOM...');
            reservationModalEl = document.querySelector(`[id="hotelReservationModal${pk}"]`);
        }

        if (!reservationModalEl) {
            console.error('Modal element not found: hotelReservationModal' + pk);
            console.log('Available modals:', Array.from(document.querySelectorAll('.modal')).map(m => m.id));
            return;
        }

        console.log('Modal element found:', reservationModalEl.id);

        if (!window.bootstrap?.Modal) {
            console.error('Bootstrap Modal not available');
            return;
        }

        try {
            // Check if modal is already visible
            const isVisible = reservationModalEl.classList.contains('show');

            // Setup focus handling for this modal
            setupModalFocusHandling(reservationModalEl);

            let modalInstance = bootstrap.Modal.getInstance(reservationModalEl);

            if (!modalInstance) {
                console.log('Creating new modal instance...');
                modalInstance = new bootstrap.Modal(reservationModalEl);
            }

            if (modalInstance && typeof modalInstance.show === 'function') {
                if (isVisible) {
                    // Modal is already open, just update content
                    console.log('Modal already visible, updating content...');
                    if (q(`adults-total-count${pk}`) && q(`additional-children-count${pk}`)) {
                        renderSelectedPlayers(pk);
                        updateSummary(pk);
                        console.log('Content updated successfully');
                    }
                } else {
                    // Modal is closed, open it and initialize
                    console.log('Showing modal...');

                    // Initialize elements AFTER modal is shown
                    reservationModalEl.addEventListener('shown.bs.modal', () => {
                        console.log('Modal shown, initializing elements...');

                        // Now the elements should exist
                        if (q(`adults-total-count${pk}`) && q(`additional-children-count${pk}`)) {
                            renderSelectedPlayers(pk);
                            updateSummary(pk);
                            console.log('Elements initialized successfully');
                        } else {
                            console.warn('Elements still not found after modal shown');
                        }
                    }, { once: true });

                    modalInstance.show();
                }
            } else {
                console.error('Modal instance invalid or show method not available');
            }
        } catch (e) {
            console.error('Error in initModal:', e);
        }
    }

    function showRooms(btnEl) {
        const pk = getPk(btnEl);
        if (!pk) return;
        const adults = totalAdults(pk);
        const addChildren = getAdditionalChildrenCount(pk);
        const players = getSelectedPlayers().length;
        const total = adults + addChildren + players;

        if (adults < 1) {
            showToast('At least one adult is required', 'warning');
            return;
        }
        if (players === 0 && addChildren === 0) {
            showToast('You must select at least one player or add at least one child', 'warning');
            return;
        }

        const reservationModalEl = q(`hotelReservationModal${pk}`);
        const roomsModalEl = q(`hotelRoomsModal${pk}`);
        if (!roomsModalEl) {
            showToast('Rooms modal not found', 'error');
            return;
        }

        const openRoomsModal = () => {
            // Filter + recommend inside the rooms modal
            filterAndRecommendRooms(roomsModalEl, total);

            if (!window.bootstrap?.Modal) return;
            // Setup focus handling for this modal
            setupModalFocusHandling(roomsModalEl);

            let inst = bootstrap.Modal.getInstance(roomsModalEl);
            if (!inst) inst = new bootstrap.Modal(roomsModalEl);
            inst.show();

            // Focus something inside rooms modal to avoid aria-hidden/focus warnings
            roomsModalEl.addEventListener('shown.bs.modal', () => {
                const closeBtn = roomsModalEl.querySelector('button.btn-close');
                if (closeBtn && typeof closeBtn.focus === 'function') closeBtn.focus();
            }, { once: true });
        };

        // Close reservation modal first
        if (reservationModalEl && window.bootstrap?.Modal && reservationModalEl.classList.contains('show')) {
            // Move focus out of the reservation modal before hiding it
            try {
                const active = document.activeElement;
                if (active && reservationModalEl.contains(active) && typeof active.blur === 'function') {
                    active.blur();
                }
                // Focus a safe element outside modals
                const sink = document.createElement('div');
                sink.tabIndex = -1;
                sink.setAttribute('aria-hidden', 'true');
                sink.style.cssText = 'position:fixed; width:1px; height:1px; left:-9999px; top:-9999px;';
                document.body.appendChild(sink);
                sink.focus();
                document.body.removeChild(sink);
            } catch (_) {}

            reservationModalEl.addEventListener('hidden.bs.modal', () => {
                openRoomsModal();
            }, { once: true });

            // Just get existing instance and hide it - don't try to create new one
            const modalInstance = bootstrap.Modal.getInstance(reservationModalEl);
            if (modalInstance && typeof modalInstance.hide === 'function') {
                try {
                    modalInstance.hide();
                } catch (e) {
                    console.warn('Error hiding modal:', e);
                    // Fallback: manually hide modal
                    reservationModalEl.classList.remove('show');
                    reservationModalEl.setAttribute('aria-hidden', 'true');
                    reservationModalEl.style.display = 'none';
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) backdrop.remove();
                    document.body.classList.remove('modal-open');
                    openRoomsModal();
                }
            } else {
                // No instance found, manually hide
                reservationModalEl.classList.remove('show');
                reservationModalEl.setAttribute('aria-hidden', 'true');
                reservationModalEl.style.display = 'none';
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) backdrop.remove();
                document.body.classList.remove('modal-open');
                openRoomsModal();
            }
            return;
        }

        openRoomsModal();
    }

    function filterAndRecommendRooms(containerEl, total) {
        if (!containerEl) return;

        const pk = containerEl.getAttribute('data-hotel-pk') || '';
        const noneMsg = containerEl.querySelector(`#rooms-none-msg${pk}`) || containerEl.querySelector('[data-nsc-rooms-none]');
        if (noneMsg) noneMsg.style.display = 'none';

        const roomListings = Array.from(containerEl.querySelectorAll('.room-listing-inline'));
        // Clear old recommendation
        roomListings.forEach(r => {
            r.classList.remove('nsc-room-recommended');
            const oldBadge = r.querySelector('.nsc-recommended-badge');
            if (oldBadge) oldBadge.remove();
        });

        const candidates = [];
        const hiddenRooms = [];

        roomListings.forEach(roomListing => {
            const capAttr = roomListing.getAttribute('data-room-capacity');
            const cap = parseInt(capAttr || '0', 10);
            const ok = cap >= total;

            if (ok) {
                const priceAttr = roomListing.getAttribute('data-room-price');
                const price = parseFloat(String(priceAttr || '0')) || 0;
                // Calculate recommendation score: lower is better
                // Priority: 1) Exact match, 2) Smallest waste, 3) Lowest price
                const waste = Math.max(0, cap - total);
                const isExactMatch = cap === total ? 0 : 1; // 0 = exact match (best), 1 = not exact
                const score = isExactMatch * 1000 + waste * 10 + price / 100; // Weight: exact match > waste > price
                candidates.push({ el: roomListing, cap: cap || 0, price, waste, isExactMatch, score });
            } else {
                hiddenRooms.push(roomListing);
            }
        });

        if (!candidates.length) {
            if (noneMsg) noneMsg.style.display = '';
            // Hide all rooms
            roomListings.forEach(r => r.style.display = 'none');
            return;
        }

        // Sort by recommendation score (lower is better)
        candidates.sort((a, b) => {
            if (a.score !== b.score) return a.score - b.score;
            // If scores are equal, prefer exact match
            if (a.isExactMatch !== b.isExactMatch) return a.isExactMatch - b.isExactMatch;
            // Then by price
            if (a.price !== b.price) return a.price - b.price;
            return 0;
        });

        // Get parent container to reorder
        const parentContainer = roomListings[0]?.parentElement;
        if (!parentContainer) return;

        // Hide rooms that don't fit
        hiddenRooms.forEach(room => {
            room.style.display = 'none';
        });

        // Reorder and show recommended rooms
        candidates.forEach((candidate, index) => {
            const roomEl = candidate.el;
            roomEl.style.display = '';

            // Mark top 3 as recommended
            if (index < 3) {
                roomEl.classList.add('nsc-room-recommended');

                // Add badge only to the first (most recommended)
                if (index === 0) {
                    const roomInfo = roomEl.querySelector('.room-info');
                    if (roomInfo && !roomInfo.querySelector('.nsc-recommended-badge')) {
                        const badge = document.createElement('div');
                        badge.className = 'nsc-recommended-badge';
                        badge.textContent = `⭐ Recommended for ${total} ${total === 1 ? 'guest' : 'guests'}`;
                        badge.style.cssText = 'background: linear-gradient(135deg, var(--mlb-blue) 0%, var(--mlb-light-blue) 100%); color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; margin-bottom: 8px; display: inline-block;';
                        roomInfo.insertBefore(badge, roomInfo.firstChild);
                    }
                }
            }

            // Move to correct position in DOM (append to maintain order)
            parentContainer.appendChild(roomEl);
        });
    }

    function renderGuestDetails(pk) {
        const selected = getSelectedPlayers();

        // Selected players form fields
        const selectedWrap = q(`guest-selected-players-wrap${pk}`);
        const selectedEl = q(`guest-selected-players${pk}`);
        if (selectedWrap && selectedEl) {
            if (selected.length === 0) {
                selectedWrap.style.display = 'none';
                selectedEl.innerHTML = '';
            } else {
                selectedWrap.style.display = 'block';
                selectedEl.innerHTML = '';

                // Get state to access player data
                const state = stateByPk.get(pk);
                const players = state?.guests?.filter(g => g.isPlayer) || [];

                selected.forEach((cb, idx) => {
                    const childItem = cb.closest('.child-item');
                    const nameDiv =
                        childItem?.querySelector('div[style*="font-weight: 700"][style*="color: var(--mlb-blue)"]') ||
                        childItem?.querySelector('div[style*="font-weight: 700"]');
                    const name = nameDiv ? nameDiv.textContent.trim() : 'Player';
                    const birth = cb.getAttribute('data-birth-date') || '';
                    const email = childItem?.getAttribute('data-child-email') || '';

                    // Try to get player data from state
                    const playerData = players[idx] || {};
                    const playerName = playerData.name || name;
                    const playerBirthDate = playerData.birthDate || birth;
                    const playerEmail = playerData.email || email;

                    // Determine if player is adult or child based on age or type
                    const playerAge = playerData.age;
                    const playerType = playerData.type || (playerAge && playerAge >= 18 ? 'adult' : 'child');

                    const block = document.createElement('div');
                    block.className = 'nsc-guest-player';
                    block.setAttribute('data-player-index', String(idx));
                    block.style.cssText = 'background:#ffffff; border:2px solid #e9ecef; border-radius:12px; padding:14px; margin-bottom:12px;';

                    block.innerHTML = `
                        <div style="font-weight:900; color: var(--mlb-blue); margin-bottom:10px;">
                            <i class="fas ${playerType === 'adult' ? 'fa-user' : 'fa-child'} me-2" style="color: var(--mlb-red);"></i>
                            ${playerType === 'adult' ? 'Player (Adult)' : 'Player (Child)'} ${idx + 1}
                        </div>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">Full Name *</label>
                                <input type="text" class="form-control nsc-player-name" required
                                       value="${escapeHtml(playerName)}"
                                       style="border-radius:10px; border:2px solid #e9ecef; padding:10px;">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">Date of Birth *</label>
                                <input type="date" class="form-control nsc-player-dob" required
                                       value="${playerBirthDate || ''}"
                                       style="border-radius:10px; border:2px solid #e9ecef; padding:10px;">
                            </div>
                            ${playerEmail ? `
                            <div class="col-md-12">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">Email</label>
                                <input type="email" class="form-control nsc-player-email"
                                       value="${escapeHtml(playerEmail)}"
                                       style="border-radius:10px; border:2px solid #e9ecef; padding:10px;">
                            </div>
                            ` : ''}
                        </div>
                    `;
                    selectedEl.appendChild(block);
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

        // Get current state or initialize
        if (!stateByPk.has(pk)) {
            stateByPk.set(pk, { rooms: [], guests: [], guestAssignments: {} }); // guestAssignments: { roomId: [guestIndex1, guestIndex2, ...] }
        }
        const state = stateByPk.get(pk);
        if (!state.rooms) {
            state.rooms = [];
        }
        if (!state.guestAssignments) {
            state.guestAssignments = {};
        }

        // Find the actual room listing element
        let roomListing = btnEl.closest('.room-listing-inline');
        if (!roomListing) {
            // If not found via closest, search in the rooms modal
            const roomsModalEl = q(`hotelRoomsModal${pk}`);
            roomListing = roomsModalEl?.querySelector(`[data-room-id="${roomId}"]`);
        }

        const capacity = parseInt(btnEl.getAttribute('data-room-capacity') || roomListing?.getAttribute('data-room-capacity') || '0', 10);

        // Check if room is already selected
        const roomIndex = state.rooms.findIndex(r => r.roomId === String(roomId));
        const isCurrentlySelected = roomIndex !== -1;

        // Calculate total capacity of all selected rooms
        const totalGuests = state.guests ? state.guests.length : totalPeople(pk);
        let totalCapacity = 0;
        state.rooms.forEach(r => {
            const roomEl = document.querySelector(`[data-room-id="${r.roomId}"]`);
            if (roomEl) {
                totalCapacity += parseInt(roomEl.getAttribute('data-room-capacity') || '0', 10);
            }
        });

        // Smart logic: Only suggest multiple rooms if single room can't accommodate
        // If removing a room, check if remaining capacity is still sufficient
        if (isCurrentlySelected) {
            // Check if removing this room would leave enough capacity
            const remainingCapacity = totalCapacity - capacity;
            if (remainingCapacity >= totalGuests && state.rooms.length > 1) {
                // Can remove this room, remaining rooms have enough capacity
            } else if (remainingCapacity < totalGuests) {
                // Can't remove, would exceed capacity
                showToast(`Cannot remove this room. Remaining capacity (${remainingCapacity}) would be insufficient for ${totalGuests} guests.`, 'warning', 4000);
                return;
            }
        } else {
            // Adding a new room - check if it's actually needed
            // Only warn if total capacity would still be insufficient, but allow selection
            const newTotalCapacity = totalCapacity + capacity;
            if (totalGuests > newTotalCapacity) {
                // Still not enough capacity even with this room
                const roomDetailUrl = btnEl.getAttribute('data-room-detail-url') || roomListing?.getAttribute('data-room-detail-url');
                let firstImageUrl = null;

                // Try to get image from already loaded room details
                const detailGallery = q(`rooms-detail-gallery${pk}`);
                if (detailGallery) {
                    const mainImg = detailGallery.querySelector('.nsc-room-detail-gallery-main img');
                    if (mainImg && mainImg.src) {
                        firstImageUrl = mainImg.src;
                    }
                }

                // Show toast
                if (firstImageUrl) {
                    showToast(`Adding this room would give you ${newTotalCapacity} total capacity, but you have ${totalGuests} guests. Please add another room or change to a room with higher capacity.`, 'warning', 6000, firstImageUrl);
                } else if (roomDetailUrl) {
                    fetch(roomDetailUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                        .then(res => res.ok ? res.json() : null)
                        .then(data => {
                            const imgUrl = (data && data.images && data.images.length > 0)
                                ? (data.images[0].image_url || data.images[0].url)
                                : null;
                            showToast(`Adding this room would give you ${newTotalCapacity} total capacity, but you have ${totalGuests} guests. Please add another room or change to a room with higher capacity.`, 'warning', 6000, imgUrl);
                        })
                        .catch(() => {
                            showToast(`Adding this room would give you ${newTotalCapacity} total capacity, but you have ${totalGuests} guests. Please add another room or change to a room with higher capacity.`, 'warning');
                        });
                } else {
                    showToast(`Adding this room would give you ${newTotalCapacity} total capacity, but you have ${totalGuests} guests. Please select more rooms or adjust guests.`, 'warning');
                }
                // Don't return - allow selection but show warning
            }
        }

        // Old single-room validation (removed - now we allow multiple rooms)
        const oldCapacityCheck = false;
        if (oldCapacityCheck && capacity && totalGuests > capacity) {
            // Get first room image for toast
            const roomDetailUrl = btnEl.getAttribute('data-room-detail-url') || roomListing?.getAttribute('data-room-detail-url');
            let firstImageUrl = null;

            // Try to get image from already loaded room details
            const detailGallery = q(`rooms-detail-gallery${pk}`);
            if (detailGallery) {
                const mainImg = detailGallery.querySelector('.nsc-room-detail-gallery-main img');
                if (mainImg && mainImg.src) {
                    firstImageUrl = mainImg.src;
                }
            }

            // Show toast immediately with image if available, or fetch it
            if (firstImageUrl) {
                showToast(`This room fits ${capacity} guests, but you have ${total} guests. Please adjust guests or choose another room.`, 'warning', 6000, firstImageUrl);
            } else if (roomDetailUrl) {
                // Fetch image quickly and show toast
                fetch(roomDetailUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                    .then(res => res.ok ? res.json() : null)
                    .then(data => {
                        const imgUrl = (data && data.images && data.images.length > 0)
                            ? (data.images[0].image_url || data.images[0].url)
                            : null;
                        showToast(`This room fits ${capacity} guests, but you have ${total} guests. Please adjust guests or choose another room.`, 'warning', 6000, imgUrl);
                    })
                    .catch(() => {
                        // Show toast without image if fetch fails
                        showToast(`This room fits ${capacity} guests, but you have ${total} guests. Please adjust guests or choose another room.`, 'warning');
                    });
            } else {
                // No image available, show toast without image
                showToast(`This room fits ${capacity} guests, but you have ${total} guests. Please adjust guests or choose another room.`, 'warning');
            }
            return;
        }
        const roomName = roomListing?.querySelector('.room-name')?.textContent?.trim() || 'Room';
        const roomFeatures = roomListing?.querySelector('.room-features')?.textContent?.trim() || '';
        const roomLabel = `${roomName}${roomFeatures ? ` • ${roomFeatures}` : ''}`;

        // Toggle room selection (add or remove from array)
        if (isCurrentlySelected) {
            // Check if removing this room would leave enough capacity
            const remainingCapacity = totalCapacity - capacity;
            if (remainingCapacity < totalGuests && state.rooms.length > 1) {
                showToast(`Cannot remove this room. Remaining capacity (${remainingCapacity}) would be insufficient for ${totalGuests} guests.`, 'warning', 4000);
                return;
            }

            // Remove room from selection
            state.rooms.splice(roomIndex, 1);
            // Remove guest assignments for this room
            delete state.guestAssignments[String(roomId)];
            if (roomListing) {
                roomListing.removeAttribute('data-selected');
            } else {
                const roomsModalEl = q(`hotelRoomsModal${pk}`);
                const foundRoom = roomsModalEl?.querySelector(`[data-room-id="${roomId}"]`);
                if (foundRoom) {
                    foundRoom.removeAttribute('data-selected');
                }
            }
            showToast(`Room "${roomLabel}" removed from selection`, 'info', 3000);
        } else {
            // Smart check: Only add if actually needed or user explicitly wants multiple rooms
            // If a single room can already accommodate all guests, warn but allow
            if (state.rooms.length > 0 && totalGuests <= totalCapacity) {
                const confirmAdd = confirm(`You already have enough capacity with ${state.rooms.length} room${state.rooms.length > 1 ? 's' : ''} (${totalCapacity} guests). Do you want to add another room anyway?`);
                if (!confirmAdd) {
                    return;
                }
            }

            // Add room to selection
            state.rooms.push({
                roomId: String(roomId),
                roomLabel: roomLabel,
                capacity: capacity
            });
            // Initialize empty guest assignments for this room
            state.guestAssignments[String(roomId)] = [];

            if (roomListing) {
                roomListing.setAttribute('data-selected', 'true');
            } else {
                const roomsModalEl = q(`hotelRoomsModal${pk}`);
                const foundRoom = roomsModalEl?.querySelector(`[data-room-id="${roomId}"]`);
                if (foundRoom) {
                    foundRoom.setAttribute('data-selected', 'true');
                }
            }
            showToast(`Room "${roomLabel}" added to selection (${state.rooms.length} room${state.rooms.length > 1 ? 's' : ''} selected)`, 'success', 3000);
        }

        // Auto-distribute guests if not manually assigned yet
        autoDistributeGuests(pk);

        // Ensure room element has rules before calculating price
        // If rules are missing, try to get them from the detail modal data
        if (roomListing && !roomListing.getAttribute('data-room-rules')) {
            const roomDetailUrl = roomListing.getAttribute('data-room-detail-url');
            if (roomDetailUrl) {
                // Fetch room details to get rules if not already loaded
                fetch(roomDetailUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                    .then(res => res.ok ? res.json() : null)
                    .then(roomData => {
                        if (roomData) {
                            if (roomData.rules && Array.isArray(roomData.rules)) {
                                roomListing.setAttribute('data-room-rules', JSON.stringify(roomData.rules));
                                console.log('selectRoom: Loaded and stored rules from API:', roomData.rules);
                            }
                            if (roomData.price_includes_guests) {
                                roomListing.setAttribute('data-room-includes-guests', String(roomData.price_includes_guests));
                            }
                            if (roomData.additional_guest_price !== undefined) {
                                roomListing.setAttribute('data-room-additional-guest-price', String(roomData.additional_guest_price));
                            }
                            if (roomData.capacity !== undefined) {
                                roomListing.setAttribute('data-room-capacity', String(roomData.capacity));
                            }
                            // Update price calculation after loading rules
                            updateRoomsPriceCalculation(pk);
                        }
                    })
                    .catch(err => console.warn('selectRoom: Error fetching room details for rules:', err));
            }
        }

        // Update price calculation
        updateRoomsPriceCalculation(pk);
        validateRoomSelection(pk);

        // Show success message
        const statusEl = q(`rooms-selection-status${pk}`);
        if (statusEl) {
            statusEl.style.display = 'block';
            statusEl.style.background = '#d4edda';
            statusEl.style.border = '1px solid #c3e6cb';
            statusEl.style.color = '#155724';
            statusEl.innerHTML = `<i class="fas fa-check-circle me-1"></i><strong>Room selected!</strong> Ready to continue.`;
        }
    }

    function backToGuests(pk) {
        const p = String(pk || '');
        if (!p) return;
        const roomsModalEl = q(`hotelRoomsModal${p}`);
        const reservationModalEl = q(`hotelReservationModal${p}`);
        if (!roomsModalEl || !reservationModalEl || !window.bootstrap?.Modal) return;

        const openReservation = () => {
            // Setup focus handling for this modal
            setupModalFocusHandling(reservationModalEl);

            let inst = bootstrap.Modal.getInstance(reservationModalEl);
            if (!inst) inst = new bootstrap.Modal(reservationModalEl);
            inst.show();
        };

        if (roomsModalEl.classList.contains('show')) {
            roomsModalEl.addEventListener('hidden.bs.modal', () => openReservation(), { once: true });
            const inst = bootstrap.Modal.getInstance(roomsModalEl);
            if (inst) inst.hide();
            else openReservation();
        } else {
            openReservation();
        }
    }

    function backToRooms(pk) {
        const p = String(pk || '');
        if (!p) return;
        const guestModalEl = q(`hotelGuestDetailsModal${p}`);
        const roomsModalEl = q(`hotelRoomsModal${p}`);
        if (!guestModalEl || !roomsModalEl || !window.bootstrap?.Modal) return;

        const openRooms = () => {
            // Setup focus handling for this modal
            const actualRoomsModal = setupModalFocusHandling(roomsModalEl) || roomsModalEl;
            let inst = bootstrap.Modal.getInstance(actualRoomsModal);
            if (!inst) inst = new bootstrap.Modal(actualRoomsModal);
            inst.show();
        };

        if (guestModalEl.classList.contains('show')) {
            guestModalEl.addEventListener('hidden.bs.modal', () => openRooms(), { once: true });
            const inst = bootstrap.Modal.getInstance(guestModalEl);
            if (inst) inst.hide();
            else openRooms();
        } else {
            openRooms();
        }
    }

    async function openRoomDetail(fromEl) {
        if (!fromEl) {
            console.warn('openRoomDetail: fromEl is null');
            return;
        }
        // Support both button clicks and room card clicks
        const roomEl = fromEl.classList?.contains('room-listing-inline') ? fromEl : fromEl.closest('.room-listing-inline');
        if (!roomEl) {
            console.warn('openRoomDetail: room element not found');
            return;
        }
        const url = roomEl.getAttribute('data-room-detail-url') || fromEl.getAttribute('data-room-detail-url') || fromEl.getAttribute('data-room-detail');
        if (!url) {
            console.warn('openRoomDetail: No URL found', roomEl);
            return;
        }

        // Get room ID and hotel PK
        const roomId = roomEl.getAttribute('data-room-id');
        const pk = getPk(roomEl) || getPk(fromEl) || roomEl.closest?.('.modal[data-hotel-pk]')?.getAttribute?.('data-hotel-pk');
        console.log('openRoomDetail: pk =', pk, 'roomId =', roomId, 'url =', url);

        if (!pk || !roomId) {
            console.warn('openRoomDetail: Missing pk or roomId');
            return;
        }

        // Open the room detail modal
        const modalEl = q(`roomDetailModal${pk}`);
        if (!modalEl) {
            console.warn('openRoomDetail: Modal not found', `roomDetailModal${pk}`);
            return;
        }

        // Get modal elements
        const titleEl = q(`room-detail-modal-title${pk}`);
        const subtitleEl = q(`room-detail-modal-subtitle${pk}`);
        const descEl = q(`room-detail-modal-description${pk}`);
        const capEl = q(`room-detail-modal-capacity${pk}`);
        const priceEl = q(`room-detail-modal-price${pk}`);
        const includesGuestsEl = q(`room-detail-modal-includes-guests${pk}`);
        const additionalPriceEl = q(`room-detail-modal-additional-price${pk}`);
        const breakfastEl = q(`room-detail-modal-breakfast${pk}`);
        const roomNumberEl = q(`room-detail-modal-room-number${pk}`);
        const galleryEl = q(`room-detail-modal-gallery${pk}`);
        const amenitiesEl = q(`room-detail-modal-amenities${pk}`);
        const rulesEl = q(`room-detail-modal-rules${pk}`);
        const rulesContainerEl = q(`room-detail-modal-rules-container${pk}`);
        const rulesValidationEl = q(`room-detail-modal-rules-validation${pk}`);
        const selectBtn = q(`room-detail-modal-select-btn${pk}`);

        // Reset UI
        if (titleEl) titleEl.textContent = 'Loading...';
        if (subtitleEl) subtitleEl.textContent = '';
        if (descEl) descEl.innerHTML = '';
        if (capEl) capEl.textContent = '-';
        if (priceEl) priceEl.textContent = '-';
        if (includesGuestsEl) includesGuestsEl.textContent = '-';
        if (additionalPriceEl) additionalPriceEl.textContent = '-';
        if (breakfastEl) breakfastEl.textContent = '-';
        if (roomNumberEl) roomNumberEl.textContent = '-';
        if (amenitiesEl) amenitiesEl.innerHTML = '';
        if (rulesEl) rulesEl.innerHTML = '';
        if (rulesValidationEl) rulesValidationEl.innerHTML = '';
        if (rulesContainerEl) rulesContainerEl.style.display = 'none';
        if (galleryEl) galleryEl.innerHTML = `<div style="padding: 18px; color: #6c757d; text-align: center;">Loading...</div>`;

        // Store room ID and PK on select button for later use
        if (selectBtn) {
            selectBtn.setAttribute('data-room-id', roomId);
            selectBtn.setAttribute('data-hotel-pk', pk);
            selectBtn.setAttribute('data-room-capacity', roomEl.getAttribute('data-room-capacity') || '0');
        }

        // Open modal
        if (!window.bootstrap?.Modal) {
            console.error('Bootstrap Modal not available');
            return;
        }
        // Setup focus handling for this modal
        setupModalFocusHandling(modalEl);

        let modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (!modalInstance) {
            modalInstance = new bootstrap.Modal(modalEl, { backdrop: true, keyboard: true, focus: true });
        }

        // Add blur effect to existing backdrop ONLY when Room Detail modal opens
        const applyBlur = function() {
            // Wait a bit for Bootstrap to create the new backdrop
            setTimeout(() => {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                if (backdrops.length > 1) {
                    // Apply blur to the first backdrop (the one from the parent modal - Available Rooms)
                    const firstBackdrop = backdrops[0];
                    firstBackdrop.style.backdropFilter = 'blur(8px)';
                    firstBackdrop.style.webkitBackdropFilter = 'blur(8px)';
                    firstBackdrop.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                    firstBackdrop.style.zIndex = '1055'; // Behind the Room Detail modal backdrop

                    // Ensure the second backdrop (Room Detail) doesn't have blur and is above
                    if (backdrops[1]) {
                        backdrops[1].style.backdropFilter = '';
                        backdrops[1].style.webkitBackdropFilter = '';
                        backdrops[1].style.zIndex = '1059'; // Above the first backdrop
                    }
                }
                // Ensure the modal itself has the highest z-index
                if (modalEl) {
                    modalEl.style.zIndex = '1060';
                }
            }, 100);
        };

        // Remove blur when Room Detail modal closes
        const removeBlur = function() {
            const backdrops = document.querySelectorAll('.modal-backdrop');
            // Only restore the first backdrop (parent modal - Available Rooms)
            if (backdrops.length > 0) {
                const firstBackdrop = backdrops[0];
                firstBackdrop.style.backdropFilter = '';
                firstBackdrop.style.webkitBackdropFilter = '';
                firstBackdrop.style.backgroundColor = '';
                firstBackdrop.style.zIndex = '';
            }
        };

        // Apply blur ONLY when Room Detail modal is shown
        modalEl.addEventListener('shown.bs.modal', applyBlur, { once: true });

        // Remove blur ONLY when Room Detail modal is hidden
        modalEl.addEventListener('hidden.bs.modal', removeBlur, { once: true });

        modalInstance.show();

        try {
            console.log('openRoomDetail: Fetching room details from', url);
            const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            if (!res.ok) throw new Error(`Request failed: ${res.status}`);
            const data = await res.json();
            console.log('openRoomDetail: Data received', data);
            console.log('openRoomDetail: Rules in data:', data.rules);

            // Store room data attributes on the room element FIRST, before updating UI
            if (roomEl) {
                if (data.price_includes_guests) {
                    roomEl.setAttribute('data-room-includes-guests', String(data.price_includes_guests));
                }
                if (data.additional_guest_price !== undefined) {
                    roomEl.setAttribute('data-room-additional-guest-price', String(data.additional_guest_price));
                }
                if (data.capacity !== undefined) {
                    roomEl.setAttribute('data-room-capacity', String(data.capacity));
                }
                if (data.rules && Array.isArray(data.rules)) {
                    console.log('openRoomDetail: Storing rules on roomEl:', data.rules);
                    roomEl.setAttribute('data-room-rules', JSON.stringify(data.rules));
                } else {
                    console.warn('openRoomDetail: No rules in data or not an array:', data.rules);
                }
            } else {
                console.warn('openRoomDetail: roomEl not found, cannot store room data');
            }

            // Update title and subtitle
            if (titleEl) {
                const roomName = data.name || data.room_type || 'Room';
                const roomNumber = data.room_number ? ` • ${data.room_number}` : '';
                titleEl.textContent = `${roomName}${roomNumber}`;
            }
            if (subtitleEl) {
                subtitleEl.textContent = data.hotel?.name ? data.hotel.name : '';
                subtitleEl.style.fontWeight = '400';
            }

            // Update description
            if (descEl) {
                if (data.description && data.description.trim()) {
                    descEl.innerHTML = `<div style="white-space: pre-wrap; line-height: 1.6; font-weight: 400;">${escapeHtml(data.description)}</div>`;
                } else {
                    descEl.innerHTML = `<div style="color: #6c757d; font-style: italic; font-size: 0.85rem; font-weight: 400;">No description available.</div>`;
                }
            }

            // Update capacity and price
            if (capEl) capEl.textContent = `${data.capacity ?? '-'} ${data.capacity === 1 ? 'person' : 'people'}`;
            if (priceEl) priceEl.textContent = `$${parseFloat(data.price_per_night || 0).toFixed(2)}`;

            // Update additional information
            const includesGuestsEl = q(`room-detail-modal-includes-guests${pk}`);
            if (includesGuestsEl) {
                const includes = data.price_includes_guests || 1;
                includesGuestsEl.textContent = `${includes} ${includes === 1 ? 'guest' : 'guests'}`;
            }

            const additionalPriceEl = q(`room-detail-modal-additional-price${pk}`);
            if (additionalPriceEl) {
                const addPrice = parseFloat(data.additional_guest_price || 0);
                additionalPriceEl.textContent = addPrice > 0 ? `$${addPrice.toFixed(2)}/night` : 'Included';
            }

            const breakfastEl = q(`room-detail-modal-breakfast${pk}`);
            if (breakfastEl) {
                breakfastEl.textContent = data.breakfast_included ? 'Included' : 'Not included';
                breakfastEl.style.color = data.breakfast_included ? 'var(--mlb-blue)' : '#6c757d';
            }

            const roomNumberEl = q(`room-detail-modal-room-number${pk}`);
            if (roomNumberEl) {
                roomNumberEl.textContent = data.room_number || '-';
            }

            // Gallery (masonry layout)
            if (galleryEl) {
                const images = Array.isArray(data.images) ? data.images : [];
                if (!images.length) {
                    galleryEl.innerHTML = `<div style="padding: 18px; color: #6c757d; text-align: center; font-size: 0.85rem;">No images available.</div>`;
                } else {
                    // Store images globally for lightbox
                    if (!window.roomImages) window.roomImages = {};
                    window.roomImages[pk] = images;

                    // Create masonry gallery with better organization
                    // Pre-calculate heights for better distribution
                    const heights = [200, 180, 220, 190, 210, 200, 185, 215]; // Alternating heights for better balance
                    const masonryItems = images.map((img, idx) => {
                        const imgUrl = img.image_url || img.url;
                        const imgAlt = escapeHtml(img.title || img.alt || `Room image ${idx + 1}`);
                        // Use alternating heights for better visual balance
                        const height = heights[idx % heights.length];
                        const rowSpan = Math.ceil(height / 10);
                        return `
                            <div class="nsc-masonry-item" data-idx="${idx}" onclick="window.NSC_HotelReservation?.openLightbox?.('${pk}', ${idx});" style="grid-row-end: span ${rowSpan};">
                                <img src="${imgUrl}" alt="${imgAlt}" loading="lazy" style="height: ${height}px; width: 100%; object-fit: cover;">
                            </div>
                        `;
                    }).join('');

                    galleryEl.innerHTML = `<div class="nsc-masonry-gallery">${masonryItems}</div>`;

                    // After images load, adjust masonry layout
                    setTimeout(() => {
                        const masonryGallery = galleryEl.querySelector('.nsc-masonry-gallery');
                        if (masonryGallery) {
                            const items = masonryGallery.querySelectorAll('.nsc-masonry-item img');
                            items.forEach((img, idx) => {
                                img.onload = function() {
                                    // Adjust height based on actual image aspect ratio
                                    const naturalHeight = img.naturalHeight;
                                    const naturalWidth = img.naturalWidth;
                                    if (naturalWidth > 0) {
                                        const aspectRatio = naturalHeight / naturalWidth;
                                        const containerWidth = img.parentElement.offsetWidth || 180;
                                        const calculatedHeight = containerWidth * aspectRatio;
                                        const clampedHeight = Math.max(150, Math.min(280, calculatedHeight));
                                        img.style.height = `${clampedHeight}px`;
                                        const rowSpan = Math.ceil(clampedHeight / 10);
                                        img.parentElement.style.gridRowEnd = `span ${rowSpan}`;
                                    }
                                };
                                // Trigger if already loaded
                                if (img.complete) img.onload();
                            });
                        }
                    }, 100);
                }
            }

            // Reglas de Ocupación
            if (rulesEl && rulesContainerEl) {
                const rules = Array.isArray(data.rules) ? data.rules : [];
                if (rules.length > 0) {
                    rulesContainerEl.style.display = 'block';
                    rulesEl.innerHTML = rules.map(rule => {
                        const desc = rule.description ||
                            `Adults: ${rule.min_adults}-${rule.max_adults} • Children: ${rule.min_children}-${rule.max_children}`;
                        return `
                            <div style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 10px; margin-bottom: 8px; font-size: 0.85rem;">
                                <div style="font-weight: 600; color: var(--mlb-blue); margin-bottom: 4px;">
                                    <i class="fas fa-check-circle me-1" style="color: var(--mlb-red);"></i>${escapeHtml(desc)}
                                </div>
                                <div style="color: #6c757d; font-size: 0.8rem; font-weight: 400;">
                                    Adults: ${rule.min_adults}-${rule.max_adults} • Children: ${rule.min_children}-${rule.max_children}
                                </div>
                            </div>
                        `;
                    }).join('');

                    // Validación de reglas con los huéspedes seleccionados
                    if (rulesValidationEl) {
                        const state = stateByPk.get(pk);
                        const adults = state?.guests?.filter(g => g.type === 'adult').length || 0;
                        const children = state?.guests?.filter(g => g.type === 'child').length || 0;

                        const validRules = rules.filter(rule => {
                            if (rule.hasOwnProperty('is_active') && !rule.is_active) return false;
                            const minAdults = parseInt(rule.min_adults) || 0;
                            const maxAdults = parseInt(rule.max_adults) || 999;
                            const minChildren = parseInt(rule.min_children) || 0;
                            const maxChildren = parseInt(rule.max_children) || 999;
                            return adults >= minAdults && adults <= maxAdults &&
                                   children >= minChildren && children <= maxChildren;
                        });

                        if (validRules.length > 0) {
                            rulesValidationEl.innerHTML = `
                                <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 10px; color: #155724; font-size: 0.85rem;">
                                    <i class="fas fa-check-circle me-1"></i>
                                    <strong>Valid:</strong> Your selection (${adults} adults, ${children} children) matches the occupancy rules.
                                </div>
                            `;
                        } else {
                            rulesValidationEl.innerHTML = `
                                <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 10px; color: #856404; font-size: 0.85rem;">
                                    <i class="fas fa-exclamation-triangle me-1"></i>
                                    <strong>Warning:</strong> Your selection (${adults} adults, ${children} children) does not match any occupancy rule.
                                </div>
                            `;
                        }
                    }
                } else {
                    rulesContainerEl.style.display = 'none';
                }
            }

            // Amenities (horizontal layout)
            if (amenitiesEl) {
                const a = Array.isArray(data.amenities) ? data.amenities : [];
                if (a.length > 0) {
                    amenitiesEl.innerHTML = a.map(am => `
                        <div class="nsc-pill" style="font-size: 0.8rem; padding: 6px 12px; background: white; border: 1px solid #e9ecef; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s ease;">
                            <i class="${escapeHtml(am.icon_class || 'fas fa-check')}" style="color: var(--mlb-red); font-size: 0.75rem;"></i>
                            <span style="font-weight: 500;">${escapeHtml(am.name || '')}</span>
                        </div>
                    `).join('');
                } else {
                    amenitiesEl.innerHTML = `<div style="color:#6c757d; font-size: 0.85rem; font-style: italic;">No amenities listed.</div>`;
                }
            }

            // Set up select button
            if (selectBtn) {
                selectBtn.onclick = function() {
                    // Find the actual room listing element in the Available Rooms modal
                    const roomsModalEl = q(`hotelRoomsModal${pk}`);
                    const actualRoomEl = roomsModalEl?.querySelector(`[data-room-id="${roomId}"]`);

                    if (actualRoomEl) {
                        // Ensure all room data attributes are set on the actual room element
                        if (data.price_includes_guests) {
                            actualRoomEl.setAttribute('data-room-includes-guests', String(data.price_includes_guests));
                        }
                        if (data.additional_guest_price !== undefined) {
                            actualRoomEl.setAttribute('data-room-additional-guest-price', String(data.additional_guest_price));
                        }
                        if (data.capacity !== undefined) {
                            actualRoomEl.setAttribute('data-room-capacity', String(data.capacity));
                        }
                        if (data.rules && Array.isArray(data.rules)) {
                            console.log('selectRoom from modal: Storing rules on actualRoomEl:', data.rules);
                            actualRoomEl.setAttribute('data-room-rules', JSON.stringify(data.rules));
                        } else {
                            console.warn('selectRoom from modal: No rules in data or not an array:', data.rules);
                        }

                        // Ensure price is also set if not already present
                        if (!actualRoomEl.getAttribute('data-room-price') && data.price_per_night) {
                            actualRoomEl.setAttribute('data-room-price', String(data.price_per_night));
                        }

                        // Create a button element to pass to selectRoom
                        const btn = document.createElement('button');
                        btn.setAttribute('data-room-id', roomId);
                        btn.setAttribute('data-hotel-pk', pk);
                        btn.setAttribute('data-room-capacity', actualRoomEl.getAttribute('data-room-capacity') || '0');
                        btn.setAttribute('data-room-price', actualRoomEl.getAttribute('data-room-price') || '0');
                        btn.closest = function(selector) {
                            return actualRoomEl.closest(selector) || actualRoomEl;
                        };

                        // Remove focus from button before closing modal
                        if (document.activeElement && document.activeElement.blur) {
                            document.activeElement.blur();
                        }

                        // Close detail modal first
                        modalInstance.hide();

                        // Wait a bit for modal to close, then select room
                        setTimeout(() => {
                            selectRoom(btn);
                            // Force update price calculation after selection
                            setTimeout(() => {
                                updateRoomsPriceCalculation(pk);
                            }, 50);
                        }, 100);
                    } else {
                        // Fallback: create button with data from modal and store in state
                        const btn = document.createElement('button');
                        btn.setAttribute('data-room-id', roomId);
                        btn.setAttribute('data-hotel-pk', pk);
                        btn.setAttribute('data-room-capacity', String(data.capacity || '0'));
                        btn.setAttribute('data-room-price', String(data.price_per_night || '0'));

                        // Store room data in a temporary element for price calculation
                        if (!stateByPk.has(pk)) {
                            stateByPk.set(pk, { rooms: [], guests: [] });
                        }
                        const state = stateByPk.get(pk);
                        if (!state.rooms) {
                            state.rooms = [];
                        }
                        // Check if room is already in selection
                        const existingIndex = state.rooms.findIndex(r => r.roomId === String(roomId));
                        if (existingIndex === -1) {
                            state.rooms.push({
                                roomId: String(roomId),
                                roomLabel: data.name || data.room_type || 'Room',
                                capacity: data.capacity || 0
                            });
                        }

                        // Create a temporary room element with all data for price calculation
                        const tempRoomEl = document.createElement('div');
                        tempRoomEl.setAttribute('data-room-id', roomId);
                        tempRoomEl.setAttribute('data-room-price', String(data.price_per_night || '0'));
                        tempRoomEl.setAttribute('data-room-includes-guests', String(data.price_includes_guests || 1));
                        tempRoomEl.setAttribute('data-room-additional-guest-price', String(data.additional_guest_price || 0));
                        tempRoomEl.setAttribute('data-room-capacity', String(data.capacity || '0'));
                        if (data.rules && Array.isArray(data.rules)) {
                            tempRoomEl.setAttribute('data-room-rules', JSON.stringify(data.rules));
                        }
                        tempRoomEl.style.display = 'none';
                        document.body.appendChild(tempRoomEl);

                        // Close detail modal
                        // Remove focus from button before closing modal
                        if (document.activeElement && document.activeElement.blur) {
                            document.activeElement.blur();
                        }

                        modalInstance.hide();

                        // Wait a bit, then select room and update price
                        setTimeout(() => {
                            selectRoom(btn);
                            // Update price calculation after selection
                            updateRoomsPriceCalculation(pk);
                            // Remove temp element after a delay
                            setTimeout(() => {
                                if (tempRoomEl.parentNode) {
                                    tempRoomEl.parentNode.removeChild(tempRoomEl);
                                }
                            }, 1000);
                        }, 100);
                    }
                };
            }

            console.log('openRoomDetail: Successfully rendered room details in modal');
        } catch (err) {
            console.error('openRoomDetail: Error loading room details', err);
            if (galleryEl) {
                galleryEl.innerHTML = `<div style="padding: 18px; color: #b30029; font-weight: 800; text-align: center;">Failed to load room details. Please try again.</div>`;
            }
            if (titleEl) titleEl.textContent = 'Error loading room';
            if (descEl) descEl.innerHTML = `<div style="color: #b30029; font-size: 0.85rem;">Error: ${escapeHtml(err.message || 'Unknown error')}</div>`;
        }
    }

    // NOTE: Stepper buttons are handled via inline onclicks calling stepper(pk, action)

    // Keep players list + totals synced
    document.addEventListener('change', (e) => {
        if (!e.target?.classList?.contains('child-checkbox')) return;
        // update any open reservation modal(s) - only if already visible
        document.querySelectorAll('.modal.show[id^=\"hotelReservationModal\"][data-hotel-pk]').forEach(modalEl => {
            const pk = modalEl.getAttribute('data-hotel-pk');
            if (pk) {
                // Only update content, don't open the modal
                renderSelectedPlayers(pk);
                updateSummary(pk);
            }
        });
    });

    // Bootstrap modal hook
    document.addEventListener('shown.bs.modal', (e) => {
        const modalEl = e.target;
        if (!modalEl || !modalEl.classList?.contains('modal') || !modalEl.id || !modalEl.id.startsWith('hotelReservationModal')) return;
        const pk = modalEl.getAttribute('data-hotel-pk');
        if (pk) initModal(String(pk));
    });

    // Guest details form: add to checkout card instead of creating reservation
    document.addEventListener('submit', (e) => {
        const form = e.target;
        if (!(form instanceof HTMLFormElement)) return;
        if (!form.id || !form.id.startsWith('guest-details-form')) return;

        // Prevent default form submission
        e.preventDefault();

        const pk = form.id.replace('guest-details-form', '');
        if (!pk) return;

        const state = stateByPk.get(pk);
        if (!state || !state.rooms || state.rooms.length === 0) {
            showToast('No rooms selected', 'error');
            return;
        }

        // Get all guest data
        const mainContactName = form.querySelector('input[name="guest_name"]')?.value?.trim() || '';
        const mainContactEmail = form.querySelector('input[name="guest_email"]')?.value?.trim() || '';
        const mainContactPhone = form.querySelector('input[name="guest_phone"]')?.value?.trim() || '';

        // Get selected players data from form fields
        const players = [];
        const playerBlocks = form.querySelectorAll('.nsc-guest-player');
        playerBlocks.forEach(block => {
            const nameInput = block.querySelector('.nsc-player-name');
            const dobInput = block.querySelector('.nsc-player-dob');
            const emailInput = block.querySelector('.nsc-player-email');

            if (nameInput && nameInput.value.trim()) {
                players.push({
                    name: nameInput.value.trim(),
                    dob: dobInput ? dobInput.value : '',
                    email: emailInput ? emailInput.value.trim() : '',
                    type: 'player'
                });
            }
        });

        // Get additional adults
        const additionalAdults = [];
        form.querySelectorAll('.nsc-guest-adult').forEach(el => {
            const name = el.querySelector('.nsc-adult-name')?.value?.trim() || '';
            const dob = el.querySelector('.nsc-adult-dob')?.value?.trim() || '';
            if (name) {
                additionalAdults.push({ name, dob, type: 'adult' });
            }
        });

        // Get additional children
        const additionalChildren = [];
        form.querySelectorAll('.nsc-guest-child').forEach(el => {
            const name = el.querySelector('.nsc-child-name')?.value?.trim() || '';
            const dob = el.querySelector('.nsc-child-dob')?.value?.trim() || '';
            if (name) {
                additionalChildren.push({ name, dob, type: 'child' });
            }
        });

        // Calculate total price from state
        const roomsModalEl = q(`hotelRoomsModal${pk}`);
        let totalPrice = 0;
        const roomDetails = [];

        state.rooms.forEach(room => {
            const roomEl = roomsModalEl?.querySelector(`[data-room-id="${room.roomId}"]`) ||
                          document.querySelector(`[data-room-id="${room.roomId}"]`);
            if (roomEl) {
                const roomPrice = parseFloat(roomEl.getAttribute('data-room-price') || '0');
                const roomIncludesGuests = parseInt(roomEl.getAttribute('data-room-includes-guests') || '1');
                const additionalGuestPrice = parseFloat(roomEl.getAttribute('data-room-additional-guest-price') || '0');
                const roomCapacity = parseInt(roomEl.getAttribute('data-room-capacity') || '0');

                // Get assigned guests for this room
                const assignedGuestIndices = state.guestAssignments[room.roomId] || [];
                const guestsForThisRoom = assignedGuestIndices.length;
                const actualGuestsForRoom = Math.min(guestsForThisRoom, roomCapacity);
                const additionalGuestsForRoom = Math.max(0, actualGuestsForRoom - roomIncludesGuests);
                const additionalCostForRoom = additionalGuestsForRoom > 0 ? additionalGuestPrice * additionalGuestsForRoom : 0;
                const roomTotal = roomPrice + additionalCostForRoom;

                totalPrice += roomTotal;

                roomDetails.push({
                    roomId: room.roomId,
                    roomLabel: room.roomLabel,
                    price: roomTotal,
                    guests: actualGuestsForRoom,
                    capacity: roomCapacity
                });
            }
        });

        // Add hotel reservation to checkout card
        addHotelReservationToCheckout(pk, {
            hotelPk: pk,
            rooms: roomDetails,
            mainContact: {
                name: mainContactName,
                email: mainContactEmail,
                phone: mainContactPhone
            },
            players: players,
            additionalAdults: additionalAdults,
            additionalChildren: additionalChildren,
            totalPrice: totalPrice,
            checkIn: form.querySelector('input[name="check_in"]')?.value || '',
            checkOut: form.querySelector('input[name="check_out"]')?.value || ''
        });

        // Close modal
        const guestModalEl = q(`hotelGuestDetailsModal${pk}`);
        if (guestModalEl && window.bootstrap?.Modal) {
            const modalInstance = bootstrap.Modal.getInstance(guestModalEl);
            if (modalInstance) {
                modalInstance.hide();
            }
        }

        showToast('Hotel reservation added to checkout', 'success');
    });

    // Add hotel reservation to checkout card
    function addHotelReservationToCheckout(pk, reservationData) {
        const checkoutCard = document.querySelector('.checkout-card');
        if (!checkoutCard) {
            console.error('Checkout card not found');
            return;
        }

        // Create hotel reservation section
        const hotelSection = document.createElement('div');
        hotelSection.className = 'hotel-reservation-item mb-3';
        hotelSection.setAttribute('data-hotel-pk', pk);
        hotelSection.style.cssText = 'border-top: 2px solid #e9ecef; padding-top: 15px; margin-top: 15px;';

        let html = `
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border: 2px solid #e9ecef; border-radius: 12px; padding: 15px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <h6 style="font-weight: 800; color: var(--mlb-blue); font-size: 0.95rem; margin: 0;">
                        <i class="fas fa-hotel me-2" style="color: var(--mlb-red);"></i>Hotel Stay
                    </h6>
                    <button type="button" class="btn-remove-hotel" onclick="this.closest('.hotel-reservation-item').remove(); updateCheckoutTotal();"
                            style="background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; cursor: pointer;">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
        `;

        // Add room details
        reservationData.rooms.forEach((room, idx) => {
            html += `
                <div style="margin-bottom: 10px; padding: 10px; background: white; border-radius: 8px; border-left: 3px solid var(--mlb-blue);">
                    <div style="font-weight: 700; color: var(--mlb-blue); font-size: 0.85rem; margin-bottom: 4px;">
                        ${escapeHtml(room.roomLabel)} (${room.guests}/${room.capacity} guests)
                    </div>
                    <div style="font-size: 0.8rem; color: #6c757d;">
                        Check-in: ${reservationData.checkIn || 'N/A'} • Check-out: ${reservationData.checkOut || 'N/A'}
                    </div>
                    <div style="font-weight: 700; color: var(--mlb-red); font-size: 0.9rem; margin-top: 4px;">
                        $${room.price.toFixed(2)}/night
                    </div>
                </div>
            `;
        });

        // Add guests summary
        const totalGuests = reservationData.players.length + reservationData.additionalAdults.length + reservationData.additionalChildren.length + 1; // +1 for main contact
        html += `
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e9ecef;">
                <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 4px;">
                    <strong>Main Contact:</strong> ${escapeHtml(reservationData.mainContact.name)}${reservationData.mainContact.email ? ` (${escapeHtml(reservationData.mainContact.email)})` : ''}
                </div>
                <div style="font-size: 0.8rem; color: #6c757d;">
                    <strong>Total Guests:</strong> ${totalGuests} (${reservationData.players.length} player${reservationData.players.length !== 1 ? 's' : ''}, ${reservationData.additionalAdults.length} additional adult${reservationData.additionalAdults.length !== 1 ? 's' : ''}, ${reservationData.additionalChildren.length} additional child${reservationData.additionalChildren.length !== 1 ? 'ren' : ''})
                </div>
            </div>
        `;

        // Add total price
        html += `
            <div style="margin-top: 12px; padding-top: 12px; border-top: 2px solid var(--mlb-red); display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 800; color: var(--mlb-blue); font-size: 1rem;">Total:</span>
                <span class="hotel-reservation-total" style="font-weight: 800; color: var(--mlb-red); font-size: 1.2rem;">
                    $${reservationData.totalPrice.toFixed(2)}/night
                </span>
            </div>
        `;

        html += `</div>`;

        hotelSection.innerHTML = html;

        // Insert before the register button or at the end of the checkout card
        const registerBtn = checkoutCard.querySelector('#register-btn');
        if (registerBtn && registerBtn.parentElement) {
            registerBtn.parentElement.insertBefore(hotelSection, registerBtn);
        } else {
            checkoutCard.appendChild(hotelSection);
        }

        // Update checkout total
        updateCheckoutTotal();
    }

    // Update checkout total including hotel reservations
    function updateCheckoutTotal() {
        const checkoutCard = document.querySelector('.checkout-card');
        if (!checkoutCard) return;

        // Calculate event registration total
        let eventTotal = 0;
        const selectedCheckboxes = document.querySelectorAll('.child-checkbox:checked');
        selectedCheckboxes.forEach(cb => {
            const priceEl = cb.closest('.child-item')?.querySelector('.child-price');
            if (priceEl) {
                const priceText = priceEl.textContent.trim().replace('$', '').replace(',', '');
                const price = parseFloat(priceText) || 0;
                eventTotal += price;
            }
        });

        // Calculate hotel reservations total
        let hotelTotal = 0;
        const hotelReservations = checkoutCard.querySelectorAll('.hotel-reservation-item');
        hotelReservations.forEach(item => {
            const totalEl = item.querySelector('.hotel-reservation-total');
            if (totalEl) {
                const priceText = totalEl.textContent.trim().replace('$', '').replace('/night', '').replace(',', '');
                const price = parseFloat(priceText) || 0;
                hotelTotal += price;
            }
        });

        const grandTotal = eventTotal + hotelTotal;

        // Update or create total display
        let totalDisplay = checkoutCard.querySelector('.checkout-grand-total');
        if (!totalDisplay) {
            totalDisplay = document.createElement('div');
            totalDisplay.className = 'checkout-grand-total';
            totalDisplay.style.cssText = 'margin-top: 15px; padding-top: 15px; border-top: 3px solid var(--mlb-red); display: flex; justify-content: space-between; align-items: center;';
            checkoutCard.appendChild(totalDisplay);
        }

        totalDisplay.innerHTML = `
            <span style="font-weight: 800; color: var(--mlb-blue); font-size: 1.1rem;">Grand Total:</span>
            <span style="font-weight: 800; color: var(--mlb-red); font-size: 1.4rem;">$${grandTotal.toFixed(2)}</span>
        `;
    }

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

    // New function: Open rooms modal directly (skip Step 1)
    function showRoomsDirect(pk, userData = null) {
        if (!pk) return;
        const roomsModalEl = q(`hotelRoomsModal${pk}`);
        if (!roomsModalEl) {
            showToast('Rooms modal not found', 'error');
            return;
        }

        // Get default guests: selected player + registrant (current user)
        const selectedPlayers = getSelectedPlayers();

        // Get registrant data - priority: parameter > window.currentUserName > data attribute > fallback
        let registrantName = null;
        let registrantEmail = null;
        let registrantBirthDate = null;

        if (userData && typeof userData === 'object') {
            registrantName = userData.name || null;
            registrantEmail = userData.email || null;
            registrantBirthDate = userData.birthDate || null;
        } else if (typeof userData === 'string') {
            // Backward compatibility: if string is passed, treat as name
            registrantName = userData;
        }

        if (!registrantName) {
            registrantName = window.currentUserName;
        }
        if (!registrantName) {
            // Try to get from data attribute on the main content
            const mainContent = document.querySelector('[data-user-name]');
            if (mainContent) {
                registrantName = mainContent.getAttribute('data-user-name');
            }
        }
        // If still no name, use a fallback
        if (!registrantName || registrantName.trim() === '') {
            registrantName = 'You';
        }

        // Calculate age if birth date is available
        let registrantAge = null;
        if (registrantBirthDate) {
            const birthDate = new Date(registrantBirthDate);
            if (!isNaN(birthDate.getTime())) {
                registrantAge = Math.floor((new Date() - birthDate) / (365.25 * 24 * 60 * 60 * 1000));
            }
        }

        // Determine type based on age
        const registrantType = registrantAge !== null && registrantAge < 18 ? 'child' : 'adult';

        // Debug log
        console.log('[showRoomsDirect] Registrant data:', {
            name: registrantName,
            email: registrantEmail,
            birthDate: registrantBirthDate,
            age: registrantAge,
            type: registrantType
        });

        const registrant = {
            name: registrantName.trim(),
            email: registrantEmail ? registrantEmail.trim() : null,
            birthDate: registrantBirthDate ? registrantBirthDate.trim() : null,
            age: registrantAge,
            type: registrantType,
            isRegistrant: true
        };

        // Store guests state
        if (!stateByPk.has(pk)) {
            stateByPk.set(pk, { roomId: null, roomLabel: null, guests: [] });
        }
        const state = stateByPk.get(pk);

        // Initialize default guests
        state.guests = [];
        if (registrant.name) {
            state.guests.push({
                type: registrant.type || 'adult',
                name: registrant.name,
                email: registrant.email || null,
                birthDate: registrant.birthDate || null,
                age: registrant.age || null,
                isRegistrant: true
            });
        }
        selectedPlayers.forEach(cb => {
            const childItem = cb.closest('.child-item');
            if (!childItem) return;

            // Get name from data attribute or DOM
            let name = childItem.getAttribute('data-child-name');
            if (!name) {
                const nameDiv = childItem.querySelector('div[style*="font-weight: 700"]');
                name = nameDiv ? nameDiv.textContent.trim() : 'Player';
            }

            // Get email from data attribute
            const email = childItem.getAttribute('data-child-email') || null;

            // Get birth date from data attribute
            const birthDate = childItem.getAttribute('data-birth-date') || null;

            // Calculate age if birth date is available
            let age = null;
            if (birthDate) {
                const birthDateObj = new Date(birthDate);
                if (!isNaN(birthDateObj.getTime())) {
                    age = Math.floor((new Date() - birthDateObj) / (365.25 * 24 * 60 * 60 * 1000));
                }
            }

            state.guests.push({
                type: 'child',
                name: name,
                email: email,
                birthDate: birthDate,
                age: age,
                isPlayer: true
            });
        });

        // Update UI
        updateRoomsGuestsList(pk);
        updateRoomsPriceCalculation(pk);
        validateRoomSelection(pk);

        // Filter and recommend rooms based on current guests
        const total = state.guests ? state.guests.length : 1;
        filterAndRecommendRooms(roomsModalEl, total);

        // Open modal
        if (!window.bootstrap?.Modal) return;
        // Setup focus handling for this modal
        setupModalFocusHandling(roomsModalEl);

        let inst = bootstrap.Modal.getInstance(roomsModalEl);
        if (!inst) inst = new bootstrap.Modal(roomsModalEl);
        inst.show();

        // Update header
        const headerEl = q(`rooms-default-guests${pk}`);
        if (headerEl) {
            const totalGuests = state.guests.length;
            headerEl.textContent = `${totalGuests} ${totalGuests === 1 ? 'guest' : 'guests'} (${state.guests.filter(g => g.type === 'adult').length} adults, ${state.guests.filter(g => g.type === 'child').length} children)`;
        }
    }

    // Update guests list in rooms modal
    function updateRoomsGuestsList(pk) {
        const listEl = q(`rooms-guests-list${pk}`);
        if (!listEl) return;
        const state = stateByPk.get(pk);
        if (!state || !state.guests) return;

        const html = state.guests.map((guest, idx) => {
            const icon = guest.type === 'adult' ? 'fa-user' : 'fa-child';
            const badge = guest.isRegistrant ? '<span style="background: var(--mlb-blue); color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-left: 6px;">Registrant</span>' :
                          guest.isPlayer ? '<span style="background: var(--mlb-red); color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-left: 6px;">Player</span>' : '';

            // Build guest info display
            let guestInfo = escapeHtml(guest.name);
            if (guest.email) {
                guestInfo += ` <span style="color: #6c757d; font-size: 0.75rem;">(${escapeHtml(guest.email)})</span>`;
            }
            if (guest.birthDate) {
                const age = guest.age !== undefined ? guest.age : (() => {
                    const birthDate = new Date(guest.birthDate);
                    return Math.floor((new Date() - birthDate) / (365.25 * 24 * 60 * 60 * 1000));
                })();
                guestInfo += ` <span style="color: #6c757d; font-size: 0.75rem;">• Age: ${age}</span>`;
            }

            // Build additional info lines
            let additionalInfo = '';
            if (guest.birthDate) {
                const birthDate = new Date(guest.birthDate);
                const formattedDate = birthDate.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
                const year = birthDate.getFullYear();
                additionalInfo += `
                    <div style="font-size: 0.75rem; color: #6c757d; margin-left: 20px; margin-top: 2px;">
                        <i class="fas fa-calendar me-1"></i>DOB: ${formattedDate} (Year: ${year})
                    </div>
                `;
            }
            if (guest.email && !guestInfo.includes(guest.email)) {
                additionalInfo += `
                    <div style="font-size: 0.75rem; color: #6c757d; margin-left: 20px; margin-top: 2px;">
                        <i class="fas fa-envelope me-1"></i>${escapeHtml(guest.email)}
                    </div>
                `;
            }

            return `
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                    <div style="flex: 1; min-width: 0;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 2px;">
                            <i class="fas ${icon}" style="color: var(--mlb-blue); font-size: 0.8rem;"></i>
                            <span style="font-size: 0.85rem; font-weight: 600;">${guestInfo}</span>
                            ${badge}
                        </div>
                        ${additionalInfo}
                    </div>
                    ${!guest.isRegistrant && !guest.isPlayer ? `
                        <button type="button" onclick="window.NSC_HotelReservation?.removeGuest?.('${pk}', ${idx});" style="background: transparent; border: none; color: #dc3545; padding: 4px 8px; cursor: pointer; border-radius: 4px; transition: all 0.2s;" onmouseover="this.style.background='#fee';" onmouseout="this.style.background='transparent';">
                            <i class="fas fa-times"></i>
                        </button>
                    ` : ''}
                </div>
            `;
        }).join('');
        listEl.innerHTML = html || '<div style="color: #6c757d; font-size: 0.85rem;">No guests added yet.</div>';
    }

    // Update price calculation
    function updateRoomsPriceCalculation(pk) {
        const calcEl = q(`rooms-price-calculation${pk}`);
        if (!calcEl) return;
        const state = stateByPk.get(pk);
        if (!state || !state.guests || !state.rooms || state.rooms.length === 0) {
            calcEl.innerHTML = '<div style="color: #6c757d; font-size: 0.85rem; font-style: italic;">Select at least one room to see price calculation</div>';
            return;
        }

        const totalGuests = state.guests.length;
        const roomsModalEl = q(`hotelRoomsModal${pk}`);
        let totalPrice = 0;
        let totalCapacity = 0;
        let allRules = [];
        let roomBreakdown = [];

        // Calculate price and capacity for all selected rooms
        state.rooms.forEach((room, idx) => {
            // Get room element
            let roomEl = roomsModalEl?.querySelector(`[data-room-id="${room.roomId}"]`);
            if (!roomEl) {
                roomEl = document.querySelector(`[data-room-id="${room.roomId}"]`);
            }
            if (!roomEl) {
                roomEl = document.body.querySelector(`[data-room-id="${room.roomId}"]`);
            }
            if (!roomEl) {
                console.warn('updateRoomsPriceCalculation: Room element not found for roomId:', room.roomId);
                return;
            }

            const roomPrice = parseFloat(roomEl.getAttribute('data-room-price') || '0');
            const roomIncludesGuests = parseInt(roomEl.getAttribute('data-room-includes-guests') || '1');
            const additionalGuestPrice = parseFloat(roomEl.getAttribute('data-room-additional-guest-price') || '0');
            const roomCapacity = parseInt(roomEl.getAttribute('data-room-capacity') || '0');
            totalCapacity += roomCapacity;

            // Get assigned guests for this room (or use auto-distribution)
            const assignedGuestIndices = state.guestAssignments[room.roomId] || [];
            const guestsForThisRoom = assignedGuestIndices.length;

            // Validate assignment doesn't exceed capacity
            const actualGuestsForRoom = Math.min(guestsForThisRoom, roomCapacity);
            const additionalGuestsForRoom = Math.max(0, actualGuestsForRoom - roomIncludesGuests);
            const additionalCostForRoom = additionalGuestsForRoom > 0 ? additionalGuestPrice * additionalGuestsForRoom : 0;
            const roomTotal = roomPrice + additionalCostForRoom;
            totalPrice += roomTotal;

            // Collect rules
            const rulesJson = roomEl.getAttribute('data-room-rules');
            if (rulesJson) {
                try {
                    const rules = JSON.parse(rulesJson);
                    allRules = allRules.concat(rules);
                } catch (e) {
                    console.warn('Error parsing rules for room:', room.roomId, e);
                }
            }

            roomBreakdown.push({
                roomId: room.roomId,
                roomLabel: room.roomLabel,
                roomPrice: roomPrice,
                roomIncludesGuests: roomIncludesGuests,
                additionalGuestsForRoom: additionalGuestsForRoom,
                additionalCostForRoom: additionalCostForRoom,
                roomTotal: roomTotal,
                roomCapacity: roomCapacity,
                assignedGuests: assignedGuestIndices,
                actualGuestsCount: actualGuestsForRoom
            });
        });

        let html = `<div style="font-weight: 600; color: var(--mlb-blue); margin-bottom: 8px; font-size: 0.9rem;">Price Breakdown (${state.rooms.length} room${state.rooms.length > 1 ? 's' : ''}):</div>`;

        // Show breakdown for each room with guest assignment
        roomBreakdown.forEach((room, idx) => {
            html += `<div style="margin-bottom: 8px; padding: 8px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid var(--mlb-blue);">`;
            html += `<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">`;
            html += `<div style="font-weight: 600; color: var(--mlb-blue); font-size: 0.85rem;">Room ${idx + 1}: ${escapeHtml(room.roomLabel)}</div>`;
            html += `<div style="display: flex; gap: 6px;">`;
            html += `<button type="button" onclick="window.NSC_HotelReservation?.showGuestAssignment?.('${pk}', '${room.roomId}');" style="background: var(--mlb-blue); color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='var(--mlb-red)';" onmouseout="this.style.background='var(--mlb-blue)';">Assign Guests</button>`;
            html += `<button type="button" onclick="window.NSC_HotelReservation?.removeRoom?.('${pk}', '${room.roomId}');" style="background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#c82333';" onmouseout="this.style.background='#dc3545';" title="Remove room from selection"><i class="fas fa-times"></i></button>`;
            html += `</div>`;
            html += `</div>`;

            // Show assigned guests
            if (room.assignedGuests && room.assignedGuests.length > 0) {
                const assignedGuestNames = room.assignedGuests.map(gi => {
                    const guest = state.guests[gi];
                    return guest ? escapeHtml(guest.name) : '';
                }).filter(n => n).join(', ');
                html += `<div style="font-size: 0.75rem; color: #6c757d; margin-bottom: 4px; font-style: italic;">Assigned: ${assignedGuestNames || 'None'}</div>`;
            } else {
                html += `<div style="font-size: 0.75rem; color: #ffc107; margin-bottom: 4px; font-style: italic;">⚠ No guests assigned to this room</div>`;
            }

            html += `<div style="font-size: 0.8rem; color: #333; margin-bottom: 2px;">Base price (${room.roomIncludesGuests} ${room.roomIncludesGuests === 1 ? 'guest' : 'guests'}): <strong>$${room.roomPrice.toFixed(2)}</strong>/night</div>`;
            if (room.additionalGuestsForRoom > 0) {
                html += `<div style="font-size: 0.8rem; color: #333; margin-bottom: 2px;">Additional guests (${room.actualGuestsCount - room.roomIncludesGuests}): <strong style="color: var(--mlb-red);">+$${room.additionalCostForRoom.toFixed(2)}</strong>/night</div>`;
            }
            html += `<div style="font-size: 0.85rem; color: var(--mlb-blue); margin-top: 4px; font-weight: 600;">Room Total: $${room.roomTotal.toFixed(2)}/night (${room.actualGuestsCount}/${room.roomCapacity} capacity)</div>`;
            html += `</div>`;
        });

        html += `<div style="font-weight: 700; color: var(--mlb-red); margin-top: 12px; padding-top: 12px; border-top: 2px solid #e9ecef; font-size: 1.1rem;">Total (All Rooms): $${totalPrice.toFixed(2)}/night</div>`;

        // Capacity validation
        const adults = state.guests.filter(g => g.type === 'adult').length;
        const children = state.guests.filter(g => g.type === 'child').length;
        const total = adults + children;
        let capacityValid = total <= totalCapacity;

        html += `<div style="margin-top: 12px; padding: 8px; border-radius: 6px; ${!capacityValid ? 'background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;' : 'background: #d4edda; border: 1px solid #c3e6cb; color: #155724;'} font-size: 0.85rem;">`;
        html += `<i class="fas ${!capacityValid ? 'fa-exclamation-circle' : 'fa-check-circle'} me-1"></i>`;
        html += `<strong>Capacity:</strong> ${total} guest${total !== 1 ? 's' : ''} (${adults} adult${adults !== 1 ? 's' : ''}, ${children} child${children !== 1 ? 'ren' : ''}) / ${totalCapacity} total capacity (${state.rooms.length} room${state.rooms.length > 1 ? 's' : ''})`;
        if (!capacityValid) {
            html += ` <span style="color: #721c24; font-weight: 700; display: block; margin-top: 6px;">⚠ Exceeds capacity by ${total - totalCapacity} guest${total - totalCapacity !== 1 ? 's' : ''}</span>`;
            html += `<div style="margin-top: 8px; padding: 8px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; color: #856404; font-size: 0.8rem;">`;
            html += `<i class="fas fa-info-circle me-1"></i><strong>Action required:</strong> Please add another room or change to a room with higher capacity to accommodate all ${total} guest${total !== 1 ? 's' : ''}.</div>`;
        }
        html += `</div>`;

        // Add occupancy rules validation
        if (allRules.length > 0) {
            try {
                const rules = allRules;

                // Find matching rules - check if adults and children are within the rule's range
                console.log('Validating rules:', {
                    totalRules: rules.length,
                    adults: adults,
                    children: children,
                    rules: rules
                });

                const validRules = rules.filter(rule => {
                    // Skip inactive rules (if is_active field exists and is false)
                    if (rule.hasOwnProperty('is_active') && !rule.is_active) {
                        console.log('Skipping inactive rule:', rule);
                        return false;
                    }
                    // Check if adults and children are within the rule's range
                    // Ensure values are numbers for comparison
                    const minAdults = parseInt(rule.min_adults) || 0;
                    const maxAdults = parseInt(rule.max_adults) || 999;
                    const minChildren = parseInt(rule.min_children) || 0;
                    const maxChildren = parseInt(rule.max_children) || 999;
                    const adultsMatch = adults >= minAdults && adults <= maxAdults;
                    const childrenMatch = children >= minChildren && children <= maxChildren;
                    const isValid = adultsMatch && childrenMatch;

                    console.log('Rule validation:', {
                        ruleId: rule.id,
                        ruleDescription: rule.description,
                        adults: adults,
                        children: children,
                        minAdults: minAdults,
                        maxAdults: maxAdults,
                        minChildren: minChildren,
                        maxChildren: maxChildren,
                        adultsMatch: adultsMatch,
                        childrenMatch: childrenMatch,
                        valid: isValid
                    });

                    return isValid;
                });

                console.log('Valid rules found:', validRules.length, validRules);

                html += `<div style="margin-top: 12px; padding-top: 12px; border-top: 2px solid #e9ecef;">`;
                html += `<div style="font-weight: 600; color: var(--mlb-blue); font-size: 0.85rem; margin-bottom: 6px;"><i class="fas fa-users-cog me-1"></i>Occupancy Rules:</div>`;

                // Only show validation if there are rules defined
                if (rules.length === 0) {
                    // No rules defined for this room - show info message
                    html += `<div style="font-size: 0.8rem; color: #6c757d; font-style: italic; padding: 8px; background: #f8f9fa; border-radius: 6px; margin-bottom: 6px;">No occupancy rules defined for this room. Any combination of guests is allowed.</div>`;
                }

                // Check capacity
                if (!capacityValid) {
                    html += `<div style="background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 6px; padding: 8px; color: #721c24; font-size: 0.8rem; margin-bottom: 6px;">`;
                    html += `<i class="fas fa-exclamation-circle me-1"></i><strong>Error:</strong> Total guests (${total}) exceeds total room capacity (${totalCapacity}).`;
                    html += `<div style="margin-top: 6px; padding: 6px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; color: #856404; font-size: 0.75rem;">`;
                    html += `<i class="fas fa-info-circle me-1"></i><strong>Solution:</strong> Please add another room or change to a room with higher capacity to accommodate all ${total} guest${total !== 1 ? 's' : ''}.</div>`;
                    html += `</div>`;

                    // Show available rules when capacity is exceeded
                    if (rules.length > 0) {
                        html += `<div style="font-size: 0.75rem; color: #6c757d; margin-top: 6px; font-weight: 600;">Available rules:</div>`;
                        rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active).forEach((rule, idx) => {
                            const desc = rule.description || `Adults: ${rule.min_adults}-${rule.max_adults} • Children: ${rule.min_children}-${rule.max_children}`;
                            html += `<div style="font-size: 0.75rem; color: #6c757d; margin-top: 4px; padding-left: 12px;">`;
                            html += `<i class="fas fa-circle me-1" style="font-size: 0.65rem;"></i>${escapeHtml(desc)}`;
                            // Show example combinations
                            if (rule.min_adults > 0 && rule.min_children > 0) {
                                html += ` <span style="color: #999; font-size: 0.7rem;">(e.g., ${rule.min_adults} adult${rule.min_adults > 1 ? 's' : ''} + ${rule.min_children} child${rule.min_children > 1 ? 'ren' : ''})</span>`;
                            } else if (rule.min_adults > 0) {
                                html += ` <span style="color: #999; font-size: 0.7rem;">(e.g., ${rule.min_adults} adult${rule.min_adults > 1 ? 's' : ''})</span>`;
                            } else if (rule.min_children > 0) {
                                html += ` <span style="color: #999; font-size: 0.7rem;">(e.g., ${rule.min_children} child${rule.min_children > 1 ? 'ren' : ''})</span>`;
                            }
                            html += `</div>`;
                        });
                    }
                } else if (validRules.length > 0) {
                    // Show which specific rules match - DON'T show available rules when valid
                    html += `<div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 8px; color: #155724; font-size: 0.8rem; margin-bottom: 6px;">`;
                    html += `<i class="fas fa-check-circle me-1"></i><strong>Valid:</strong> Your selection (${adults} adults, ${children} children) matches ${validRules.length} rule(s).`;
                    if (validRules.length === 1) {
                        const rule = validRules[0];
                        const desc = rule.description || `Adults: ${rule.min_adults}-${rule.max_adults} • Children: ${rule.min_children}-${rule.max_children}`;
                        html += `<div style="margin-top: 4px; font-size: 0.75rem;">Matching rule: ${escapeHtml(desc)}</div>`;
                    }
                    html += `</div>`;
                } else {
                    // Show warning and available rules when no rules match
                    html += `<div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 8px; color: #856404; font-size: 0.8rem; margin-bottom: 6px;">`;
                    html += `<i class="fas fa-exclamation-triangle me-1"></i><strong>Warning:</strong> Your selection (${adults} adults, ${children} children) does not match any occupancy rule.`;
                    html += `</div>`;

                    // Show available rules only when rules don't match
                    if (rules.length > 0) {
                        html += `<div style="font-size: 0.75rem; color: #6c757d; margin-top: 6px; font-weight: 600;">Available rules:</div>`;
                        rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active).forEach((rule, idx) => {
                            const desc = rule.description || `Adults: ${rule.min_adults}-${rule.max_adults} • Children: ${rule.min_children}-${rule.max_children}`;
                            html += `<div style="font-size: 0.75rem; color: #6c757d; margin-top: 4px; padding-left: 12px;">`;
                            html += `<i class="fas fa-circle me-1" style="font-size: 0.65rem;"></i>${escapeHtml(desc)}`;
                            // Show example combinations
                            if (rule.min_adults > 0 && rule.min_children > 0) {
                                html += ` <span style="color: #999; font-size: 0.7rem;">(e.g., ${rule.min_adults} adult${rule.min_adults > 1 ? 's' : ''} + ${rule.min_children} child${rule.min_children > 1 ? 'ren' : ''})</span>`;
                            } else if (rule.min_adults > 0) {
                                html += ` <span style="color: #999; font-size: 0.7rem;">(e.g., ${rule.min_adults} adult${rule.min_adults > 1 ? 's' : ''})</span>`;
                            } else if (rule.min_children > 0) {
                                html += ` <span style="color: #999; font-size: 0.7rem;">(e.g., ${rule.min_children} child${rule.min_children > 1 ? 'ren' : ''})</span>`;
                            }
                            html += `</div>`;
                        });
                    }
                }

                html += `</div>`;
            } catch (e) {
                console.error('Error parsing room rules:', e);
            }
        }

        calcEl.innerHTML = html;
    }

    // Add additional guest - Opens modal
    function addAdditionalGuest(pk) {
        const modalEl = q(`addGuestModal${pk}`);
        if (!modalEl) {
            showToast('Guest form modal not found', 'error');
            return;
        }

        // Reset form
        const form = document.getElementById(`addGuestForm${pk}`);
        if (form) {
            form.reset();
            // Set default to adult
            const adultRadio = document.getElementById(`guestTypeAdult${pk}`);
            if (adultRadio) adultRadio.checked = true;
        }

        // Open modal
        if (!window.bootstrap?.Modal) {
            showToast('Bootstrap Modal not available', 'error');
            return;
        }

        // Setup focus handling for this modal
        setupModalFocusHandling(modalEl);

        // Setup focus handling for this modal
        setupModalFocusHandling(modalEl);

        let modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (!modalInstance) {
            modalInstance = new bootstrap.Modal(modalEl, {
                backdrop: 'static',
                keyboard: false
            });
        }

        // Add blur effect to existing backdrop ONLY when Add Guest modal opens
        const applyBlur = function() {
            // Wait a bit for Bootstrap to create the new backdrop
            setTimeout(() => {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                if (backdrops.length > 1) {
                    // Apply blur to the first backdrop (the one from the parent modal - Available Rooms)
                    const firstBackdrop = backdrops[0];
                    firstBackdrop.style.backdropFilter = 'blur(8px)';
                    firstBackdrop.style.webkitBackdropFilter = 'blur(8px)';
                    firstBackdrop.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                    firstBackdrop.style.zIndex = '1049'; // Keep it behind the Add Guest modal backdrop

                    // Ensure the second backdrop (Add Guest) doesn't have blur
                    if (backdrops[1]) {
                        backdrops[1].style.backdropFilter = '';
                        backdrops[1].style.webkitBackdropFilter = '';
                        backdrops[1].style.zIndex = '1059'; // Above the first backdrop
                    }
                }
            }, 100);
        };

        // Remove blur when Add Guest modal closes
        const removeBlur = function() {
            const backdrops = document.querySelectorAll('.modal-backdrop');
            // Only restore the first backdrop (parent modal - Available Rooms)
            if (backdrops.length > 0) {
                const firstBackdrop = backdrops[0];
                firstBackdrop.style.backdropFilter = '';
                firstBackdrop.style.webkitBackdropFilter = '';
                firstBackdrop.style.backgroundColor = '';
                firstBackdrop.style.zIndex = '';
            }
        };

        // Apply blur ONLY when Add Guest modal is shown
        modalEl.addEventListener('shown.bs.modal', applyBlur, { once: true });

        // Remove blur ONLY when Add Guest modal is hidden
        modalEl.addEventListener('hidden.bs.modal', removeBlur, { once: true });

        modalInstance.show();
    }

    // Save guest from modal form
    function saveGuest(pk) {
        const form = document.getElementById(`addGuestForm${pk}`);
        if (!form) {
            showToast('Guest form not found', 'error');
            return;
        }

        // Validate form
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const firstName = document.getElementById(`guestFirstName${pk}`)?.value?.trim();
        const lastName = document.getElementById(`guestLastName${pk}`)?.value?.trim();
        const email = document.getElementById(`guestEmail${pk}`)?.value?.trim();
        const birthDate = document.getElementById(`guestBirthDate${pk}`)?.value;
        const typeRadio = document.querySelector(`input[name="guestType${pk}"]:checked`);
        const type = typeRadio?.value || 'adult';

        if (!firstName || !lastName || !email || !birthDate) {
            showToast('Please fill all required fields', 'warning');
            return;
        }

        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showToast('Please enter a valid email address', 'warning');
            return;
        }

        // Validate birth date (must be in the past)
        const birthDateObj = new Date(birthDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (birthDateObj >= today) {
            showToast('Date of birth must be in the past', 'warning');
            return;
        }

        // Calculate age to verify type
        const age = Math.floor((today - birthDateObj) / (365.25 * 24 * 60 * 60 * 1000));
        const actualType = age >= 18 ? 'adult' : 'child';

        // Auto-correct type if it doesn't match age (but allow override)
        if (type !== actualType) {
            // The type should already be corrected by the date input listener, but double-check
            const correctRadio = document.querySelector(`input[name="guestType${pk}"][value="${actualType}"]`);
            if (correctRadio) {
                correctRadio.checked = true;
                type = actualType; // Update the type variable
            }
        }

        // Validate age is reasonable (not negative, not too old)
        if (age < 0) {
            showToast('Invalid date of birth', 'error');
            return;
        }
        if (age > 120) {
            showToast('Please verify the date of birth', 'warning');
        }

        const state = stateByPk.get(pk);
        if (!state) {
            showToast('Reservation state not found', 'error');
            return;
        }

        // Add guest to state
        const fullName = `${firstName} ${lastName}`;
        state.guests.push({
            type: type,
            name: fullName,
            firstName: firstName,
            lastName: lastName,
            email: email,
            birthDate: birthDate,
            age: age
        });

        console.log('[DEBUG] saveGuest: Guest added to state. Total guests now:', state.guests.length);
        console.log('[DEBUG] saveGuest: State guests:', state.guests);

        // Close modal
        const modalEl = q(`addGuestModal${pk}`);
        if (modalEl) {
            // Remove focus from active element before closing modal
            if (document.activeElement && document.activeElement.blur) {
                document.activeElement.blur();
            }

            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            if (modalInstance) {
                // Use setTimeout to ensure focus is removed before hiding
                setTimeout(() => {
                    modalInstance.hide();
                }, 50);
            }
        }

        // Update UI - First update the list
        updateRoomsGuestsList(pk);

        // Re-filter and recommend rooms based on new total guests
        const roomsModalEl = q(`hotelRoomsModal${pk}`);
        if (roomsModalEl) {
            const state = stateByPk.get(pk);
            if (state && state.guests) {
                const total = state.guests.length;
                console.log('[DEBUG] saveGuest: Re-filtering rooms for total guests:', total);
                filterAndRecommendRooms(roomsModalEl, total);

                // Check if there's a better recommended room than currently selected
                const recommendedRooms = Array.from(roomsModalEl.querySelectorAll('.room-listing-inline.nsc-room-recommended'));
                if (recommendedRooms.length > 0) {
                    const mostRecommended = recommendedRooms[0]; // First one is the most recommended
                    const recommendedRoomId = mostRecommended.getAttribute('data-room-id');

                    // Check if user has selected rooms
                    if (state.rooms && state.rooms.length > 0) {
                        // Check if the most recommended room is already selected
                        const isRecommendedSelected = state.rooms.some(r => String(r.roomId) === String(recommendedRoomId));

                        if (!isRecommendedSelected) {
                            // Get room name for the notification
                            const roomNameEl = mostRecommended.querySelector('.room-name');
                            const roomName = roomNameEl ? roomNameEl.textContent.trim() : 'a room';
                            const roomPrice = parseFloat(mostRecommended.getAttribute('data-room-price') || '0');
                            const roomCapacity = parseInt(mostRecommended.getAttribute('data-room-capacity') || '0');

                            // Show notification about better room
                            setTimeout(() => {
                                showToast(
                                    `⭐ Better room available: "${roomName}" ($${roomPrice.toFixed(2)}/night, ${roomCapacity} guests) is now recommended for ${total} ${total === 1 ? 'guest' : 'guests'}`,
                                    'info',
                                    5000
                                );
                            }, 500);
                        }
                    } else {
                        // No rooms selected yet - show notification about recommended room
                        const roomNameEl = mostRecommended.querySelector('.room-name');
                        const roomName = roomNameEl ? roomNameEl.textContent.trim() : 'a room';
                        const roomPrice = parseFloat(mostRecommended.getAttribute('data-room-price') || '0');
                        const roomCapacity = parseInt(mostRecommended.getAttribute('data-room-capacity') || '0');

                        setTimeout(() => {
                            showToast(
                                `⭐ Recommended room: "${roomName}" ($${roomPrice.toFixed(2)}/night, ${roomCapacity} guests) is perfect for ${total} ${total === 1 ? 'guest' : 'guests'}`,
                                'info',
                                5000
                            );
                        }, 500);
                    }
                }
            }
        }

        // Auto-distribute guests if rooms are selected
        if (state.rooms && state.rooms.length > 0) {
            console.log('[DEBUG] saveGuest: Auto-distributing guests to selected rooms');
            autoDistributeGuests(pk);
        }

        // Update price calculation - Force update even if no rooms selected to show current guest count
        console.log('[DEBUG] saveGuest: Updating price calculation. State:', state);
        console.log('[DEBUG] saveGuest: Selected rooms:', state.rooms);
        console.log('[DEBUG] saveGuest: Total guests:', state.guests.length);
        console.log('[DEBUG] saveGuest: Guest assignments:', state.guestAssignments);

        // Use requestAnimationFrame to ensure DOM is updated, then update price calculation
        requestAnimationFrame(() => {
            // Small delay to ensure state is fully updated
            setTimeout(() => {
                updateRoomsPriceCalculation(pk);
                validateRoomSelection(pk);
            }, 50);
        });

        showToast(`Guest ${fullName} added successfully`, 'success');
    }

    // Remove guest
    function removeGuest(pk, index) {
        const state = stateByPk.get(pk);
        if (!state || !state.guests) return;
        const guest = state.guests[index];
        if (guest && (guest.isRegistrant || guest.isPlayer)) {
            showToast('Cannot remove registrant or selected player', 'warning');
            return;
        }
        state.guests.splice(index, 1);
        updateRoomsGuestsList(pk);
        updateRoomsPriceCalculation(pk);
        validateRoomSelection(pk);
    }

    // Validate room selection against rules
    function validateRoomSelection(pk) {
        const state = stateByPk.get(pk);
        if (!state || !state.guests) return;

        const adults = state.guests.filter(g => g.type === 'adult').length;
        const children = state.guests.filter(g => g.type === 'child').length;
        const total = adults + children;

        // Update selection status
        const statusEl = q(`rooms-selection-status${pk}`);
        const footerMsgEl = q(`rooms-footer-message${pk}`);
        const continueBtn = q(`rooms-continue-btn${pk}`);

        if (state.rooms && state.rooms.length > 0) {
            // Calculate total capacity
            const roomsModalEl = q(`hotelRoomsModal${pk}`);
            let totalCapacity = 0;
            const allRules = [];

            state.rooms.forEach(room => {
                const roomEl = roomsModalEl?.querySelector(`[data-room-id="${room.roomId}"]`) ||
                              document.querySelector(`[data-room-id="${room.roomId}"]`);
                if (roomEl) {
                    totalCapacity += parseInt(roomEl.getAttribute('data-room-capacity') || '0', 10);

                    // Collect rules from this room
                    const rulesJson = roomEl.getAttribute('data-room-rules');
                    if (rulesJson) {
                        try {
                            const rules = JSON.parse(rulesJson);
                            allRules.push(...rules);
                        } catch (e) {
                            console.warn('Error parsing rules for room:', room.roomId, e);
                        }
                    }
                }
            });

            // Validate capacity
            const capacityValid = total <= totalCapacity;

            // Validate occupancy rules
            let rulesValid = true;
            if (allRules.length > 0) {
                const activeRules = allRules.filter(r => !r.hasOwnProperty('is_active') || r.is_active);
                if (activeRules.length > 0) {
                    const validRules = activeRules.filter(rule => {
                        const minAdults = parseInt(rule.min_adults) || 0;
                        const maxAdults = parseInt(rule.max_adults) || 999;
                        const minChildren = parseInt(rule.min_children) || 0;
                        const maxChildren = parseInt(rule.max_children) || 999;
                        return adults >= minAdults && adults <= maxAdults &&
                               children >= minChildren && children <= maxChildren;
                    });
                    rulesValid = validRules.length > 0;
                }
            }

            // Determine if we can continue
            const canContinue = total >= 1 && adults >= 1 && capacityValid && rulesValid;

            if (statusEl) {
                statusEl.style.display = 'block';
                if (canContinue) {
                    statusEl.style.background = '#d4edda';
                    statusEl.style.border = '1px solid #c3e6cb';
                    statusEl.style.color = '#155724';
                    statusEl.innerHTML = `<i class="fas fa-check-circle me-1"></i><strong>${state.rooms.length} room${state.rooms.length > 1 ? 's' : ''} selected!</strong> Ready to continue.`;
                } else {
                    statusEl.style.background = '#fff3cd';
                    statusEl.style.border = '1px solid #ffc107';
                    statusEl.style.color = '#856404';
                    const errors = [];
                    if (total < 1 || adults < 1) {
                        errors.push('You must have at least one adult guest');
                    }
                    if (!capacityValid) {
                        errors.push(`${total} guest${total !== 1 ? 's' : ''} exceed${total === 1 ? 's' : ''} ${totalCapacity} capacity by ${total - totalCapacity}`);
                    }
                    if (!rulesValid && allRules.length > 0) {
                        errors.push('Occupancy rules not met');
                    }
                    statusEl.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i><strong>Warning:</strong> ${errors.join('. ')}. Please add another room or change to a room with higher capacity.`;
                }
            }

            if (footerMsgEl) {
                if (canContinue) {
                    footerMsgEl.innerHTML = `<i class="fas fa-check-circle me-1" style="color: #28a745;"></i>${state.rooms.length} room${state.rooms.length > 1 ? 's' : ''} selected. Click 'Continue' to proceed`;
                    footerMsgEl.style.color = '#28a745';
                } else {
                    const errors = [];
                    if (total < 1 || adults < 1) {
                        errors.push('At least one adult required');
                    }
                    if (!capacityValid) {
                        errors.push('Capacity exceeded');
                    }
                    if (!rulesValid && allRules.length > 0) {
                        errors.push('Occupancy rules not met');
                    }
                    footerMsgEl.innerHTML = `<i class="fas fa-exclamation-triangle me-1" style="color: #ffc107;"></i>Cannot continue: ${errors.join('. ')}. Please add another room or change to a room with higher capacity.`;
                    footerMsgEl.style.color = '#856404';
                }
            }

            if (continueBtn) {
                continueBtn.disabled = !canContinue;
                if (canContinue) {
                    continueBtn.style.opacity = '1';
                    continueBtn.style.cursor = 'pointer';
                    continueBtn.removeAttribute('title');
                } else {
                    continueBtn.style.opacity = '0.5';
                    continueBtn.style.cursor = 'not-allowed';
                    const errors = [];
                    if (total < 1 || adults < 1) {
                        errors.push('You must have at least one adult guest');
                    }
                    if (!capacityValid) {
                        errors.push(`Capacity exceeded: ${total} guests vs ${totalCapacity} capacity`);
                    }
                    if (!rulesValid && allRules.length > 0) {
                        errors.push('Occupancy rules not met');
                    }
                    continueBtn.setAttribute('title', `Cannot continue: ${errors.join('. ')}. Please fix these errors.`);
                }
            }
        } else {
            if (statusEl) {
                statusEl.style.display = 'block';
                statusEl.style.background = '#fff3cd';
                statusEl.style.border = '1px solid #ffc107';
                statusEl.style.color = '#856404';
                statusEl.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i>Please select a room from the list below`;
            }
            if (footerMsgEl) {
                footerMsgEl.innerHTML = `<i class="fas fa-info-circle me-1"></i>Please select a room to continue`;
                footerMsgEl.style.color = '#6c757d';
            }
            if (continueBtn) {
                continueBtn.disabled = true;
                continueBtn.style.opacity = '0.5';
                continueBtn.style.cursor = 'not-allowed';
                continueBtn.setAttribute('title', 'Please select at least one room to continue');
            }
        }
    }

    // Continue to guest details
    function continueToGuestDetails(pk) {
        const state = stateByPk.get(pk);
        if (!state || !state.rooms || state.rooms.length === 0) {
            showToast('Please select at least one room first', 'warning');
            return;
        }

        const adults = state.guests ? state.guests.filter(g => g.type === 'adult').length : 0;
        const children = state.guests ? state.guests.filter(g => g.type === 'child').length : 0;
        const total = adults + children;

        if (total < 1 || adults < 1) {
            showToast('You must have at least one adult guest', 'warning');
            return;
        }

        const guestModalEl = q(`hotelGuestDetailsModal${pk}`);
        if (!guestModalEl) {
            showToast('Guest details modal not found', 'error');
            return;
        }

        const roomsModalEl = q(`hotelRoomsModal${pk}`);

        // Populate guest modal
        const roomInput = q(`guest-room${pk}`);
        // For multiple rooms, we might need to handle this differently in the form
        // For now, store the first room ID for backward compatibility
        if (roomInput && state.rooms.length > 0) {
            roomInput.value = String(state.rooms[0].roomId);
        }

        const labelEl = q(`selected-room-label${pk}`);
        if (labelEl) {
            if (state.rooms.length === 1) {
                labelEl.textContent = state.rooms[0].roomLabel;
            } else if (state.rooms.length > 1) {
                labelEl.textContent = `${state.rooms.length} rooms selected`;
            }
        }

        renderGuestDetails(pk);

        // Pre-fill Main Contact (registrant) data
        const mainContactNameInput = guestModalEl.querySelector('input[name="guest_name"]');
        const mainContactEmailInput = guestModalEl.querySelector('input[name="guest_email"]');
        const mainContactPhoneInput = guestModalEl.querySelector('input[name="guest_phone"]');

        if (state.guests && state.guests.length > 0) {
            // Find registrant (first adult or guest with isRegistrant flag)
            const registrant = state.guests.find(g => g.isRegistrant) ||
                              state.guests.find(g => g.type === 'adult') ||
                              state.guests[0];

            if (registrant) {
                if (mainContactNameInput && registrant.name) {
                    mainContactNameInput.value = registrant.name;
                }
                if (mainContactEmailInput && registrant.email) {
                    mainContactEmailInput.value = registrant.email;
                }
                // Phone might not be in state, but we can try to get it from user profile if available
                // For now, leave phone empty as it's not stored in state
            }
        }

        // Pre-fill player data in additional children/adults sections
        if (state.guests && state.guests.length > 0) {
            const players = state.guests.filter(g => g.isPlayer);

            if (players.length > 0) {
                // Separate players by type
                const playerAdults = players.filter(p => p.type === 'adult');
                const playerChildren = players.filter(p => p.type === 'child');

                // Pre-fill adult players (excluding main contact)
                const adultBlocks = guestModalEl.querySelectorAll('.nsc-guest-adult');
                playerAdults.forEach((player, idx) => {
                    if (idx < adultBlocks.length && player.name) {
                        const block = adultBlocks[idx];
                        const nameInput = block.querySelector('.nsc-adult-name');
                        const dobInput = block.querySelector('.nsc-adult-dob');

                        if (nameInput) {
                            nameInput.value = player.name;
                        }
                        if (dobInput && player.birthDate) {
                            dobInput.value = player.birthDate;
                        }
                    }
                });

                // Pre-fill child players
                const childBlocks = guestModalEl.querySelectorAll('.nsc-guest-child');
                playerChildren.forEach((player, idx) => {
                    if (idx < childBlocks.length && player.name) {
                        const block = childBlocks[idx];
                        const nameInput = block.querySelector('.nsc-child-name');
                        const dobInput = block.querySelector('.nsc-child-dob');

                        if (nameInput) {
                            nameInput.value = player.name;
                        }
                        if (dobInput && player.birthDate) {
                            dobInput.value = player.birthDate;
                        }
                    }
                });
            }
        }

        const openGuestDetails = () => {
            if (!window.bootstrap?.Modal) return;
            // Setup focus handling for this modal
            setupModalFocusHandling(guestModalEl);

            let modalInstance = bootstrap.Modal.getInstance(guestModalEl);
            if (!modalInstance) modalInstance = new bootstrap.Modal(guestModalEl);
            modalInstance.show();
        };

        // Close rooms modal first (avoid backdrop conflicts), then open guest modal
        if (roomsModalEl && window.bootstrap?.Modal && roomsModalEl.classList.contains('show')) {
            roomsModalEl.addEventListener('hidden.bs.modal', () => openGuestDetails(), { once: true });
            const inst = bootstrap.Modal.getInstance(roomsModalEl);
            if (inst) {
                inst.hide();
            } else {
                roomsModalEl.classList.remove('show');
                roomsModalEl.setAttribute('aria-hidden', 'true');
                roomsModalEl.style.display = 'none';
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) backdrop.remove();
                document.body.classList.remove('modal-open');
                openGuestDetails();
            }
        } else {
            openGuestDetails();
        }
    }

    // Lightbox functions
    function openLightbox(pk, index) {
        if (!window.roomImages || !window.roomImages[pk]) return;
        const images = window.roomImages[pk];
        if (!images || images.length === 0) return;

        const lightbox = q(`roomImageLightbox${pk}`);
        const lightboxImg = q(`lightbox-image${pk}`);
        const lightboxCounter = q(`lightbox-counter${pk}`);

        if (!lightbox || !lightboxImg) return;

        // Store current index
        if (!window.lightboxState) window.lightboxState = {};
        window.lightboxState[pk] = { currentIndex: index, images: images };

        // Show image
        const img = images[index];
        if (img) {
            lightboxImg.src = img.image_url || img.url;
            lightboxImg.alt = img.title || img.alt || `Room image ${index + 1}`;
            if (lightboxCounter) {
                lightboxCounter.textContent = `${index + 1} / ${images.length}`;
            }
        }

        // Show lightbox
        lightbox.classList.add('show');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }

    function closeLightbox(pk) {
        const lightbox = q(`roomImageLightbox${pk}`);
        if (lightbox) {
            lightbox.classList.remove('show');
            document.body.style.overflow = ''; // Restore scrolling
        }
    }

    function prevLightboxImage(pk) {
        if (!window.lightboxState || !window.lightboxState[pk]) return;
        const state = window.lightboxState[pk];
        const newIndex = state.currentIndex > 0 ? state.currentIndex - 1 : state.images.length - 1;
        openLightbox(pk, newIndex);
    }

    function nextLightboxImage(pk) {
        if (!window.lightboxState || !window.lightboxState[pk]) return;
        const state = window.lightboxState[pk];
        const newIndex = state.currentIndex < state.images.length - 1 ? state.currentIndex + 1 : 0;
        openLightbox(pk, newIndex);
    }

    // Close lightbox on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.nsc-lightbox.show').forEach(lightbox => {
                const pk = lightbox.id.replace('roomImageLightbox', '');
                closeLightbox(pk);
            });
        } else if (e.key === 'ArrowLeft') {
            document.querySelectorAll('.nsc-lightbox.show').forEach(lightbox => {
                const pk = lightbox.id.replace('roomImageLightbox', '');
                prevLightboxImage(pk);
            });
        } else if (e.key === 'ArrowRight') {
            document.querySelectorAll('.nsc-lightbox.show').forEach(lightbox => {
                const pk = lightbox.id.replace('roomImageLightbox', '');
                nextLightboxImage(pk);
            });
        }
    });

    // Sort rooms function
    function sortRooms(pk, sortBy) {
        const roomsModalEl = q(`hotelRoomsModal${pk}`);
        if (!roomsModalEl) return;

        const containerEl = roomsModalEl.querySelector('[style*="max-height: 70vh"]');
        if (!containerEl) return;

        const roomListings = Array.from(containerEl.querySelectorAll('.room-listing-inline'));
        if (roomListings.length === 0) return;

        // Get current total guests for recommendation calculation
        const state = stateByPk.get(pk);
        const total = state?.guests?.length || 1;

        // Calculate sort values for each room
        const roomsWithData = roomListings.map(roomEl => {
            const cap = parseInt(roomEl.getAttribute('data-room-capacity') || '0', 10);
            const price = parseFloat(roomEl.getAttribute('data-room-price') || '0');
            const waste = Math.max(0, cap - total);
            const isExactMatch = cap === total ? 0 : 1;
            const recommendationScore = isExactMatch * 1000 + waste * 10 + price / 100;

            return {
                el: roomEl,
                cap,
                price,
                waste,
                isExactMatch,
                recommendationScore
            };
        });

        // Sort based on selected option
        let sortedRooms;
        switch (sortBy) {
            case 'recommended':
                sortedRooms = roomsWithData.sort((a, b) => {
                    if (a.recommendationScore !== b.recommendationScore) {
                        return a.recommendationScore - b.recommendationScore;
                    }
                    if (a.isExactMatch !== b.isExactMatch) return a.isExactMatch - b.isExactMatch;
                    if (a.price !== b.price) return a.price - b.price;
                    return 0;
                });
                break;
            case 'price-low-high':
                sortedRooms = roomsWithData.sort((a, b) => a.price - b.price);
                break;
            case 'price-high-low':
                sortedRooms = roomsWithData.sort((a, b) => b.price - a.price);
                break;
            case 'capacity-low-high':
                sortedRooms = roomsWithData.sort((a, b) => a.cap - b.cap);
                break;
            case 'capacity-high-low':
                sortedRooms = roomsWithData.sort((a, b) => b.cap - a.cap);
                break;
            default:
                sortedRooms = roomsWithData;
        }

        // Clear old recommendation badges
        roomListings.forEach(r => {
            r.classList.remove('nsc-room-recommended');
            const oldBadge = r.querySelector('.nsc-recommended-badge');
            if (oldBadge) oldBadge.remove();
        });

        // Reorder rooms in DOM
        const parentContainer = roomListings[0]?.parentElement;
        if (parentContainer) {
            sortedRooms.forEach((roomData, index) => {
                const roomEl = roomData.el;

                // Add recommendation badge for top 3 if sorting by recommended
                if (sortBy === 'recommended' && index < 3) {
                    roomEl.classList.add('nsc-room-recommended');
                    if (index === 0) {
                        const roomInfo = roomEl.querySelector('.room-info');
                        if (roomInfo && !roomInfo.querySelector('.nsc-recommended-badge')) {
                            const badge = document.createElement('div');
                            badge.className = 'nsc-recommended-badge';
                            badge.textContent = `⭐ Recommended for ${total} ${total === 1 ? 'guest' : 'guests'}`;
                            badge.style.cssText = 'background: linear-gradient(135deg, var(--mlb-blue) 0%, var(--mlb-light-blue) 100%); color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; margin-bottom: 8px; display: inline-block;';
                            roomInfo.insertBefore(badge, roomInfo.firstChild);
                        }
                    }
                }

                parentContainer.appendChild(roomEl);
            });
        }
    }

    // Auto-distribute guests across selected rooms
    function autoDistributeGuests(pk) {
        const state = stateByPk.get(pk);
        if (!state || !state.guests || !state.rooms || state.rooms.length === 0) return;

        // Check if any room has manual assignments
        const hasManualAssignments = Object.values(state.guestAssignments || {}).some(arr => arr.length > 0);

        // If there are manual assignments, check if all guests are assigned
        if (hasManualAssignments) {
            const totalAssigned = Object.values(state.guestAssignments || {}).reduce((sum, arr) => sum + arr.length, 0);
            const totalGuests = state.guests.length;

            // If all guests are already assigned, don't redistribute
            if (totalAssigned >= totalGuests) {
                return;
            }

            // If there are unassigned guests, assign them to rooms with available capacity
            // Find unassigned guest indices
            const assignedIndices = new Set();
            Object.values(state.guestAssignments || {}).forEach(arr => {
                arr.forEach(idx => assignedIndices.add(idx));
            });

            const unassignedIndices = [];
            for (let i = 0; i < state.guests.length; i++) {
                if (!assignedIndices.has(i)) {
                    unassignedIndices.push(i);
                }
            }

            // Assign unassigned guests to rooms with available capacity
            const roomsModalEl = q(`hotelRoomsModal${pk}`);
            for (const guestIdx of unassignedIndices) {
                for (const room of state.rooms) {
                    const roomEl = roomsModalEl?.querySelector(`[data-room-id="${room.roomId}"]`) ||
                                  document.querySelector(`[data-room-id="${room.roomId}"]`);
                    const capacity = roomEl ? parseInt(roomEl.getAttribute('data-room-capacity') || '0', 10) : room.capacity;
                    const currentAssigned = state.guestAssignments[room.roomId]?.length || 0;

                    if (currentAssigned < capacity) {
                        if (!state.guestAssignments[room.roomId]) {
                            state.guestAssignments[room.roomId] = [];
                        }
                        state.guestAssignments[room.roomId].push(guestIdx);
                        break; // Guest assigned, move to next
                    }
                }
            }

            return; // Done assigning unassigned guests
        }

        // Clear all assignments
        state.guestAssignments = {};
        state.rooms.forEach(room => {
            state.guestAssignments[room.roomId] = [];
        });

        // Get room capacities
        const roomsModalEl = q(`hotelRoomsModal${pk}`);
        const roomsWithCapacity = state.rooms.map(room => {
            const roomEl = roomsModalEl?.querySelector(`[data-room-id="${room.roomId}"]`) ||
                          document.querySelector(`[data-room-id="${room.roomId}"]`);
            const capacity = roomEl ? parseInt(roomEl.getAttribute('data-room-capacity') || '0', 10) : room.capacity;
            return { ...room, capacity };
        });

        // Distribute guests optimally
        let guestIndex = 0;
        for (let i = 0; i < roomsWithCapacity.length && guestIndex < state.guests.length; i++) {
            const room = roomsWithCapacity[i];
            const remainingCapacity = room.capacity - (state.guestAssignments[room.roomId]?.length || 0);
            const guestsToAssign = Math.min(remainingCapacity, state.guests.length - guestIndex);

            for (let j = 0; j < guestsToAssign; j++) {
                if (!state.guestAssignments[room.roomId]) {
                    state.guestAssignments[room.roomId] = [];
                }
                state.guestAssignments[room.roomId].push(guestIndex);
                guestIndex++;
            }
        }

        // Update price calculation
        updateRoomsPriceCalculation(pk);
    }

    // Show guest assignment modal
    function showGuestAssignment(pk, roomId) {
        const state = stateByPk.get(pk);
        if (!state || !state.guests || !state.rooms) return;

        const room = state.rooms.find(r => r.roomId === roomId);
        if (!room) return;

        // Get room capacity and rules
        const roomsModalEl = q(`hotelRoomsModal${pk}`);
        const roomEl = roomsModalEl?.querySelector(`[data-room-id="${roomId}"]`) ||
                      document.querySelector(`[data-room-id="${roomId}"]`);
        const capacity = roomEl ? parseInt(roomEl.getAttribute('data-room-capacity') || '0', 10) : room.capacity;

        // Get room rules
        let rules = [];
        const rulesJson = roomEl?.getAttribute('data-room-rules');
        if (rulesJson) {
            try {
                rules = JSON.parse(rulesJson);
            } catch (e) {
                console.warn('Error parsing rules:', e);
            }
        }

        // Get currently assigned guests for this room
        const assignedIndices = state.guestAssignments[roomId] || [];

        // Calculate current assignment stats
        const assignedGuests = assignedIndices.map(idx => state.guests[idx]).filter(g => g);
        const assignedAdults = assignedGuests.filter(g => g.type === 'adult').length;
        const assignedChildren = assignedGuests.filter(g => g.type === 'child').length;
        const assignedTotal = assignedAdults + assignedChildren;

        // Validate against rules
        let rulesValidation = null;
        if (rules.length > 0) {
            const activeRules = rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active);
            const validRules = activeRules.filter(rule => {
                const minAdults = parseInt(rule.min_adults) || 0;
                const maxAdults = parseInt(rule.max_adults) || 999;
                const minChildren = parseInt(rule.min_children) || 0;
                const maxChildren = parseInt(rule.max_children) || 999;
                return assignedAdults >= minAdults && assignedAdults <= maxAdults &&
                       assignedChildren >= minChildren && assignedChildren <= maxChildren;
            });

            rulesValidation = {
                valid: validRules.length > 0,
                validRules: validRules,
                allRules: activeRules,
                assignedAdults: assignedAdults,
                assignedChildren: assignedChildren
            };
        }

        // Create modal content
        let html = `<div style="padding: 20px;">`;
        html += `<h5 style="margin-bottom: 16px; color: var(--mlb-blue);">Assign Guests to ${escapeHtml(room.roomLabel)}</h5>`;
        html += `<p style="font-size: 0.85rem; color: #6c757d; margin-bottom: 8px;">Capacity: ${capacity} guests</p>`;
        html += `<p style="font-size: 0.85rem; color: #6c757d; margin-bottom: 16px;">Currently assigned: ${assignedTotal} (${assignedAdults} adult${assignedAdults !== 1 ? 's' : ''}, ${assignedChildren} child${assignedChildren !== 1 ? 'ren' : ''})</p>`;

        // Show rules validation
        if (rulesValidation) {
            if (rulesValidation.valid) {
                html += `<div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 10px; margin-bottom: 16px; color: #155724; font-size: 0.85rem;">`;
                html += `<i class="fas fa-check-circle me-1"></i><strong>Valid:</strong> Current assignment matches ${rulesValidation.validRules.length} rule(s).`;
                if (rulesValidation.validRules.length === 1) {
                    const rule = rulesValidation.validRules[0];
                    const desc = rule.description || `Adults: ${rule.min_adults}-${rule.max_adults} • Children: ${rule.min_children}-${rule.max_children}`;
                    html += `<div style="margin-top: 4px; font-size: 0.8rem;">Matching rule: ${escapeHtml(desc)}</div>`;
                }
                html += `</div>`;
            } else {
                html += `<div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 10px; margin-bottom: 16px; color: #856404; font-size: 0.85rem;">`;
                html += `<i class="fas fa-exclamation-triangle me-1"></i><strong>Warning:</strong> Current assignment (${assignedAdults} adults, ${assignedChildren} children) does not match any occupancy rule.`;
                html += `<div style="margin-top: 8px; font-size: 0.8rem; font-weight: 600;">Available rules:</div>`;
                rulesValidation.allRules.forEach((rule, idx) => {
                    const desc = rule.description || `Adults: ${rule.min_adults}-${rule.max_adults} • Children: ${rule.min_children}-${rule.max_children}`;
                    html += `<div style="font-size: 0.75rem; color: #6c757d; margin-top: 4px; padding-left: 12px;">`;
                    html += `<i class="fas fa-circle me-1" style="font-size: 0.65rem;"></i>${escapeHtml(desc)}`;
                    html += `</div>`;
                });
                html += `</div>`;
            }
        } else if (rules.length === 0) {
            html += `<div style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 10px; margin-bottom: 16px; color: #6c757d; font-size: 0.85rem; font-style: italic;">No occupancy rules defined for this room. Any combination of guests is allowed.</div>`;
        }

        html += `<div style="max-height: 400px; overflow-y: auto;">`;

        state.guests.forEach((guest, idx) => {
            const isAssigned = assignedIndices.includes(idx);
            const isAssignedToOtherRoom = Object.entries(state.guestAssignments || {}).some(([rid, indices]) =>
                rid !== roomId && indices.includes(idx)
            );

            html += `<div style="display: flex; align-items: center; justify-content: space-between; padding: 10px; margin-bottom: 8px; border: 1px solid #e9ecef; border-radius: 6px; background: ${isAssigned ? '#d4edda' : isAssignedToOtherRoom ? '#fff3cd' : '#fff'};">`;
            html += `<div style="flex: 1;">`;
            html += `<div style="font-weight: 600; color: #333;">${escapeHtml(guest.name)}</div>`;
            html += `<div style="font-size: 0.75rem; color: #6c757d;">${guest.type === 'adult' ? 'Adult' : 'Child'}${guest.age ? ` • Age: ${guest.age}` : ''}</div>`;
            if (isAssignedToOtherRoom) {
                html += `<div style="font-size: 0.7rem; color: #856404; margin-top: 4px;">⚠ Already assigned to another room</div>`;
            }
            html += `</div>`;
            html += `<input type="checkbox" ${isAssigned ? 'checked' : ''} ${isAssignedToOtherRoom ? 'disabled' : ''} onchange="window.NSC_HotelReservation?.toggleGuestAssignment?.('${pk}', '${roomId}', ${idx}, this.checked, ${capacity});" style="width: 20px; height: 20px; cursor: pointer;">`;
            html += `</div>`;
        });

        html += `</div>`;
        html += `<div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #e9ecef; display: flex; justify-content: space-between; align-items: center;">`;
        html += `<button type="button" onclick="if (document.activeElement && document.activeElement.blur) document.activeElement.blur(); window.NSC_HotelReservation?.autoDistributeGuests?.('${pk}'); setTimeout(() => { const modal = bootstrap.Modal.getInstance(document.getElementById('guestAssignmentModal${pk}')); if (modal) modal.hide(); }, 50);" style="background: #6c757d; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">Auto-Distribute</button>`;
        html += `<button type="button" onclick="if (document.activeElement && document.activeElement.blur) document.activeElement.blur(); setTimeout(() => { const modal = bootstrap.Modal.getInstance(document.getElementById('guestAssignmentModal${pk}')); if (modal) modal.hide(); window.NSC_HotelReservation?.updateRoomsPriceCalculation?.('${pk}'); }, 50);" style="background: var(--mlb-blue); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">Done</button>`;
        html += `</div>`;
        html += `</div>`;

        // Create or update modal
        let modalEl = q(`guestAssignmentModal${pk}`);
        if (!modalEl) {
            modalEl = document.createElement('div');
            modalEl.id = `guestAssignmentModal${pk}`;
            modalEl.className = 'modal fade';
            modalEl.setAttribute('tabindex', '-1');
            modalEl.innerHTML = `
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-body" id="guestAssignmentModalBody${pk}"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(modalEl);
        }

        const bodyEl = q(`guestAssignmentModalBody${pk}`);
        if (bodyEl) {
            bodyEl.innerHTML = html;
        }

        // Show modal
        if (window.bootstrap?.Modal) {
            // Setup focus handling for this modal
            setupModalFocusHandling(modalEl);

            const modalInstance = new bootstrap.Modal(modalEl);
            modalInstance.show();
        }
    }

    // Remove room from selection
    function removeRoom(pk, roomId) {
        const state = stateByPk.get(pk);
        if (!state || !state.rooms) return;

        const roomIndex = state.rooms.findIndex(r => r.roomId === String(roomId));
        if (roomIndex === -1) return;

        const room = state.rooms[roomIndex];
        const totalGuests = state.guests ? state.guests.length : 0;

        // Calculate remaining capacity
        let remainingCapacity = 0;
        state.rooms.forEach((r, idx) => {
            if (idx !== roomIndex) {
                const roomsModalEl = q(`hotelRoomsModal${pk}`);
                const roomEl = roomsModalEl?.querySelector(`[data-room-id="${r.roomId}"]`) ||
                              document.querySelector(`[data-room-id="${r.roomId}"]`);
                if (roomEl) {
                    remainingCapacity += parseInt(roomEl.getAttribute('data-room-capacity') || '0', 10);
                } else {
                    remainingCapacity += r.capacity || 0;
                }
            }
        });

        // Check if removing would leave insufficient capacity
        if (remainingCapacity < totalGuests && state.rooms.length > 1) {
            const confirmRemove = confirm(`Removing this room would leave ${remainingCapacity} capacity for ${totalGuests} guests. Do you want to continue?`);
            if (!confirmRemove) {
                return;
            }
        }

        // Remove room from selection
        state.rooms.splice(roomIndex, 1);
        // Remove guest assignments for this room
        if (state.guestAssignments) {
            delete state.guestAssignments[String(roomId)];
        }

        // Update UI - remove selected attribute
        const roomsModalEl = q(`hotelRoomsModal${pk}`);
        const roomEl = roomsModalEl?.querySelector(`[data-room-id="${roomId}"]`) ||
                      document.querySelector(`[data-room-id="${roomId}"]`);
        if (roomEl) {
            roomEl.removeAttribute('data-selected');
        }

        // Auto-redistribute guests if needed
        autoDistributeGuests(pk);

        // Update price calculation and validation
        updateRoomsPriceCalculation(pk);
        validateRoomSelection(pk);

        showToast(`Room "${room.roomLabel}" removed from selection`, 'info', 3000);
    }

    // Toggle guest assignment to a room
    function toggleGuestAssignment(pk, roomId, guestIndex, assign, capacity) {
        const state = stateByPk.get(pk);
        if (!state || !state.guestAssignments) return;

        if (!state.guestAssignments[roomId]) {
            state.guestAssignments[roomId] = [];
        }

        // Remove from other rooms first
        Object.keys(state.guestAssignments).forEach(rid => {
            if (rid !== roomId) {
                state.guestAssignments[rid] = state.guestAssignments[rid].filter(gi => gi !== guestIndex);
            }
        });

        if (assign) {
            // Check capacity
            const currentCount = state.guestAssignments[roomId].length;
            if (currentCount >= capacity) {
                showToast(`Room capacity (${capacity}) reached. Cannot assign more guests.`, 'warning');
                return false;
            }

            // Add to this room temporarily to check rules
            const tempAssignments = [...state.guestAssignments[roomId]];
            if (!tempAssignments.includes(guestIndex)) {
                tempAssignments.push(guestIndex);
            }

            // Get room rules
            const roomsModalEl = q(`hotelRoomsModal${pk}`);
            const roomEl = roomsModalEl?.querySelector(`[data-room-id="${roomId}"]`) ||
                          document.querySelector(`[data-room-id="${roomId}"]`);
            const rulesJson = roomEl?.getAttribute('data-room-rules');

            if (rulesJson) {
                try {
                    const rules = JSON.parse(rulesJson);
                    const activeRules = rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active);

                    if (activeRules.length > 0) {
                        // Calculate what the assignment would be
                        const tempAssignedGuests = tempAssignments.map(idx => state.guests[idx]).filter(g => g);
                        const tempAdults = tempAssignedGuests.filter(g => g.type === 'adult').length;
                        const tempChildren = tempAssignedGuests.filter(g => g.type === 'child').length;

                        // Check if this assignment would match any rule
                        const wouldMatchRule = activeRules.some(rule => {
                            const minAdults = parseInt(rule.min_adults) || 0;
                            const maxAdults = parseInt(rule.max_adults) || 999;
                            const minChildren = parseInt(rule.min_children) || 0;
                            const maxChildren = parseInt(rule.max_children) || 999;
                            return tempAdults >= minAdults && tempAdults <= maxAdults &&
                                   tempChildren >= minChildren && tempChildren <= maxChildren;
                        });

                        if (!wouldMatchRule) {
                            const confirmAssign = confirm(`This assignment (${tempAdults} adults, ${tempChildren} children) does not match any occupancy rule. Do you want to continue anyway?`);
                            if (!confirmAssign) {
                                return false;
                            }
                        }
                    }
                } catch (e) {
                    console.warn('Error validating rules:', e);
                }
            }

            // Add to this room
            if (!state.guestAssignments[roomId].includes(guestIndex)) {
                state.guestAssignments[roomId].push(guestIndex);
            }
        } else {
            // Remove from this room
            state.guestAssignments[roomId] = state.guestAssignments[roomId].filter(gi => gi !== guestIndex);
        }

        // Remove focus from checkbox before refreshing modal to avoid aria-hidden issues
        if (document.activeElement && document.activeElement.blur) {
            document.activeElement.blur();
        }

        // Use setTimeout to ensure focus is removed before modal refresh
        setTimeout(() => {
            showGuestAssignment(pk, roomId);
        }, 50);

        return true;
    }

    return { initModal, showRooms, showRoomsDirect, selectRoom, openRoomDetail, updateSummary, addAdult, addChild, stepper, backToGuests, backToRooms, addAdditionalGuest, saveGuest, removeGuest, continueToGuestDetails, openLightbox, closeLightbox, prevLightboxImage, nextLightboxImage, sortRooms, autoDistributeGuests, showGuestAssignment, toggleGuestAssignment, updateRoomsPriceCalculation, removeRoom };
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
