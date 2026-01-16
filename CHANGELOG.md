# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Sin versión]

### Actualizado: 2026-01-16 11:17:44

- **[f8ecfc7]** ```
  - *Fecha:* 2026-01-16 11:17:44
  - *Autor:* cgallego17
  - *Archivos modificados:* 3 archivo(s)
    - `apps/accounts/urls.py`
    - `apps/accounts/views_admin.py`
    - `templates/accounts/admin/team_list.html`
  - *Detalles:*
    - feat: Add toggle active/inactive button for teams in admin list view
    - - Add admin_team_toggle_active URL pattern for POST requests to toggle team status
    - - Implement admin_team_toggle_active view with authentication and staff permission checks
    - - Toggle team.is_active status and save with update_fields for efficiency
    - - Display success message indicating whether team was activated or deactivated
    - - Add inline form with pause/play icon buttons in team_list.html based on current status
    - - Import get



### Actualizado: 2026-01-16 11:01:49

- **[cdf6242]** ```
  - *Fecha:* 2026-01-16 11:01:49
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `apps/accounts/templatetags/url_filters.py`
  - *Detalles:*
    - style: Format url_filters.py with consistent quote style and improve intcomma_dot robustness
    - - Replace single quotes with double quotes throughout the file
    - - Reorder imports to place standard library before third-party
    - - Enhance intcomma_dot filter to handle multiple input formats (3435.68, 3,435.68, 3.435,68)
    - - Add logic to detect decimal and thousands separators based on position and digit count
    - - Normalize input by removing spaces and non-numeric characters except separators
    - - Support negative



### Actualizado: 2026-01-15 15:34:36

- **[0fea4c9]** feat: Add admin team management with CRUD operations and cascading location filters
  - *Fecha:* 2026-01-15 15:34:36
  - *Autor:* cgallego17
  - *Archivos modificados:* 8 archivo(s)
    - `apps/accounts/forms.py`
    - `apps/accounts/urls.py`
    - `apps/accounts/views_admin.py`
    - `apps/core/context_processors.py`
    - `templates/accounts/admin/team_confirm_delete.html`
    - `templates/accounts/admin/team_form.html`
    - `templates/accounts/admin/team_list.html`
    - `templates/base.html`
  - *Detalles:*
    - - Create AdminTeamForm with all team fields including manager, location, and is_active status
    - - Add cascading country/state/city dropdowns with dynamic queryset filtering
    - - Implement AdminTeamListView with search and is_active filters, paginated by 25
    - - Add AdminTeamCreateView, AdminTeamUpdateView, and AdminTeamDeleteView with success messages
    - - Register admin team URL patterns for list, create, edit, and delete endpoints



### Actualizado: 2026-01-15 14:41:00

- **[b169553]** ```
  - *Fecha:* 2026-01-15 14:41:00
  - *Autor:* cgallego17
  - *Archivos modificados:* 7 archivo(s)
    - `templates/accounts/public_home.html`
    - `templates/accounts/public_login.html`
    - `templates/accounts/public_player_list.html`
    - `templates/accounts/public_register.html`
    - `templates/accounts/public_team_list.html`
    - `templates/events/public_list.html`
    - `templates/registration/login.html`
  - *Detalles:*
    - feat: Add password visibility toggle button to all login forms
    - - Wrap password inputs in input-group/password-wrapper containers across all templates
    - - Add toggle-password-btn/password-toggle-btn with eye icon next to password fields
    - - Implement JavaScript to toggle password visibility on button click
    - - Toggle between fa-eye and fa-eye-slash icons based on visibility state
    - - Add aria-label for accessibility on toggle buttons
    - - Apply changes to public_home.html, public_login.html, public_player



### Actualizado: 2026-01-15 13:52:18

- **[94a242f]** ```
  - *Fecha:* 2026-01-15 13:52:18
  - *Autor:* cgallego17
  - *Archivos modificados:* 9 archivo(s)
    - `apps/accounts/forms.py`
    - `apps/accounts/tests/test_email_confirmation_flow.py`
    - `apps/accounts/urls.py`
    - `apps/accounts/views_public.py`
    - `templates/registration/email_confirmation_complete.html`
    - `templates/registration/email_confirmation_email.txt`
    - `templates/registration/email_confirmation_email_html.html`
    - `templates/registration/email_confirmation_sent.html`
    - `templates/registration/email_confirmation_subject.txt`
  - *Detalles:*
    - feat: Add email confirmation requirement for new user registrations
    - - Set is_active=False for newly registered users in PublicRegistrationForm
    - - Add email confirmation URL patterns for sent confirmation and token verification endpoints
    - - Implement _send_email_confirmation helper to send confirmation emails with token links
    - - Add confirm_email view to validate tokens and activate user accounts
    - - Create EmailConfirmationSentView template view for post-registration confirmation page
    - - Update PublicLogin



