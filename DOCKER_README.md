# Docker Configuration for NSC International

This document explains how to use Docker with the NSC International Django application.

## Files Overview

- `Dockerfile` - Production-ready Docker image
- `Dockerfile.dev` - Development Docker image
- `docker-compose.yml` - Development environment
- `docker-compose.prod.yml` - Production environment
- `.dockerignore` - Files to exclude from Docker build context
- `nginx.conf` - Nginx configuration for development
- `nginx.prod.conf` - Nginx configuration for production
- `nsc_admin/settings_prod.py` - Production Django settings

## Quick Start

### Development Environment

1. **Start the development environment:**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create a superuser:**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Access the application:**
   - Web application: http://localhost:8000
   - Admin interface: http://localhost:8000/admin/

### Production Environment

1. **Copy environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your production values
   ```

2. **Start the production environment:**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

3. **Run migrations:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
   ```

4. **Create a superuser:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
   ```

## Services

### Development (`docker-compose.yml`)

- **web**: Django application (development server)
- **db**: PostgreSQL database
- **nginx**: Reverse proxy (optional for development)

### Production (`docker-compose.prod.yml`)

- **web**: Django application (Gunicorn)
- **db**: PostgreSQL database
- **nginx**: Reverse proxy with SSL support

## Environment Variables

Create a `.env` file based on `env.example`:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database Settings
POSTGRES_DB=nsc_international
POSTGRES_USER=nsc_user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## SSL Configuration (Production)

For production with SSL:

1. **Create SSL directory:**
   ```bash
   mkdir ssl
   ```

2. **Add your SSL certificates:**
   - `ssl/cert.pem` - SSL certificate
   - `ssl/key.pem` - SSL private key

3. **Update nginx.prod.conf** if needed for your domain

## Docker Commands

### Build Images

```bash
# Build production image
docker build -t nsc-international:latest .

# Build development image
docker build -f Dockerfile.dev -t nsc-international:dev .
```

### Run Containers

```bash
# Run production container
docker run -d -p 8000:8000 --env-file .env nsc-international:latest

# Run development container
docker run -d -p 8000:8000 --env-file .env nsc-international:dev
```

### Management Commands

```bash
# Run Django management commands
docker-compose exec web python manage.py <command>

# Access Django shell
docker-compose exec web python manage.py shell

# Collect static files
docker-compose exec web python manage.py collectstatic

# Run tests
docker-compose exec web python manage.py test
```

## Troubleshooting

### Database Connection Issues

1. **Check if database is running:**
   ```bash
   docker-compose ps
   ```

2. **Check database logs:**
   ```bash
   docker-compose logs db
   ```

3. **Reset database:**
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

### Static Files Issues

1. **Collect static files:**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

2. **Check static files volume:**
   ```bash
   docker-compose exec web ls -la /app/staticfiles/
   ```

### Permission Issues

If you encounter permission issues:

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Rebuild containers
docker-compose down
docker-compose up --build
```

## GitHub Actions

The project includes GitHub Actions workflow (`.github/workflows/docker.yml`) that:

1. Builds and pushes Docker images to GitHub Container Registry
2. Runs tests in the container
3. Performs security scanning with Trivy

The workflow automatically triggers on:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Version tags (`v*`)

## Security Considerations

- Never commit `.env` files with real credentials
- Use strong passwords for database and Django secret key
- Regularly update base images and dependencies
- Enable SSL in production
- Use proper firewall rules
- Monitor logs for suspicious activity

## Performance Optimization

- Use multi-stage builds for smaller images
- Enable gzip compression in Nginx
- Use CDN for static files in production
- Configure proper caching headers
- Use database connection pooling
- Monitor resource usage
