/**
 * Sistema moderno de traducciones del lado del cliente
 * Funciona sin recargar la página y es más reactivo
 */

class I18nManager {
    constructor() {
        this.currentLanguage = this.getStoredLanguage() || 'en';
        this.translations = {
            en: {
                // Schedule Section
                'schedule_title': '2026 EVENT CALENDAR',
                'schedule_subtitle': 'REGIONAL EXPANSION AND NEW NATIONAL AND REGIONAL CHAMPIONSHIPS FOR 2026',
                'schedule_description': 'As we move forward into 2026, NSC International continues to elevate its tournament and showcase platform. With a regional presence expansion for ages 7U-18U, new and improved National and Regional Championship events, and an even broader showcase schedule across the country, NSC remains dedicated to providing the highest standard of competition and experience for players, coaches and families alike.',
                
                // Showcase Section
                'showcase_title': 'SHOWCASES AND PROSPECT GATEWAYS',
                'showcase_subtitle': 'REGIONAL AND NATIONAL SHOWCASES',
                'showcase_description': 'Perfect Game is thrilled to offer showcases (HS) and Prospect Gateways (13U/14U) across the country for the 2025 calendar. This includes regional events for all ages and new invite only events! PG strives to delivery the very best events and experience for all players, coaches and families across the country.',
            },
            es: {
                // Schedule Section
                'schedule_title': 'CALENDARIO DE EVENTOS 2026',
                'schedule_subtitle': 'EXPANSIÓN REGIONAL Y NUEVOS CAMPEONATOS NACIONALES Y REGIONALES PARA 2026',
                'schedule_description': 'A medida que avanzamos hacia 2026, NSC International continúa elevando su plataforma de torneos y exhibiciones. Con una expansión de la presencia regional para edades 7U-18U, nuevos y mejorados eventos de Campeonatos Nacionales y Regionales, y una programación aún más amplia de exhibiciones en todo el país, NSC se mantiene dedicado a ofrecer el más alto estándar de competencia y experiencia para jugadores, entrenadores y familias por igual.',
                
                // Showcase Section
                'showcase_title': 'SHOWCASES Y PORTALES DE PROSPECTO',
                'showcase_subtitle': 'SHOWCASES REGIONALES Y NACIONALES',
                'showcase_description': 'Perfect Game se complace en ofrecer showcases (HS) y Prospect Gateways (13U/14U) en todo el país para el calendario 2025. Esto incluye eventos regionales para todas las edades y nuevos eventos solo por invitación. PG se esfuerza por ofrecer los mejores eventos y experiencias para todos los jugadores, entrenadores y familias en todo el país.',
            }
        };
        
        this.init();
    }
    
    getStoredLanguage() {
        return localStorage.getItem('preferred_language') || 
               document.documentElement.lang || 
               'en';
    }
    
    setStoredLanguage(lang) {
        localStorage.setItem('preferred_language', lang);
        this.currentLanguage = lang;
    }
    
    init() {
        // Esperar a que las traducciones de la BD se carguen (si están disponibles)
        // Las traducciones de la BD se inyectan después de que este script se carga
        setTimeout(() => {
            this.applyTranslations();
        }, 100);
        
        // Escuchar cambios de idioma desde los formularios
        this.setupLanguageSwitchers();
    }
    