### Actualizado: 2026-01-15 13:29:45

- **[e283d7c]** ```
  - *Fecha:* 2026-01-15 13:29:45
  - *Autor:* cgallego17
  - *Archivos modificados:* 14 archivo(s)
    - `apps/accounts/urls.py`
    - `templates/accounts/public_home.html`
    - `templates/accounts/public_login.html`
    - `templates/accounts/public_player_list.html`
    - `templates/accounts/public_register.html`
    - `templates/accounts/public_team_list.html`
    - `templates/events/public_list.html`
    - `templates/registration/password_reset_complete.html`
    - `templates/registration/password_reset_confirm.html`
    - `templates/registration/password_reset_done.html`
    - ... y 4 archivo(s) más
  - *Detalles:*
    - feat: Add password reset functionality with forgot password links in login forms
    - - Add password reset URL patterns using Django's built-in auth views in accounts/urls.py
    - - Configure password_reset, password_reset_done, password_reset_confirm, and password_reset_complete endpoints
    - - Import auth_views and reverse_lazy for password reset flow
    - - Add "Forgot your password?" link to login forms in public_home.html, public_login.html, public_player_list.html, public_register.html, public_team_list.html, an



### Actualizado: 2026-01-15 10:16:24

- **[e165825]** ```
  - *Fecha:* 2026-01-15 10:16:24
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `apps/accounts/forms.py`
    - `templates/accounts/public_register.html`
  - *Detalles:*
    - feat: Add Netherlands phone prefix to registration form and remove trailing whitespace
    - - Add +31 (Netherlands) option to phone_prefix choices in PublicRegistrationForm
    - - Add +31 (Netherlands) option to phone prefix dropdown in public_register.html template
    - - Remove trailing whitespace from PlayerUpdateForm profile_picture widget attrs
    - ```



### Actualizado: 2026-01-14 23:55:57

- **[ae94ca3]** ```
  - *Fecha:* 2026-01-14 23:55:56
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/events/public_detail.html`
  - *Detalles:*
    - feat: Add image gallery modal for location and accommodation photos in event detail page
    - - Add CSS for location-accommodation-grid with 2-column layout and responsive breakpoint
    - - Style location-icon and hotel-icon with fixed dimensions and border radius
    - - Add gallery-trigger, gallery-container, and gallery-hint styles for interactive image preview
    - - Implement hover effects with scale transform and brightness filter on gallery images
    - - Restructure location and accommodation sections into side



### Actualizado: 2026-01-14 23:46:48

- **[ac8ab56]** ```
  - *Fecha:* 2026-01-14 23:46:47
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/accounts/team_detail.html`
  - *Detalles:*
    - refactor: Extract footer HTML to reusable include template in team detail page
    - - Replace inline footer markup with {% include 'includes/footer_mlb.html' %}
    - - Remove 30 lines of duplicate footer HTML from team_detail.html
    - - Improve maintainability by centralizing footer content
    - ```



### Actualizado: 2026-01-14 23:08:55

- **[0f900d5]** ```
  - *Fecha:* 2026-01-14 23:08:55
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `apps/accounts/views_admin.py`
  - *Detalles:*
    - feat: Add fallback logic to infer wallet deduction amount for checkout reservation release
    - - Add inferred_wallet_deduction flag to track when amount is inferred vs. from breakdown
    - - Implement fallback to find reserve transaction by reference_id within 2-hour window of checkout creation
    - - Add last resort fallback using pending_balance when it matches expected reservation pattern
    - - Include inferred_wallet_deduction flag in JSON response
    - - Improve handling of older checkouts missing wallet_deduction in



### Actualizado: 2026-01-14 23:05:31

- **[ca36351]** ```
  - *Fecha:* 2026-01-14 23:05:31
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `apps/accounts/views_admin.py`
  - *Detalles:*
    - feat: Allow GET method for admin wallet reservation release endpoint
    - - Change admin_release_wallet_reservation_for_checkout from POST-only to accept both GET and POST methods
    - ```



### Actualizado: 2026-01-14 23:00:26

- **[6ee1f46]** ```
  - *Fecha:* 2026-01-14 23:00:25
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `apps/accounts/urls.py`
    - `apps/accounts/views_admin.py`
  - *Detalles:*
    - feat: Add admin endpoint to manually release wallet reservations for checkouts
    - - Add URL pattern for admin_release_wallet_reservation_for_checkout endpoint
    - - Import StripeEventCheckout model and InvalidOperation exception
    - - Implement POST endpoint to release reserved wallet funds for a checkout
    - - Check checkout status and prevent release for paid checkouts
    - - Extract wallet_deduction from checkout breakdown with error handling
    - - Verify no duplicate processing using reference_id checks
    - - Release



