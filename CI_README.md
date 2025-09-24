# CI/CD Pipeline - NSC Admin Dashboard

Este proyecto incluye una configuración completa de CI/CD usando GitHub Actions para verificar la calidad del código, ejecutar pruebas y desplegar la aplicación.

## 🚀 Características del Pipeline

### Verificaciones de Código
- **Formateo de código**: Black para formateo automático
- **Ordenamiento de imports**: isort para organizar imports
- **Linting**: flake8 para detectar errores de código
- **Seguridad**: Bandit para detectar vulnerabilidades de seguridad
- **Dependencias**: Safety para verificar vulnerabilidades en dependencias

### Pruebas
- **Pruebas unitarias**: Django TestCase
- **Pruebas de integración**: Pruebas de vistas y modelos
- **Cobertura de código**: Coverage con reportes HTML y XML
- **Múltiples versiones de Python**: 3.8, 3.9, 3.10, 3.11, 3.12

### Validaciones de Django
- **Verificación de configuración**: `python manage.py check --deploy`
- **Validación de migraciones**: `python manage.py makemigrations --check --dry-run`
- **Recopilación de archivos estáticos**: `python manage.py collectstatic`

## 📁 Archivos de Configuración

### `.github/workflows/ci.yml`
Workflow principal de GitHub Actions que ejecuta:
1. **Test Job**: Verificaciones de código y pruebas
2. **Build Job**: Construcción de la aplicación (solo en main)
3. **Deploy Job**: Despliegue a producción (solo en main)

### `pyproject.toml`
Configuración para herramientas de Python:
- Black (formateo)
- isort (ordenamiento de imports)
- Bandit (seguridad)
- Coverage (cobertura de código)

### `.flake8`
Configuración de flake8 para linting:
- Longitud máxima de línea: 127 caracteres
- Complejidad máxima: 10
- Exclusiones para migraciones y archivos estáticos

### `pytest.ini`
Configuración de pytest para pruebas:
- Cobertura mínima: 80%
- Reportes en HTML, XML y terminal
- Marcadores para diferentes tipos de pruebas

### `.pre-commit-config.yaml`
Hooks de pre-commit para verificación local:
- Formateo automático con Black
- Ordenamiento de imports con isort
- Linting con flake8
- Verificaciones de seguridad con Bandit
- Verificaciones de Django

## 🛠️ Uso Local

### Instalación de dependencias de desarrollo
```bash
pip install -r requirements-dev.txt
```

### Instalación de pre-commit hooks
```bash
pre-commit install
```

### Ejecución de verificaciones manuales
```bash
# Formateo de código
black .

# Ordenamiento de imports
isort .

# Linting
flake8 .

# Verificaciones de seguridad
bandit -r .

# Verificación de dependencias
safety check

# Pruebas con cobertura
pytest --cov=.
```

### Verificaciones de Django
```bash
# Verificación de configuración
python manage.py check --deploy

# Verificación de migraciones
python manage.py makemigrations --check --dry-run

# Ejecución de pruebas
python manage.py test
```

## 📊 Reportes

### Cobertura de Código
- **Terminal**: Muestra cobertura en la consola
- **HTML**: Genera reporte en `htmlcov/index.html`
- **XML**: Genera `coverage.xml` para integración con CI

### Reportes de Seguridad
- **Bandit**: Reporte JSON en `bandit-report.json`
- **Safety**: Reporte JSON en `safety-report.json`

## 🔧 Configuración de GitHub Secrets

Para el despliegue, configura los siguientes secrets en GitHub:

- `DJANGO_SECRET_KEY`: Clave secreta de Django para producción
- `ALLOWED_HOSTS`: Hosts permitidos para producción

## 📈 Mejores Prácticas

1. **Commits pequeños**: Hacer commits frecuentes y pequeños
2. **Pre-commit hooks**: Usar pre-commit para verificar código antes de commit
3. **Cobertura de pruebas**: Mantener cobertura mínima del 80%
4. **Revisión de código**: Revisar todos los pull requests
5. **Seguridad**: Revisar reportes de seguridad regularmente

## 🚨 Solución de Problemas

### Error de formateo
```bash
black . --check --diff
```

### Error de imports
```bash
isort . --check-only --diff
```

### Error de linting
```bash
flake8 . --show-source --statistics
```

### Error de pruebas
```bash
python manage.py test --verbosity=2
```

## 📝 Notas Adicionales

- El pipeline se ejecuta en cada push y pull request
- Los reportes de seguridad se suben como artefactos
- La cobertura se reporta a Codecov automáticamente
- El despliegue solo ocurre en la rama `main`
