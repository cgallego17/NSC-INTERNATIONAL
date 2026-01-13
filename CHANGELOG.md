# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Sin versión]

### Actualizado: 2026-01-13 16:53:28

- **[f15a6d1]** ```
  - *Fecha:* 2026-01-13 16:53:28
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `apps/accounts/views_private.py`
    - `templates/accounts/admin/user_admin_detail.html`
  - *Detalles:*
    - feat: Add tabbed interface to admin user detail view with payment plan tracking and team player management
    - - Add Bootstrap tabs for organizing user information into sections: General, Familia, Equipos/Jugadores, Órdenes, Payment Plans, Wallet, Stripe, Notificaciones, Push, and Eventos
    - - Add payment_plan_orders query filtering orders with payment_mode="plan" limited to last 50
    - - Add active_payment_plan_orders query filtering by plan_payments_remaining > 0 or non-empty stripe_subscription_id
    - - Add payment



### Actualizado: 2026-01-13 14:37:17

- **[b5e02e1]** ```
  - *Fecha:* 2026-01-13 14:37:16
  - *Autor:* cgallego17
  - *Archivos modificados:* 4 archivo(s)
    - `apps/accounts/urls.py`
    - `apps/accounts/views_private.py`
    - `templates/accounts/admin/user_admin_detail.html`
    - `templates/accounts/user_list.html`
  - *Detalles:*
    - feat: Add comprehensive user detail view for staff with related data aggregation
    - - Add AdminUserDetailView with user_obj context for detailed user information
    - - Create admin_user_detail URL pattern at users/<int:pk>/detail/
    - - Aggregate wallet data with last 50 transactions ordered by creation date
    - - Include user orders with event and stripe checkout relationships
    - - Display stripe checkouts, notifications, and push subscriptions
    - - Show managed teams with prefetched players
    - - Include player profile



### Actualizado: 2026-01-13 14:11:05

- **[93ed922]** ```
  - *Fecha:* 2026-01-13 14:11:04
  - *Autor:* cgallego17
  - *Archivos modificados:* 5 archivo(s)
    - `scripts/utilities/generate_pwa_icons.sh`
    - `static/images/ncs-app-icon.svg`
    - `static/images/pwa-baseball.svg`
    - `static/manifest.json`
    - `templates/base.html`
  - *Detalles:*
    - feat: Add Progressive Web App (PWA) manifest and mobile app configuration
    - - Add manifest.json link for PWA installation support
    - - Configure theme color #0d2c54 for browser UI customization
    - - Enable iOS web app capabilities with apple-mobile-web-app-capable meta tag
    - - Set default status bar style for iOS devices
    - - Add apple-touch-icon references for iOS home screen icons
    - - Include mask-icon for Safari pinned tab with theme color
    - - Set app title "NCS International" for iOS home screen
    - ```



### Actualizado: 2026-01-13 13:47:48

- **[2a997f8]** ```
  - *Fecha:* 2026-01-13 13:47:48
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `static/js/admin.js`
  - *Detalles:*
    - refactor: Add automatic service worker registration and push notification prompts for staff users
    - - Extract service worker registration into _ensureServiceWorkerRegistered helper method
    - - Add _promptWebPushEnableIfNeeded method to automatically prompt staff users to enable push notifications
    - - Check for existing service worker registration before creating new one
    - - Show toast notification when push is not enabled and permission is default
    - - Add active class to notification button and focus enable



### Actualizado: 2026-01-13 13:36:15

- **[f872e80]** ```
  - *Fecha:* 2026-01-13 13:36:14
  - *Autor:* cgallego17
  - *Archivos modificados:* 13 archivo(s)
    - `apps/accounts/migrations/0051_pushsubscription.py`
    - `apps/accounts/migrations/0052_rename_accounts_pu_user_id_2db9b6_idx_accounts_pu_user_id_125f9c_idx.py`
    - `apps/accounts/models.py`
    - `apps/accounts/signals.py`
    - `apps/accounts/urls.py`
    - `apps/accounts/views_private.py`
    - `apps/core/views.py`
    - `docker-compose.prod.yml`
    - `nsc_admin/settings_prod.py`
    - `nsc_admin/urls.py`
    - ... y 3 archivo(s) más
  - *Detalles:*
    - feat: Add web push notification system for staff users with player and user registration alerts
    - - Add PushSubscription model with endpoint, p256dh, auth, user_agent, and is_active fields
    - - Create database indexes on user, is_active, and created_at for optimized queries
    - - Add post_save signals for Player and User models to notify staff of new registrations
    - - Implement send_web_push_for_staff_notifications signal to deliver push notifications via pywebpush
    - - Add push subscription API endpoints:



### Actualizado: 2026-01-13 12:35:33

- **[6170de4]** ```
  - *Fecha:* 2026-01-13 12:35:33
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `static/js/admin.js`
  - *Detalles:*
    - refactor: Add notification button state management and accessibility improvements
    - - Add notificationBtn element reference for notification button state updates
    - - Apply has-notifications class to notification button when count > 0
    - - Update aria-label attribute with notification count for screen reader accessibility
    - - Remove has-notifications class and reset aria-label when no notifications present
    - ```



### Actualizado: 2026-01-13 12:26:52