### Actualizado: 2026-01-14 22:52:42

- **[9201fd0]** ```
  - *Fecha:* 2026-01-14 22:52:41
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `apps/accounts/views_admin.py`
    - `apps/accounts/views_private.py`
  - *Detalles:*
    - feat: Improve user search case-sensitivity and add stale wallet reservation cleanup
    - - Import Lower function from django.db.models.functions in views_admin.py
    - - Convert search query to lowercase and use annotated lowercase fields
    - - Replace icontains with contains on lowercased fields for consistent case-insensitive search
    - - Add _cleanup_stale_wallet_reservations method to UserDashboardView
    - - Release reserved wallet funds for checkouts older than 24 hours
    - - Mark stale checkouts and related orders as expired/



### Actualizado: 2026-01-14 22:34:29

- **[ec01139]** ```
  - *Fecha:* 2026-01-14 22:34:29
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/base.html`
  - *Detalles:*
    - feat: Reset main content z-index to auto when modal is open
    - - Change #mainContent z-index from 2000 to auto when body has modal-open class
    - - Allow modal and backdrop to properly layer above main content without explicit z-index conflicts
    - ```



### Actualizado: 2026-01-14 22:31:32

- **[27b14fb]** ```
  - *Fecha:* 2026-01-14 22:31:31
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `static/css/admin.css`
    - `staticfiles/css/admin.css`
  - *Detalles:*
    - feat: Hide sidebar overlay on mobile when modal is open
    - - Add display none rule for #sidebarOverlay when body has modal-open class
    - - Apply to both modal-open and modal-open.sidebar-open states
    - - Prevent sidebar overlay from appearing above modal on mobile devices
    - ```



### Actualizado: 2026-01-14 22:29:33

- **[b2db062]** ```
  - *Fecha:* 2026-01-14 22:29:33
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `static/css/admin.css`
    - `staticfiles/css/admin.css`
  - *Detalles:*
    - feat: Fix modal z-index conflicts and hide sidebar overlay when modal is open
    - - Increase modal z-index to 20030 and backdrop to 20020 with !important
    - - Hide sidebar overlay when body has modal-open class
    - - Prevent sidebar overlay from appearing above modal backdrop
    - ```



### Actualizado: 2026-01-14 22:22:57

- **[d46e2ab]** ```
  - *Fecha:* 2026-01-14 22:22:57
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/locations/hotel_room_form.html`
  - *Detalles:*
    - feat: Restore visual preview grid for selected room media items
    - - Show preview wrap when items are selected, hide when empty
    - - Add card-based preview grid with thumbnails and titles
    - - Include remove button on each preview card
    - - Simplify hidden input creation without form validation checks
    - - Display selected media visually before form submission
    - ```



### Actualizado: 2026-01-14 22:17:45

- **[6ca4209]** ```
  - *Fecha:* 2026-01-14 22:17:44
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/locations/hotel_room_form.html`
  - *Detalles:*
    - feat: Center room media pagination controls and add fixed width to page info
    - - Change pagination layout from space-between to center with gap-3
    - - Add min-width 140px and text-align center to page info element
    - - Improve visual balance of pagination controls in room media modal
    - ```



### Actualizado: 2026-01-14 22:15:34

- **[2fe9856]** ```
  - *Fecha:* 2026-01-14 22:15:34
  - *Autor:* cgallego17
  - *Archivos modificados:* 3 archivo(s)
    - `staticfiles/css/admin.css`
    - `staticfiles/js/admin.js`
    - `templates/locations/hotel_room_form.html`
  - *Detalles:*
    - feat: Add pagination to room media modal and refactor mobile sidebar state management
    - - Add pagination controls to room media modal with prev/next buttons and page info
    - - Update loadMedia to accept page parameter and handle pagination state
    - - Store current page, total pages, and has_prev/has_next state
    - - Show/hide pagination controls based on total pages (>1)
    - - Update search and clear handlers to reset to page 1
    - - Change media limit from 60 to 24 per page with pagination
    - - Refactor handleRe



### Actualizado: 2026-01-14 22:06:35

- **[2ce7e62]** ```
  - *Fecha:* 2026-01-14 22:06:34
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `static/css/admin.css`
    - `static/js/admin.js`
  - *Detalles:*
    - feat: Fix sidebar visibility state when resizing from desktop to mobile
    - - Change overlay selector from #sidebar.show to body.sidebar-open for consistency
    - - Add check in handleResize to remove show class if sidebar-open not present
    - - Prevent sidebar from remaining stuck visible when resizing to mobile without explicit open state
    - ```



### Actualizado: 2026-01-14 22:02:34

- **[c9328ec]** ```
  - *Fecha:* 2026-01-14 22:02:33
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `static/js/admin.js`
    - `templates/base.html`
  - *Detalles:*
    - feat: Refactor mobile sidebar state management and add mobile-web-app-capable meta tag
    - - Refactor handleResize to clear drawer state when leaving mobile breakpoint (>769px)
    - - Remove show, sidebar-open, mobile-open classes and reset body overflow above 769px
    - - Clear desktop-only collapsed and mini states when entering mobile breakpoint
    - - Refactor toggleMobileMenu to delegate to adminDashboard instance method
    - - Remove duplicate mobile menu toggle implementation
    - - Add mobile-web-app-capable meta tag to



