# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Sin versión]

### Actualizado: 2026-01-12 23:08:16

- **[cdedeb4]** ```
  - *Fecha:* 2026-01-12 23:08:15
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `apps/accounts/views_public.py`
  - *Detalles:*
    - refactor: Simplify registration success flow and add rate limiting to form validation
    - - Change success_url from accounts:profile to panel for all user types
    - - Remove user type-based redirect logic after registration
    - - Remove unused imports (HttpResponseForbidden, RATE_LIMIT_WINDOW)
    - - Simplify form_valid to always redirect to panel instead of conditional redirects
    - - Add form_invalid method with rate limiting and login attempt tracking
    - - Implement session-based error handling for failed registration



### Actualizado: 2026-01-12 23:01:19

- **[9ef5beb]** refactor: Improve itinerary fallback logic and add itinerary display to public event detail
  - *Fecha:* 2026-01-12 23:01:18
  - *Autor:* cgallego17
  - *Archivos modificados:* 4 archivo(s)
    - `apps/events/views.py`
    - `apps/events/views_public.py`
    - `templates/events/event_form.html`
    - `templates/events/public_detail.html`
  - *Detalles:*
    - - Simplify itinerary fallback in EventCreateView and EventUpdateView to apply generic itinerary to all user types
    - - Remove player-only restriction from fallback logic
    - - Add itinerary context data to PublicEventDetailView with user type filtering
    - - Implement fallback to player itinerary when team_manager or spectator itineraries are missing
    - - Add tabbed itinerary section in public event detail template with



### Actualizado: 2026-01-12 22:30:59

- **[80e4764]** refactor: Add fallback UI for non-embeddable video URLs in public event detail
  - *Fecha:* 2026-01-12 22:30:59
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/events/public_detail.html`
  - *Detalles:*
    - - Add fallback alert div with external link button for videos that can't be embedded
    - - Update video URL handling script to detect non-embeddable URLs
    - - Show fallback message when URL doesn't contain '/embed/' pattern
    - - Provide "Open Video" button to view content in new tab
    - - Remove iframe src attribute when fallback is displayed
    - - Add translations for fallback message and button text



### Actualizado: 2026-01-12 22:29:01