- **[8b489a1]** ```
  - *Fecha:* 2026-01-13 12:26:52
  - *Autor:* cgallego17
  - *Archivos modificados:* 3 archivo(s)
    - `apps/accounts/signals.py`
    - `apps/accounts/views_private.py`
    - `templates/emails/order_staff_notification.html`
  - *Detalles:*
    - refactor: Add staff email notifications for order creation and payment with detailed player information
    - - Import EmailMultiAlternatives, render_to_string, get_user_model, and settings for email functionality
    - - Add Player model import for player data enrichment in signals
    - - Extract staff emails from active staff users for order notifications
    - - Build comprehensive email context including event details, player information, and hotel reservations
    - - Support multiple player data sources: registere



### Actualizado: 2026-01-13 11:35:30

- **[dcc216d]** ```
  - *Fecha:* 2026-01-13 11:35:30
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `apps/accounts/views_private.py`
  - *Detalles:*
    - refactor: Add comprehensive duplicate registration prevention for event checkout
    - - Import EventAttendance model for attendance status validation
    - - Block duplicate registrations if players have existing EventAttendance records with active status (pending/confirmed/waiting)
    - - Prevent creating new checkout if pending checkout exists with overlapping player selections
    - - Add resume_checkout_id detection to force resuming existing pending checkouts
    - - Block duplicate registrations if players are already in



### Actualizado: 2026-01-13 11:28:25

- **[0183e99]** ```
  - *Fecha:* 2026-01-13 11:28:25
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/events/public_detail.html`
  - *Detalles:*
    - refactor: Remove service fee display from event registration plan details
    - - Remove service fee display from player registration plan details
    - - Remove service fee display from team manager registration plan details
    - - Remove service fee display from spectator registration plan details
    - - Service fees are now handled internally without being shown to users during registration
    - ```



### Actualizado: 2026-01-13 11:21:47

- **[aa4567a]** ```
  - *Fecha:* 2026-01-13 11:21:47
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `templates/accounts/panel_tabs/detalle_evento.html`
    - `templates/events/public_detail.html`
  - *Detalles:*
    - refactor: Use spectator-specific entry fee for child registration and add autoplay to video player
    - - Update child-item data-child-price to use default_entry_fee_spectator for spectators with fallback to default_entry_fee
    - - Update pricePerPlayer JavaScript variable to use spectator-specific fee based on is_spectator flag
    - - Add autoplay, muted, and preload="metadata" attributes to HTML5 video element for better user experience
    - ```



### Actualizado: 2026-01-13 11:11:16

- **[fdb4a83]** ```
  - *Fecha:* 2026-01-13 11:11:15
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/events/public_detail.html`
  - *Detalles:*
    - refactor: Simplify video display logic to use native HTML5 video player for direct video files
    - - Replace iframe-based video embedding with native HTML5 video element for .mp4, .webm, and .ogg files
    - - Remove JavaScript video URL conversion logic for YouTube, Vimeo, and other providers
    - - Change fallback behavior to show direct link for all non-video file URLs
    - - Update fallback alert from warning to info style with simplified messaging
    - - Remove mixed content prevention and embed URL transformation



### Actualizado: 2026-01-13 11:08:43

- **[18e3f61]** ```
  - *Fecha:* 2026-01-13 11:08:42
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/events/public_detail.html`
  - *Detalles:*
    - refactor: Attempt direct iframe embed for unrecognized video URLs before showing fallback
    - - Change fallback behavior to try direct iframe embedding for unrecognized URLs
    - - Set iframe.src to url instead of removing src attribute
    - - Update comment to explain fallback link remains available if provider blocks iframes
    - - Keep fallback visible to provide alternative access method
    - ```



### Actualizado: 2026-01-13 11:02:48

- **[c4bc3b7]** ```
  - *Fecha:* 2026-01-13 11:02:48
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `apps/accounts/views_admin.py`
  - *Detalles:*
    - refactor: Add backward compatibility for missing breakdown fields in admin order detail view
    - - Add default values for no_show_fee and hotel_buy_out_fee in breakdown dictionary
    - - Implement setdefault logic to handle legacy orders missing new breakdown fields
    - - Add type check to ensure breakdown is a dictionary before setting defaults
    - - Add comment explaining template compatibility issue with missing keys
    - ```



### Actualizado: 2026-01-13 09:09:38

- **[9ef2010]** ```
  - *Fecha:* 2026-01-13 09:09:37
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `apps/accounts/views_admin.py`
  - *Detalles:*
    - refactor: Add detailed order information to admin order detail view
    - - Add registered_players context data with fallback logic for legacy orders
    - - Implement EventAttendance-based player reconstruction using stripe_session_id for orders without registered_player_ids
    - - Add hotel_reservations context data from order
    - - Include payment_plan_summary for payment plan orders
    - - Add breakdown JSON data to context
    - - Add event_attendances context for player registration status
    - - Import EventAttendance an



### Actualizado: 2026-01-12 23:23:34

- **[ba72880]** refactor: Set Home tab as default for all users and simplify Events tab logic
  - *Fecha:* 2026-01-12 23:23:33
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/accounts/panel_usuario.html`
  - *Detalles:*
    - - Change Home tab to be active by default when no active_tab is set for spectators
    - - Remove spectator-specific default active state from Events tab
    - - Update Home tab content visibility to show by default for all users when no active_tab is set
    - - Simplify Events tab content visibility logic to remove spectator-specific conditions
    - - Update comment to reflect Home tab as default for all users instead of Events for spectators



### Actualizado: 2026-01-12 23:19:36

- **[fb1730c]** refactor: Add Home, Registrations, and Profile tabs to spectator panel navigation
  - *Fecha:* 2026-01-12 23:19:36
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/accounts/panel_usuario.html`
  - *Detalles:*
    - - Add Home tab button to spectator quick actions
    - - Add Registrations tab button with pending registrations badge for spectators
    - - Add Profile tab button to spectator quick actions
    - - Update comment to reflect new tabs available for spectators (Home, Events, Registrations, Reservations, Plans & Payments, Profile)
    - - Modify Home tab content visibility logic to show for spectators when explicitly selected
    - - Change default



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
