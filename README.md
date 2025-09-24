# NSC Admin Dashboard - Django

Un dashboard administrativo moderno y modular desarrollado con Django para NSC International.

## 🚀 Características

### ✨ Diseño Moderno
- **Interfaz limpia y profesional** con diseño Material Design
- **Tema oscuro/claro** con persistencia de preferencias
- **Sidebar colapsible** para optimizar el espacio
- **Diseño completamente responsivo** para todos los dispositivos

### 🏗️ Arquitectura Modular
- **Aplicaciones separadas** para cada funcionalidad
- **Modelos bien estructurados** con relaciones apropiadas
- **Vistas basadas en clases** para mejor organización
- **Sistema de permisos** integrado con Django

### 📊 Dashboard Principal
- **Métricas clave** en tiempo real (Ventas, Órdenes, Clientes, Reembolsos)
- **Gráficos interactivos** usando Chart.js
- **Tablas de datos** con información de productos e inventario
- **Gestión de órdenes** con estados y acciones

### 🎛️ Funcionalidades Interactivas
- **Navegación sidebar** con menús desplegables
- **Panel de notificaciones** deslizable
- **Menú de usuario** con opciones de perfil
- **Búsqueda global** en tiempo real
- **Toggle de tema** con persistencia

### 📱 Responsive Design
- **Mobile-first** approach
- **Breakpoints optimizados** para tablets y móviles
- **Menú hamburguesa** para dispositivos móviles
- **Tablas responsivas** con scroll horizontal

## 🛠️ Tecnologías Utilizadas

- **Django 4.2.7** - Framework web principal
- **Python 3.8+** - Lenguaje de programación
- **Bootstrap 5.3** - Framework CSS
- **Chart.js** - Gráficos y visualizaciones
- **Font Awesome** - Iconografía
- **SQLite/PostgreSQL** - Base de datos
- **WhiteNoise** - Servir archivos estáticos

## 📁 Estructura del Proyecto

```
nsc_admin/
├── manage.py
├── requirements.txt
├── env.example
├── nsc_admin/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── admin.py
│   │   └── urls.py
│   ├── dashboard/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── admin.py
│   │   └── urls.py
│   ├── products/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── admin.py
│   │   └── urls.py
│   ├── orders/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── admin.py
│   │   └── urls.py
│   ├── customers/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── admin.py
│   │   └── urls.py
│   └── users/
│       ├── models.py
│       ├── views.py
│       ├── admin.py
│       └── urls.py
├── templates/
│   ├── base.html
│   ├── dashboard/
│   ├── users/
│   └── ...
└── static/
    ├── css/
    │   └── admin.css
    └── js/
        └── admin.js
```

## 🚀 Instalación y Configuración

### Opción 1: Instalación Rápida (Recomendada)
```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Ejecutar configuración automática
python quick_setup.py
```

### Opción 2: Instalación Manual
```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias básicas
pip install -r requirements_basic.txt

# 3. Crear directorios necesarios
mkdir -p logs media/products media/categories media/customers/avatars media/users/avatars staticfiles

# 4. Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Recopilar archivos estáticos
python manage.py collectstatic --noinput

# 7. Ejecutar servidor
python manage.py runserver
```

### Opción 3: Instalación Completa (Con todas las dependencias)
```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate

# 2. Instalar todas las dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# 4. Ejecutar configuración automática
python setup.py
```

## 🔧 Configuración de Producción

### Variables de Entorno
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Base de datos PostgreSQL
DB_NAME=nsc_admin
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Configuración de Base de Datos
El proyecto está configurado para usar SQLite en desarrollo y PostgreSQL en producción.

### Archivos Estáticos
```bash
python manage.py collectstatic
```

## 📊 Aplicaciones Incluidas

### 🏠 Core
- Configuraciones del sitio
- Sistema de notificaciones
- Registro de actividades
- Context processors

### 📈 Dashboard
- Métricas principales
- Widgets personalizables
- Gráficos interactivos
- Datos en tiempo real

### 📦 Products
- Gestión de productos
- Categorías
- Inventario
- Reseñas de productos

### 🛒 Orders
- Gestión de órdenes
- Estados de órdenes
- Historial de cambios
- Facturación

### 👥 Customers
- Gestión de clientes
- Direcciones múltiples
- Notas internas
- Historial de compras

### 👤 Users
- Perfiles de usuario
- Gestión de permisos
- Autenticación
- Cambio de contraseñas

## 🎨 Personalización

### Temas
El dashboard incluye un sistema de temas completo:
- **Tema claro** (por defecto)
- **Tema oscuro** con persistencia
- **Variables CSS** para fácil personalización

### Colores
Los colores principales se pueden modificar en las variables CSS:
```css
:root {
    --primary-color: #6675ed;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
}
```

## 🔐 Seguridad

- **Autenticación** requerida para todas las vistas
- **CSRF protection** habilitado
- **Validación de datos** en formularios
- **Sanitización** de inputs
- **Configuración segura** para producción

## 📱 API Endpoints

### Dashboard
- `GET /dashboard/` - Vista principal del dashboard
- `GET /dashboard/data/` - Datos para gráficos (AJAX)

### Productos
- `GET /products/` - Lista de productos
- `POST /products/create/` - Crear producto
- `GET /products/<slug>/` - Detalle de producto
- `PUT /products/<slug>/edit/` - Editar producto

### Órdenes
- `GET /orders/` - Lista de órdenes
- `POST /orders/create/` - Crear orden
- `GET /orders/<id>/` - Detalle de orden
- `PUT /orders/<id>/status/` - Cambiar estado

### Clientes
- `GET /customers/` - Lista de clientes
- `POST /customers/create/` - Crear cliente
- `GET /customers/<id>/` - Detalle de cliente

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Tests con cobertura
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📈 Monitoreo y Logs

El proyecto incluye configuración de logging:
- **Archivo de logs** en `logs/django.log`
- **Console logging** para desarrollo
- **Log levels** configurables

## 🚀 Despliegue

### Heroku
```bash
# Crear Procfile
echo "web: gunicorn nsc_admin.wsgi" > Procfile

# Desplegar
git push heroku main
```

### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "nsc_admin.wsgi"]
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Desarrollado por

**NSC International** - Dashboard administrativo moderno y funcional.

## 📞 Soporte

Para soporte técnico o preguntas:
- **Email**: support@nscinternational.com
- **Documentación**: [Wiki del proyecto]
- **Issues**: [GitHub Issues]

---

*Dashboard administrativo desarrollado con Django para NSC International*