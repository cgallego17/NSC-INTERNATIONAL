# Lista Completa de URLs del Backend - NCS International

## 📋 Índice
- [URLs Principales (Root)](#urls-principales-root)
- [Accounts (accounts/)](#accounts-accounts)
- [Events (events/)](#events-events)
- [Locations (locations/)](#locations-locations)
- [Media (files/)](#media-files)

---

## URLs Principales (Root)

| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/` | `home` | Home público | ❌ | ❌ |
| `/admin/` | - | Django Admin | ✅ | ✅ |
| `/admin/login/` | `admin_login` | Login admin | ❌ | ❌ |
| `/dashboard/` | `dashboard` | Dashboard principal | ✅ | ✅ |
| `/panel/` | `panel` | Panel de usuario | ✅ | ❌ |
| `/teams/` | `public_team_list` | Lista pública de equipos | ❌ | ❌ |
| `/players/` | `public_player_list` | Lista pública de jugadores | ❌ | ❌ |
| `/players/<int:pk>/` | `public_player_profile_pk` | Perfil público jugador (PK) | ❌ | ❌ |
| `/players/<slug:slug>/` | `public_player_profile` | Perfil público jugador (slug) | ❌ | ❌ |
| `/i18n/setlang/` | `set_language` | Cambio de idioma | ❌ | ❌ |
| `/jsi18n/` | `javascript-catalog` | Catálogo JS i18n | ❌ | ❌ |

---

## Accounts (accounts/)

### URLs Públicas
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/login/` | `accounts:login` | Login público | ❌ | ❌ |
| `/accounts/register/` | `accounts:register` | Registro público | ❌ | ❌ |
| `/accounts/players/<int:pk>/` | `accounts:front_player_profile` | Perfil jugador (front) | ✅ | ❌ |
| `/accounts/api/instagram/posts/` | `accounts:instagram_posts_api` | API Instagram posts | ❌ | ❌ |
| `/accounts/api/instagram/image-proxy/` | `accounts:instagram_image_proxy` | Proxy imágenes Instagram | ❌ | ❌ |

### URLs Privadas (Requieren Login)
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/logout/` | `accounts:logout` | Logout | ✅ | ❌ |
| `/accounts/user-dashboard/` | `accounts:user_dashboard` | Dashboard usuario | ✅ | ❌ |
| `/accounts/profile/` | `accounts:profile` | Perfil usuario | ✅ | ❌ |
| `/accounts/profile/edit/` | `accounts:profile_edit` | Editar perfil | ✅ | ❌ |
| `/accounts/profile/user-edit/` | `accounts:user_edit` | Editar info usuario | ✅ | ❌ |

### Equipos (Teams)
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/teams/` | `accounts:team_list` | Lista de equipos | ✅ | ❌ |
| `/accounts/teams/<int:pk>/` | `accounts:team_detail` | Detalle equipo | ✅ | ❌ |
| `/accounts/teams/create/` | `accounts:team_create` | Crear equipo | ✅ | ❌ |
| `/accounts/teams/<int:pk>/edit/` | `accounts:team_edit` | Editar equipo | ✅ | ❌ |

### Jugadores (Players) - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/players/manage/` | `accounts:player_list` | Lista de jugadores | ✅ | ✅ |
| `/accounts/players/<int:pk>/` | `accounts:player_detail` | Detalle jugador | ✅ | ✅ |
| `/accounts/players/register/` | `accounts:player_register` | Registrar jugador | ✅ | ✅ |
| `/accounts/players/<int:pk>/edit/` | `accounts:player_edit` | Editar jugador | ✅ | ✅ |
| `/accounts/players/<int:pk>/approve-verification/` | `accounts:approve_age_verification` | Aprobar verificación edad | ✅ | ✅ |
| `/accounts/players/<int:player_id>/age-verification-document/` | `accounts:serve_age_verification_document` | Servir documento verificación | ✅ | ✅ |
| `/accounts/players/register-child/` | `accounts:parent_player_register` | Registrar hijo (padre) | ✅ | ❌ |

### Verificaciones de Edad
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/age-verifications/` | `accounts:age_verification_list` | Lista verificaciones | ✅ | ✅/Manager |

### Eventos en Panel
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/events/<int:pk>/` | `accounts:panel_event_detail` | Detalle evento panel | ✅ | ❌ |
| `/accounts/events/<int:pk>/register/` | `accounts:register_children_to_event` | Registrar hijos a evento | ✅ | ❌ |
| `/accounts/panel-tabs/eventos/` | `accounts:panel_eventos_embed` | Embed eventos | ✅ | ❌ |
| `/accounts/panel-tabs/events/<int:pk>/` | `accounts:panel_event_detail_embed` | Embed detalle evento | ✅ | ❌ |

### Stripe/Pagos
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/events/<int:pk>/stripe/create-checkout-session/` | `accounts:create_stripe_event_checkout_session` | Crear sesión Stripe | ✅ | ❌ |
| `/accounts/events/<int:pk>/stripe/success/` | `accounts:stripe_event_checkout_success` | Éxito Stripe | ✅ | ❌ |
| `/accounts/events/<int:pk>/stripe/cancel/` | `accounts:stripe_event_checkout_cancel` | Cancelar Stripe | ✅ | ❌ |
| `/accounts/stripe/webhook/` | `accounts:stripe_webhook` | Webhook Stripe | ❌ | ❌ |
| `/accounts/stripe/invoice/<int:pk>/` | `accounts:stripe_invoice` | Ver factura | ✅ | ❌ |
| `/accounts/payment/confirmation/<int:pk>/` | `accounts:payment_confirmation` | Confirmación pago | ✅ | ❌ |
| `/accounts/wallet/add-funds/` | `accounts:wallet_add_funds` | Agregar fondos wallet | ✅ | ❌ |

### Usuarios - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/users/` | `accounts:user_list` | Lista de usuarios | ✅ | ✅ |

### Banners del Home - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/banners/` | `accounts:banner_list` | Lista banners | ✅ | ✅ |
| `/accounts/banners/create/` | `accounts:banner_create` | Crear banner | ✅ | ✅ |
| `/accounts/banners/<int:pk>/` | `accounts:banner_detail` | Detalle banner | ✅ | ✅ |
| `/accounts/banners/<int:pk>/edit/` | `accounts:banner_update` | Editar banner | ✅ | ✅ |
| `/accounts/banners/<int:pk>/delete/` | `accounts:banner_delete` | Eliminar banner | ✅ | ✅ |

### Configuración del Sitio - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/edit-site-settings/` | `accounts:edit_site_settings_redirect` | Redirect settings | ✅ | ✅ |
| `/accounts/edit-schedule-settings/` | `accounts:edit_schedule_settings` | Editar schedule | ✅ | ✅ |
| `/accounts/edit-showcase-settings/` | `accounts:edit_showcase_settings` | Editar showcase | ✅ | ✅ |
| `/accounts/edit-contact-settings/` | `accounts:edit_contact_settings` | Editar contacto | ✅ | ✅ |
| `/accounts/home-content/` | `accounts:home_content_admin` | Admin contenido home | ✅ | ✅ |

### Sponsors - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/sponsors/` | `accounts:sponsor_list` | Lista sponsors | ✅ | ✅ |
| `/accounts/sponsors/create/` | `accounts:sponsor_create` | Crear sponsor | ✅ | ✅ |
| `/accounts/sponsors/<int:pk>/` | `accounts:sponsor_detail` | Detalle sponsor | ✅ | ✅ |
| `/accounts/sponsors/<int:pk>/edit/` | `accounts:sponsor_update` | Editar sponsor | ✅ | ✅ |
| `/accounts/sponsors/<int:pk>/delete/` | `accounts:sponsor_delete` | Eliminar sponsor | ✅ | ✅ |

### Banners del Dashboard - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/dashboard-banners/` | `accounts:dashboard_banner_list` | Lista banners dashboard | ✅ | ✅ |
| `/accounts/dashboard-banners/create/` | `accounts:dashboard_banner_create` | Crear banner dashboard | ✅ | ✅ |
| `/accounts/dashboard-banners/<int:pk>/` | `accounts:dashboard_banner_detail` | Detalle banner dashboard | ✅ | ✅ |
| `/accounts/dashboard-banners/<int:pk>/edit/` | `accounts:dashboard_banner_update` | Editar banner dashboard | ✅ | ✅ |
| `/accounts/dashboard-banners/<int:pk>/delete/` | `accounts:dashboard_banner_delete` | Eliminar banner dashboard | ✅ | ✅ |

### Gestión de Hoteles - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/accounts/hotels/` | `accounts:hotel_list` | Lista hoteles | ✅ | ✅ |
| `/accounts/hotels/create/` | `accounts:hotel_create` | Crear hotel | ✅ | ✅ |
| `/accounts/hotels/<int:pk>/` | `accounts:hotel_detail` | Detalle hotel | ✅ | ✅ |
| `/accounts/hotels/<int:pk>/edit/` | `accounts:hotel_update` | Editar hotel | ✅ | ✅ |
| `/accounts/hotels/<int:pk>/delete/` | `accounts:hotel_delete` | Eliminar hotel | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/images/` | `accounts:hotel_image_list` | Lista imágenes hotel | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/images/create/` | `accounts:hotel_image_create` | Crear imagen hotel | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/images/<int:pk>/edit/` | `accounts:hotel_image_update` | Editar imagen hotel | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/images/<int:pk>/delete/` | `accounts:hotel_image_delete` | Eliminar imagen hotel | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/amenities/` | `accounts:hotel_amenity_list` | Lista amenidades | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/amenities/create/` | `accounts:hotel_amenity_create` | Crear amenidad | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/amenities/<int:pk>/edit/` | `accounts:hotel_amenity_update` | Editar amenidad | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/amenities/<int:pk>/delete/` | `accounts:hotel_amenity_delete` | Eliminar amenidad | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/rooms/` | `accounts:hotel_room_list` | Lista habitaciones | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/rooms/create/` | `accounts:hotel_room_create` | Crear habitación | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/rooms/<int:pk>/edit/` | `accounts:hotel_room_update` | Editar habitación | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/rooms/<int:pk>/delete/` | `accounts:hotel_room_delete` | Eliminar habitación | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/services/` | `accounts:hotel_service_list` | Lista servicios | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/services/create/` | `accounts:hotel_service_create` | Crear servicio | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/services/<int:pk>/edit/` | `accounts:hotel_service_update` | Editar servicio | ✅ | ✅ |
| `/accounts/hotels/<int:hotel_pk>/services/<int:pk>/delete/` | `accounts:hotel_service_delete` | Eliminar servicio | ✅ | ✅ |

---

## Events (events/)

### URLs Públicas
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/events/` | `events:public_list` | Lista pública eventos | ❌ | ❌ |
| `/events/<int:pk>/` | `events:public_detail` | Detalle público evento | ❌ | ❌ |

### URLs Admin - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/events/dashboard/` | `events:dashboard` | Dashboard eventos | ✅ | ✅ |
| `/events/list/` | `events:list` | Lista admin eventos | ✅ | ✅ |
| `/events/create/` | `events:create` | Crear evento | ✅ | ✅ |
| `/events/admin/<int:pk>/` | `events:admin_detail` | Detalle admin evento | ✅ | ✅ |
| `/events/<int:pk>/edit/` | `events:update` | Editar evento | ✅ | ✅ |
| `/events/<int:pk>/delete/` | `events:delete` | Eliminar evento | ✅ | ✅ |
| `/events/<int:pk>/toggle-publish/` | `events:toggle_publish` | Publicar/despublicar | ✅ | ✅ |
| `/events/calendar/` | `events:calendar` | Calendario eventos | ✅ | ✅ |
| `/events/<int:event_id>/attend/` | `events:attend` | Asistir a evento | ✅ | ❌ |
| `/events/api/detail/<int:pk>/` | `events:api_detail` | API detalle evento | ✅ | ✅ |

### Divisiones - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/events/divisions/` | `events:division_list` | Lista divisiones | ✅ | ✅ |
| `/events/divisions/create/` | `events:division_create` | Crear división | ✅ | ✅ |
| `/events/divisions/<int:pk>/` | `events:division_detail` | Detalle división | ✅ | ✅ |
| `/events/divisions/<int:pk>/edit/` | `events:division_update` | Editar división | ✅ | ✅ |
| `/events/divisions/<int:pk>/delete/` | `events:division_delete` | Eliminar división | ✅ | ✅ |

### Contactos de Eventos - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/events/event-contacts/` | `events:eventcontact_list` | Lista contactos | ✅ | ✅ |
| `/events/event-contacts/create/` | `events:eventcontact_create` | Crear contacto | ✅ | ✅ |
| `/events/event-contacts/<int:pk>/` | `events:eventcontact_detail` | Detalle contacto | ✅ | ✅ |
| `/events/event-contacts/<int:pk>/edit/` | `events:eventcontact_update` | Editar contacto | ✅ | ✅ |
| `/events/event-contacts/<int:pk>/delete/` | `events:eventcontact_delete` | Eliminar contacto | ✅ | ✅ |

### Tipos de Evento - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/events/event-types/` | `events:eventtype_list` | Lista tipos evento | ✅ | ✅ |
| `/events/event-types/create/` | `events:eventtype_create` | Crear tipo evento | ✅ | ✅ |
| `/events/event-types/<int:pk>/` | `events:eventtype_detail` | Detalle tipo evento | ✅ | ✅ |
| `/events/event-types/<int:pk>/edit/` | `events:eventtype_update` | Editar tipo evento | ✅ | ✅ |
| `/events/event-types/<int:pk>/delete/` | `events:eventtype_delete` | Eliminar tipo evento | ✅ | ✅ |

### Tipos de Gate Fee - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/events/gate-fee-types/` | `events:gatefeetype_list` | Lista gate fee types | ✅ | ✅ |
| `/events/gate-fee-types/create/` | `events:gatefeetype_create` | Crear gate fee type | ✅ | ✅ |
| `/events/gate-fee-types/<int:pk>/` | `events:gatefeetype_detail` | Detalle gate fee type | ✅ | ✅ |
| `/events/gate-fee-types/<int:pk>/edit/` | `events:gatefeetype_update` | Editar gate fee type | ✅ | ✅ |
| `/events/gate-fee-types/<int:pk>/delete/` | `events:gatefeetype_delete` | Eliminar gate fee type | ✅ | ✅ |

---

## Locations (locations/)

### URLs Admin - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/locations/countries/` | `locations:country_list` | Lista países | ✅ | ✅ |
| `/locations/countries/<int:pk>/` | `locations:country_detail` | Detalle país | ✅ | ✅ |
| `/locations/countries/create/` | `locations:country_create` | Crear país | ✅ | ✅ |
| `/locations/countries/<int:pk>/edit/` | `locations:country_update` | Editar país | ✅ | ✅ |
| `/locations/countries/<int:pk>/delete/` | `locations:country_delete` | Eliminar país | ✅ | ✅ |
| `/locations/states/` | `locations:state_list` | Lista estados | ✅ | ✅ |
| `/locations/states/<int:pk>/` | `locations:state_detail` | Detalle estado | ✅ | ✅ |
| `/locations/states/create/` | `locations:state_create` | Crear estado | ✅ | ✅ |
| `/locations/states/<int:pk>/edit/` | `locations:state_update` | Editar estado | ✅ | ✅ |
| `/locations/states/<int:pk>/delete/` | `locations:state_delete` | Eliminar estado | ✅ | ✅ |
| `/locations/cities/` | `locations:city_list` | Lista ciudades | ✅ | ✅ |
| `/locations/cities/<int:pk>/` | `locations:city_detail` | Detalle ciudad | ✅ | ✅ |
| `/locations/cities/create/` | `locations:city_create` | Crear ciudad | ✅ | ✅ |
| `/locations/cities/<int:pk>/edit/` | `locations:city_update` | Editar ciudad | ✅ | ✅ |
| `/locations/cities/<int:pk>/delete/` | `locations:city_delete` | Eliminar ciudad | ✅ | ✅ |
| `/locations/seasons/` | `locations:season_list` | Lista temporadas | ✅ | ✅ |
| `/locations/seasons/<int:pk>/` | `locations:season_detail` | Detalle temporada | ✅ | ✅ |
| `/locations/seasons/create/` | `locations:season_create` | Crear temporada | ✅ | ✅ |
| `/locations/seasons/<int:pk>/edit/` | `locations:season_update` | Editar temporada | ✅ | ✅ |
| `/locations/seasons/<int:pk>/delete/` | `locations:season_delete` | Eliminar temporada | ✅ | ✅ |
| `/locations/rules/` | `locations:rule_list` | Lista reglas | ✅ | ✅ |
| `/locations/rules/<int:pk>/` | `locations:rule_detail` | Detalle regla | ✅ | ✅ |
| `/locations/rules/create/` | `locations:rule_create` | Crear regla | ✅ | ✅ |
| `/locations/rules/<int:pk>/edit/` | `locations:rule_update` | Editar regla | ✅ | ✅ |
| `/locations/rules/<int:pk>/delete/` | `locations:rule_delete` | Eliminar regla | ✅ | ✅ |
| `/locations/sites/` | `locations:site_list` | Lista sitios | ✅ | ✅ |
| `/locations/sites/<int:pk>/` | `locations:site_detail` | Detalle sitio | ✅ | ✅ |
| `/locations/sites/create/` | `locations:site_create` | Crear sitio | ✅ | ✅ |
| `/locations/sites/<int:pk>/edit/` | `locations:site_update` | Editar sitio | ✅ | ✅ |
| `/locations/sites/<int:pk>/delete/` | `locations:site_delete` | Eliminar sitio | ✅ | ✅ |

### URLs Admin (Hoteles) - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/locations/admin/countries/` | `locations:admin_country_list` | Lista admin países | ✅ | ✅ |
| `/locations/admin/countries/<int:pk>/` | `locations:admin_country_detail` | Detalle admin país | ✅ | ✅ |
| `/locations/admin/countries/create/` | `locations:admin_country_create` | Crear admin país | ✅ | ✅ |
| `/locations/admin/countries/<int:pk>/edit/` | `locations:admin_country_update` | Editar admin país | ✅ | ✅ |
| `/locations/admin/countries/<int:pk>/delete/` | `locations:admin_country_delete` | Eliminar admin país | ✅ | ✅ |
| `/locations/admin/states/` | `locations:admin_state_list` | Lista admin estados | ✅ | ✅ |
| `/locations/admin/states/<int:pk>/` | `locations:admin_state_detail` | Detalle admin estado | ✅ | ✅ |
| `/locations/admin/states/create/` | `locations:admin_state_create` | Crear admin estado | ✅ | ✅ |
| `/locations/admin/states/<int:pk>/edit/` | `locations:admin_state_update` | Editar admin estado | ✅ | ✅ |
| `/locations/admin/states/<int:pk>/delete/` | `locations:admin_state_delete` | Eliminar admin estado | ✅ | ✅ |
| `/locations/admin/cities/` | `locations:admin_city_list` | Lista admin ciudades | ✅ | ✅ |
| `/locations/admin/cities/<int:pk>/` | `locations:admin_city_detail` | Detalle admin ciudad | ✅ | ✅ |
| `/locations/admin/cities/create/` | `locations:admin_city_create` | Crear admin ciudad | ✅ | ✅ |
| `/locations/admin/cities/<int:pk>/edit/` | `locations:admin_city_update` | Editar admin ciudad | ✅ | ✅ |
| `/locations/admin/cities/<int:pk>/delete/` | `locations:admin_city_delete` | Eliminar admin ciudad | ✅ | ✅ |
| `/locations/admin/seasons/` | `locations:admin_season_list` | Lista admin temporadas | ✅ | ✅ |
| `/locations/admin/seasons/<int:pk>/` | `locations:admin_season_detail` | Detalle admin temporada | ✅ | ✅ |
| `/locations/admin/seasons/create/` | `locations:admin_season_create` | Crear admin temporada | ✅ | ✅ |
| `/locations/admin/seasons/<int:pk>/edit/` | `locations:admin_season_update` | Editar admin temporada | ✅ | ✅ |
| `/locations/admin/seasons/<int:pk>/delete/` | `locations:admin_season_delete` | Eliminar admin temporada | ✅ | ✅ |
| `/locations/admin/rules/` | `locations:admin_rule_list` | Lista admin reglas | ✅ | ✅ |
| `/locations/admin/rules/<int:pk>/` | `locations:admin_rule_detail` | Detalle admin regla | ✅ | ✅ |
| `/locations/admin/rules/create/` | `locations:admin_rule_create` | Crear admin regla | ✅ | ✅ |
| `/locations/admin/rules/<int:pk>/edit/` | `locations:admin_rule_update` | Editar admin regla | ✅ | ✅ |
| `/locations/admin/rules/<int:pk>/delete/` | `locations:admin_rule_delete` | Eliminar admin regla | ✅ | ✅ |
| `/locations/admin/sites/` | `locations:admin_site_list` | Lista admin sitios | ✅ | ✅ |
| `/locations/admin/sites/<int:pk>/` | `locations:admin_site_detail` | Detalle admin sitio | ✅ | ✅ |
| `/locations/admin/sites/create/` | `locations:admin_site_create` | Crear admin sitio | ✅ | ✅ |
| `/locations/admin/sites/<int:pk>/edit/` | `locations:admin_site_update` | Editar admin sitio | ✅ | ✅ |
| `/locations/admin/sites/<int:pk>/delete/` | `locations:admin_site_delete` | Eliminar admin sitio | ✅ | ✅ |
| `/locations/admin/hotels/` | `locations:admin_hotel_list` | Lista admin hoteles | ✅ | ✅ |
| `/locations/admin/hotels/<int:pk>/` | `locations:admin_hotel_detail` | Detalle admin hotel | ✅ | ✅ |
| `/locations/admin/hotels/create/` | `locations:admin_hotel_create` | Crear admin hotel | ✅ | ✅ |
| `/locations/admin/hotels/<int:pk>/edit/` | `locations:admin_hotel_update` | Editar admin hotel | ✅ | ✅ |
| `/locations/admin/hotels/<int:pk>/delete/` | `locations:admin_hotel_delete` | Eliminar admin hotel | ✅ | ✅ |
| `/locations/admin/hotels/<int:hotel_pk>/images/` | `locations:admin_hotel_image_list` | Lista imágenes hotel | ✅ | ✅ |
| `/locations/admin/hotels/<int:hotel_pk>/images/create/` | `locations:admin_hotel_image_create` | Crear imagen hotel | ✅ | ✅ |
| `/locations/admin/hotels/<int:hotel_pk>/images/<int:pk>/edit/` | `locations:admin_hotel_image_update` | Editar imagen hotel | ✅ | ✅ |
| `/locations/admin/hotels/<int:hotel_pk>/images/<int:pk>/delete/` | `locations:admin_hotel_image_delete` | Eliminar imagen hotel | ✅ | ✅ |
| `/locations/admin/hotels/<int:hotel_pk>/amenities/` | `locations:admin_hotel_amenity_list` | Lista amenidades hotel | ✅ | ✅ |
| `/locations/admin/hotels/<int:hotel_pk>/amenities/create/` | `locations:admin_hotel_amenity_create` | Crear amenidad hotel | ✅ | ✅ |
| `/locations/admin/hotels/<int:hotel_pk>/amenities/<int:pk>/edit/` | `locations:admin_hotel_amenity_update` | Editar amenidad hotel | ✅ | ✅ |
| `/locations/admin/hotels/<int:hotel_pk>/amenities/<int:pk>/delete/` | `locations:admin_hotel_amenity_delete` | Eliminar amenidad hotel | ✅ | ✅ |
| `/locations/admin/hotel-rooms/` | `locations:admin_hotel_room_list` | Lista habitaciones | ✅ | ✅ |
| `/locations/admin/hotel-rooms/create/` | `locations:admin_hotel_room_create` | Crear habitación | ✅ | ✅ |
| `/locations/admin/hotel-rooms/<int:pk>/edit/` | `locations:admin_hotel_room_update` | Editar habitación | ✅ | ✅ |
| `/locations/admin/hotel-rooms/<int:pk>/delete/` | `locations:admin_hotel_room_delete` | Eliminar habitación | ✅ | ✅ |
| `/locations/admin/hotel-rooms/images/<int:pk>/delete/` | `locations:admin_hotel_room_image_delete` | Eliminar imagen habitación | ✅ | ✅ |
| `/locations/admin/hotel-rooms/taxes/create/` | `locations:admin_hotel_room_tax_create_ajax` | Crear impuesto habitación | ✅ | ✅ |
| `/locations/admin/hotel-rooms/<int:room_id>/taxes/<int:tax_id>/delete/` | `locations:admin_hotel_room_tax_delete_ajax` | Eliminar impuesto habitación | ✅ | ✅ |
| `/locations/admin/hotel-services/` | `locations:admin_hotel_service_list` | Lista servicios hotel | ✅ | ✅ |
| `/locations/admin/hotel-services/create/` | `locations:admin_hotel_service_create` | Crear servicio hotel | ✅ | ✅ |
| `/locations/admin/hotel-services/<int:pk>/edit/` | `locations:admin_hotel_service_update` | Editar servicio hotel | ✅ | ✅ |
| `/locations/admin/hotel-services/<int:pk>/delete/` | `locations:admin_hotel_service_delete` | Eliminar servicio hotel | ✅ | ✅ |
| `/locations/admin/hotel-reservations/` | `locations:admin_hotel_reservation_list` | Lista reservas hotel | ✅ | ✅ |
| `/locations/admin/hotel-reservations/<int:pk>/` | `locations:admin_hotel_reservation_detail` | Detalle reserva hotel | ✅ | ✅ |
| `/locations/admin/hotel-reservations/create/` | `locations:admin_hotel_reservation_create` | Crear reserva hotel | ✅ | ✅ |
| `/locations/admin/hotel-reservations/<int:pk>/edit/` | `locations:admin_hotel_reservation_update` | Editar reserva hotel | ✅ | ✅ |
| `/locations/admin/hotel-reservations/<int:pk>/delete/` | `locations:admin_hotel_reservation_delete` | Eliminar reserva hotel | ✅ | ✅ |

### URLs Front (Hoteles) - Requieren Login
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/locations/hotels/` | `locations:front_hotel_list` | Lista hoteles front | ✅ | ❌ |
| `/locations/hotels/<int:pk>/` | `locations:front_hotel_detail` | Detalle hotel front | ✅ | ❌ |
| `/locations/hotels/reservations/` | `locations:front_hotel_reservation_list` | Lista reservas usuario | ✅ | ❌ |
| `/locations/hotels/reservations/create/` | `locations:front_hotel_reservation_create` | Crear reserva | ✅ | ❌ |
| `/locations/hotels/reservations/<int:pk>/` | `locations:front_hotel_reservation_detail` | Detalle reserva | ✅ | ❌ |
| `/locations/hotels/reservations/<int:pk>/checkout/` | `locations:front_hotel_reservation_checkout` | Checkout reserva | ✅ | ❌ |
| `/locations/hotels/cart/` | `locations:hotel_cart` | Carrito hoteles | ✅ | ❌ |
| `/locations/hotels/cart/add/` | `locations:add_to_cart` | Agregar al carrito | ✅ | ❌ |
| `/locations/hotels/cart/remove/` | `locations:remove_from_cart` | Remover del carrito | ✅ | ❌ |
| `/locations/hotels/cart/clear/` | `locations:clear_cart` | Limpiar carrito | ✅ | ❌ |
| `/locations/hotels/cart/checkout/` | `locations:checkout_cart` | Checkout carrito | ✅ | ❌ |

### URLs AJAX Front
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/locations/ajax/hotels/<int:hotel_id>/rooms/` | `locations:get_hotel_rooms` | Obtener habitaciones | ✅ | ❌ |
| `/locations/ajax/hotels/<int:hotel_id>/services/` | `locations:get_hotel_services` | Obtener servicios | ✅ | ❌ |
| `/locations/ajax/reservations/calculate-total/` | `locations:calculate_reservation_total` | Calcular total | ✅ | ❌ |
| `/locations/ajax/rooms/<int:room_id>/detail/` | `locations:get_room_detail` | Detalle habitación | ✅ | ❌ |
| `/locations/ajax/cart/` | `locations:get_cart_json` | Obtener carrito JSON | ✅ | ❌ |

### URLs AJAX Admin
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/locations/ajax/states/<int:country_id>/` | `locations:get_states_by_country` | Estados por país | ✅ | ✅ |
| `/locations/ajax/cities/<int:state_id>/` | `locations:get_cities_by_state` | Ciudades por estado | ✅ | ✅ |

### URLs API Públicas (Sin Autenticación)
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/locations/ajax/states/<int:country_id>/` | `locations:get_states_by_country` | Estados por país (público) | ❌ | ❌ |
| `/locations/ajax/cities/<int:state_id>/` | `locations:get_cities_by_state` | Ciudades por estado (público) | ❌ | ❌ |
| `/locations/api/countries/` | `locations:countries_api` | API países | ❌ | ❌ |
| `/locations/api/states/` | `locations:states_api` | API estados | ❌ | ❌ |
| `/locations/api/cities/` | `locations:cities_api` | API ciudades | ❌ | ❌ |
| `/locations/api/seasons/` | `locations:seasons_api` | API temporadas | ❌ | ❌ |
| `/locations/api/rules/` | `locations:rules_api` | API reglas | ❌ | ❌ |
| `/locations/api/sites/` | `locations:sites_api` | API sitios | ❌ | ❌ |
| `/locations/countries/api/` | `locations:countries_api` | API países (alternativa) | ❌ | ❌ |
| `/locations/states/api/` | `locations:states_api` | API estados (alternativa) | ❌ | ❌ |
| `/locations/cities/api/` | `locations:cities_api` | API ciudades (alternativa) | ❌ | ❌ |
| `/locations/seasons/api/` | `locations:seasons_api` | API temporadas (alternativa) | ❌ | ❌ |
| `/locations/rules/api/` | `locations:rules_api` | API reglas (alternativa) | ❌ | ❌ |
| `/locations/sites/api/` | `locations:sites_api` | API sitios (alternativa) | ❌ | ❌ |
| `/locations/hotels/api/` | `locations:hotels_api` | API hoteles | ❌ | ❌ |

---

## Media (files/)

### URLs - **REQUIERE STAFF**
| URL | Nombre | Descripción | Requiere Auth | Requiere Staff |
|-----|--------|-------------|--------------|----------------|
| `/files/` | `media:list` | Lista archivos multimedia | ✅ | ✅ |
| `/files/create/` | `media:create` | Crear archivo multimedia | ✅ | ✅ |
| `/files/<int:pk>/` | `media:detail` | Detalle archivo multimedia | ✅ | ✅ |
| `/files/<int:pk>/edit/` | `media:update` | Editar archivo multimedia | ✅ | ✅ |
| `/files/<int:pk>/delete/` | `media:delete` | Eliminar archivo multimedia | ✅ | ✅ |
| `/files/upload/` | `media:upload_ajax` | Subir archivo AJAX | ✅ | ✅ |
| `/files/bulk-delete/` | `media:bulk_delete` | Eliminar múltiples archivos | ✅ | ✅ |
| `/files/bulk-update/` | `media:bulk_update` | Actualizar múltiples archivos | ✅ | ✅ |
| `/files/<int:pk>/update-ajax/` | `media:update_ajax` | Actualizar archivo AJAX | ✅ | ✅ |
| `/files/list-ajax/` | `media:list_ajax` | Listar archivos AJAX | ✅ | ✅ |

---

## 🔐 Leyenda

- ✅ = Requiere
- ❌ = No requiere
- ✅/Manager = Requiere staff O manager de equipo

---

## 📝 Notas

1. **URLs marcadas con "REQUIERE STAFF"** ahora están protegidas con `StaffRequiredMixin` en el backend y solo muestran el layout admin si el usuario es staff.

2. **URLs públicas** (sin autenticación) están disponibles para todos los usuarios.

3. **URLs front** (hoteles, reservas) requieren login pero no requieren staff.

4. **APIs públicas** están disponibles sin autenticación para uso en formularios de registro, etc.

5. Todas las URLs de **Events**, **Locations** (admin), **Media** y **Players** ahora requieren staff.

---

**Última actualización:** 2026-01-07
**Total de URLs documentadas:** ~200+