### Actualizado: 2026-01-14 21:57:20

- **[681f8f5]** ```
  - *Fecha:* 2026-01-14 21:57:20
  - *Autor:* cgallego17
  - *Archivos modificados:* 3 archivo(s)
    - `static/css/admin.css`
    - `static/js/admin.js`
    - `templates/base.html`
  - *Detalles:*
    - feat: Refactor mobile sidebar overlay from pseudo-element to dedicated element
    - - Replace body.sidebar-open::before pseudo-element with #sidebarOverlay div
    - - Add dedicated overlay element in base.html template
    - - Add click handler to close sidebar when overlay is clicked
    - - Add handleResize method to clear drawer state when leaving mobile breakpoint
    - - Normalize responsive state on page load to prevent stale mobile states
    - - Add media query at 769px with explicit sidebar drawer styles
    - - Force sidebar width



### Actualizado: 2026-01-14 21:51:32

- **[03fb64d]** ```
  - *Fecha:* 2026-01-14 21:51:32
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `static/css/admin.css`
  - *Detalles:*
    - feat: Add mobile toggle button display controls at 769px breakpoint
    - - Change mobile breakpoint from 768px to 769px for consistency
    - - Show mobile-toggle button with display flex below 769px
    - - Hide sidebar-toggle button on mobile devices
    - - Maintain existing sidebar width and transform behavior
    - ```



### Actualizado: 2026-01-14 21:49:21

- **[b924ff0]** ```
  - *Fecha:* 2026-01-14 21:49:20
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `static/css/admin.css`
    - `static/js/admin.js`
  - *Detalles:*
    - feat: Add responsive mobile sidebar with overlay and drawer behavior
    - - Add mobile breakpoint styles at 768px and 480px for sidebar
    - - Set sidebar width to 280px on tablets, 100% on phones
    - - Implement slide-in drawer animation with translateX transform
    - - Add dark overlay backdrop (rgba(0,0,0,0.45)) when sidebar is open
    - - Set sidebar z-index to 20010 and backdrop to 20005 for proper layering
    - - Prevent body scroll when sidebar is open with overflow hidden
    - - Adjust topbar and main-content to full



### Actualizado: 2026-01-14 21:44:07

- **[a368798]** ```
  - *Fecha:* 2026-01-14 21:44:06
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `static/css/admin.css`
  - *Detalles:*
    - feat: Increase modal z-index to prevent overlay conflicts
    - - Set modal z-index to 20000 to ensure proper layering
    - - Set modal-backdrop z-index to 19990 to maintain correct stacking order
    - - Prevent modals from appearing behind other UI elements
    - ```



### Actualizado: 2026-01-14 21:40:35