    setupLanguageSwitchers() {
        // Interceptar envío de formularios de idioma
        const forms = document.querySelectorAll('form[action*="set_language"]');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const formData = new FormData(form);
                const language = formData.get('language');
                // Guardar selección para UI (y para cualquier lógica que dependa de localStorage)
                if (language === 'en' || language === 'es') {
                    localStorage.setItem('preferred_language', language);
                    localStorage.setItem('user_selected_language', language);
                    this.changeLanguage(language);
                }

                // IMPORTANTE:
                // No prevenimos el submit. Dejamos que Django i18n/setlang haga redirect
                // a `next` y recargue la página, para que las traducciones de templates
                // ({% trans %}) se apliquen correctamente.
            });
        });
    }
    
    changeLanguage(lang) {
        if (lang !== this.currentLanguage && (lang === 'en' || lang === 'es')) {
            this.setStoredLanguage(lang);
            this.applyTranslations();
            this.updateLanguageSelector(lang);
            this.updateHTMLAttributes(lang);
        }
    }
    
    applyTranslations() {
        const lang = this.currentLanguage;
        const translations = this.translations[lang] || this.translations['en'];
        
        // Traducir elementos con data-i18n
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (translations[key]) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.value = translations[key];
                } else {
                    element.textContent = translations[key];
                }
            }
        });
        
        // Traducir elementos con data-i18n-html (para HTML)
        document.querySelectorAll('[data-i18n-html]').forEach(element => {
            const key = element.getAttribute('data-i18n-html');
            if (translations[key]) {
                element.innerHTML = translations[key];
            }
        });
        
        // Traducir elementos específicos por clase o ID
        this.translateSpecificElements(lang, translations);
    }
    
    translateSpecificElements(lang, translations) {
        // Schedule section
        const scheduleTitle = document.querySelector('.schedule-heading');
        if (scheduleTitle && !scheduleTitle.hasAttribute('data-i18n')) {
            scheduleTitle.textContent = translations['schedule_title'];
        }
        
        const scheduleSubtitle = document.querySelector('.schedule-subheading');
        if (scheduleSubtitle && !scheduleSubtitle.hasAttribute('data-i18n')) {
            scheduleSubtitle.textContent = translations['schedule_subtitle'];
        }
        
        const scheduleDescription = document.querySelector('.schedule-description');
        if (scheduleDescription && !scheduleDescription.hasAttribute('data-i18n')) {
            scheduleDescription.textContent = translations['schedule_description'];
        }
        
        // Showcase section (si existe)
        const showcaseTitle = document.querySelectorAll('.schedule-heading')[1];
        if (showcaseTitle && !showcaseTitle.hasAttribute('data-i18n')) {
            showcaseTitle.textContent = translations['showcase_title'];
        }
        
        const showcaseSubtitle = document.querySelectorAll('.schedule-subheading')[1];
        if (showcaseSubtitle && !showcaseSubtitle.hasAttribute('data-i18n')) {
            showcaseSubtitle.textContent = translations['showcase_subtitle'];
        }
        
        const showcaseDescription = document.querySelectorAll('.schedule-description')[1];
        if (showcaseDescription && !showcaseDescription.hasAttribute('data-i18n')) {
            showcaseDescription.textContent = translations['showcase_description'];
        }
    }
    
    updateLanguageSelector(lang) {
        // Actualizar el selector visual
        const btn = document.getElementById('languageSelectorBtn');
        if (btn) {
            const flagIcon = btn.querySelector('.flag-icon');
            const langText = btn.querySelector('.language-text');
            
            if (flagIcon) {
                flagIcon.className = 'flag-icon ' + (lang === 'es' ? 'flag-es' : 'flag-us');
            }
            if (langText) {
                langText.textContent = lang === 'es' ? 'ES' : 'EN';
            }
        }
        
        // Actualizar clases active en los botones
        document.querySelectorAll('.language-option').forEach(option => {
            const form = option.closest('form');
            if (form) {
                const formLang = form.querySelector('input[name="language"]').value;
                if (formLang === lang) {
                    option.classList.add('active');
                } else {
                    option.classList.remove('active');
                }
            }
        });
    }
    
    updateHTMLAttributes(lang) {
        document.documentElement.lang = lang;
    }
    
    getTranslation(key, lang = null) {
        const targetLang = lang || this.currentLanguage;
        return this.translations[targetLang]?.[key] || this.translations['en'][key] || key;
    }
}

// Inicializar cuando el DOM esté listo
let i18nManager;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        i18nManager = new I18nManager();
    });
} else {
    i18nManager = new I18nManager();
}

// Exponer globalmente para uso en consola
window.i18nManager = i18nManager;

