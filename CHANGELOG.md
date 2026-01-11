# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Sin versión]

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