- **[80988d5]** ```
  - *Fecha:* 2026-01-14 21:40:35
  - *Autor:* cgallego17
  - *Archivos modificados:* 3 archivo(s)
    - `apps/accounts/views_admin.py`
    - `apps/accounts/views_private.py`
    - `templates/accounts/admin/order_detail.html`
  - *Detalles:*
    - feat: Add detailed hotel tax breakdown and wallet deduction display
    - - Add wallet_deduction field to breakdown defaults in admin order detail view
    - - Add hotel tax fields (hotel_room_base, hotel_services_total, hotel_iva, hotel_ish, hotel_total_taxes, hotel_total) to breakdown defaults
    - - Calculate derived hotel taxes when hotel_total_taxes is zero by subtracting base and services from total
    - - Fetch hotel room taxes from HotelRoomTax model when breakdown taxes are zero
    - - Iterate through hotel reserv



### Actualizado: 2026-01-14 21:23:11

- **[83affed]** ```
  - *Fecha:* 2026-01-14 21:23:10
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `static/js/vue/event-detail.js`
  - *Detalles:*
    - feat: Hide register-only button for spectators in event detail
    - - Add !isSpectator condition to register-only button visibility check
    - - Prevent spectators from accessing registration-only checkout flow
    - - Maintain existing isResumedCheckout condition for button display
    - ```



### Actualizado: 2026-01-14 21:20:57

- **[5f4ece5]** ```
  - *Fecha:* 2026-01-14 21:20:57
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `apps/accounts/views_private.py`
  - *Detalles:*
    - feat: Expand pending status detection for registration cards
    - - Include "pending" order status alongside "pending_registration" for is_pending flag
    - - Add fallback to checkout status when order is None
    - - Check for "created" and "registered" checkout statuses as pending indicators
    - ```



### Actualizado: 2026-01-14 21:17:35

- **[f62d9d9]** ```
  - *Fecha:* 2026-01-14 21:17:35
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/accounts/panel_tabs/registrations.html`
  - *Detalles:*
    - feat: Add checkout ID and database order ID to registration details
    - - Add checkout ID display with hashtag icon when checkout exists
    - - Show database order ID below order number with smaller font and muted color
    - - Maintain existing order number and creation date display
    - - Use consistent styling with 0.7rem font size and #6c757d color for metadata
    - ```



### Actualizado: 2026-01-14 21:14:57

- **[547535b]** ```
  - *Fecha:* 2026-01-14 21:14:57
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `apps/accounts/views_private.py`
    - `static/js/vue/event-detail.js`
  - *Detalles:*
    - feat: Add auto-resume for pending checkout sessions
    - - Add resume_checkout as alternative parameter name alongside resume_checkout_id
    - - Return both resume_checkout_id and resume_checkout in 400 error response
    - - Implement retry logic in event-detail.js to auto-resume pending checkouts
    - - Parse error response to extract resume_checkout_id or resume_checkout value
    - - Retry fetch request with resume parameters when 400 status and resumeId detected
    - - Limit retry attempts to 2 to prevent infinite loops
    - -



### Actualizado: 2026-01-14 21:05:26

- **[e9c1480]** ```
  - *Fecha:* 2026-01-14 21:05:25
  - *Autor:* cgallego17
  - *Archivos modificados:* 3 archivo(s)
    - `apps/accounts/views_admin.py`
    - `debug_order_4.py`
    - `templates/accounts/admin/order_detail.html`
  - *Detalles:*
    - feat: Add user type display to admin order detail view
    - - Remove unused json import from views_admin.py
    - - Add customer_user_type context variable with profile.user_type mapping
    - - Map spectator, parent, and team_manager to display values (coach for team_manager)
    - - Add User Type field to customer information section in order_detail.html template
    - - Simplify hotel_reservations query by removing unnecessary try-except block
    - ```



### Actualizado: 2026-01-14 12:05:53

- **[af297a2]** ```
  - *Fecha:* 2026-01-14 12:05:53
  - *Autor:* cgallego17
  - *Archivos modificados:* 8 archivo(s)
    - `apps/accounts/views_admin.py`
    - `templates/accounts/admin/order_detail.html`
    - `templates/accounts/panel_tabs/invoice.html`
    - `templates/accounts/panel_tabs/payment_confirmation.html`
    - `templates/accounts/public_home.html`
    - `templates/accounts/public_player_profile.html`
    - `templates/base.html`
    - `templates/includes/footer_mlb.html`
  - *Detalles:*
    - refactor: Optimize hotel reservation queries and update branding assets
    - - Remove unused F import from django.db.models in views_admin.py
    - - Add select_related and prefetch_related optimization for hotel reservation queries
    - - Remove unused user variable assignment in AdminWalletTopUpForm.clean_user_id
    - - Replace NCS International PNG logo with SVG assets across all templates
    - - Use ncs-white.svg for footer, sidebar, and dark backgrounds
    - - Use ncs-app-icon.svg for invoice, payment confirmation, and mini



### Actualizado: 2026-01-14 02:05:46

- **[45f4579]** ```
  - *Fecha:* 2026-01-14 02:05:45
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/events/public_detail.html`
  - *Detalles:*
    - refactor: Remove duplicate itinerary section from player plan card
    - - Remove redundant itinerary_player section displaying event days
    - - Delete 19 lines including plan-includes-section wrapper, title, and list items
    - - Eliminate duplicate day.title and day.day date display with English locale enforcement
    - - Keep only registration button for player plan
    - ```



### Actualizado: 2026-01-14 01:50:10

- **[2f35a48]** ```
  - *Fecha:* 2026-01-14 01:50:09
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/events/public_detail.html`
  - *Detalles:*
    - refactor: Remove duplicate itinerary section from spectator plan card
    - - Remove redundant itinerary_spectator section displaying event days
    - - Delete 20 lines including plan-includes-section wrapper, title, and list items
    - - Eliminate duplicate day.title and day.day date display with English locale enforcement
    - - Keep only registration button for spectator plan
    - ```



