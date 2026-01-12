# Vue.js Implementation for Event Detail Page

Esta es la implementación Vue.js que reemplaza el JavaScript vanilla para la página de detalle de eventos (`/accounts/events/<pk>/`).

## Estructura

```
static/js/vue/
├── event-detail.js    # Componentes Vue y lógica principal
└── README.md          # Esta documentación
```

## Características

### Componentes Vue

1. **EventDetailApp** - Componente principal que orquesta toda la aplicación
2. **RoomSelectionModal** - Modal para selección de habitaciones
3. **GuestDetailsModal** - Modal para agregar detalles de huéspedes
4. **ToastComponent** - Sistema de notificaciones toast

### Servicios/Composables

1. **useHotelReservation** - Maneja la selección de habitaciones y asignación de huéspedes
2. **usePriceCalculation** - Calcula precios basado en habitaciones y huéspedes
3. **useToast** - Sistema de notificaciones

## Uso

### 1. Incluir Vue.js en el template

```html
<!-- En detalle_evento.html, reemplazar la sección de modales -->
{% include 'accounts/panel_tabs/detalle_evento_vue.html' %}
```

### 2. Estructura de datos requerida

El template debe proporcionar datos JSON de habitaciones:

```html
<script id="rooms-data" type="application/json">
[
    {
        "id": 1,
        "name": "Standard Room",
        "description": "Comfortable room with basic amenities",
        "capacity": 4,
        "price_per_night": 100.00,
        "price_includes_guests": 2,
        "additional_guest_price": 25.00,
        "amenities": ["WiFi", "TV", "AC"],
        "images": [
            {"url": "/media/room1.jpg", "alt": "Room image"}
        ]
    }
]
</script>
```

### 3. Inicialización

La aplicación Vue se inicializa automáticamente cuando se carga el script. Asegúrate de tener un contenedor:

```html
<div id="event-detail-app" data-hotel-pk="{{ event.hotel.pk }}"></div>
```

## Migración desde JavaScript vanilla

### Antes (JavaScript vanilla):
```javascript
window.NSC_HotelReservation.selectRoom(buttonElement);
```

### Después (Vue.js):
```javascript
// La lógica está encapsulada en el componente Vue
// Se accede a través de eventos y props
```

## Ventajas de Vue.js

1. **Organización**: Código más limpio y modular
2. **Reactividad**: Actualizaciones automáticas del DOM
3. **Mantenibilidad**: Separación clara de responsabilidades
4. **Reutilización**: Componentes reutilizables
5. **Type Safety**: Mejor con TypeScript (opcional)

## Próximos pasos

1. Migrar más funcionalidades a Vue.js
2. Agregar tests unitarios
3. Considerar TypeScript para type safety
4. Optimizar bundle size con tree-shaking

## Compatibilidad

- Vue.js 3.x
- Navegadores modernos (ES6+)
- Requiere Bootstrap 5 para estilos de modales

