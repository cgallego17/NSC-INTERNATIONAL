# Development Setup Guide

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd NSC-INTERNATIONAL
python scripts/setup_dev.py
```

### 2. Manual Setup (Alternative)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-security.txt
pip install black isort flake8 mypy pre-commit

# Setup pre-commit hooks
pre-commit install

# Run Django setup
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 🛠️ Development Tools

### Code Quality Tools

- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Bandit**: Security linting
- **Safety**: Dependency vulnerability scanning

### Pre-commit Hooks

Automatically run quality checks before commits:

```bash
pre-commit install
```

### VS Code Configuration

The project includes VS Code settings for:

- Python development
- Django support
- Code formatting
- Linting
- Testing

## 📋 Available Scripts

### Development Scripts

```bash
# Setup development environment
python scripts/setup_dev.py

# Run security scans
python scripts/validate_sarif.py <file>
python scripts/bandit_to_sarif.py <input> <output>

# Code formatting
black .
isort .

# Security checks
python -m safety check
python -m bandit -r . --skip B101,B601

# Django commands
python manage.py check
python manage.py test
python manage.py migrate
```

### Docker Commands

```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up --build -d

# Run tests in container
docker-compose exec web python manage.py test
```

## 🔧 Configuration Files

### pyproject.toml

Centralized configuration for:

- Black formatting
- isort import sorting
- Bandit security scanning
- pytest testing
- Coverage reporting

### .pre-commit-config.yaml

Pre-commit hooks for:

- Code formatting
- Import sorting
- Linting
- Security scanning
- Type checking

### .vscode/

VS Code configuration for:

- Python development
- Django support
- Code formatting
- Testing

## 🧪 Testing

### Running Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test apps.events

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Structure

```
apps/
├── events/
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   └── test_forms.py
└── locations/
    └── tests/
        ├── test_models.py
        └── test_views.py
```

## 🔒 Security

### Security Tools

- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability scanning
- **Semgrep**: Static analysis
- **Trivy**: Container vulnerability scanning
- **Docker Scout**: Container security analysis

### Security Workflows

- `.github/workflows/security-advanced.yml`: Comprehensive security scanning
- `.github/workflows/code-quality-security.yml`: Code quality and security
- `.github/workflows/code-quality.yml`: Code quality checks

### Running Security Scans

```bash
# Dependency vulnerabilities
python -m safety check

# Code security issues
python -m bandit -r . --skip B101,B601

# Static analysis
semgrep --config=auto .

# Container security
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image <image-name>
```

## 🐳 Docker Development

### Development Environment

```bash
# Start development environment
docker-compose up --build

# Access services
# Web: http://localhost:8000
# Database: localhost:5432
# Admin: http://localhost:8000/admin/
```

### Production Environment

```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up --build -d

# With SSL
docker-compose -f docker-compose.prod.yml up --build -d
```

### Docker Commands

```bash
# Build image
docker build -t nsc-international .

# Run container
docker run -p 8000:8000 nsc-international

# Run tests
docker run --rm nsc-international python manage.py test

# Access shell
docker-compose exec web python manage.py shell
```

## 📊 Monitoring and Logging

### Logging Configuration

- **Development**: Console output
- **Production**: File and console logging
- **Docker**: Container logs

### Monitoring

- **Health checks**: Built into Docker containers
- **Security scanning**: Automated via GitHub Actions
- **Code quality**: Pre-commit hooks and CI/CD

## 🚀 Deployment

### GitHub Actions

Automated workflows for:

- Code quality checks
- Security scanning
- Docker builds
- Testing

### Environment Variables

```bash
# Copy example
cp env.example .env

# Edit with your values
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
POSTGRES_DB=nsc_international
POSTGRES_USER=nsc_user
POSTGRES_PASSWORD=your-password
```

## 📚 Additional Resources

### Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Security Best Practices](SECURITY.md)

### Troubleshooting

- Check `SECURITY_FIXES.md` for common issues
- Review GitHub Actions logs
- Check Docker container logs
- Run security scans locally

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper formatting
4. Run tests and security scans
5. Submit a pull request

### Code Standards

- Follow Black formatting
- Sort imports with isort
- Pass all linting checks
- Write tests for new features
- Ensure security scans pass