### Actualizado: 2026-01-14 01:49:22

- **[0e35f21]** ```
  - *Fecha:* 2026-01-14 01:49:22
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/events/public_detail.html`
  - *Detalles:*
    - refactor: Remove duplicate itinerary section from team manager plan card
    - - Remove redundant itinerary_team_manager section displaying event days
    - - Delete 19 lines including plan-includes-section wrapper, title, and list items
    - - Eliminate duplicate day.title and day.day date display with English locale enforcement
    - - Keep only registration button for team manager plan
    - ```



### Actualizado: 2026-01-14 01:41:38

- **[f2a91fd]** ```
  - *Fecha:* 2026-01-14 01:41:38
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/events/public_detail.html`
  - *Detalles:*
    - fix: Force English locale for date formatting in event day displays
    - - Wrap all day.day date filters with {% language 'en' %} tags to ensure consistent "M d, Y" format
    - - Apply to 4 instances across event detail cards and plan includes sections
    - - Prevent date format from being affected by user's selected language preference
    - ```



### Actualizado: 2026-01-14 01:30:39

- **[d47a3a6]** ```
  - *Fecha:* 2026-01-14 01:30:38
  - *Autor:* cgallego17
  - *Archivos modificados:* 4 archivo(s)
    - `locale/en/LC_MESSAGES/django.mo`
    - `locale/en/LC_MESSAGES/django.po`
    - `locale/es/LC_MESSAGES/django.mo`
    - `locale/es/LC_MESSAGES/django.po`
  - *Detalles:*
    - chore: Update English translation catalog with new message strings
    - - Regenerate django.mo compiled translation file from updated source
    - - Update POT-Creation-Date timestamp to 2026-01-14 01:30-0500
    - - Add translation entries for new templates including order_detail.html, invoice.html, public_login.html, and public_team_list.html
    - - Add msgid entries for new UI strings: "Individual Player", "Parent / Guardian", "Spectator"
    - - Expand location references across 50+ template files with updated line



### Actualizado: 2026-01-14 01:29:27

- **[1a557e7]** ```
  - *Fecha:* 2026-01-14 01:29:27
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/includes/navbar_mlb.html`
  - *Detalles:*
    - fix: Wrap language names in trans tags for proper translation in MLB navbar
    - - Add {% trans "English" %} tag around "English" language option text
    - - Add {% trans "Spanish" %} tag around "Español" language option text
    - - Enable proper i18n support for language selector labels in navbar_mlb.html template
    - ```



### Actualizado: 2026-01-14 01:23:28

- **[36f1f29]** ```
  - *Fecha:* 2026-01-14 01:23:28
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `templates/accounts/panel_tabs/registrar_hijo.html`
    - `templates/accounts/parent_player_register.html`
  - *Detalles:*
    - fix: Improve location cascade selectors with fallback field names and enhanced error handling
    - - Add fallback selectors for child-prefixed field names (child-country, child-state, child-city) alongside standard names
    - - Add HTTP response validation in fetch calls for states and cities endpoints
    - - Add empty data array validation with user-friendly fallback messages
    - - Display "No states/cities available" when API returns empty results
    - - Throw descriptive errors for non-OK HTTP responses
    - - Apply



### Actualizado: 2026-01-14 01:07:21

- **[5656d8e]** ```
  - *Fecha:* 2026-01-14 01:07:20
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `scripts/import/importar_netherlands.py`
  - *Detalles:*
    - feat: Add dynamic project root discovery for import scripts
    - - Add _discover_project_root() function to walk up directory tree searching for manage.py
    - - Replace hardcoded directory navigation with automatic Django project root detection
    - - Search up to 8 parent directories for manage.py marker file
    - - Fallback to two levels up from scripts/import if manage.py not found
    - - Improve portability of import script across different project structures
    - ```



### Actualizado: 2026-01-14 01:03:09

- **[d9066c5]** ```
  - *Fecha:* 2026-01-14 01:03:08
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `scripts/import/importar_netherlands.py`
  - *Detalles:*
    - fix: Add exception handling for module spec discovery in settings auto-detection
    - - Wrap find_spec() call in try-except block to catch ModuleNotFoundError and ValueError
    - - Continue iteration when module spec lookup fails instead of crashing
    - - Improve robustness of settings module discovery process
    - ```



### Actualizado: 2026-01-14 01:02:00

- **[bca53b6]** ```
  - *Fecha:* 2026-01-14 01:01:59
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `scripts/import/importar_netherlands.py`
    - `static/js/admin.js`
  - *Detalles:*
    - feat: Add auto-discovery for Django settings module and simplify notification UI logging
    - - Add _discover_settings_module() function to automatically detect Django settings module
    - - Support settings override via CLI argument, DJANGO_SETTINGS_MODULE env var, or common defaults
    - - Scan top-level packages for settings.py to build candidate list
    - - Replace hardcoded "nsc_admin.settings" with dynamic settings_module detection
    - - Remove verbose console.log statement from notification system setup
    - - Ad