- **[9dcebb3]** refactor: Enhance video URL handling with support for YouTube Shorts, Vimeo, and HTTPS enforcement
  - *Fecha:* 2026-01-12 22:29:00
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/events/public_detail.html`
  - *Detalles:*
    - - Move video URL from src to data-video-url attribute to prevent premature loading
    - - Add automatic HTTPS upgrade for HTTP URLs to prevent mixed content warnings
    - - Implement YouTube Shorts URL conversion to embed format
    - - Add Vimeo URL detection and conversion to player.vimeo.com embed format
    - - Add fallback for pre-formatted embed URLs and other compatible platforms
    - - Include additional iframe permissions



### Actualizado: 2026-01-12 22:22:29

- **[56da03d]** refactor: Add backward compatibility for generic itinerary data in event forms
  - *Fecha:* 2026-01-12 22:22:29
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `apps/events/views.py`
  - *Detalles:*
    - - Add fallback logic to handle templates sending generic "itinerary_days" field name
    - - Check for generic_itinerary_days_data when user-type-specific data is missing
    - - Apply generic itinerary to "player" user type when no type-specific data exists
    - - Implement same compatibility layer in both EventCreateView and EventUpdateView
    - - Maintain support for both legacy and new itinerary input formats



### Actualizado: 2026-01-12 22:08:41

- **[198e41b]** refactor: Add event view tracking system and improve site image handling
  - *Fecha:* 2026-01-12 22:08:41
  - *Autor:* cgallego17
  - *Archivos modificados:* 17 archivo(s)
    - `apps/events/migrations/0039_event_views_eventview.py`
    - `apps/events/migrations/0040_alter_event_video_url.py`
    - `apps/events/models.py`
    - `apps/events/views_public.py`
    - `apps/locations/forms.py`
    - `apps/locations/migrations/0028_alter_site_image.py`
    - `apps/locations/migrations/0029_siteimage.py`
    - `apps/locations/models.py`
    - `apps/locations/views.py`
    - `templates/accounts/panel_tabs/detalle_evento.html`
    - ... y 7 archivo(s) más
  - *Detalles:*
    - - Add gettext_lazy import for internationalization in Event model
    - - Add views field to Event model for tracking visit counts
    - - Create EventView model to record event page visits with IP, user, and session tracking
    - - Implement view recording in PublicEventDetailView with IP detection and duplicate prevention
    - - Convert Site.image from ImageField to URLField for media library integration
    - - Create SiteImage model for site gallery



### Actualizado: 2026-01-12 19:57:19

- **[8f3cbbf]** refactor: Enhance user profile management with billing, notifications, and Stripe integration
  - *Fecha:* 2026-01-12 19:57:18
  - *Autor:* cgallego17
  - *Archivos modificados:* 30 archivo(s)
    - `apps/accounts/forms.py`
    - `apps/accounts/migrations/0049_userprofile_email_notifications_and_more.py`
    - `apps/accounts/migrations/0050_userprofile_stripe_customer_id.py`
    - `apps/accounts/models.py`
    - `apps/accounts/urls.py`
    - `apps/accounts/views_private.py`
    - `templates/403.html`
    - `templates/404.html`
    - `templates/accounts/base_public.html`
    - `templates/accounts/front_player_profile.html`
    - ... y 20 archivo(s) más
  - *Detalles:*
    - - Add PasswordChangeForm import and create CustomPasswordChangeForm with Bootstrap styling
    - - Add NotificationPreferencesForm for managing email, event, reservation, and marketing notifications
    - - Extend UserProfileForm with additional fields: last_name2, phone_secondary, address_line_2, preferred_language, website, and social_media
    - - Create BillingAddressForm for separate billing address management with



### Actualizado: 2026-01-12 18:28:39

- **[936c003]** refactor: Improve JSON serialization and Vue app initialization
  - *Fecha:* 2026-01-12 18:28:39
  - *Autor:* cgallego17
  - *Archivos modificados:* 4 archivo(s)
    - `apps/events/views.py`
    - `templates/accounts/panel_tabs/detalle_evento_vue.html`
    - `templates/base.html`
    - `templates/events/dashboard.html`
  - *Detalles:*
    - - Add json module import to events views
    - - Serialize events_by_category and events_by_division to JSON in DashboardView
    - - Pass JSON-serialized data to dashboard template for Chart.js consumption
    - - Refactor Vue app initialization with safeParseJsonScript helper function
    - - Simplify error handling and reduce code duplication in detalle_evento_vue.html
    - - Fix script tag closure in base.html template



### Actualizado: 2026-01-12 18:10:22

- **[008b6b7]** refactor: Improve event banner responsiveness and modal z-index handling
  - *Fecha:* 2026-01-12 18:10:22
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `static/js/vue/event-detail.js`
    - `templates/base.html`
  - *Detalles:*
    - - Update event banner height to use clamp() for responsive sizing (180px-300px based on viewport)
    - - Add z-index override for mainContent when modal is open to ensure proper layering
    - - Improve mobile viewing experience with adaptive banner dimensions



### Actualizado: 2026-01-12 17:51:08

- **[a5d63a9]** refactor: Apply code formatting and improve date comparison logic
  - *Fecha:* 2026-01-12 17:51:08
  - *Autor:* cgallego17
  - *Archivos modificados:* 9 archivo(s)
    - `apps/events/views.py`
    - `apps/events/views_data_management.py`
    - `templates/base.html`
    - `templates/events/dashboard.html`
    - `templates/events/division_form.html`
    - `templates/events/event_form.html`
    - `templates/events/eventcontact_form.html`
    - `templates/events/eventtype_form.html`
    - `templates/events/gatefeetype_form.html`
  - *Detalles:*
    - - Reformat imports to follow alphabetical ordering
    - - Apply consistent string quote style (single to double quotes)
    - - Improve code formatting with proper line breaks and indentation
    - - Update date comparison logic in DashboardView to use date objects instead of datetime for more accurate filtering
    - - Remove unused EventService import
    - - Add proper spacing and formatting throughout event views



### Actualizado: 2026-01-12 15:19:28

- **[658387e]** Integreacion de wallets
  - *Fecha:* 2026-01-12 15:19:28
  - *Autor:* cgallego17
  - *Archivos modificados:* 650 archivo(s)
    - `CHANGELOG_FIX_SUMMARY.md`
    - `PASOS_SIGUIENTES_SEGURIDAD.md`
    - `SECURITY_AUDIT_REGISTRO_PUBLICO.md`
    - `SECURITY_IMPROVEMENTS_INSTALLED.md`
    - `apps/accounts/admin.py`
    - `apps/accounts/apps.py`
    - `apps/accounts/management/commands/verify_wallet_integrity.py`
    - `apps/accounts/migrations/0043_alter_order_payment_mode_alter_order_status_and_more.py`
    - `apps/accounts/migrations/0044_remove_stripeeventcheckout_currency_and_more.py`
    - `apps/accounts/migrations/0045_staffwallettopup.py`
    - ... y 640 archivo(s) más



### Actualizado: 2026-01-10 21:39:01

- **[cd04294]** settings
  - *Fecha:* 2026-01-10 21:39:01
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `nsc_admin/settings_simple.py`



### Actualizado: 2026-01-10 21:25:19

- **[0a5e52d]** Varios
  - *Fecha:* 2026-01-10 21:25:19
  - *Autor:* cgallego17
  - *Archivos modificados:* 21 archivo(s)
    - `apps/accounts/forms.py`
    - `apps/accounts/templatetags/url_filters.py`
    - `apps/accounts/urls_private.py`
    - `apps/accounts/views_private.py`
    - `apps/accounts/views_public.py`
    - `apps/events/forms.py`
    - `apps/events/migrations/0034_add_event_service.py`
    - `apps/events/migrations/0035_add_user_type_to_event_itinerary.py`
    - `apps/events/migrations/0036_add_description_player_to_event.py`
    - `apps/events/migrations/0037_add_event_includes_model.py`
    - ... y 11 archivo(s) más



### Actualizado: 2026-01-09 23:08:19

- **[9b784a2]** feat: Update user panel to enhance spectator experience
  - *Fecha:* 2026-01-09 23:08:19
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/accounts/panel_usuario.html`
  - *Detalles:*
    - - Modified the user panel template to display relevant tabs for spectators, including Events, Reservations, and Plans & Payments.
    - - Adjusted tab activation logic to default to the Events tab for spectators and the Home tab for other user types.
    - - Removed unnecessary buttons and streamlined the quick actions for better usability based on user roles.



