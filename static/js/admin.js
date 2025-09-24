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

// Sidebar enhancements
function initializeSidebarEnhancements() {
    // Add hover effects to navigation items
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        const link = item.querySelector('.nav-link');
        
        // Add ripple effect on click
        link.addEventListener('click', function(e) {
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
        link.addEventListener('mouseenter', function() {
            if (!this.closest('.nav-item').classList.contains('active')) {
                this.style.transform = 'translateX(2px)';
            }
        });
        
        link.addEventListener('mouseleave', function() {
            if (!this.closest('.nav-item').classList.contains('active')) {
                this.style.transform = 'translateX(0)';
            }
        });
    });
    
    // Add section collapse/expand functionality
    const sectionTitles = document.querySelectorAll('.nav-section-title');
    sectionTitles.forEach(title => {
        title.style.cursor = 'pointer';
        title.addEventListener('click', function() {
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

// ===== TOPBAR BUTTON FUNCTIONS =====

// Mobile Menu Toggle
AdminDashboard.prototype.toggleMobileMenu = function() {
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
AdminDashboard.prototype.toggleFullscreen = function() {
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
AdminDashboard.prototype.handleSearchInput = function(value) {
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

AdminDashboard.prototype.showSearchSuggestions = function() {
    const searchSuggestions = document.getElementById('searchSuggestions');
    if (searchSuggestions) {
        searchSuggestions.style.display = 'block';
    }
}

AdminDashboard.prototype.hideSearchSuggestions = function() {
    const searchSuggestions = document.getElementById('searchSuggestions');
    if (searchSuggestions) {
        searchSuggestions.style.display = 'none';
    }
}

AdminDashboard.prototype.loadSearchSuggestions = function(query) {
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

AdminDashboard.prototype.getSuggestionIcon = function(type) {
    const icons = {
        'event': 'calendar',
        'user': 'user',
        'setting': 'cog'
    };
    return icons[type] || 'search';
}

AdminDashboard.prototype.handleSearchKeydown = function(e) {
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

AdminDashboard.prototype.clearSearch = function() {
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
AdminDashboard.prototype.toggleNotifications = function() {
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

AdminDashboard.prototype.closeNotifications = function() {
    const notificationPanel = document.getElementById('notificationPanel');
    const notificationBtn = document.getElementById('notificationsBtn');
    
    if (notificationPanel) {
        notificationPanel.classList.remove('show');
    }
    
    if (notificationBtn) {
        notificationBtn.classList.remove('active');
    }
}

AdminDashboard.prototype.loadNotifications = function() {
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

AdminDashboard.prototype.getNotificationIcon = function(type) {
    const icons = {
        'success': 'check-circle',
        'info': 'info-circle',
        'warning': 'exclamation-triangle',
        'error': 'times-circle'
    };
    return icons[type] || 'bell';
}

AdminDashboard.prototype.markNotificationAsRead = function(notificationId) {
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

AdminDashboard.prototype.markAllNotificationsRead = function() {
    const notificationItems = document.querySelectorAll('.notification-item.unread');
    notificationItems.forEach(item => {
        item.classList.remove('unread');
        item.classList.add('read');
    });
    
    this.updateNotificationBadge();
    console.log('All notifications marked as read');
}

AdminDashboard.prototype.updateNotificationBadge = function() {
    const badge = document.getElementById('notificationBadge');
    const unreadCount = document.querySelectorAll('.notification-item.unread').length;
    
    if (badge) {
        badge.textContent = unreadCount;
        badge.style.display = unreadCount > 0 ? 'flex' : 'none';
    }
}

// User Menu Functions
AdminDashboard.prototype.toggleUserDropdown = function() {
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

AdminDashboard.prototype.closeUserDropdown = function() {
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
AdminDashboard.prototype.handleOutsideClick = function(e) {
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

AdminDashboard.prototype.handleKeyboardShortcuts = function(e) {
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