### Actualizado: 2026-01-14 00:56:02

- **[c2f84fb]** ```
  - *Fecha:* 2026-01-14 00:56:01
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/accounts/public_home.html`
  - *Detalles:*
    - fix: Normalize quote style in escapejs filtered trans tags from escaped double quotes to single quotes
    - - Change \"...\" to "..." in three trans tag instances within escapejs filters
    - - Affects "Link copied to clipboard", "Tournament / Showcase", and "All Categories" translations
    - - Maintain consistent quote style across template while preserving escapejs filtering
    - ```



### Actualizado: 2026-01-14 00:26:56

- **[f33a483]** importar NL
  - *Fecha:* 2026-01-14 00:26:54
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `scripts/import/importar_netherlands.py`



### Actualizado: 2026-01-13 19:47:28

- **[a142a76]** Fix UnboundLocalError: rename _ variables shadowing gettext in views_private.py
  - *Fecha:* 2026-01-13 19:47:28
  - *Autor:* cgallego17
  - *Archivos modificados:* 14 archivo(s)
    - `apps/accounts/forms.py`
    - `apps/accounts/tests/test_order_creation_flow.py`
    - `apps/accounts/views_private.py`
    - `static/js/admin.js`
    - `templates/accounts/panel_tabs/invoice.html`
    - `templates/accounts/panel_tabs/payment_confirmation.html`
    - `templates/accounts/panel_tabs/registrar_hijo.html`
    - `templates/accounts/panel_usuario.html`
    - `templates/accounts/profile.html`
    - `templates/accounts/public_home.html`
    - ... y 4 archivo(s) más



### Actualizado: 2026-01-13 18:06:44

- **[4488a48]** ```
  - *Fecha:* 2026-01-13 18:06:44
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/accounts/admin/user_admin_detail.html`
  - *Detalles:*
    - fix: Update hijack form parameter from user_id to user_pk for correct user acquisition
    - - Change hidden input field name from user_id to user_pk in hijack form
    - - Align with django-hijack's expected parameter name for user acquisition
    - ```



### Actualizado: 2026-01-13 18:02:32

- **[46ea7d8]** ```
  - *Fecha:* 2026-01-13 18:02:31
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `nsc_admin/settings_simple.py`
    - `templates/accounts/admin/user_admin_detail.html`
  - *Detalles:*
    - fix: Update django-hijack integration to use correct app name and acquire URL pattern
    - - Change hijack_admin to hijack.contrib.admin in THIRD_PARTY_APPS
    - - Update hijack acquire URL from hijack:acquire with pk parameter to hijack:acquire with user_id POST parameter
    - - Add hidden input field for user_id in hijack form submission
    - ```



### Actualizado: 2026-01-13 17:58:56

- **[6c237c7]** ```
  - *Fecha:* 2026-01-13 17:58:55
  - *Autor:* cgallego17
  - *Archivos modificados:* 4 archivo(s)
    - `nsc_admin/settings_simple.py`
    - `nsc_admin/urls.py`
    - `requirements/requirements.txt`
    - `templates/accounts/admin/user_admin_detail.html`
  - *Detalles:*
    - feat: Add django-hijack for user impersonation with superuser-only access control
    - - Add django-hijack and hijack_admin to THIRD_PARTY_APPS in settings_simple.py
    - - Include HijackUserMiddleware in MIDDLEWARE configuration
    - - Configure HIJACK_AUTHORIZE_HANDLER to superusers_only for security
    - - Set HIJACK_ALLOW_GET_REQUESTS to False to require POST requests
    - - Add hijack URLs at /hijack/ path
    - - Include django-hijack>=3.6.0 in requirements.txt
    - - Add "Login as" button to user_admin_detail.html template with



### Actualizado: 2026-01-13 17:46:25

- **[1632913]** ```
  - *Fecha:* 2026-01-13 17:46:25
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `apps/accounts/urls.py`
    - `apps/accounts/views_private.py`
  - *Detalles:*
    - feat: Add player deletion functionality with staff-only access control
    - - Add PlayerDeleteView with UserPassesTestMixin for staff/superuser authorization
    - - Create player_delete URL pattern at players/<int:pk>/delete/
    - - Include DeleteView import from django.views.generic
    - - Set success_url to redirect to player_list after deletion
    - - Add player_confirm_delete.html template reference for deletion confirmation
    - ```



### Actualizado: 2026-01-13 17:40:20

- **[78a3b3e]** ```
  - *Fecha:* 2026-01-13 17:40:19
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `apps/accounts/views_private.py`
    - `templates/accounts/admin/player_admin_detail.html`
  - *Detalles:*
    - feat: Enhance admin player detail view with comprehensive player information and account data
    - - Add profile context with age_as_of_april_30, age_division, grade_division, eligible_divisions, is_eligible, and eligible_message
    - - Include try-except wrapper for player eligibility calculations with fallback to None values
    - - Add notifications context with last 50 notifications including order and event relationships
    - - Add push_subscriptions context ordered by creation date
    - - Add wallet context with User



