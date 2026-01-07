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
        const messageLower = message.toLowerCase();
        const isPlayerRegistration =
            (title && (title.includes('Registro') || title.includes('Registration'))) ||
            (messageLower.includes('player') && (messageLower.includes('registered') || messageLower.includes('registrado'))) ||
            (messageLower.includes('jugador') && messageLower.includes('registrado'));

        if (isPlayerRegistration) {
            toastClass += ' player-registered';
        }

        toast.className = toastClass;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        const iconOrImage = (imageUrl && imageUrl !== 'null' && imageUrl !== 'undefined' && String(imageUrl).length > 10)
            ? `<div class="toast-icon toast-image" style="width: 48px; height: 48px; border-radius: 8px; overflow: hidden; flex-shrink: 0; background: #f8f9fa;">
                <img src="${imageUrl}" alt="" style="width: 100%; height: 100%; object-fit: cover;">
               </div>`
            : `<div class="toast-icon">
                <i class="fas ${icon}"></i>
               </div>`;

        const titleHtml = (title && title !== 'null' && title !== 'undefined') ? `<div class="toast-title">${title}</div>` : '';

        toast.innerHTML = `
            <div class="toast-content">
                ${iconOrImage}
                <div class="toast-body-wrapper">
                    ${titleHtml}
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

        // Asegurar que el toast tenga pointer-events habilitado
        toast.style.pointerEvents = 'all';

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
        try {
            // Verificar que el toast existe y está conectado al DOM
            if (!toast || !toast.isConnected) {
                console.warn('⚠️ Toast node is not connected to DOM, cannot hide');
                return;
            }

            toast.classList.remove('show');
            toast.classList.add('hide');

            setTimeout(() => {
                try {
                    // Verificar nuevamente antes de eliminar
                    if (toast.isConnected && toast.parentNode) {
                        toast.remove(); // Usar remove() en lugar de removeChild() (más moderno y seguro)
                    }
                } catch (error) {
                    console.error('Error removing toast:', error);
                }
            }, 300);
        } catch (error) {
            console.error('Error in hideToast:', error);
        }
    }

    createToastContainer() {
        const container = document.getElementById('toastContainer');
        if (container) {
            return container;
        }

        const newContainer = document.createElement('div');
        newContainer.id = 'toastContainer';
        newContainer.className = 'modern-toast-container';

        // Asegurar que el contenedor tenga los estilos correctos inline también
        newContainer.style.position = 'fixed';
        newContainer.style.top = '20px';
        newContainer.style.right = '20px';
        newContainer.style.zIndex = '9999';
        newContainer.style.display = 'flex';
        newContainer.style.flexDirection = 'column';
        newContainer.style.gap = '12px';
        newContainer.style.maxWidth = '400px';
        newContainer.style.pointerEvents = 'none';

        document.body.appendChild(newContainer);
        return newContainer;
    }

    convertDjangoMessagesToToasts() {
        try {
            // Find all Django messages and convert them to toasts
            const messages = document.querySelectorAll('.django-message');
            if (messages.length === 0) {
                return;
            }

            // Array para rastrear mensajes procesados
            const processedMessages = [];

            messages.forEach(msg => {
                try {
                    // Verificar que el nodo todavía existe en el DOM
                    if (!msg.isConnected) {
                        console.warn('⚠️ Message node is not connected to DOM, skipping');
                        return;
                    }

                    const tag = msg.getAttribute('data-tag');
                    const message = msg.getAttribute('data-message');
                    const extraTags = msg.getAttribute('data-extra-tags') || '';

                    // Validar que tenemos un mensaje válido
                    if (!message) {
                        console.warn('⚠️ Message node has no data-message attribute, skipping');
                        return;
                    }

                    // Map Django message tags to toast types
                    let toastType = 'info';
                    if (tag === 'success') toastType = 'success';
                    else if (tag === 'error' || tag === 'danger') toastType = 'error';
                    else if (tag === 'warning') toastType = 'warning';
                    else if (tag === 'info') toastType = 'info';

                    // Special handling for player registration and updates
                    let title = null;
                    let duration = 5000;
                    const messageLower = message.toLowerCase();

                    // Detect player registration messages in both Spanish and English
                    const isPlayerRegistration =
                        extraTags.includes('player_registered') ||
                        (messageLower.includes('player') && (messageLower.includes('registered') || messageLower.includes('registrado'))) ||
                        (messageLower.includes('jugador') && messageLower.includes('registrado'));

                    // Detect player update messages
                    const isPlayerUpdate =
                        extraTags.includes('player_updated') ||
                        (messageLower.includes('player') && (messageLower.includes('updated') || messageLower.includes('actualizado') || messageLower.includes('actualizada'))) ||
                        (messageLower.includes('jugador') && (messageLower.includes('actualizado') || messageLower.includes('actualizada'))) ||
                        (messageLower.includes('información') && (messageLower.includes('actualizada') || messageLower.includes('updated'))) ||
                        (messageLower.includes('information') && messageLower.includes('updated'));

                    if (isPlayerRegistration) {
                        toastType = 'success';
                        // Detect language and set appropriate title
                        if (messageLower.includes('registrado') || messageLower.includes('jugador')) {
                        title = '¡Registro Exitoso!';
                        } else {
                            title = 'Registration Successful!';
                        }
                        duration = 7000; // Show longer for important messages
                    } else if (isPlayerUpdate) {
                        toastType = 'success';
                        // Detect language and set appropriate title
                        if (messageLower.includes('actualizado') || messageLower.includes('actualizada') || messageLower.includes('información')) {
                            title = '¡Actualización Exitosa!';
                        } else {
                            title = 'Update Successful!';
                        }
                        duration = 6000; // Show longer for important messages
                    }

                    // Show toast
                    this.showToast(message, toastType, title, duration);

                    // Marcar como procesado solo si el nodo todavía existe
                    if (msg.isConnected) {
                        processedMessages.push(msg);
                    }
                } catch (error) {
                    console.error('Error processing individual message:', error);
                }
            });

            // Eliminar mensajes procesados del DOM para evitar duplicados
            // Usar requestAnimationFrame para asegurar que el DOM esté listo
            if (processedMessages.length > 0) {
                requestAnimationFrame(() => {
                    processedMessages.forEach(msg => {
                        try {
                            // Verificar que el nodo todavía existe y está conectado
                            if (msg.isConnected && msg.parentNode) {
                                msg.remove(); // Usar remove() en lugar de removeChild() (más moderno y seguro)
                            }
                        } catch (error) {
                            console.error('Error removing message node:', error);
                        }
                    });

                    // Ocultar el contenedor de mensajes si está vacío
                    try {
                        const messagesContainer = document.querySelector('.messages-container');
                        if (messagesContainer && messagesContainer.children.length === 0) {
                            messagesContainer.style.display = 'none';
                        }
                    } catch (error) {
                        console.error('Error hiding messages container:', error);
                    }

                    console.log(`✅ ${processedMessages.length} messages converted and removed from DOM`);
                });
            }
        } catch (error) {
            console.error('Error in convertDjangoMessagesToToasts:', error);
        }
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

    // ---------------------------------------------
    // Django JS i18n (djangojs.po via /jsi18n/)
    // ---------------------------------------------
    // We intentionally use gettext() so makemessages -d djangojs can extract strings.
    // On pages where jsi18n isn't loaded, we fall back to identity.
    const gettext = (typeof window !== 'undefined' && typeof window.gettext === 'function')
        ? window.gettext
        : (s) => s;

    const I18N = {
        labelSolution: gettext('Solution'),
        assignGuests: gettext('Assign guests'),
        removeRoom: gettext('Remove room from selection'),
        autoDistribute: gettext('Auto-distribute'),
        done: gettext('Done'),
        assignGuestsToRoomTitle: gettext('Assign guests to {room}'),
        selectedOne: gettext('Selected: {room}'),
        selectedMany: gettext('Selected rooms: {count}'),
        notEnoughRoomsAvailableMax: gettext('Not enough rooms available (max capacity {max})'),
        needBiggerRoomForGuests: gettext('Need a bigger room for {guests} guests'),
        noMoreRoomsAvailableToAdd: gettext('No more rooms available to add'),
        needPlusCapacityAddRoom: gettext('Need +{diff} capacity (add room)'),
        changeToBiggerRoom: gettext('Change to a bigger room'),
        replaceARoom: gettext('Replace a room'),
        roomsSelectedReady: gettext('{count} room(s) selected! Ready to continue.'),
        noGuestsAssignedTo: gettext('No guests assigned to: {rooms}'),
        occupancyPerRoomNotMet: gettext('Occupancy rules per room not met: {details}'),
        guestsExceedCapacityBy: gettext('{guests} guest(s) exceed {cap} capacity by {diff}'),
        notEnoughRoomsAvailableDetail: gettext('Not enough rooms available: max capacity is {max} but you have {guests} guests'),
        actionAutoAssignGuests: gettext('Auto-assign guests'),
        actionAssignNow: gettext('Assign now'),
        actionAddRoomFor: gettext('Add room for {diff} guest(s)'),
        infoRoomFitsChange: gettext('You have {guests} guests but this room fits {cap}. Change to a bigger room that fits everyone.'),
        infoRoomFitsAdd: gettext('You have {guests} guests but this room fits {cap}. Add another room for the remaining guests.'),
        roomRulesNotMetTitle: gettext('Occupancy rules are not being met for this room'),
        roomRulesNotMetShort: gettext('Not meeting occupancy rules'),
        roomRulesNotMetDetail: gettext('The current assignment ({adults} adults, {children} children) does not match any occupancy rule.'),
        unknownError: gettext('Unknown error'),
        recommendedForGuests: gettext('Recommended for {guests} guest(s)'),
        recommendedAddCapacity: gettext('Recommended to add capacity'),
        atLeastN: gettext('at least {n} {noun}'),
        exactlyN: gettext('exactly {n} {noun}'),
        betweenNAndM: gettext('between {min} and {max} {noun}'),
        adultOne: gettext('adult'),
        adultMany: gettext('adults'),
        childOne: gettext('child'),
        childMany: gettext('children'),
        nowYouHave: gettext('Now you have: {adults} {adultWord} and {children} {childWord}.'),
        requirementPrefix: gettext('Requirement:'),
        requirementLine: gettext('{adultsReq} and {childrenReq}.'),
        youNeedToAdd: gettext('You need to add {n} {noun}.'),
        youHaveExtra: gettext('You have {n} extra {noun}.'),
        roomFitsButYouHave: gettext('This room fits {cap} guests, but you have {guests} guests. Please adjust guests or choose another room.'),
        roomCapacityReached: gettext('Room capacity ({cap}) reached. Cannot assign more guests.'),
        footerRoomsSelectedContinue: gettext('{count} room(s) selected. Click Continue to proceed'),
        atLeastOneAdultRequired: gettext('At least one adult required'),
        guestsMustBeAssignedEveryRoom: gettext('Guests must be assigned to every selected room'),
        perRoomRulesNotMetShort: gettext('Per-room occupancy rules not met'),
        capacityExceededShort: gettext('Capacity exceeded'),
        cannotContinuePrefix: gettext('Cannot continue'),
        pleaseFixErrors: gettext('Please fix these errors'),
        selectRoomFromList: gettext('Please select a room from the list below'),
        selectRoomToContinue: gettext('Please select a room to continue'),
        selectAtLeastOneRoomToContinue: gettext('Please select at least one room to continue'),
        selectNewRoomReplace: gettext('Select a new room to replace the previous one'),
        replaceRoomInstruction: gettext('To replace a room, deselect one and select another'),
        pleaseSelectRoomFirst: gettext('Please select at least one room first'),
        autoAssignTooManyRooms: gettext('You have {guests} guests but selected {rooms} rooms. Some rooms will remain without guests.'),
        autoAssignStillEmpty: gettext('Auto-assign completed, but some rooms still have no guests. Please assign manually.'),
        autoAssignSuccess: gettext('Guests auto-assigned across selected rooms.'),
        priceBreakdownTitle: gettext('Price breakdown ({count} room(s)):'),
        assignedLabel: gettext('Assigned: {names}'),
        none: gettext('None'),
        noGuestsAssignedThisRoom: gettext('No guests assigned to this room'),
        rulesSatisfied: gettext('Occupancy rules satisfied'),
        capacitySummary: gettext('Capacity: {total} guest(s) ({adults} adult(s), {children} child(ren)) / {totalCapacity} total capacity ({rooms} room(s))'),
        capacityLine: gettext('Capacity: {cap} guests'),
        currentlyAssignedLine: gettext('Currently assigned: {total} ({adults} adult(s), {children} child(ren))'),
        rulesComplyTitle: gettext('Complies'),
        assignmentCompliesNRules: gettext('Current assignment complies with {n} rule(s).'),
        availableRulesLabel: gettext('Available rules:'),
        attention: gettext('Attention'),
        correct: gettext('Correct'),
        youMustHaveAdult: gettext('You must have at least 1 adult'),
        occupancyNotMet: gettext('Occupancy rules are not being met'),
        occupancyNotMetFor: gettext('Occupancy rules are not being met for: {rooms}'),
        cannotRemoveRoomCapacity: gettext('Cannot remove this room. Remaining capacity ({remaining}) would be insufficient for {guests} guests.'),
        confirmReplaceWithBiggerRoom: gettext(
            'You have {guests} guests. Instead of selecting multiple rooms, you can use a single bigger room:\n' +
            '- {label} (capacity {cap})\n\n' +
            'Do you want to replace your current selection with this room?'
        ),
        switchedToRoomOne: gettext('Switched to "{label}" to fit all guests in one room.'),
        addRoomStillInsufficient: gettext('Adding this room would give you {cap} total capacity, but you have {guests} guests. Please add another room or change to a room with higher capacity.'),
        addRoomStillInsufficientAlt: gettext('Adding this room would give you {cap} total capacity, but you have {guests} guests. Please select more rooms or adjust guests.'),
        roomRemoved: gettext('Room "{label}" removed from selection'),
        roomAdded: gettext('Room "{label}" added ({count} selected)'),
        alreadyEnoughCapacityConfirm: gettext('You already have enough capacity with {count} room(s) ({cap} guests). Do you want to add another room anyway?'),
        roomSelectedReady: gettext('Room selected! Ready to continue.'),
        noAmenities: gettext('No amenities listed.'),
        roomNoRules: gettext('No occupancy rules defined for this room. Any combination of guests is allowed.'),
        errorGuestsExceedCapacity: gettext('Total guests ({total}) exceeds total room capacity ({cap}).'),
        solutionAddOrChangeRoom: gettext('Please add another room or change to a room with higher capacity to accommodate all {total} guest(s).'),
        availableRules: gettext('Available rules:'),
        matchingRule: gettext('Matching rule:'),
        selectionMatchesRules: gettext('Your selection ({adults} adults, {children} children) matches the occupancy rules.'),
        selectionMatchesNRules: gettext('Your selection ({adults} adults, {children} children) matches {n} rule(s).'),
        selectionDoesNotMatchRules: gettext('Your selection ({adults} adults, {children} children) does not match any occupancy rule.'),
        noRoomAllowsZeroChildren: gettext('In this hotel, all rooms require at least 1 child. Your group includes 0 children.'),
        noRoomAllowsChildren: gettext('In this hotel, no room allows children (max children = 0 for all rooms).'),
        noRoomAllowsAdults: gettext('In this hotel, no room allows adults (max adults = 0 for all rooms).'),
        tooManyChildrenForHotel: gettext('Too many children for the available rooms (max children allowed: {max}).'),
        tooManyAdultsForHotel: gettext('Too many adults for the available rooms (max adults allowed: {max}).'),
        noRoomsCompatibleGuestMix: gettext('No available rooms are compatible with your guest mix.'),
        pleaseAddGuestsFirst: gettext('Please add guests before selecting a room.'),
        invalidRoomCapacity: gettext('Invalid room capacity. Cannot select this room.'),
        roomRulesNotMetBeforeSelect: gettext('This room does not meet occupancy rules. You have {adults} adult(s) and {children} child(ren), but this room requires: {requirements}.')
    };

    function formatWithParams(str, params) {
        let out = String(str || '');
        const p = params || {};
        Object.keys(p).forEach((k) => {
            out = out.replaceAll(`{${k}}`, String(p[k]));
        });
        return out;
    }

    function t(key, params) {
        const raw = I18N[key] || key;
        return formatWithParams(raw, params);
    }

    // Helpers for bilingual rule messaging
    function nounForCount(n, oneKey, manyKey) {
        return (Number(n) === 1) ? t(oneKey) : t(manyKey);
    }

    function rangeText(min, max, nounOneKey, nounManyKey) {
        const minN = parseInt(min) || 0;
        const maxN = parseInt(max);
        const isInf = Number.isFinite(maxN) && maxN >= 999;
        if (isInf) {
            return t('atLeastN', { n: minN, noun: nounForCount(minN, nounOneKey, nounManyKey) });
        }
        const maxVal = Number.isFinite(maxN) ? maxN : 0;
        if (minN === maxVal) {
            return t('exactlyN', { n: minN, noun: nounForCount(minN, nounOneKey, nounManyKey) });
        }
        return t('betweenNAndM', { min: minN, max: maxVal, noun: t(nounManyKey) });
    }

    function makeActionHint(assigned, min, max, nounOneKey, nounManyKey) {
        const minN = parseInt(min) || 0;
        const maxN = parseInt(max);
        const isInf = Number.isFinite(maxN) && maxN >= 999;
        const maxVal = isInf ? null : (Number.isFinite(maxN) ? maxN : 0);
        if (assigned < minN) {
            const missing = minN - assigned;
            return t('youNeedToAdd', { n: missing, noun: nounForCount(missing, nounOneKey, nounManyKey) });
        }
        if (maxVal !== null && assigned > maxVal) {
            const extra = assigned - maxVal;
            return t('youHaveExtra', { n: extra, noun: nounForCount(extra, nounOneKey, nounManyKey) });
        }
        return null;
    }

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
            if (window.adminDashboard && window.adminDashboard.showToast) {
            // La firma de adminDashboard.showToast es (message, type, title, duration, imageUrl)
                window.adminDashboard.showToast(message, type, null, duration, imageUrl);
        } else if (window.AdminUtils && window.AdminUtils.showToast) {
                window.AdminUtils.showToast(message, type);
        } else {
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

    // Helper: Get or create Bootstrap Modal instance
    function getOrCreateModalInstance(modalEl) {
        if (!modalEl || !window.bootstrap?.Modal) return null;
        let inst = bootstrap.Modal.getInstance(modalEl);
        if (!inst) {
            inst = new bootstrap.Modal(modalEl);
        }
        return inst;
    }

    // Helper: Open modal with focus handling and scroll to top
    function openModalWithScroll(modalEl) {
        if (!modalEl) return;
        setupModalFocusHandling(modalEl);
        const inst = getOrCreateModalInstance(modalEl);
        if (inst) {
            inst.show();
            // Scroll to top
            modalEl.scrollTop = 0;
            if (window.parent) {
                window.parent.postMessage({ type: 'nsc-scroll-to-top', tabId: window.name }, window.location.origin);
            }
        }
    }

    // Helper: Close one modal and open another
    function closeAndOpenModal(closeModalEl, openModalEl) {
        if (!closeModalEl || !openModalEl) return;

        const openModal = () => {
            openModalWithScroll(openModalEl);
        };

        if (closeModalEl.classList.contains('show')) {
            closeModalEl.addEventListener('hidden.bs.modal', openModal, { once: true });
            const inst = getOrCreateModalInstance(closeModalEl);
            if (inst) {
                inst.hide();
            } else {
                openModal();
            }
        } else {
            openModal();
        }
    }

    // Helper: Find room element in modal by room ID (with fallback to document)
    function findRoomInModal(pk, roomId) {
        const roomsModalEl = q(`hotelRoomsModal${pk}`);
        if (roomsModalEl) {
            const roomEl = roomsModalEl.querySelector(`[data-room-id="${roomId}"]`);
            if (roomEl) return roomEl;
        }
        // Fallback to document-wide search
        return document.querySelector(`[data-room-id="${roomId}"]`) || null;
    }

    // Helper: Get room image URL from detail gallery or fetch from API
    function getRoomImageUrl(pk, roomDetailUrl) {
        // Try to get image from already loaded room details
        const detailGallery = q(`rooms-detail-gallery${pk}`);
        if (detailGallery) {
            const mainImg = detailGallery.querySelector('.nsc-room-detail-gallery-main img');
            if (mainImg && mainImg.src) {
                return Promise.resolve(mainImg.src);
            }
        }

        // If not found, fetch from API
        if (roomDetailUrl) {
            return fetch(roomDetailUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(res => res.ok ? res.json() : null)
                .then(data => {
                    if (data && data.images && data.images.length > 0) {
                        return data.images[0].image_url || data.images[0].url || null;
                    }
                    return null;
                })
                .catch(() => null);
        }

        return Promise.resolve(null);
    }

    // Helper: Set or remove data-selected attribute on room element
    function setRoomSelected(pk, roomId, selected) {
        const roomEl = findRoomInModal(pk, roomId);
        if (roomEl) {
            if (selected) {
                roomEl.setAttribute('data-selected', 'true');
            } else {
                roomEl.removeAttribute('data-selected');
            }
        }
    }

    // Helper: Add room to state and update UI
    function addRoomToState(pk, state, roomId, roomLabel, capacity) {
        state.rooms.push({
            roomId: String(roomId),
            roomLabel: roomLabel,
            capacity: capacity
        });
        state.guestAssignments[String(roomId)] = [];
        setRoomSelected(pk, roomId, true);

        // Update hidden input for form submission (backward compatibility)
        const roomInput = q(`guest-room${pk}`);
        if (roomInput && state.rooms.length > 0) {
            // Store the first room ID for backward compatibility
            roomInput.value = String(state.rooms[0].roomId);
        }
    }

    // Helper: Remove room from state and update UI
    function removeRoomFromState(pk, state, roomId) {
        const roomIndex = state.rooms.findIndex(r => r.roomId === String(roomId));
        if (roomIndex !== -1) {
            state.rooms.splice(roomIndex, 1);
        }
        if (state.guestAssignments) {
            delete state.guestAssignments[String(roomId)];
        }
        setRoomSelected(pk, roomId, false);
    }

    // Helper: Clear all room selections
    function clearAllRoomSelections(pk, state, listings = null) {
        state.rooms = [];
        state.guestAssignments = {};
        if (listings && Array.isArray(listings)) {
            listings.forEach((el) => el.removeAttribute('data-selected'));
        } else {
            // Clear all rooms in modal
            const roomsModalEl = q(`hotelRoomsModal${pk}`);
            if (roomsModalEl) {
                roomsModalEl.querySelectorAll('.room-listing-inline[data-selected="true"]').forEach(el => {
                    el.removeAttribute('data-selected');
                });
            }
        }
    }

    // Helper: Update room selection (call after adding/removing rooms)
    function updateRoomSelectionState(pk) {
        const state = stateByPk.get(pk);
        if (state && state.rooms && state.rooms.length > 0) {
            // Update hidden input for form submission
            const roomInput = q(`guest-room${pk}`);
            if (roomInput) {
                roomInput.value = String(state.rooms[0].roomId);
            }
        }
        autoDistributeGuests(pk);
        updateRoomsPriceCalculation(pk);
        validateRoomSelection(pk);
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
                    <div style="font-weight:800; color: var(--mlb-blue);">${gettext('Adult')} ${index}</div>
                </div>
                <div class="row g-3">
                    <div class="col-md-6">
                        <label class="form-label" style="font-weight:600; color:var(--mlb-blue); font-size:0.85rem;">${gettext('Full Name')} <span style="color: var(--mlb-red);">*</span></label>
                        <input type="text" class="form-control adult-name-input" name="adult_name_${index}" data-index="${index}" required style="border:2px solid #e9ecef; border-radius:8px; padding:10px;">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label" style="font-weight:600; color:var(--mlb-blue); font-size:0.85rem;">${gettext('Email')} <span style="color: var(--mlb-red);">*</span></label>
                        <input type="email" class="form-control adult-email-input" name="adult_email_${index}" data-index="${index}" required style="border:2px solid #e9ecef; border-radius:8px; padding:10px;">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label" style="font-weight:600; color:var(--mlb-blue); font-size:0.85rem;">${gettext('Phone')} <span style="color: var(--mlb-red);">*</span></label>
                        <input type="tel" class="form-control adult-phone-input" name="adult_phone_${index}" data-index="${index}" required style="border:2px solid #e9ecef; border-radius:8px; padding:10px;">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label" style="font-weight:600; color:var(--mlb-blue); font-size:0.85rem;">${gettext('Date of Birth')} <span style="color: var(--mlb-red);">*</span></label>
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
                <div style="font-weight:800; color: var(--mlb-blue); margin-bottom:12px;">${gettext('Child')} ${index}</div>
                <div class="row g-3">
                    <div class="col-md-6">
                        <label class="form-label" style="font-weight:600; color:var(--mlb-blue); font-size:0.85rem;">${gettext('Full Name')} <span style="color: var(--mlb-red);">*</span></label>
                        <input type="text" class="form-control child-name-input" name="additional_child_name_${index}" data-index="${index}" required style="border:2px solid #e9ecef; border-radius:8px; padding:10px;">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label" style="font-weight:600; color:var(--mlb-blue); font-size:0.85rem;">${gettext('Date of Birth')} <span style="color: var(--mlb-red);">*</span></label>
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

            const modalInstance = getOrCreateModalInstance(reservationModalEl);

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
                    // Defer heavy operations to prevent blocking modal animation
                    reservationModalEl.addEventListener('shown.bs.modal', () => {
                        console.log('Modal shown, initializing elements...');

                        // Defer DOM operations to next frame
                        requestAnimationFrame(() => {
                            // Now the elements should exist
                            if (q(`adults-total-count${pk}`) && q(`additional-children-count${pk}`)) {
                                renderSelectedPlayers(pk);
                                updateSummary(pk);
                                console.log('Elements initialized successfully');
                            } else {
                                console.warn('Elements still not found after modal shown');
                            }
                        });
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
            showToast(gettext('At least one adult is required'), 'warning');
            return;
        }
        if (players === 0 && addChildren === 0) {
            showToast(gettext('You must select at least one player or add at least one child'), 'warning');
            return;
        }

        const reservationModalEl = q(`hotelReservationModal${pk}`);
        const roomsModalEl = q(`hotelRoomsModal${pk}`);
        if (!roomsModalEl) {
            showToast(gettext('Rooms modal not found'), 'error');
            return;
        }

        // Close reservation modal first, then open rooms modal
        // After rooms modal opens, filter and recommend rooms, and focus close button
        // Use requestAnimationFrame to defer heavy operations and prevent UI blocking
        roomsModalEl.addEventListener('shown.bs.modal', () => {
            // Focus first to give immediate feedback
            const closeBtn = roomsModalEl.querySelector('button.btn-close');
            if (closeBtn && typeof closeBtn.focus === 'function') closeBtn.focus();

            // Defer heavy filtering operation to next frame to prevent blocking
            requestAnimationFrame(() => {
                // Use setTimeout to allow browser to paint first
                setTimeout(() => {
                    filterAndRecommendRooms(roomsModalEl, total);
                }, 0);
            });
        }, { once: true });

        closeAndOpenModal(reservationModalEl, roomsModalEl);
    }

    function filterAndRecommendRooms(containerEl, total) {
        if (!containerEl) return;

        const pk = containerEl.getAttribute('data-hotel-pk') || '';
        const noneMsg = containerEl.querySelector(`#rooms-none-msg${pk}`) || containerEl.querySelector('[data-nsc-rooms-none]');
        if (noneMsg) noneMsg.style.display = 'none';

        // Try to use current guests breakdown (adults/children) to filter rooms by occupancy rules too
        const state = stateByPk.get(String(pk));
        const adults = state && state.guests ? state.guests.filter(g => g.type === 'adult').length : 0;
        const children = state && state.guests ? state.guests.filter(g => g.type === 'child').length : 0;

        // Rules helpers:
        // - "single room mode": room must allow ALL guests (adults/children totals) in one room
        // - "multi room mode": room must allow SOME feasible subset (best-effort) of guests (not necessarily all)
        function rulesAllowAllGuestsForThisRoom(roomEl) {
            try {
                const rulesJson = roomEl.getAttribute('data-room-rules');
                if (!rulesJson) return null; // unknown (not loaded yet)
                const rules = JSON.parse(rulesJson) || [];
                const activeRules = Array.isArray(rules) ? rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active) : [];
                if (!activeRules.length) return true; // no rules -> allowed
                return activeRules.some(rule => {
                    const minAdults = parseInt(rule.min_adults) || 0;
                    const maxAdults = parseInt(rule.max_adults) || 999;
                    const minChildren = parseInt(rule.min_children) || 0;
                    const maxChildren = parseInt(rule.max_children) || 999;
                    return adults >= minAdults && adults <= maxAdults &&
                           children >= minChildren && children <= maxChildren;
                });
            } catch (e) {
                return null;
            }
        }

        function rulesAllowAnySubsetForThisRoom(roomEl) {
            // Best-effort feasibility check for multi-room:
            // if rules exist, we only need that there exists SOME rule whose minimums are <= available counts.
            // (Later per-room validation will enforce exact assignments.)
            try {
                const rulesJson = roomEl.getAttribute('data-room-rules');
                if (!rulesJson) return null; // unknown
                const rules = JSON.parse(rulesJson) || [];
                const activeRules = Array.isArray(rules) ? rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active) : [];
                if (!activeRules.length) return true;
                return activeRules.some(rule => {
                    const minAdults = parseInt(rule.min_adults) || 0;
                    const minChildren = parseInt(rule.min_children) || 0;
                    // Need to be able to satisfy minimums with available pool
                    return adults >= minAdults && children >= minChildren;
                });
            } catch (e) {
                return null;
            }
        }

        const roomListings = Array.from(containerEl.querySelectorAll('.room-listing-inline'));
        // Clear old recommendation and remove any badges (aggressive cleanup)
        roomListings.forEach(r => {
            r.classList.remove('nsc-room-recommended');
            // Remove any badge elements that might exist
            const oldBadge = r.querySelector('.nsc-recommended-badge');
            if (oldBadge) {
                oldBadge.remove();
            }
            // Also check in room-info directly
            const roomInfo = r.querySelector('.room-info');
            if (roomInfo) {
                const badgeInInfo = roomInfo.querySelector('.nsc-recommended-badge');
                if (badgeInInfo) badgeInInfo.remove();
            }
        });

        // Decide mode:
        // - If there exists at least one room that can fit ALL guests (capacity + rules when known), use single-room mode.
        // - Otherwise, use multi-room mode (show rooms that can help increase capacity).
        let singleRoomMode = false;
        try {
            singleRoomMode = roomListings.some((roomEl) => {
                const cap = parseInt(roomEl.getAttribute('data-room-capacity') || '0', 10) || 0;
                if (cap < total) return false;
                const rulesOk = rulesAllowAllGuestsForThisRoom(roomEl);
                if (rulesOk === false) return false;
                // If rules unknown, we don't block single-room mode; we can still recommend but will re-run after fetch.
                return true;
            });
        } catch (e) {
            singleRoomMode = false;
        }

        // Compute selected capacity + deficit (used for multi-room recommendations)
        const selectedRoomIds = new Set((state?.rooms || []).map(r => String(r.roomId)));
        let selectedCapacity = 0;
        try {
            selectedRoomIds.forEach((rid) => {
                const el = containerEl.querySelector(`[data-room-id="${rid}"]`) || document.querySelector(`[data-room-id="${rid}"]`);
                if (!el) return;
                selectedCapacity += parseInt(el.getAttribute('data-room-capacity') || '0', 10) || 0;
            });
        } catch (e) {}
        const deficit = Math.max(0, (parseInt(String(total), 10) || 0) - selectedCapacity);

        const candidates = [];
        const hiddenRooms = [];
        const unknownRuleRooms = [];

        roomListings.forEach(roomListing => {
            const capAttr = roomListing.getAttribute('data-room-capacity');
            const cap = parseInt(capAttr || '0', 10);
            const capOk = Number.isFinite(cap) && cap > 0;
            const ok = singleRoomMode ? (cap >= total) : capOk;

            if (ok) {
                // Filter by rules when rules are loaded:
                // - single mode: must allow all guests in one room
                // - multi mode: must allow some subset (min requirements can be met)
                const rulesOk = singleRoomMode
                    ? rulesAllowAllGuestsForThisRoom(roomListing)
                    : rulesAllowAnySubsetForThisRoom(roomListing);

                if (rulesOk === false) {
                    hiddenRooms.push(roomListing);
                    return;
                }
                const priceAttr = roomListing.getAttribute('data-room-price');
                const price = parseFloat(String(priceAttr || '0')) || 0;
                // Calculate recommendation score: lower is better
                const rulesPenalty = (rulesOk === null) ? 5000 : 0; // unknown rules -> less recommended
                const selectedPenalty = selectedRoomIds.has(String(roomListing.getAttribute('data-room-id') || '')) ? 20000 : 0;
                let score = rulesPenalty;
                if (singleRoomMode) {
                    // Priority: exact/smallest waste, then cheapest
                const waste = Math.max(0, cap - total);
                    const isExactMatch = cap === total ? 0 : 1;
                    score += selectedPenalty + isExactMatch * 1000 + waste * 10 + price / 100;
                candidates.push({ el: roomListing, cap: cap || 0, price, waste, isExactMatch, score });
                } else {
                    // Multi-room mode:
                    // Prioritize covering the current deficit with minimal waste, then cheaper.
                    // Rooms already selected get a big penalty (still visible, but not recommended).
                    const needed = deficit > 0 ? deficit : total; // fallback if deficit is 0
                    const shortageAfter = Math.max(0, needed - cap);
                    const waste = Math.max(0, cap - needed);
                    const isExactMatch = (cap === needed) ? 0 : 1;
                    score += selectedPenalty + shortageAfter * 1000 + waste * 10 + price / 100;
                    candidates.push({ el: roomListing, cap: cap || 0, price, waste, isExactMatch, score });
                }
                if (rulesOk === null) unknownRuleRooms.push(roomListing);
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
                // NOTE: Badge insertion removed - it was breaking the room-info layout
                // The recommended class (nsc-room-recommended) is sufficient for styling
                if (index === 0) {
                    // Just add the class, don't insert badge to avoid layout issues
                    // const roomInfo = roomEl.querySelector('.room-info');
                    // Badge insertion removed to prevent layout conflicts
                }
            }

            // Move to correct position in DOM (append to maintain order)
            parentContainer.appendChild(roomEl);
        });

        // If some rooms have unknown rules, attempt to load them in background so filtering improves after fetch.
        // (Fail-open: don't block UI.)
        try {
            unknownRuleRooms.forEach((roomEl) => {
                const url = roomEl.getAttribute('data-room-detail-url');
                if (!url) return;
                if (roomEl.getAttribute('data-room-rules')) return;
                fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                    .then(res => res.ok ? res.json() : null)
                    .then(data => {
                        if (!data) return;
                        if (data.rules && Array.isArray(data.rules)) {
                            roomEl.setAttribute('data-room-rules', JSON.stringify(data.rules));
                        }
                        // Re-run filtering once rules arrive
                        setTimeout(() => {
                            try {
                                const state2 = stateByPk.get(String(pk));
                                const total2 = state2 && state2.guests ? state2.guests.length : total;
                                filterAndRecommendRooms(containerEl, total2);
                            } catch (e) {}
                        }, 0);
                    })
                    .catch(() => null);
            });
        } catch (e) {
            // ignore
        }
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

                // Get registrant email (guest_email) to use for all players
                const registrantEmail = q(`#guest-details-form${pk} input[name="guest_email"]`)?.value || '';

                // Get state to access player data
                const state = stateByPk.get(pk);
                const players = state?.guests?.filter(g => g.isPlayer) || [];

                selected.forEach((cb, idx) => {
                    const childItem = cb.closest('.child-item');
                    const nameDiv =
                        childItem?.querySelector('div[style*="font-weight: 700"][style*="color: var(--mlb-blue)"]') ||
                        childItem?.querySelector('div[style*="font-weight: 700"]');
                    const name = nameDiv ? nameDiv.textContent.trim() : gettext('Player');
                    const birth = cb.getAttribute('data-birth-date') || '';

                    // Try to get player data from state
                    const playerData = players[idx] || {};
                    const playerName = playerData.name || name;
                    const playerBirthDate = playerData.birthDate || birth;
                    // Use registrant email for all players instead of player email
                    const playerEmail = registrantEmail;

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
                            ${playerType === 'adult' ? gettext('Player (Adult)') : gettext('Player (Child)')} ${idx + 1}
                        </div>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">${gettext('Full Name')} *</label>
                                <input type="text" class="form-control nsc-player-name" required
                                       value="${escapeHtml(playerName)}"
                                       style="border-radius:10px; border:2px solid #e9ecef; padding:10px;">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">${gettext('Date of Birth')} *</label>
                                <input type="date" class="form-control nsc-player-dob" required
                                       value="${playerBirthDate || ''}"
                                       style="border-radius:10px; border:2px solid #e9ecef; padding:10px;">
                            </div>
                            <div class="col-md-12">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">${gettext('Email')}</label>
                                <input type="email" class="form-control nsc-player-email"
                                       value="${escapeHtml(playerEmail)}"
                                       style="border-radius:10px; border:2px solid #e9ecef; padding:10px;">
                            </div>
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
                        <div style="font-weight:900; color: var(--mlb-blue); margin-bottom:10px;">${gettext('Adult')} ${idx}</div>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">${gettext('Full Name')} *</label>
                                <input type="text" class="form-control nsc-adult-name" required style="border-radius:10px; border:2px solid #e9ecef; padding:10px;">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">${gettext('Date of Birth')} *</label>
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
                        <div style="font-weight:900; color: var(--mlb-blue); margin-bottom:10px;">${gettext('Child')} ${i}</div>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">${gettext('Full Name')} *</label>
                                <input type="text" class="form-control nsc-child-name" required style="border-radius:10px; border:2px solid #e9ecef; padding:10px;">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label" style="font-weight:700; font-size:0.85rem;">${gettext('Date of Birth')} *</label>
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
            stateByPk.set(pk, { rooms: [], guests: [], guestAssignments: {} });
        }
        const state = stateByPk.get(pk);
        if (!state.rooms) state.rooms = [];
        if (!state.guestAssignments) state.guestAssignments = {};

        // Find the actual room listing element
        let roomListing = btnEl.closest('.room-listing-inline');
        if (!roomListing) {
            roomListing = findRoomInModal(pk, roomId);
        }

        const capacity = parseInt(btnEl.getAttribute('data-room-capacity') || roomListing?.getAttribute('data-room-capacity') || '0', 10);

        // Check if room is already selected
        const roomIndex = state.rooms.findIndex(r => r.roomId === String(roomId));
        const isCurrentlySelected = roomIndex !== -1;

        const roomName = roomListing?.querySelector('.room-name')?.textContent?.trim() || gettext('Room');
        const roomFeatures = roomListing?.querySelector('.room-features')?.textContent?.trim() || '';
        const roomLabel = `${roomName}${roomFeatures ? ` • ${roomFeatures}` : ''}`;

        // Toggle room selection (add or remove from array) - NO VALIDATIONS
        if (isCurrentlySelected) {
            // Remove room from selection
            removeRoomFromState(pk, state, roomId);
            showToast(t('roomRemoved', { label: roomLabel }), 'info', 3000);
        } else {
            // Add room to selection
            addRoomToState(pk, state, roomId, roomLabel, capacity);
            showToast(t('roomAdded', { label: roomLabel, count: state.rooms.length }), 'success', 3000);
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

        // Update hidden input for form submission
        const roomInput = q(`guest-room${pk}`);
        if (roomInput && state.rooms.length > 0) {
            roomInput.value = String(state.rooms[0].roomId);
        }

        // Update price calculation
        updateRoomsPriceCalculation(pk);
        validateRoomSelection(pk);

        // Forzar scroll al inicio del modal para que el usuario vea el botón de continuar
        const roomsModalElForScroll = q(`hotelRoomsModal${pk}`);
        if (roomsModalElForScroll) {
            roomsModalElForScroll.scrollTop = 0;
            if (window.parent) {
                window.parent.postMessage({ type: 'nsc-scroll-to-top', tabId: window.name }, window.location.origin);
            }
        }

        // Show success message
        const statusEl = q(`rooms-selection-status${pk}`);
        if (statusEl) {
            statusEl.style.display = 'block';
            statusEl.style.background = '#d4edda';
            statusEl.style.border = '1px solid #c3e6cb';
            statusEl.style.color = '#155724';
            statusEl.innerHTML = `<i class="fas fa-check-circle me-1"></i><strong>${escapeHtml(t('roomSelectedReady'))}</strong>`;
        }
    }

    function backToGuests(pk) {
        const p = String(pk || '');
        if (!p) return;
        const roomsModalEl = q(`hotelRoomsModal${p}`);
        const reservationModalEl = q(`hotelReservationModal${p}`);
        if (!roomsModalEl || !reservationModalEl || !window.bootstrap?.Modal) return;

        // Use helper function to close rooms modal and open reservation modal
        closeAndOpenModal(roomsModalEl, reservationModalEl);
    }

    function backToRooms(pk) {
        const p = String(pk || '');
        if (!p) return;
        const guestModalEl = q(`hotelGuestDetailsModal${p}`);
        const roomsModalEl = q(`hotelRoomsModal${p}`);
        if (!guestModalEl || !roomsModalEl || !window.bootstrap?.Modal) return;

        // Use helper function to close guest modal and open rooms modal
            const actualRoomsModal = setupModalFocusHandling(roomsModalEl) || roomsModalEl;
        closeAndOpenModal(guestModalEl, actualRoomsModal);
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
        if (titleEl) titleEl.textContent = gettext('Loading...');
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
        if (galleryEl) galleryEl.innerHTML = `<div style="padding: 18px; color: #6c757d; text-align: center;">${gettext('Loading...')}</div>`;

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

        let modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: true, keyboard: true, focus: true });
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
                const roomName = data.name || data.room_type || gettext('Room');
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
                    descEl.innerHTML = `<div style="color: #6c757d; font-style: italic; font-size: 0.85rem; font-weight: 400;">${gettext('No description available.')}</div>`;
                }
            }

            // Update capacity and price
            if (capEl) capEl.textContent = `${data.capacity ?? '-'} ${data.capacity === 1 ? gettext('person') : gettext('people')}`;
            if (priceEl) priceEl.textContent = `$${parseFloat(data.price_per_night || 0).toFixed(2)}`;

            // Update additional information
            const includesGuestsEl = q(`room-detail-modal-includes-guests${pk}`);
            if (includesGuestsEl) {
                const includes = data.price_includes_guests || 1;
                includesGuestsEl.textContent = `${includes} ${includes === 1 ? gettext('guest') : gettext('guests')}`;
            }

            const additionalPriceEl = q(`room-detail-modal-additional-price${pk}`);
            if (additionalPriceEl) {
                const addPrice = parseFloat(data.additional_guest_price || 0);
                additionalPriceEl.textContent = addPrice > 0 ? `$${addPrice.toFixed(2)}/${gettext('night')}` : gettext('Included');
            }

            const breakfastEl = q(`room-detail-modal-breakfast${pk}`);
            if (breakfastEl) {
                breakfastEl.textContent = data.breakfast_included ? gettext('Included') : gettext('Not included');
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
                    galleryEl.innerHTML = `<div style="padding: 18px; color: #6c757d; text-align: center; font-size: 0.85rem;">${gettext('No images available.')}</div>`;
                } else {
                    // Store images globally for lightbox
                    if (!window.roomImages) window.roomImages = {};
                    window.roomImages[pk] = images;

                    // Create masonry gallery with better organization
                    // Pre-calculate heights for better distribution
                    const heights = [200, 180, 220, 190, 210, 200, 185, 215]; // Alternating heights for better balance
                    const masonryItems = images.map((img, idx) => {
                        const imgUrl = img.image_url || img.url;
                        const imgAlt = escapeHtml(img.title || img.alt || interpolate(gettext('Room image %(num)s'), { num: idx + 1 }, true));
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
                            interpolate(gettext('Adults: %(minAdults)s-%(maxAdults)s • Children: %(minChildren)s-%(maxChildren)s'), {
                                minAdults: rule.min_adults,
                                maxAdults: rule.max_adults,
                                minChildren: rule.min_children,
                                maxChildren: rule.max_children
                            }, true);
                        return `
                            <div style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 10px; margin-bottom: 8px; font-size: 0.85rem;">
                                <div style="font-weight: 600; color: var(--mlb-blue); margin-bottom: 4px;">
                                    <i class="fas fa-check-circle me-1" style="color: var(--mlb-red);"></i>${escapeHtml(desc)}
                                </div>
                                <div style="color: #6c757d; font-size: 0.8rem; font-weight: 400;">
                                    ${interpolate(gettext('Adults: %(minAdults)s-%(maxAdults)s • Children: %(minChildren)s-%(maxChildren)s'), {
                                        minAdults: rule.min_adults,
                                        maxAdults: rule.max_adults,
                                        minChildren: rule.min_children,
                                        maxChildren: rule.max_children
                                    }, true)}
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
                                    <strong>✅ ${escapeHtml(t('correct'))}:</strong> ${escapeHtml(t('selectionMatchesRules', { adults, children }))}
                                </div>
                            `;
                        } else {
                            rulesValidationEl.innerHTML = `
                                <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 10px; color: #856404; font-size: 0.85rem;">
                                    <i class="fas fa-exclamation-triangle me-1"></i>
                                    <strong>⚠ ${escapeHtml(t('attention'))}:</strong> ${escapeHtml(t('selectionDoesNotMatchRules', { adults, children }))}
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
                    amenitiesEl.innerHTML = `<div style="color:#6c757d; font-size: 0.85rem; font-style: italic;">${escapeHtml(t('noAmenities'))}</div>`;
                }
            }

            // Set up select button
            if (selectBtn) {
                selectBtn.onclick = function() {
                    // Find the actual room listing element in the Available Rooms modal
                    const actualRoomEl = findRoomInModal(pk, roomId);

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
                galleryEl.innerHTML = `<div style="padding: 18px; color: #b30029; font-weight: 800; text-align: center;">${gettext('Failed to load room details. Please try again.')}</div>`;
            }
            if (titleEl) titleEl.textContent = gettext('Error loading room');
        if (descEl) descEl.innerHTML = `<div style="color: #b30029; font-size: 0.85rem;">${gettext('Error')}: ${escapeHtml(err.message || t('unknownError'))}</div>`;
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

    // Bootstrap modal hook - optimized to only run for specific modals
    document.addEventListener('shown.bs.modal', (e) => {
        const modalEl = e.target;
        // Early return if not the modal we care about
        if (!modalEl || !modalEl.classList?.contains('modal') || !modalEl.id || !modalEl.id.startsWith('hotelReservationModal')) return;
        const pk = modalEl.getAttribute('data-hotel-pk');
        if (pk) {
            // Defer initialization to prevent blocking modal animation
            requestAnimationFrame(() => {
                initModal(String(pk));
            });
        }
    }, { passive: true });

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
            showToast(gettext('No rooms selected'), 'error');
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
            const roomEl = findRoomInModal(pk, room.roomId);
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

        showToast(gettext('Hotel reservation added to checkout'), 'success');
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
                        <i class="fas fa-hotel me-2" style="color: var(--mlb-red);"></i>${gettext('Hotel Stay')}
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
                        ${escapeHtml(room.roomLabel)} (${room.guests}/${room.capacity} ${gettext('guests')})
                    </div>
                    <div style="font-size: 0.8rem; color: #6c757d;">
                        ${gettext('Check-in')}: ${reservationData.checkIn || gettext('N/A')} • ${gettext('Check-out')}: ${reservationData.checkOut || gettext('N/A')}
                    </div>
                    <div style="font-weight: 700; color: var(--mlb-red); font-size: 0.9rem; margin-top: 4px;">
                        $${room.price.toFixed(2)}/${gettext('night')}
                    </div>
                </div>
            `;
        });

        // Add guests summary
        const totalGuests = reservationData.players.length + reservationData.additionalAdults.length + reservationData.additionalChildren.length + 1; // +1 for main contact
        html += `
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e9ecef;">
                <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 4px;">
                    <strong>${gettext('Main Contact')}:</strong> ${escapeHtml(reservationData.mainContact.name)}${reservationData.mainContact.email ? ` (${escapeHtml(reservationData.mainContact.email)})` : ''}
                </div>
                <div style="font-size: 0.8rem; color: #6c757d;">
                    <strong>${gettext('Total Guests')}:</strong> ${totalGuests} (${reservationData.players.length} ${reservationData.players.length !== 1 ? gettext('players') : gettext('player')}, ${reservationData.additionalAdults.length} ${reservationData.additionalAdults.length !== 1 ? gettext('additional adults') : gettext('additional adult')}, ${reservationData.additionalChildren.length} ${reservationData.additionalChildren.length !== 1 ? gettext('additional children') : gettext('additional child')})
                </div>
            </div>
        `;

        // Add total price
        html += `
            <div style="margin-top: 12px; padding-top: 12px; border-top: 2px solid var(--mlb-red); display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 800; color: var(--mlb-blue); font-size: 1rem;">${gettext('Total')}:</span>
                <span class="hotel-reservation-total" style="font-weight: 800; color: var(--mlb-red); font-size: 1.2rem;">
                    $${reservationData.totalPrice.toFixed(2)}/${gettext('night')}
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

        // No mostrar total general adicional en el checkout (requerimiento de UX).
        // Si existe de ejecuciones anteriores, eliminarlo.
        const totalDisplay = checkoutCard.querySelector('.checkout-grand-total');
        if (totalDisplay) {
            totalDisplay.remove();
        }
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
        let registrantPhone = null;

        if (userData && typeof userData === 'object') {
            registrantName = userData.name || null;
            registrantEmail = userData.email || null;
            registrantBirthDate = userData.birthDate || null;
            registrantPhone = userData.phone || null;
        }

        if (!registrantName) registrantName = window.currentUserName;
        if (!registrantName) {
            const mainContent = document.querySelector('[data-user-name]');
            if (mainContent) registrantName = mainContent.getAttribute('data-user-name');
            }
        if (!registrantName) registrantName = 'You';

        // Calculate age
        let registrantAge = null;
        if (registrantBirthDate) {
            const birthDate = new Date(registrantBirthDate);
            if (!isNaN(birthDate.getTime())) {
                registrantAge = Math.floor((new Date() - birthDate) / (365.25 * 24 * 60 * 60 * 1000));
            }
        }

        const registrantType = registrantAge !== null && registrantAge < 18 ? 'child' : 'adult';

        const registrant = {
            name: registrantName.trim(),
            email: registrantEmail ? registrantEmail.trim() : null,
            phone: registrantPhone ? registrantPhone.trim() : null,
            birthDate: registrantBirthDate ? registrantBirthDate.trim() : null,
            age: registrantAge,
            type: registrantType,
            isRegistrant: true
        };

        // Store guests state
        if (!stateByPk.has(pk)) {
            stateByPk.set(pk, { rooms: [], guests: [], guestAssignments: {} });
        }
        const state = stateByPk.get(pk);

        // Initialize default guests
        state.guests = [];
        if (registrant.name) {
            state.guests.push(registrant);
        }

        selectedPlayers.forEach(cb => {
            const childItem = cb.closest('.child-item');
            if (!childItem) return;

            let name = childItem.getAttribute('data-child-name');
            if (!name) {
                const nameDiv = childItem.querySelector('div[style*="font-weight: 700"]');
                name = nameDiv ? nameDiv.textContent.trim() : 'Player';
            }

            const email = childItem.getAttribute('data-child-email') || null;
            const birthDate = childItem.getAttribute('data-birth-date') || null;
            let age = null;
            if (birthDate) {
                const bd = new Date(birthDate);
                if (!isNaN(bd.getTime())) {
                    age = Math.floor((new Date() - bd) / (365.25 * 24 * 60 * 60 * 1000));
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

        // FILTRADO INTELIGENTE: Ocultar habitaciones con capacidad insuficiente
        const totalGuestsCount = state.guests.length;
        const roomListings = roomsModalEl.querySelectorAll('.room-listing-inline');
        let visibleRoomsCount = 0;

        roomListings.forEach(el => {
            const cap = parseInt(el.getAttribute('data-room-capacity') || '0', 10);
            if (cap < totalGuestsCount) {
                el.style.display = 'none';
            } else {
                el.style.display = 'block';
                visibleRoomsCount++;
            }
        });

        // Mostrar mensaje si no hay habitaciones
        let noRoomsAlert = roomsModalEl.querySelector('.nsc-no-rooms-alert');
        if (visibleRoomsCount === 0) {
            if (!noRoomsAlert) {
                noRoomsAlert = document.createElement('div');
                noRoomsAlert.className = 'alert alert-warning nsc-no-rooms-alert text-center m-3';
                noRoomsAlert.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i> ${gettext('No rooms available for')} ${totalGuestsCount} ${gettext('guests')}.`;
                const listZone = roomsModalEl.querySelector('.rooms-list-zone') || roomsModalEl.querySelector('.modal-body');
                if (listZone) listZone.prepend(noRoomsAlert);
            } else {
                noRoomsAlert.style.display = 'block';
            }
        } else if (noRoomsAlert) {
            noRoomsAlert.style.display = 'none';
        }

        // Update UI
        updateRoomsGuestsList(pk);
        updateRoomsPriceCalculation(pk);
        validateRoomSelection(pk);

        // Open modal
        if (!window.bootstrap?.Modal) return;
        // Setup focus handling for this modal
        setupModalFocusHandling(roomsModalEl);

        let inst = bootstrap.Modal.getOrCreateInstance(roomsModalEl);
        inst.show();

        // Forzar scroll al inicio del modal
        roomsModalEl.scrollTop = 0;
        if (window.parent) {
            window.parent.postMessage({ type: 'nsc-scroll-to-top', tabId: window.name }, window.location.origin);
        }

        // Update header
        const headerEl = q(`rooms-default-guests${pk}`);
        if (headerEl) {
            headerEl.textContent = `${totalGuestsCount} ${totalGuestsCount === 1 ? gettext('guest') : gettext('guests')} (${state.guests.filter(g => g.type === 'adult').length} ${gettext('adults')}, ${state.guests.filter(g => g.type === 'child').length} ${gettext('children')})`;
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
            const roomEl = findRoomInModal(pk, room.roomId);
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

            // Validate roomCapacity is valid
            if (!Number.isFinite(roomCapacity) || roomCapacity <= 0) {
                console.warn('updateRoomsPriceCalculation: Invalid room capacity for roomId:', room.roomId, 'capacity:', roomCapacity);
            }

            totalCapacity += (Number.isFinite(roomCapacity) && roomCapacity > 0) ? roomCapacity : 0;

            // Get assigned guests for this room (or use auto-distribution)
            const assignedGuestIndices = state.guestAssignments[room.roomId] || [];
            const guestsForThisRoom = assignedGuestIndices.length;

            // Calculate actual guests for this room
            // If no guests assigned, use 0 for display but still show base price
            const actualGuestsForRoom = Math.min(guestsForThisRoom, roomCapacity);

            // Calculate additional guests and cost only if there are assigned guests
            // Base price is always shown, additional cost only applies when guests exceed base included
            const additionalGuestsForRoom = (actualGuestsForRoom > 0) ? Math.max(0, actualGuestsForRoom - roomIncludesGuests) : 0;
            const additionalCostForRoom = additionalGuestsForRoom > 0 ? additionalGuestPrice * additionalGuestsForRoom : 0;

            // Room total: base price + additional guest costs
            // Base price is always included even if no guests assigned yet
            const roomTotal = roomPrice + additionalCostForRoom;
            totalPrice += roomTotal;

            // Collect rules
            const rulesJson = roomEl.getAttribute('data-room-rules');
            let activeRoomRules = [];
            let roomRuleStatus = null; // { valid: boolean, matchedDesc?: string, allowedDesc?: string[] }
            if (rulesJson) {
                try {
                    const rules = JSON.parse(rulesJson);
                    allRules = allRules.concat(rules);
                    activeRoomRules = Array.isArray(rules) ? rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active) : [];
                } catch (e) {
                    console.warn('Error parsing rules for room:', room.roomId, e);
                }
            }

            // Per-room rules validation based on ASSIGNED guests (not global totals)
            try {
                if (activeRoomRules && activeRoomRules.length > 0) {
                    const assignedGuestsObjs = assignedGuestIndices.map(gi => state.guests[gi]).filter(Boolean);
                    const assignedAdults = assignedGuestsObjs.filter(g => g.type === 'adult').length;
                    const assignedChildren = assignedGuestsObjs.filter(g => g.type === 'child').length;
                    const isGenericDesc = (desc) => {
                        const d = (desc || '').toString().trim().toLowerCase();
                        return !d || /^regla\s*\d+$/i.test(d) || /^rule\s*\d+$/i.test(d);
                    };
                    const describeRule = (rule) => {
                        const minA = parseInt(rule.min_adults) || 0;
                        const maxA = parseInt(rule.max_adults) || 0;
                        const minC = parseInt(rule.min_children) || 0;
                        const maxC = parseInt(rule.max_children) || 0;
                        const current = t('nowYouHave', {
                            adults: assignedAdults,
                            adultWord: nounForCount(assignedAdults, 'adultOne', 'adultMany'),
                            children: assignedChildren,
                            childWord: nounForCount(assignedChildren, 'childOne', 'childMany')
                        });
                        const req = `${t('requirementPrefix')} ` + t('requirementLine', {
                            adultsReq: rangeText(minA, rule.max_adults, 'adultOne', 'adultMany'),
                            childrenReq: rangeText(minC, rule.max_children, 'childOne', 'childMany')
                        });
                        const hintA = makeActionHint(assignedAdults, minA, rule.max_adults, 'adultOne', 'adultMany');
                        const hintC = makeActionHint(assignedChildren, minC, rule.max_children, 'childOne', 'childMany');
                        const hint = [hintA, hintC].filter(Boolean).join(' ');
                        const custom = rule.description;
                        const customText = isGenericDesc(custom) ? '' : `${escapeHtml(custom)}. `;
                        return `${customText}${current} ${req}${hint ? ' ' + hint : ''}`;
                    };
                    const validRules = activeRoomRules.filter(rule => {
                        const minAdults = parseInt(rule.min_adults) || 0;
                        const maxAdults = parseInt(rule.max_adults) || 999;
                        const minChildren = parseInt(rule.min_children) || 0;
                        const maxChildren = parseInt(rule.max_children) || 999;
                        return assignedAdults >= minAdults && assignedAdults <= maxAdults &&
                               assignedChildren >= minChildren && assignedChildren <= maxChildren;
                    });
                    if (validRules.length > 0) {
                        const rule = validRules[0];
                        roomRuleStatus = { valid: true, matchedDesc: describeRule(rule), assignedAdults, assignedChildren };
                    } else {
                        const allowedDesc = activeRoomRules.map(rule => describeRule(rule));
                        roomRuleStatus = { valid: false, allowedDesc, assignedAdults, assignedChildren };
                    }
                }
            } catch (e) {
                // fail-open
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
                actualGuestsCount: actualGuestsForRoom,
                roomRuleStatus: roomRuleStatus
            });
        });

        let html = `<div style="font-weight: 600; color: var(--mlb-blue); margin-bottom: 8px; font-size: 0.9rem;">${escapeHtml(t('priceBreakdownTitle', { count: state.rooms.length }))}</div>`;

        // Show breakdown for each room with guest assignment
        roomBreakdown.forEach((room, idx) => {
            html += `<div style="margin-bottom: 8px; padding: 8px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid var(--mlb-blue);">`;
            html += `<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">`;
            html += `<div style="font-weight: 600; color: var(--mlb-blue); font-size: 0.85rem;">${escapeHtml(interpolate(gettext('Room %(id)s'), { id: idx + 1 }, true))}: ${escapeHtml(room.roomLabel)}</div>`;
            html += `<div style="display: flex; gap: 6px;">`;
            html += `<button type="button" onclick="window.NSC_HotelReservation?.showGuestAssignment?.('${pk}', '${room.roomId}');" style="background: var(--mlb-blue); color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='var(--mlb-red)';" onmouseout="this.style.background='var(--mlb-blue)';">${escapeHtml(t('assignGuests'))}</button>`;
            html += `<button type="button" onclick="window.NSC_HotelReservation?.removeRoom?.('${pk}', '${room.roomId}');" style="background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#c82333';" onmouseout="this.style.background='#dc3545';" title="${escapeHtml(t('removeRoom'))}"><i class="fas fa-times"></i></button>`;
            html += `</div>`;
            html += `</div>`;

            // Show assigned guests
            if (room.assignedGuests && room.assignedGuests.length > 0) {
                const assignedGuestNames = room.assignedGuests.map(gi => {
                    const guest = state.guests[gi];
                    return guest ? escapeHtml(guest.name) : '';
                }).filter(n => n).join(', ');
                html += `<div style="font-size: 0.75rem; color: #6c757d; margin-bottom: 4px; font-style: italic;">${escapeHtml(t('assignedLabel', { names: assignedGuestNames || t('none') }))}</div>`;
            } else {
                html += `<div style="font-size: 0.75rem; color: #ffc107; margin-bottom: 4px; font-style: italic;">⚠ ${escapeHtml(t('noGuestsAssignedThisRoom'))}</div>`;
            }

            // Per-room occupancy rule help (based on assigned guests)
            if (room.roomRuleStatus) {
                if (room.roomRuleStatus.valid) {
                    // Keep this subtle; the important UX is when it fails
                    html += `<div style="font-size: 0.74rem; color: #155724; margin-bottom: 4px; font-weight: 800;">✅ ${escapeHtml(t('rulesSatisfied'))}</div>`;
                if (room.roomRuleStatus.matchedDesc) {
                        html += `<div style="font-size: 0.73rem; color: #6c757d; margin-bottom: 4px;">${escapeHtml(room.roomRuleStatus.matchedDesc)}</div>`;
                    }
                } else {
                    html += `<div style="font-size: 0.75rem; color: #b45309; margin-bottom: 4px; font-weight: 900;">⚠ ${escapeHtml(t('roomRulesNotMetTitle'))}</div>`;
                    if (room.roomRuleStatus.allowedDesc && room.roomRuleStatus.allowedDesc.length) {
                        const list = room.roomRuleStatus.allowedDesc.map(d => `<div style="font-size: 0.72rem; color: #6c757d; padding-left: 10px; margin-top: 2px;">• ${escapeHtml(d)}</div>`).join('');
                        html += `<div style="margin-bottom: 6px;">${list}</div>`;
                    }
                }
            }

            html += `<div style="font-size: 0.8rem; color: #333; margin-bottom: 2px;">${gettext('Base price')} (${room.roomIncludesGuests} ${room.roomIncludesGuests === 1 ? gettext('guest') : gettext('guests')}): <strong>$${room.roomPrice.toFixed(2)}</strong>/${gettext('night')}</div>`;
            if (room.additionalGuestsForRoom > 0) {
                html += `<div style="font-size: 0.8rem; color: #333; margin-bottom: 2px;">${gettext('Additional guests')} (${room.actualGuestsCount - room.roomIncludesGuests}): <strong style="color: var(--mlb-red);">+$${room.additionalCostForRoom.toFixed(2)}</strong>/${gettext('night')}</div>`;
            }
            // Show capacity correctly - use actual assigned count or show 0 if none assigned
            const displayGuestCount = (room.assignedGuests && room.assignedGuests.length > 0) ? room.actualGuestsCount : 0;
            html += `<div style="font-size: 0.85rem; color: var(--mlb-blue); margin-top: 4px; font-weight: 600;">${gettext('Room Total')}: $${room.roomTotal.toFixed(2)}/${gettext('night')} (${displayGuestCount}/${room.roomCapacity} ${gettext('capacity')})</div>`;
            html += `</div>`;
        });

        html += `<div style="font-weight: 700; color: var(--mlb-red); margin-top: 12px; padding-top: 12px; border-top: 2px solid #e9ecef; font-size: 1.1rem;">${gettext('Total (All Rooms)')}: $${totalPrice.toFixed(2)}/${gettext('night')}</div>`;

        // Capacity validation
        const adults = state.guests.filter(g => g.type === 'adult').length;
        const children = state.guests.filter(g => g.type === 'child').length;
        const total = adults + children;
        let capacityValid = total <= totalCapacity;

        html += `<div style="margin-top: 12px; padding: 8px; border-radius: 6px; ${!capacityValid ? 'background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;' : 'background: #d4edda; border: 1px solid #c3e6cb; color: #155724;'} font-size: 0.85rem;">`;
        html += `<i class="fas ${!capacityValid ? 'fa-exclamation-circle' : 'fa-check-circle'} me-1"></i>`;
        html += `<strong>${escapeHtml(t('capacitySummary', { total, adults, children, totalCapacity, rooms: state.rooms.length }))}</strong>`;
        if (!capacityValid) {
            html += ` <span style="color: #721c24; font-weight: 700; display: block; margin-top: 6px;">⚠ ${gettext('Exceeds capacity by')} ${total - totalCapacity} ${(total - totalCapacity) === 1 ? gettext('guest') : gettext('guests')}</span>`;
            html += `<div style="margin-top: 8px; padding: 8px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; color: #856404; font-size: 0.8rem;">`;
            html += `<i class="fas fa-info-circle me-1"></i><strong>${gettext('Action required')}:</strong> ${interpolate(gettext('Please add another room or change to a room with higher capacity to accommodate all %(total)s guests.'), { total }, true)}</div>`;
        }
        html += `</div>`;

        // Occupancy rules summary:
        // NOTE: When multiple rooms are selected, rules are validated PER ROOM (using assigned guests),
        // not as a single combined rule across all rooms.
        const roomsWithRuleStatus = roomBreakdown.filter(r => r.roomRuleStatus);
        if (roomsWithRuleStatus.length > 0) {
                html += `<div style="margin-top: 12px; padding-top: 12px; border-top: 2px solid #e9ecef;">`;
            html += `<div style="font-weight: 600; color: var(--mlb-blue); font-size: 0.85rem; margin-bottom: 6px;"><i class="fas fa-users-cog me-1"></i>${gettext('Occupancy Rules')}:</div>`;

            const invalidRooms = roomsWithRuleStatus.filter(r => r.roomRuleStatus && r.roomRuleStatus.valid === false);
            if (invalidRooms.length === 0) {
                    html += `<div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 8px; color: #155724; font-size: 0.8rem; margin-bottom: 6px;">`;
                html += `<i class="fas fa-check-circle me-1"></i><strong>✅ ${gettext('All selected rooms meet occupancy rules.')}</strong>`;
                    html += `</div>`;
                } else {
                    html += `<div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 8px; color: #856404; font-size: 0.8rem; margin-bottom: 6px;">`;
                html += `<i class="fas fa-exclamation-triangle me-1"></i><strong>⚠ ${gettext('Attention')}:</strong> ${gettext('Some selected rooms do not meet occupancy rules.')}`;
                    html += `</div>`;

                invalidRooms.forEach((room, idx) => {
                    html += `<div style="font-size: 0.8rem; color: #6c757d; margin-top: 6px; font-weight: 800;">${escapeHtml(interpolate(gettext('Room %(id)s'), { id: idx + 1 }, true))}: ${escapeHtml(room.roomLabel)}</div>`;
                    if (room.roomRuleStatus?.allowedDesc?.length) {
                        const list = room.roomRuleStatus.allowedDesc.map(d => `<div style="font-size: 0.75rem; color: #6c757d; margin-top: 4px; padding-left: 12px;">• ${escapeHtml(d)}</div>`).join('');
                        html += `<div style="margin-top: 4px;">${list}</div>`;
                    }
                });
                }

                html += `</div>`;
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

        // Ensure guestAssignments exists (some older states may not initialize it)
        if (!state.guestAssignments) {
            state.guestAssignments = {};
        }

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
            const roomsWithoutGuests = [];
            const roomsWithRuleViolations = [];

            // Determine if there exists ANY single available room that can fit all guests
            // AND can satisfy occupancy rules with those guests (adults/children) when everyone stays in one room.
            // This lets us recommend "Change room" instead of "Add room" when capacity is exceeded.
            let singleRoomCandidate = null; // { roomId, cap, price, label }
            try {
                if (!roomsModalEl) return;
                const listings = Array.from(roomsModalEl.querySelectorAll('.room-listing-inline') || []);
                const candidates = listings
                    .map((el) => {
                        const cap = parseInt(el.getAttribute('data-room-capacity') || '0', 10) || 0;
                        const price = parseFloat(el.getAttribute('data-room-price') || '0') || 0;
                        const roomId = el.getAttribute('data-room-id') || '';
                        const label = el.querySelector('.room-name')?.textContent?.trim() || 'Room';
                        // Rules feasibility:
                        // - if rules loaded: must satisfy
                        // - if rules not loaded: treat as UNKNOWN (do not recommend single-room change yet)
                        let rulesOk = null;
                        const rulesJson = el.getAttribute('data-room-rules');
                        if (!rulesJson) {
                            rulesOk = null;
                        } else {
                            try {
                                const rules = JSON.parse(rulesJson) || [];
                                const activeRules = Array.isArray(rules)
                                    ? rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active)
                                    : [];
                                if (activeRules.length > 0) {
                                    rulesOk = activeRules.some(rule => {
                                        const minAdults = parseInt(rule.min_adults) || 0;
                                        const maxAdults = parseInt(rule.max_adults) || 999;
                                        const minChildren = parseInt(rule.min_children) || 0;
                                        const maxChildren = parseInt(rule.max_children) || 999;
                                        return adults >= minAdults && adults <= maxAdults &&
                                               children >= minChildren && children <= maxChildren;
                                    });
                                } else {
                                    rulesOk = true;
                                }
                            } catch (e) {
                                rulesOk = null;
                            }
                        }
                        return { el, roomId, cap, price, label };
                    })
                    .filter((c) => c.cap >= total && (c.el ? true : true));

                if (candidates.length) {
                    // Filter out candidates that don't satisfy rules (if rules exist)
                    const filtered = candidates.filter((c) => {
                        try {
                            const rulesJson = c.el?.getAttribute?.('data-room-rules');
                            if (!rulesJson) return false; // unknown rules -> do not recommend change yet
                            const rules = JSON.parse(rulesJson) || [];
                            const activeRules = Array.isArray(rules)
                                ? rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active)
                                : [];
                            if (!activeRules.length) return true;
                            return activeRules.some(rule => {
                                const minAdults = parseInt(rule.min_adults) || 0;
                                const maxAdults = parseInt(rule.max_adults) || 999;
                                const minChildren = parseInt(rule.min_children) || 0;
                                const maxChildren = parseInt(rule.max_children) || 999;
                                return adults >= minAdults && adults <= maxAdults &&
                                       children >= minChildren && children <= maxChildren;
                            });
                        } catch (e) {
                            return false;
                        }
                    });

                    // Prefer exact/smallest fit, then cheaper
                    filtered.sort((a, b) => (a.cap - b.cap) || (a.price - b.price));
                    const best = filtered[0];
                    singleRoomCandidate = { roomId: best.roomId, cap: best.cap, price: best.price, label: best.label };
                }
            } catch (e) {
                // ignore
            }

            state.rooms.forEach(room => {
                const roomEl = findRoomInModal(pk, room.roomId);
                if (roomEl) {
                    const roomCap = parseInt(roomEl.getAttribute('data-room-capacity') || '0', 10);
                    // Validate capacity is a valid number
                    if (Number.isFinite(roomCap) && roomCap > 0) {
                        totalCapacity += roomCap;
                    } else {
                        console.warn('validateRoomSelection: Invalid room capacity for roomId:', room.roomId, 'capacity:', roomCap);
                    }

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

                // Validate guest assignment per room: every selected room must have at least one guest
                const assignments = state.guestAssignments ? (state.guestAssignments[String(room.roomId)] || []) : [];
                if (!assignments || assignments.length === 0) {
                    roomsWithoutGuests.push(room);
                } else {
                    // Validate occupancy rules PER ROOM (based on assigned guests)
                    try {
                        const assignedGuests = assignments.map(idx => state.guests[idx]).filter(Boolean);
                        const assignedAdults = assignedGuests.filter(g => g.type === 'adult').length;
                        const assignedChildren = assignedGuests.filter(g => g.type === 'child').length;

                        const rulesJson = roomEl?.getAttribute('data-room-rules');
                        let rules = [];
                        if (rulesJson) {
                            try { rules = JSON.parse(rulesJson) || []; } catch (e) { rules = []; }
                        }
                        const activeRules = Array.isArray(rules) ? rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active) : [];
                if (activeRules.length > 0) {
                    const validRules = activeRules.filter(rule => {
                        const minAdults = parseInt(rule.min_adults) || 0;
                        const maxAdults = parseInt(rule.max_adults) || 999;
                        const minChildren = parseInt(rule.min_children) || 0;
                        const maxChildren = parseInt(rule.max_children) || 999;
                                return assignedAdults >= minAdults && assignedAdults <= maxAdults &&
                                       assignedChildren >= minChildren && assignedChildren <= maxChildren;
                            });
                            if (validRules.length === 0) {
                                roomsWithRuleViolations.push({
                                    room,
                                    assignedAdults,
                                    assignedChildren,
                                    activeRules
                                });
                            }
                        }
                    } catch (e) {
                        // If we can't validate, fail-open (do not block)
                    }
                }
            });

            // Highlight rooms that need guest assignment
            try {
                const roomsModalEl2 = q(`hotelRoomsModal${pk}`);
                const allRoomEls = roomsModalEl2 ? roomsModalEl2.querySelectorAll(`[data-room-id]`) : document.querySelectorAll(`[data-room-id]`);
                allRoomEls.forEach((el) => {
                    if (!el || !el.classList || !el.classList.contains('room-listing-inline')) return;
                    el.removeAttribute('data-needs-guests');
                });
                roomsWithoutGuests.forEach((room) => {
                    const el = findRoomInModal(pk, room.roomId);
                    if (el) el.setAttribute('data-needs-guests', 'true');
                });
            } catch (e) {
                // ignore
            }

            // Validate capacity
            const capacityValid = total <= totalCapacity;
            // Validate if there exists ANY combination that could possibly fit all guests (capacity availability)
            let capacityPossible = true;
            let maxAvailableCapacity = null;
            let unselectedRoomsCount = null;
            try {
                const roomsModalElForAvail = q(`hotelRoomsModal${pk}`);
                const listingsAvail = Array.from(roomsModalElForAvail?.querySelectorAll('.room-listing-inline') || []);
                const seen = new Set();
                let sum = 0;
                let unselected = 0;
                const selectedSet = new Set((state.rooms || []).map(r => String(r.roomId)));
                listingsAvail.forEach((el) => {
                    const rid = String(el.getAttribute('data-room-id') || '');
                    if (!rid || seen.has(rid)) return;
                    seen.add(rid);
                    const cap = parseInt(el.getAttribute('data-room-capacity') || '0', 10) || 0;
                    sum += cap;
                    if (!selectedSet.has(rid)) unselected += 1;
                });
                maxAvailableCapacity = sum;
                unselectedRoomsCount = unselected;
                if (maxAvailableCapacity > 0 && total > maxAvailableCapacity) {
                    capacityPossible = false;
                }
            } catch (e) {
                // fail-open
                capacityPossible = true;
            }

            // Validate if the guest mix (adults/children) is even feasible with available room rules.
            // This is a conservative check meant to catch obvious "no solution" cases like:
            // - 0 children, but every room requires at least 1 child
            // - children > sum of max_children across all rooms (or adults > sum max_adults)
            // Only hard-block when rules are known for all rooms we inspected.
            let rulesPossible = true;
            let rulesPossibleReason = null;
            let rulesKnownForAll = true;
            try {
                const roomsModalElForRules = q(`hotelRoomsModal${pk}`);
                const listingsRules = Array.from(roomsModalElForRules?.querySelectorAll('.room-listing-inline') || []);
                const seen = new Set();
                let sumMaxAdults = 0;
                let sumMaxChildren = 0;
                let anyAllowsZeroChildren = false;
                let anyAllowsAnyChildren = false;
                let anyAllowsAnyAdults = false;

                listingsRules.forEach((el) => {
                    const rid = String(el.getAttribute('data-room-id') || '');
                    if (!rid || seen.has(rid)) return;
                    seen.add(rid);
                    const cap = parseInt(el.getAttribute('data-room-capacity') || '0', 10) || 0;
                    const rulesJson = el.getAttribute('data-room-rules');
                    if (!rulesJson) {
                        rulesKnownForAll = false;
                        // Unknown rules: don't assume restrictive; keep fail-open.
                        sumMaxAdults += cap;
                        sumMaxChildren += cap;
                        anyAllowsZeroChildren = true;
                        anyAllowsAnyChildren = true;
                        anyAllowsAnyAdults = true;
                        return;
                    }

                    let rules = [];
                    try { rules = JSON.parse(rulesJson) || []; } catch (e) { rules = []; rulesKnownForAll = false; }
                    const activeRules = Array.isArray(rules) ? rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active) : [];
                    if (!activeRules.length) {
                        // No active rules => unrestricted by type, only capacity matters
                        sumMaxAdults += cap;
                        sumMaxChildren += cap;
                        anyAllowsZeroChildren = true;
                        anyAllowsAnyChildren = true;
                        anyAllowsAnyAdults = true;
                        return;
                    }

                    // For bounds, use the most permissive rule (max) while respecting cap.
                    let roomMaxA = 0;
                    let roomMaxC = 0;
                    let roomAllowsZeroChild = false;
                    let roomAllowsAnyChild = false;
                    let roomAllowsAnyAdult = false;
                    activeRules.forEach((rule) => {
                        const minA = parseInt(rule.min_adults) || 0;
                        const maxA = parseInt(rule.max_adults) || 999;
                        const minC = parseInt(rule.min_children) || 0;
                        const maxC = parseInt(rule.max_children) || 999;
                        roomMaxA = Math.max(roomMaxA, Math.min(cap, maxA));
                        roomMaxC = Math.max(roomMaxC, Math.min(cap, maxC));
                        if (minC === 0) roomAllowsZeroChild = true;
                        if (maxC > 0) roomAllowsAnyChild = true;
                        if (maxA > 0) roomAllowsAnyAdult = true;
                    });

                    sumMaxAdults += roomMaxA;
                    sumMaxChildren += roomMaxC;
                    if (roomAllowsZeroChild) anyAllowsZeroChildren = true;
                    if (roomAllowsAnyChild) anyAllowsAnyChildren = true;
                    if (roomAllowsAnyAdult) anyAllowsAnyAdults = true;
                });

                if (rulesKnownForAll) {
                    if (children === 0 && !anyAllowsZeroChildren) {
                        rulesPossible = false;
                        rulesPossibleReason = t('noRoomAllowsZeroChildren');
                    } else if (children > 0 && !anyAllowsAnyChildren) {
                        rulesPossible = false;
                        rulesPossibleReason = t('noRoomAllowsChildren');
                    } else if (adults > 0 && !anyAllowsAnyAdults) {
                        rulesPossible = false;
                        rulesPossibleReason = t('noRoomAllowsAdults');
                    } else if (children > sumMaxChildren && sumMaxChildren > 0) {
                        rulesPossible = false;
                        rulesPossibleReason = t('tooManyChildrenForHotel', { max: sumMaxChildren });
                    } else if (adults > sumMaxAdults && sumMaxAdults > 0) {
                        rulesPossible = false;
                        rulesPossibleReason = t('tooManyAdultsForHotel', { max: sumMaxAdults });
                    }
                }
            } catch (e) {
                // fail-open
                rulesPossible = true;
            }

            // Validate guest assignment (each selected room must have >= 1 assigned guest)
            const allRoomsHaveGuests = roomsWithoutGuests.length === 0;
            // Validate per-room rules (each room must satisfy at least 1 active rule, if rules exist)
            const perRoomRulesValid = roomsWithRuleViolations.length === 0;

            // Determine if we can continue
            // IMPORTANT: Occupancy rules must be satisfied PER ROOM (based on assigned guests),
            // not via a single combined rule using the total adults/children across all rooms.
            const canContinue = total >= 1 && adults >= 1 && capacityValid && capacityPossible && rulesPossible && allRoomsHaveGuests && perRoomRulesValid;

            // Update "Change room" CTA text (selected room(s))
            try {
                const ctaTextEl = document.getElementById(`rooms-selected-room-text${pk}`);
                const changeBtn = document.getElementById(`rooms-change-room-btn${pk}`);
                const addBtn = document.getElementById(`rooms-add-room-btn${pk}`);
                if (ctaTextEl) {
                    if (state.rooms.length === 1) {
                        ctaTextEl.textContent = t('selectedOne', { room: state.rooms[0].roomLabel || 'Room' });
                        if (changeBtn) changeBtn.innerHTML = `<i class="fas fa-exchange-alt me-2"></i>${escapeHtml(t('replaceARoom'))}`;
                    } else {
                        ctaTextEl.textContent = t('selectedMany', { count: state.rooms.length });
                        if (changeBtn) changeBtn.innerHTML = `<i class="fas fa-exchange-alt me-2"></i>${escapeHtml(t('replaceARoom'))}`;
                    }
                }

                // Capacity guidance:
                // - If guests exceed current selected capacity and a single room can fit all guests => recommend CHANGE (bigger room)
                // - Otherwise => recommend ADD room(s)
                if (addBtn) {
                    const needMoreCapacity = total > totalCapacity;
                    const canChangeToSingle = !!singleRoomCandidate;

                    if (!needMoreCapacity) {
                        addBtn.disabled = true;
                        addBtn.style.display = 'none';
                        addBtn.removeAttribute('title');
                        if (changeBtn) changeBtn.style.display = 'inline-flex';
                    } else if (!capacityPossible) {
                        // Impossible state: even selecting all rooms cannot fit all guests
                        addBtn.disabled = true;
                        addBtn.style.display = 'none';
                        addBtn.removeAttribute('title');
                        if (changeBtn) changeBtn.style.display = 'inline-flex';
                        if (ctaTextEl && maxAvailableCapacity !== null) {
                            ctaTextEl.textContent += ` • ${t('notEnoughRoomsAvailableMax', { max: maxAvailableCapacity })}`;
                        }
                    } else if (canChangeToSingle) {
                        // Recommend changing to a bigger room
                        addBtn.disabled = true;
                        addBtn.style.display = 'none';
                        addBtn.removeAttribute('title');
                        if (changeBtn) {
                            changeBtn.style.display = 'inline-flex';
                            // more explicit label in this scenario
                            changeBtn.innerHTML = `<i class="fas fa-exchange-alt me-2"></i>${escapeHtml(t('changeToBiggerRoom'))}`;
                            changeBtn.setAttribute('title', `A room is available that fits ${total} guests (e.g. ${singleRoomCandidate.label}, cap ${singleRoomCandidate.cap})`);
                        }
                        if (ctaTextEl) {
                            ctaTextEl.textContent += ` • ${t('needBiggerRoomForGuests', { guests: total })}`;
                        }
                    } else {
                        // Must add a room (no single room can fit everyone)
                        const diff = total - totalCapacity;
                        // If there are no unselected rooms remaining, disable (nothing else to add)
                        if (unselectedRoomsCount === 0) {
                            addBtn.disabled = true;
                            addBtn.style.display = 'inline-flex';
                            addBtn.setAttribute('title', t('noMoreRoomsAvailableToAdd'));
                            if (ctaTextEl) {
                                ctaTextEl.textContent += ` • ${t('noMoreRoomsAvailableToAdd')}`;
                            }
                        } else {
                            addBtn.disabled = false;
                            addBtn.style.display = 'inline-flex';
                            addBtn.setAttribute('title', t('actionAddRoomFor', { diff }));
                            if (ctaTextEl) {
                                ctaTextEl.textContent += ` • ${t('needPlusCapacityAddRoom', { diff })}`;
                            }
                        }
                        if (changeBtn && state.rooms.length === 1) {
                            changeBtn.style.display = 'none';
                        }
                    }
                }
            } catch (e) {
                // ignore
            }

            if (statusEl) {
                statusEl.style.display = 'block';
                if (canContinue) {
                    statusEl.style.background = '#d4edda';
                    statusEl.style.border = '1px solid #c3e6cb';
                    statusEl.style.color = '#155724';
                    statusEl.innerHTML = `<i class="fas fa-check-circle me-1"></i><strong>${escapeHtml(t('roomsSelectedReady', { count: state.rooms.length }))}</strong>`;
                } else {
                    statusEl.style.background = '#fff3cd';
                    statusEl.style.border = '1px solid #ffc107';
                    statusEl.style.color = '#856404';
                    const errors = [];
                    if (total < 1 || adults < 1) {
                        errors.push(t('youMustHaveAdult'));
                    }
                    if (!allRoomsHaveGuests) {
                        const names = roomsWithoutGuests.map(r => r.roomLabel || `Room ${r.roomId}`).join(', ');
                        errors.push(t('noGuestsAssignedTo', { rooms: names }));
                    }
                    if (!perRoomRulesValid) {
                        const msg = roomsWithRuleViolations.map(v => {
                            const label = v.room.roomLabel || `Room ${v.room.roomId}`;
                            const ruleHints = (v.activeRules || []).map(r => {
                                const minA = parseInt(r.min_adults) || 0;
                                const maxA = parseInt(r.max_adults) || 999;
                                const minC = parseInt(r.min_children) || 0;
                                const maxC = parseInt(r.max_children) || 999;
                                return `${minA}-${maxA} adults, ${minC}-${maxC} children`;
                            }).join(' OR ');
                            return `${label} (${v.assignedAdults}A/${v.assignedChildren}C) must match: ${ruleHints}`;
                        }).join(' | ');
                        errors.push(t('occupancyPerRoomNotMet', { details: msg }));
                    }
                    // Hard "no solution" guardrail for guest mix vs room rules (when rules are known)
                    if (typeof rulesPossible !== 'undefined' && rulesPossible === false) {
                        errors.push(rulesPossibleReason || 'No available rooms are compatible with your guest mix.');
                    }
                    if (!capacityValid) {
                        errors.push(t('guestsExceedCapacityBy', { guests: total, cap: totalCapacity, diff: (total - totalCapacity) }));
                    }
                    // NOTE: global rulesValid check removed; per-room rule validation is authoritative.
                    const actionButtons = [];
                    if (!allRoomsHaveGuests) {
                        actionButtons.push(`
                            <button type="button"
                                    onclick="window.NSC_HotelReservation?.autoDistributeGuests?.('${pk}');"
                                    style="background: var(--mlb-red); color: white; border: none; padding: 8px 12px; border-radius: 8px; font-weight: 800; cursor: pointer;">
                                <i class="fas fa-magic me-1"></i>${escapeHtml(t('actionAutoAssignGuests'))}
                            </button>
                        `);
                        actionButtons.push(`
                            <button type="button"
                                    onclick="window.NSC_HotelReservation?.showGuestAssignment?.('${pk}', '${roomsWithoutGuests[0]?.roomId || ''}');"
                                    style="background: var(--mlb-blue); color: white; border: none; padding: 8px 12px; border-radius: 8px; font-weight: 800; cursor: pointer;">
                                <i class="fas fa-users me-1"></i>${escapeHtml(t('actionAssignNow'))}
                            </button>
                        `);
                    }

                    // If capacity is the issue, guide user:
                    // - if a single room can fit all guests: change to bigger room
                    // - else: add another room
                    if (!capacityValid) {
                        const diff = total - totalCapacity;
                        if (!capacityPossible && maxAvailableCapacity !== null) {
                            errors.push(t('notEnoughRoomsAvailableDetail', { max: maxAvailableCapacity, guests: total }));
                        } else if (singleRoomCandidate) {
                            actionButtons.push(`
                                <button type="button"
                                        onclick="if (window.nscShowRoomsListZone) window.nscShowRoomsListZone('${pk}');"
                                        style="background: var(--mlb-red); color: white; border: none; padding: 8px 12px; border-radius: 8px; font-weight: 900; cursor: pointer;">
                                    <i class="fas fa-exchange-alt me-1"></i>${escapeHtml(t('changeToBiggerRoom'))}
                                </button>
                            `);
                        } else {
                            actionButtons.push(`
                                <button type="button"
                                        onclick="if (window.nscShowRoomsListZone) window.nscShowRoomsListZone('${pk}');"
                                        style="background: var(--mlb-blue); color: white; border: none; padding: 8px 12px; border-radius: 8px; font-weight: 900; cursor: pointer;">
                                    <i class="fas fa-plus me-1"></i>${escapeHtml(t('actionAddRoomFor', { diff }))}
                                </button>
                            `);
                        }
                    }

                    const actions = actionButtons.length
                        ? `<div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; justify-content:center;">${actionButtons.join('')}</div>`
                        : '';
                    statusEl.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i><strong>Atención:</strong> ${errors.join('. ')}.${actions}`;
                }
            }

            if (footerMsgEl) {
                if (canContinue) {
                    footerMsgEl.innerHTML = `<i class="fas fa-check-circle me-1" style="color: #28a745;"></i>${escapeHtml(t('footerRoomsSelectedContinue', { count: state.rooms.length }))}`;
                    footerMsgEl.style.color = '#28a745';
                } else {
                    const errors = [];
                    if (total < 1 || adults < 1) {
                        errors.push(t('atLeastOneAdultRequired'));
                    }
                    if (!allRoomsHaveGuests) {
                        errors.push(t('guestsMustBeAssignedEveryRoom'));
                    }
                    if (!perRoomRulesValid) {
                        errors.push(t('perRoomRulesNotMetShort'));
                    }
                    if (!capacityValid) {
                        errors.push(t('capacityExceededShort'));
                    }
                    // NOTE: global rulesValid check removed; per-room rule validation is authoritative.
                    footerMsgEl.innerHTML = `<i class="fas fa-exclamation-triangle me-1" style="color: #ffc107;"></i>${escapeHtml(t('cannotContinuePrefix'))}: ${escapeHtml(errors.join('. '))}. ${escapeHtml(t('pleaseFixErrors'))}.`;
                    footerMsgEl.style.color = '#856404';
                }
            }

            // Continue button is always enabled - no validation
        } else {
            if (statusEl) {
                statusEl.style.display = 'block';
                statusEl.style.background = '#fff3cd';
                statusEl.style.border = '1px solid #ffc107';
                statusEl.style.color = '#856404';
                statusEl.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i>${escapeHtml(t('selectRoomFromList'))}`;
            }
            if (footerMsgEl) {
                footerMsgEl.innerHTML = `<i class="fas fa-info-circle me-1"></i>${escapeHtml(t('selectRoomToContinue'))}`;
                footerMsgEl.style.color = '#6c757d';
            }
            // Continue button is always enabled - no validation

            // Hide Add room button until at least one room is selected
            try {
                const addBtn = document.getElementById(`rooms-add-room-btn${pk}`);
                if (addBtn) {
                    addBtn.disabled = true;
                    addBtn.style.display = 'none';
                    addBtn.removeAttribute('title');
                }
            } catch (e) {
                // ignore
            }
        }
    }

    // Change currently selected room:
    // - if exactly 1 room selected: remove it and show the room list again
    // - if multiple rooms selected: show the list and let user deselect/select (non-destructive)
    function changeSelectedRoom(pk) {
        const state = stateByPk.get(pk);
        if (!state || !state.rooms || state.rooms.length === 0) {
            // Nothing selected, just show list
            if (window.nscShowRoomsListZone) window.nscShowRoomsListZone(pk);
            return;
        }

        if (state.rooms.length === 1) {
            // If the real issue is capacity (more guests than this room fits), do NOT replace.
            // Decide between changing to a bigger single room vs adding another room based on availability.
            try {
                const roomsModalEl = q(`hotelRoomsModal${pk}`);
                const roomId = String(state.rooms[0].roomId);
                const roomEl = findRoomInModal(pk, roomId);
                const capacity = roomEl ? parseInt(roomEl.getAttribute('data-room-capacity') || '0', 10) : 0;
                const totalGuests = state.guests ? state.guests.length : 0;
                if (capacity > 0 && totalGuests > capacity) {
                    // If there exists any available room that can fit all guests, recommend CHANGE.
                    let hasSingleFit = false;
                    try {
                        if (!roomsModalEl) return;
                const listings = Array.from(roomsModalEl.querySelectorAll('.room-listing-inline') || []);
                        hasSingleFit = listings.some((el) => {
                            const cap = parseInt(el.getAttribute('data-room-capacity') || '0', 10) || 0;
                            return cap >= totalGuests;
                        });
                    } catch (e) { /* ignore */ }

                    if (window.nscShowRoomsListZone) window.nscShowRoomsListZone(pk);
                    if (hasSingleFit) {
                        showToast(t('infoRoomFitsChange', { guests: totalGuests, cap: capacity }), 'info', 6500);
                    } else {
                        showToast(t('infoRoomFitsAdd', { guests: totalGuests, cap: capacity }), 'info', 6500);
                    }
                    return;
                }
            } catch (e) {
                // ignore
            }

            const roomId = String(state.rooms[0].roomId);
            removeRoom(pk, roomId);
            if (window.nscShowRoomsListZone) window.nscShowRoomsListZone(pk);
            showToast(t('selectNewRoomReplace'), 'info', 3500);
            return;
        }

        if (window.nscShowRoomsListZone) window.nscShowRoomsListZone(pk);
        showToast(t('replaceRoomInstruction'), 'info', 4500);
    }

    // Continue to guest details
    function continueToGuestDetails(pk) {
        const state = stateByPk.get(pk);
        if (!state || !state.rooms || state.rooms.length === 0) {
            showToast(t('pleaseSelectRoomFirst'), 'warning');
            return;
        }

        // Block if any selected room has no guest assignment
        if (!state.guestAssignments) state.guestAssignments = {};
        const roomsWithoutGuests = (state.rooms || []).filter((room) => {
            const assignments = state.guestAssignments[String(room.roomId)] || [];
            return !assignments || assignments.length === 0;
        });
        if (roomsWithoutGuests.length > 0) {
            const names = roomsWithoutGuests.map(r => r.roomLabel || `Room ${r.roomId}`).join(', ');
            showToast(t('noGuestsAssignedTo', { rooms: names }), 'warning');
            return;
        }

        // Block if any selected room violates its occupancy rules (based on assigned guests)
        try {
            const roomsModalEl = q(`hotelRoomsModal${pk}`);
            const invalidRooms = [];
            state.rooms.forEach((room) => {
                const roomEl = findRoomInModal(pk, room.roomId);
                const rulesJson = roomEl?.getAttribute('data-room-rules');
                if (!rulesJson) return;
                let rules = [];
                try { rules = JSON.parse(rulesJson) || []; } catch (e) { rules = []; }
                const activeRules = Array.isArray(rules) ? rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active) : [];
                if (!activeRules.length) return;

                const assignedIdxs = (state.guestAssignments || {})[String(room.roomId)] || [];
                const assignedGuests = assignedIdxs.map(i => state.guests[i]).filter(Boolean);
                const a = assignedGuests.filter(g => g.type === 'adult').length;
                const c = assignedGuests.filter(g => g.type === 'child').length;
                const ok = activeRules.some(rule => {
                    const minAdults = parseInt(rule.min_adults) || 0;
                    const maxAdults = parseInt(rule.max_adults) || 999;
                    const minChildren = parseInt(rule.min_children) || 0;
                    const maxChildren = parseInt(rule.max_children) || 999;
                    return a >= minAdults && a <= maxAdults && c >= minChildren && c <= maxChildren;
                });
                if (!ok) invalidRooms.push(room.roomLabel || `Room ${room.roomId}`);
            });
            if (invalidRooms.length) {
                showToast(t('occupancyNotMetFor', { rooms: invalidRooms.join(', ') }), 'warning');
                return;
            }
        } catch (e) {
            // fail-open
        }

        const adults = state.guests ? state.guests.filter(g => g.type === 'adult').length : 0;
        const children = state.guests ? state.guests.filter(g => g.type === 'child').length : 0;
        const total = adults + children;

        if (total < 1 || adults < 1) {
            showToast(t('youMustHaveAdult'), 'warning');
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

            // Forzar scroll al inicio del modal de huéspedes
            guestModalEl.scrollTop = 0;
            if (window.parent) {
                window.parent.postMessage({ type: 'nsc-scroll-to-top', tabId: window.name }, window.location.origin);
            }
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

        // Find the rooms grid container more reliably
        const containerEl = roomsModalEl.querySelector('[style*="max-height: 70vh"]');
        if (!containerEl) return;

        const roomsGridContainer = containerEl.querySelector('.rooms-grid-container');
        if (!roomsGridContainer) return;

        const roomListings = Array.from(roomsGridContainer.querySelectorAll('.room-listing-inline'));
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

        // Clear old recommendation badges (aggressive cleanup)
        roomListings.forEach(r => {
            r.classList.remove('nsc-room-recommended');
            // Remove any badge elements that might exist
            const oldBadge = r.querySelector('.nsc-recommended-badge');
            if (oldBadge) {
                oldBadge.remove();
            }
            // Also check in room-info directly
            const roomInfo = r.querySelector('.room-info');
            if (roomInfo) {
                const badgeInInfo = roomInfo.querySelector('.nsc-recommended-badge');
                if (badgeInInfo) badgeInInfo.remove();
            }
        });

        // Reorder rooms in DOM
        // Use the rooms-grid-container directly for more reliable parent reference
        if (roomsGridContainer) {
            sortedRooms.forEach((roomData, index) => {
                const roomEl = roomData.el;

                // Add recommendation badge for top 3 if sorting by recommended
                // NOTE: Badge insertion removed - it was breaking the room-info layout
                // The recommended class (nsc-room-recommended) is sufficient for styling
                if (sortBy === 'recommended' && index < 3) {
                    roomEl.classList.add('nsc-room-recommended');
                    // Badge insertion removed to prevent layout conflicts
                } else {
                    // Remove recommendation class if not in top 3 or not sorting by recommended
                    roomEl.classList.remove('nsc-room-recommended');
                }

                roomsGridContainer.appendChild(roomEl);
            });
        }
    }

    // Auto-distribute guests across selected rooms
    function autoDistributeGuests(pk) {
        const state = stateByPk.get(pk);
        if (!state || !state.guests || !state.rooms || state.rooms.length === 0) return;

        // Ensure guestAssignments exists
        if (!state.guestAssignments) state.guestAssignments = {};

        const roomsModalEl = q(`hotelRoomsModal${pk}`);

        function getRoomMeta(roomId) {
            const roomEl = findRoomInModal(pk, roomId);
            const capacity = roomEl ? parseInt(roomEl.getAttribute('data-room-capacity') || '0', 10) : 0;
            const label = roomEl?.querySelector('.room-name')?.textContent?.trim()
                || roomEl?.getAttribute('data-room-label')
                || `Room ${roomId}`;
            let rules = [];
            const rulesJson = roomEl?.getAttribute('data-room-rules');
            if (rulesJson) {
                try { rules = JSON.parse(rulesJson) || []; } catch (e) { rules = []; }
            }
            const activeRules = Array.isArray(rules) ? rules.filter(r => !r.hasOwnProperty('is_active') || r.is_active) : [];
            return { roomId: String(roomId), capacity: Number.isFinite(capacity) ? capacity : 0, label, activeRules };
        }

        const roomMetas = (state.rooms || []).map(r => getRoomMeta(String(r.roomId))).filter(r => r.roomId);
        if (!roomMetas.length) return;

        function ensureRoomKey(roomId) {
            if (!state.guestAssignments[String(roomId)]) state.guestAssignments[String(roomId)] = [];
        }

        roomMetas.forEach(r => ensureRoomKey(r.roomId));

            const totalGuests = state.guests.length;
        const roomCount = roomMetas.length;

        // Determine if there are manual assignments (keep them, but improve)
        const hasManualAssignments = Object.values(state.guestAssignments || {}).some(arr => Array.isArray(arr) && arr.length > 0);

        function assignedSet() {
            const s = new Set();
            Object.values(state.guestAssignments || {}).forEach(arr => {
                (arr || []).forEach(idx => s.add(idx));
            });
            return s;
        }

        function getUnassigned() {
            const s = assignedSet();
            const res = [];
            for (let i = 0; i < totalGuests; i++) if (!s.has(i)) res.push(i);
            return res;
        }

        function countTypes(indices) {
            let adults = 0, children = 0;
            (indices || []).forEach(idx => {
                const g = state.guests[idx];
                if (!g) return;
                if (g.type === 'adult') adults++;
                else children++;
            });
            return { adults, children, total: adults + children };
        }

        function pickGuestIndexOfType(unassigned, type) {
            const idx = unassigned.find(i => state.guests[i] && state.guests[i].type === type);
            if (idx === undefined) return null;
            // remove from array
            const pos = unassigned.indexOf(idx);
            if (pos >= 0) unassigned.splice(pos, 1);
            return idx;
        }

        function pushIfCapacity(roomId, guestIdx, capacity) {
            const arr = state.guestAssignments[String(roomId)] || [];
            if (arr.length >= capacity) return false;
            arr.push(guestIdx);
            state.guestAssignments[String(roomId)] = arr;
            return true;
        }

        function roomNeedsAdult(meta, assigned) {
            if (!meta.activeRules || meta.activeRules.length === 0) return true; // common-sense: ensure adult possible
            // If every active rule requires at least 1 adult, then we need an adult
            const minAdultsAll = meta.activeRules.map(r => parseInt(r.min_adults) || 0);
            const requiresAdult = minAdultsAll.length ? Math.min(...minAdultsAll) >= 1 : true;
            const counts = countTypes(assigned);
            return requiresAdult && counts.adults < 1;
        }

        function ensureNoEmptyRooms(unassigned) {
            if (totalGuests < roomCount) return; // impossible to give every room 1 guest
            const emptyRooms = roomMetas.filter(r => (state.guestAssignments[r.roomId] || []).length === 0);
            emptyRooms.forEach((meta) => {
                // Prefer adult if rules suggest it
                let pick = null;
                if (roomNeedsAdult(meta, [])) pick = pickGuestIndexOfType(unassigned, 'adult');
                if (pick === null) pick = pickGuestIndexOfType(unassigned, 'child');
                if (pick === null) pick = unassigned.shift() ?? null;

                if (pick !== null) {
                    pushIfCapacity(meta.roomId, pick, meta.capacity);
                return;
            }

                // No unassigned guests left; move from a room with >1
                const donor = roomMetas
                    .map(r => ({ r, assigned: state.guestAssignments[r.roomId] || [] }))
                    .filter(x => x.assigned.length > 1)
                    .sort((a, b) => b.assigned.length - a.assigned.length)[0];
                if (donor) {
                    const moved = donor.assigned.pop();
                    if (moved !== undefined) {
                        pushIfCapacity(meta.roomId, moved, meta.capacity);
                    }
                }
            });
        }

        function distributeBalanced(unassigned) {
            // Assign remaining guests to the room with lowest fill ratio (assigned/capacity)
            while (unassigned.length > 0) {
                const guestIdx = unassigned.shift();
                if (guestIdx === undefined) break;
                const candidates = roomMetas
                    .map(r => {
                        const assigned = state.guestAssignments[r.roomId] || [];
                        const cap = r.capacity || 0;
                        const ratio = cap > 0 ? (assigned.length / cap) : 1e9;
                        return { r, assigned, cap, ratio };
                    })
                    .filter(x => x.cap > 0 && x.assigned.length < x.cap)
                    .sort((a, b) => a.ratio - b.ratio || a.assigned.length - b.assigned.length);
                if (!candidates.length) break;
                pushIfCapacity(candidates[0].r.roomId, guestIdx, candidates[0].cap);
            }
        }

        function roomRulesSatisfied(meta, assignedIdxs) {
            try {
                const indices = assignedIdxs || [];
                if (indices.length <= 0) return false;
                if (!meta.activeRules || meta.activeRules.length === 0) return true;
                const counts = countTypes(indices);
                return meta.activeRules.some(rule => {
                    const minAdults = parseInt(rule.min_adults) || 0;
                    const maxAdults = parseInt(rule.max_adults) || 999;
                    const minChildren = parseInt(rule.min_children) || 0;
                    const maxChildren = parseInt(rule.max_children) || 999;
                    return counts.adults >= minAdults && counts.adults <= maxAdults &&
                           counts.children >= minChildren && counts.children <= maxChildren;
                });
            } catch (e) {
                return true; // fail-open
            }
        }

        function strictRepairAssignments() {
            // Try to repair per-room rule violations by moving guests between rooms (heuristic).
            // Only runs if there are rules; otherwise no-op.
            const maxMoves = 80;
            let moves = 0;

            function getMeta(roomId) {
                return roomMetas.find(r => String(r.roomId) === String(roomId));
            }

            function getAssigned(roomId) {
                return state.guestAssignments[String(roomId)] || [];
            }

            function setAssigned(roomId, arr) {
                state.guestAssignments[String(roomId)] = arr;
            }

            function canTake(roomId) {
                const meta = getMeta(roomId);
                if (!meta) return false;
                return getAssigned(roomId).length < meta.capacity;
            }

            function moveOne(fromRoomId, toRoomId, type) {
                const from = getAssigned(fromRoomId);
                const to = getAssigned(toRoomId);
                const metaTo = getMeta(toRoomId);
                if (!metaTo) return false;
                if (to.length >= metaTo.capacity) return false;
                const idxPos = from.findIndex(i => state.guests[i] && state.guests[i].type === type);
                if (idxPos === -1) return false;
                const guestIdx = from[idxPos];

                // Apply move
                from.splice(idxPos, 1);
                to.push(guestIdx);
                setAssigned(fromRoomId, from);
                setAssigned(toRoomId, to);
                return true;
            }

            function findViolations() {
                return roomMetas
                    .map(m => ({ m, assigned: getAssigned(m.roomId) }))
                    .filter(x => x.m.activeRules && x.m.activeRules.length > 0)
                    .filter(x => !roomRulesSatisfied(x.m, x.assigned));
            }

            while (moves < maxMoves) {
                const violations = findViolations();
                if (!violations.length) break;

                // Work on the "most violated" room: pick the one with smallest assignment size (often needs mins)
                violations.sort((a, b) => a.assigned.length - b.assigned.length);
                const target = violations[0];
                const meta = target.m;
                const assigned = target.assigned;
                const counts = countTypes(assigned);

                // Find the "closest" rule to satisfy
                const rules = meta.activeRules || [];
                const scored = rules.map(rule => {
                    const minA = parseInt(rule.min_adults) || 0;
                    const maxA = parseInt(rule.max_adults) || 999;
                    const minC = parseInt(rule.min_children) || 0;
                    const maxC = parseInt(rule.max_children) || 999;
                    const needA = Math.max(0, minA - counts.adults) + Math.max(0, counts.adults - maxA);
                    const needC = Math.max(0, minC - counts.children) + Math.max(0, counts.children - maxC);
                    return { rule, minA, maxA, minC, maxC, score: needA + needC, needA, needC };
                }).sort((a, b) => a.score - b.score);
                const best = scored[0];
                if (!best) break;

                // If missing adults/children, try to pull from other rooms (that remain valid after giving)
                const donors = roomMetas
                    .filter(r => r.roomId !== meta.roomId)
                    .map(r => ({ r, assigned: getAssigned(r.roomId), counts: countTypes(getAssigned(r.roomId)) }))
                    .filter(x => x.assigned.length > 1); // avoid emptying donor

                let didMove = false;

                if (counts.adults < best.minA) {
                    for (const d of donors) {
                        // donor must have an adult to give
                        if (d.counts.adults <= 0) continue;
                        // simulate donor after move: remove 1 adult
                        const newDonorIdxs = [...d.assigned];
                        const pos = newDonorIdxs.findIndex(i => state.guests[i] && state.guests[i].type === 'adult');
                        if (pos === -1) continue;
                        newDonorIdxs.splice(pos, 1);
                        // donor should remain valid if it has rules
                        if (d.r.activeRules && d.r.activeRules.length > 0 && !roomRulesSatisfied(d.r, newDonorIdxs)) continue;
                        if (!moveOne(d.r.roomId, meta.roomId, 'adult')) continue;
                        moves++;
                        didMove = true;
                        break;
                    }
                }

                if (!didMove && counts.children < best.minC) {
                    for (const d of donors) {
                        if (d.counts.children <= 0) continue;
                        const newDonorIdxs = [...d.assigned];
                        const pos = newDonorIdxs.findIndex(i => state.guests[i] && state.guests[i].type === 'child');
                        if (pos === -1) continue;
                        newDonorIdxs.splice(pos, 1);
                        if (d.r.activeRules && d.r.activeRules.length > 0 && !roomRulesSatisfied(d.r, newDonorIdxs)) continue;
                        if (!moveOne(d.r.roomId, meta.roomId, 'child')) continue;
                        moves++;
                        didMove = true;
                        break;
                    }
                }

                // If we couldn't pull required types, stop (user must resolve manually)
                if (!didMove) break;
            }
        }

        // If there are no manual assignments, do a smarter fresh allocation (respecting rules best-effort)
        if (!hasManualAssignments) {
        state.guestAssignments = {};
            roomMetas.forEach(r => ensureRoomKey(r.roomId));

            // Build pools
            const unassigned = [];
            for (let i = 0; i < totalGuests; i++) unassigned.push(i);

            // Greedy: allocate minimums for one "best" rule per room (most restrictive first)
            const roomOrder = [...roomMetas].sort((a, b) => {
                const aStrict = a.activeRules && a.activeRules.length
                    ? Math.max(...a.activeRules.map(r => (parseInt(r.min_adults) || 0) + (parseInt(r.min_children) || 0)))
                    : 0;
                const bStrict = b.activeRules && b.activeRules.length
                    ? Math.max(...b.activeRules.map(r => (parseInt(r.min_adults) || 0) + (parseInt(r.min_children) || 0)))
                    : 0;
                return bStrict - aStrict;
            });

            for (const meta of roomOrder) {
                // Choose a feasible rule
                const rules = meta.activeRules || [];
                let chosen = null;
                if (rules.length) {
                    const sorted = [...rules].sort((a, b) => {
                        const aNeed = (parseInt(a.min_adults) || 0) + (parseInt(a.min_children) || 0);
                        const bNeed = (parseInt(b.min_adults) || 0) + (parseInt(b.min_children) || 0);
                        return bNeed - aNeed;
                    });
                    for (const rule of sorted) {
                        const minA = parseInt(rule.min_adults) || 0;
                        const minC = parseInt(rule.min_children) || 0;
                        if (minA + minC > meta.capacity) continue;
                        // Check if pool has enough
                        const poolAdults = unassigned.filter(i => state.guests[i]?.type === 'adult').length;
                        const poolChildren = unassigned.filter(i => state.guests[i]?.type === 'child').length;
                        if (poolAdults >= minA && poolChildren >= minC) {
                            chosen = { minA, minC };
                            break;
                        }
                    }
                }
                // Default: require at least 1 adult if possible
                if (!chosen) {
                    const poolAdults = unassigned.filter(i => state.guests[i]?.type === 'adult').length;
                    chosen = poolAdults > 0 ? { minA: 1, minC: 0 } : { minA: 0, minC: 1 };
                }

                // Allocate mins
                for (let a = 0; a < (chosen.minA || 0); a++) {
                    const idx = pickGuestIndexOfType(unassigned, 'adult');
                    if (idx === null) break;
                    pushIfCapacity(meta.roomId, idx, meta.capacity);
                }
                for (let c = 0; c < (chosen.minC || 0); c++) {
                    const idx = pickGuestIndexOfType(unassigned, 'child');
                    if (idx === null) break;
                    pushIfCapacity(meta.roomId, idx, meta.capacity);
                }
            }

            // Ensure every selected room has >=1 guest if possible
            ensureNoEmptyRooms(unassigned);
            // Distribute remaining guests
            distributeBalanced(unassigned);
        } else {
            // Manual assignments exist: do not destroy them.
            const unassigned = getUnassigned();
            ensureNoEmptyRooms(unassigned);
            distributeBalanced(unassigned);
        }

        // Strict pass: attempt to repair assignments so per-room rules are satisfied (best-effort).
        try { strictRepairAssignments(); } catch (e) {}

        // Refresh UI + validations (so the button can be a single call)
        try { updateRoomsGuestsList(pk); } catch (e) {}
        try { updateRoomsPriceCalculation(pk); } catch (e) {}
        try { validateRoomSelection(pk); } catch (e) {}

        // Feedback
        try {
            const roomsWithoutGuests = roomMetas.filter(r => (state.guestAssignments[r.roomId] || []).length === 0);
            if (totalGuests < roomCount) {
                showToast(t('autoAssignTooManyRooms', { guests: totalGuests, rooms: roomCount }), 'warning', 5000);
            } else if (roomsWithoutGuests.length) {
                showToast(t('autoAssignStillEmpty'), 'warning', 5000);
            } else {
                showToast(t('autoAssignSuccess'), 'success', 3000);
            }
        } catch (e) {
            // ignore
        }
    }

    // Show guest assignment modal
    function showGuestAssignment(pk, roomId) {
        const state = stateByPk.get(pk);
        if (!state || !state.guests || !state.rooms) return;

        const room = state.rooms.find(r => r.roomId === roomId);
        if (!room) return;

        // Get room capacity and rules
        const roomsModalEl = q(`hotelRoomsModal${pk}`);
        const roomEl = findRoomInModal(pk, roomId);
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
        html += `<h5 style="margin-bottom: 16px; color: var(--mlb-blue);">${escapeHtml(t('assignGuestsToRoomTitle', { room: room.roomLabel }))}</h5>`;
        html += `<p style="font-size: 0.85rem; color: #6c757d; margin-bottom: 8px;">${escapeHtml(t('capacityLine', { cap: capacity }))}</p>`;
        html += `<p style="font-size: 0.85rem; color: #6c757d; margin-bottom: 16px;">${escapeHtml(t('currentlyAssignedLine', { total: assignedTotal, adults: assignedAdults, children: assignedChildren }))}</p>`;

        // Show rules validation
        if (rulesValidation) {
            if (rulesValidation.valid) {
                html += `<div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 10px; margin-bottom: 16px; color: #155724; font-size: 0.85rem;">`;
                html += `<i class="fas fa-check-circle me-1"></i><strong>${escapeHtml(t('rulesComplyTitle'))}:</strong> ${escapeHtml(t('assignmentCompliesNRules', { n: rulesValidation.validRules.length }))}`;
                if (rulesValidation.validRules.length === 1) {
                    const rule = rulesValidation.validRules[0];
                    const isGeneric = (desc) => {
                        const d = (desc || '').toString().trim().toLowerCase();
                        return !d || /^regla\s*\d+$/i.test(d) || /^rule\s*\d+$/i.test(d);
                    };
                    const current = t('nowYouHave', {
                        adults: assignedAdults,
                        adultWord: nounForCount(assignedAdults, 'adultOne', 'adultMany'),
                        children: assignedChildren,
                        childWord: nounForCount(assignedChildren, 'childOne', 'childMany')
                    });
                    const req = `${t('requirementPrefix')} ` + t('requirementLine', {
                        adultsReq: rangeText(rule.min_adults, rule.max_adults, 'adultOne', 'adultMany'),
                        childrenReq: rangeText(rule.min_children, rule.max_children, 'childOne', 'childMany')
                    });
                    const custom = rule.description;
                    html += `<div style="margin-top: 4px; font-size: 0.8rem;">${isGeneric(custom) ? `${current} ${req}` : `${escapeHtml(custom)} — ${current} ${req}`}</div>`;
                }
                html += `</div>`;
            } else {
                html += `<div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 10px; margin-bottom: 16px; color: #856404; font-size: 0.85rem;">`;
                html += `<i class="fas fa-exclamation-triangle me-1"></i><strong>⚠ ${escapeHtml(t('roomRulesNotMetShort'))}:</strong> ${escapeHtml(t('roomRulesNotMetDetail', { adults: assignedAdults, children: assignedChildren }))}`;
                html += `<div style="margin-top: 8px; font-size: 0.8rem; font-weight: 700;">${escapeHtml(t('availableRulesLabel'))}</div>`;
                rulesValidation.allRules.forEach((rule, idx) => {
                    const isGeneric = (desc) => {
                        const d = (desc || '').toString().trim().toLowerCase();
                        return !d || /^regla\s*\d+$/i.test(d) || /^rule\s*\d+$/i.test(d);
                    };
                    const noun = (n, singular, plural) => (n === 1 ? singular : plural);
                    const rangeText = (min, max, singular, plural) => {
                        const minN = parseInt(min) || 0;
                        const maxN = parseInt(max);
                        const isInf = Number.isFinite(maxN) && maxN >= 999;
                        if (isInf) return `al menos ${minN} ${noun(minN, singular, plural)}`;
                        const maxVal = Number.isFinite(maxN) ? maxN : 0;
                        if (minN === maxVal) return `exactamente ${minN} ${noun(minN, singular, plural)}`;
                        return `entre ${minN} y ${maxVal} ${plural}`;
                    };
                    const current = `Ahora: ${assignedAdults} ${noun(assignedAdults, 'adulto', 'adultos')} y ${assignedChildren} ${noun(assignedChildren, 'niño', 'niños')}.`;
                    const req = `Requisito: ${rangeText(rule.min_adults, rule.max_adults, 'adulto', 'adultos')} y ${rangeText(rule.min_children, rule.max_children, 'niño', 'niños')}.`;
                    const custom = rule.description;
                    const desc = isGeneric(custom) ? `${current} ${req}` : `${custom} — ${current} ${req}`;
                    html += `<div style="font-size: 0.75rem; color: #6c757d; margin-top: 4px; padding-left: 12px;">`;
                    html += `<i class="fas fa-circle me-1" style="font-size: 0.65rem;"></i>${escapeHtml(desc)}`;
                    html += `</div>`;
                });
                html += `</div>`;
            }
        } else if (rules.length === 0) {
            html += `<div style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 10px; margin-bottom: 16px; color: #6c757d; font-size: 0.85rem; font-style: italic;">Esta habitación no tiene reglas de ocupación. Cualquier combinación es válida.</div>`;
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
        html += `<button type="button" onclick="if (document.activeElement && document.activeElement.blur) document.activeElement.blur(); window.NSC_HotelReservation?.autoDistributeGuests?.('${pk}'); setTimeout(() => { const modal = bootstrap.Modal.getInstance(document.getElementById('guestAssignmentModal${pk}')); if (modal) modal.hide(); }, 50);" style="background: #6c757d; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">${escapeHtml(t('autoDistribute'))}</button>`;
        html += `<button type="button" onclick="if (document.activeElement && document.activeElement.blur) document.activeElement.blur(); setTimeout(() => { const modal = bootstrap.Modal.getInstance(document.getElementById('guestAssignmentModal${pk}')); if (modal) modal.hide(); window.NSC_HotelReservation?.updateRoomsPriceCalculation?.('${pk}'); }, 50);" style="background: var(--mlb-blue); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">${escapeHtml(t('done'))}</button>`;
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
                const roomEl = findRoomInModal(pk, r.roomId);
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
        removeRoomFromState(pk, state, roomId);

        // Auto-redistribute guests if needed
        autoDistributeGuests(pk);

        // Update price calculation and validation
        updateRoomsPriceCalculation(pk);
        validateRoomSelection(pk);

        showToast(t('roomRemoved', { label: room.roomLabel }), 'info', 3000);
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
                showToast(t('roomCapacityReached', { cap: capacity }), 'warning');
                return false;
            }

            // Add to this room temporarily to check rules
            const tempAssignments = [...state.guestAssignments[roomId]];
            if (!tempAssignments.includes(guestIndex)) {
                tempAssignments.push(guestIndex);
            }

            // Get room rules
            const roomsModalEl = q(`hotelRoomsModal${pk}`);
            const roomEl = findRoomInModal(pk, roomId);
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

    return {
        initModal,
        showRooms,
        showRoomsDirect,
        selectRoom,
        openRoomDetail,
        updateSummary,
        addAdult,
        addChild,
        stepper,
        backToGuests,
        backToRooms,
        addAdditionalGuest,
        saveGuest,
        removeGuest,
        continueToGuestDetails,
        openLightbox,
        closeLightbox,
        prevLightboxImage,
        nextLightboxImage,
        sortRooms,
        autoDistributeGuests,
        showGuestAssignment,
        toggleGuestAssignment,
        updateRoomsPriceCalculation,
        validateRoomSelection,
        updateRoomsGuestsList,
        changeSelectedRoom,
        removeRoom
    };
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

// Initialize the dashboard
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.adminDashboard) {
            window.adminDashboard = new AdminDashboard();
            console.log('🚀 AdminDashboard initialized');
        }
    });
}