### Actualizado: 2026-01-09 23:02:20

- **[3cfd2ff]** feat: Add Event Itinerary model and management functionality
  - *Fecha:* 2026-01-09 23:02:19
  - *Autor:* cgallego17
  - *Archivos modificados:* 4 archivo(s)
    - `apps/events/migrations/0033_eventitinerary.py`
    - `apps/events/models.py`
    - `apps/events/views.py`
    - `templates/events/event_form.html`
  - *Detalles:*
    - - Introduced the EventItinerary model to manage daily itineraries for events, including fields for day, title, description, and schedule items.
    - - Updated EventCreateView and EventUpdateView to handle itinerary saving and processing upon event creation and updates.
    - - Enhanced the event form template with a dynamic itinerary management interface, allowing users to add, edit, and remove itinerary days and activities.
    - - Implemented JavaScript functionality for automatic day generation based on event start and end dates.



### Actualizado: 2026-01-09 22:32:20

- **[44474d7]** Update CHANGELOG.md to include recent enhancements in media file management, documenting pagination implementation, user type pre-selection in registration, and improvements in event ID retrieval and error handling.
  - *Fecha:* 2026-01-09 22:32:19
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `CHANGELOG.md`



### Actualizado: 2026-01-09 22:31:15

- **[a86c69b]** Update CHANGELOG.md to reflect recent enhancements in media file management, including pagination implementation, user type pre-selection in registration, and improvements in event ID retrieval and error handling.
  - *Fecha:* 2026-01-09 22:29:49
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `CHANGELOG.md`



### Actualizado: 2026-01-09 22:30:47

- **[a86c69b]** Update CHANGELOG.md to reflect recent enhancements in media file management, including pagination implementation, user type pre-selection in registration, and improvements in event ID retrieval and error handling.
  - *Fecha:* 2026-01-09 22:29:49
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `CHANGELOG.md`



### Actualizado: 2026-01-09 22:29:43

- **[764ad14]** Update CHANGELOG.md to include recent enhancements in media file management
  - *Fecha:* 2026-01-09 22:29:43
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `CHANGELOG.md`
  - *Detalles:*
    - - Documented the implementation of pagination in the media file list AJAX view for improved navigation.
    - - Added details on user type pre-selection in the public registration view based on URL parameters.
    - - Noted refactoring of event ID retrieval logic and improvements in error handling during registration.



### Actualizado: 2026-01-09 22:29:39

- **[eb25c2b]** Update CHANGELOG.md to include recent enhancements in media file management
  - *Fecha:* 2026-01-09 22:29:39
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `CHANGELOG.md`
  - *Detalles:*
    - - Documented the implementation of pagination in the media file list AJAX view for improved navigation.
    - - Added details on user type pre-selection in the public registration view based on URL parameters.
    - - Noted refactoring of event ID retrieval logic and improvements in error handling during registration.



### Actualizado: 2026-01-09 22:26:37

- **[9ea0d07]** feat: Implement pagination and user type pre-selection in media file management
  - *Fecha:* 2026-01-09 22:26:36
  - *Autor:* cgallego17
  - *Archivos modificados:* 15 archivo(s)
    - `CHANGELOG.md`
    - `apps/accounts/views.py`
    - `apps/media/views.py`
    - `docs/CHANGELOG_SETUP.md`
    - `scripts/test_changelog_hook.py`
    - `templates/accounts/front_player_profile.html`
    - `templates/accounts/panel_usuario.html`
    - `templates/accounts/parent_player_register.html`
    - `templates/accounts/player_register.html`
    - `templates/accounts/profile_edit.html`
    - ... y 5 archivo(s) más
  - *Detalles:*
    - - Enhanced the media file list AJAX view to support pagination, allowing users to navigate through media files more efficiently.
    - - Updated the public registration view to pre-select user type based on URL parameters, improving user experience during registration.
    - - Refactored event ID retrieval logic to ensure it can be obtained from both session and request parameters, enhancing robustness.
    - - Improved error handling in the registration process to manage invalid event IDs gracefully.



### [Fecha de última actualización]
- Proyecto inicializado