### Actualizado: 2026-01-13 17:34:33

- **[e291e30]** ```
  - *Fecha:* 2026-01-13 17:34:33
  - *Autor:* cgallego17
  - *Archivos modificados:* 2 archivo(s)
    - `.github/workflows/ci.yml`
    - `apps/accounts/views_private.py`
  - *Detalles:*
    - fix: Convert querysets to lists in admin player detail view for database compatibility
    - - Wrap Order querysets with list() for related_orders, related_payment_plan_orders, and related_active_payment_plan_orders
    - - Wrap StripeEventCheckout querysets with list() for related_checkouts, related_plan_checkouts, and related_active_plan_checkouts
    - - Ensure querysets evaluated before fallback logic to prevent lazy evaluation issues
    - - Remove Python 3.8 and 3.9 from CI test matrix, keeping 3.10, 3.11, and 3



### Actualizado: 2026-01-13 17:30:50

- **[51b2404]** ```
  - *Fecha:* 2026-01-13 17:30:50
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `apps/accounts/views_private.py`
  - *Detalles:*
    - fix: Add database compatibility fallback for JSONField contains queries in admin player detail view
    - - Wrap Order queries with try-except to catch NotSupportedError for registered_player_ids__contains lookups
    - - Add fallback logic fetching last 1000 orders and filtering in Python when JSONField queries unsupported
    - - Wrap StripeEventCheckout queries with try-except for player_ids__contains lookups
    - - Add fallback logic fetching last 1000 checkouts and filtering in Python
    - - Import NotSupportedError from django.



### Actualizado: 2026-01-13 17:25:28

- **[a5dbbce]** ```
  - *Fecha:* 2026-01-13 17:25:27
  - *Autor:* cgallego17
  - *Archivos modificados:* 5 archivo(s)
    - `apps/accounts/urls.py`
    - `apps/accounts/views_private.py`
    - `requirements/requirements.txt`
    - `templates/accounts/admin/player_admin_detail.html`
    - `templates/accounts/player_list.html`
  - *Detalles:*
    - feat: Add admin player detail view with comprehensive related data aggregation
    - - Add AdminPlayerDetailView with player_obj context for detailed player information
    - - Create admin_player_detail URL pattern at players/<int:pk>/admin-detail/
    - - Aggregate parent relations with user profile data ordered by creation date
    - - Include related orders with event, stripe checkout, and user relationships limited to last 50
    - - Display payment plan orders filtered by payment_mode="plan"
    - - Show active payment plan orders with



### Actualizado: 2026-01-13 17:13:52

- **[7285d72]** ```
  - *Fecha:* 2026-01-13 17:13:52
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `requirements/requirements.txt`
  - *Detalles:*
    - fix: Downgrade Django version requirement from 6.x to 5.2.x for compatibility
    - - Change Django version constraint from >=6.0,<7.0 to >=5.2,<6.0
    - - Maintain compatibility with stable Django 5.2 LTS release
    - ```



### Actualizado: 2026-01-13 17:04:01

- **[ef585b1]** ```
  - *Fecha:* 2026-01-13 17:04:00
  - *Autor:* cgallego17
  - *Archivos modificados:* 1 archivo(s)
    - `templates/accounts/admin/user_admin_detail.html`
  - *Detalles:*
    - style: Improve tab navigation styling in admin user detail view
    - - Add color #212529 for default nav-link state
    - - Add hover color #0b5ed7 for better visual feedback
    - - Style active tab with white background and bottom border removal
    - - Add font-weight 600 to active tab for emphasis
    - - Set consistent border-bottom-color #dee2e6 for nav-tabs
    - ```



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
