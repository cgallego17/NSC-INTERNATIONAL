import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.locations.models import City, Country, State

from .models import (
    HomeBanner,
    Player,
    PlayerParent,
    SiteSettings,
    Sponsor,
    Team,
    UserProfile,
)


class EmailAuthenticationForm(AuthenticationForm):
    """
    Formulario de autenticación que usa correo electrónico en vez de username
    """

    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("you@email.com"),
                "autofocus": True,
            }
        ),
        error_messages={
            "required": _("Please enter your email address."),
            "invalid": _("Please enter a valid email address."),
        },
    )

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": _("Enter your password")}
        ),
        error_messages={"required": _("Please enter your password.")},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cambiar el label del campo username a Email
        self.fields["username"].label = "Correo Electrónico"
        self.fields["password"].label = "Contraseña"

    def clean_username(self):
        """
        Limpiar el campo username (que ahora es email) y buscar el usuario
        Convierte el email a username para la autenticación
        """
        email = self.cleaned_data.get("username")

        if not email:
            raise forms.ValidationError(_("Email is required."))

        # Buscar usuario por email (case-insensitive)
        try:
            user = User.objects.get(email__iexact=email)
            # Retornar el username para que Django pueda autenticar
            return user.username
        except User.DoesNotExist:
            # No revelar que el email no existe por seguridad
            # Usar un username que no existe para que la autenticación falle
            # y Django muestre un mensaje genérico
            raise forms.ValidationError(_("Please enter a correct email and password."))
        except User.MultipleObjectsReturned:
            # Si hay múltiples usuarios con el mismo email (no debería pasar)
            # Usar el primero
            user = User.objects.filter(email__iexact=email).first()
            return user.username


class PublicRegistrationForm(UserCreationForm):
    """Formulario de registro público completo"""

    USER_TYPE_CHOICES = [
        ("parent", _("Parent/Guardian")),
        ("team_manager", _("Team Manager")),
    ]

    # Información básica de usuario
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": _("Email")}
        ),
    )
    first_name = forms.CharField(
        label=_("First Name"),
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("First Name")}
        ),
    )
    last_name = forms.CharField(
        label=_("First Last Name"),
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("First Last Name")}
        ),
    )
    last_name2 = forms.CharField(
        label=_("Second Last Name"),
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Second last name (optional)"),
            }
        ),
    )
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(),
        label=_("Registration Type")
    )

    # Información de contacto
    phone_prefix = forms.ChoiceField(
        label=_("Country Code"),
        required=True,
        choices=[
            ("", _("Select")),
            ("+1", "+1 (USA/Canada)"),
            ("+52", "+52 (Mexico)"),
            ("+57", "+57 (Colombia)"),
            ("+51", "+51 (Peru)"),
            ("+56", "+56 (Chile)"),
            ("+54", "+54 (Argentina)"),
            ("+55", "+55 (Brazil)"),
            ("+58", "+58 (Venezuela)"),
            ("+593", "+593 (Ecuador)"),
            ("+506", "+506 (Costa Rica)"),
            ("+507", "+507 (Panama)"),
            ("+502", "+502 (Guatemala)"),
            ("+504", "+504 (Honduras)"),
            ("+505", "+505 (Nicaragua)"),
            ("+503", "+503 (El Salvador)"),
            ("+34", "+34 (Spain)"),
            ("+44", "+44 (United Kingdom)"),
            ("+33", "+33 (France)"),
            ("+49", "+49 (Germany)"),
            ("+39", "+39 (Italy)"),
            ("+81", "+81 (Japan)"),
            ("+86", "+86 (China)"),
            ("+82", "+82 (South Korea)"),
            ("+61", "+61 (Australia)"),
            ("+64", "+64 (New Zealand)"),
            ("+27", "+27 (South Africa)"),
            ("+91", "+91 (India)"),
        ],
        widget=forms.Select(attrs={"class": "form-select", "id": "id_phone_prefix"}),
    )
    phone = forms.CharField(
        label=_("Phone Number"),
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Phone number"),
                "id": "id_phone",
            }
        ),
    )
    phone_secondary = forms.CharField(
        label=_("Secondary Phone"),
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Secondary phone (optional)"),
            }
        ),
    )
    birth_date = forms.DateField(
        label=_("Date of Birth"),
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date", "placeholder": _("Date of Birth")}),
    )

    # Foto de perfil
    profile_picture = forms.ImageField(
        label=_("Profile Picture"),
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
    )

    # Ubicación
    country = forms.ModelChoiceField(
        label=_("Country"),
        queryset=Country.objects.filter(is_active=True).order_by("name"),
        required=False,
        empty_label=_("Select a country"),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_country"}),
    )
    state = forms.ModelChoiceField(
        label=_("State"),
        queryset=State.objects.none(),
        required=False,
        empty_label=_("Select a state"),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_state"}),
    )
    city = forms.ModelChoiceField(
        label=_("City"),
        queryset=City.objects.none(),
        required=False,
        empty_label=_("Select a city"),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_city"}),
    )

    # Dirección
    address = forms.CharField(
        label=_("Address"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": _("Full address"),
            }
        ),
    )
    address_line_2 = forms.CharField(
        label=_("Address Line 2"),
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Apartment, suite, etc. (optional)"),
            }
        ),
    )
    postal_code = forms.CharField(
        label=_("Postal Code"),
        max_length=10,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Postal Code")}
        ),
    )

    # Información adicional
    bio = forms.CharField(
        label=_("Biography / About You"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": _("Tell us about yourself..."),
            }
        ),
    )
    website = forms.URLField(
        label=_("Website"),
        required=False,
        widget=forms.URLInput(
            attrs={"class": "form-control", "placeholder": _("https://your-website.com")}
        ),
    )
    social_media = forms.CharField(
        label=_("Social Media"),
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("@instagram_user, @twitter_user"),
            }
        ),
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password1", "password2"]
        widgets = {
            "password1": forms.PasswordInput(
                attrs={"class": "form-control", "placeholder": _("Password")}
            ),
            "password2": forms.PasswordInput(
                attrs={"class": "form-control", "placeholder": _("Confirm Password")}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar el campo username del formulario
        if "username" in self.fields:
            del self.fields["username"]

        self.fields["password1"].label = _("Password")
        self.fields["password2"].label = _("Confirm Password")
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("Password")}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("Confirm Password")}
        )

        # Si hay un país seleccionado, cargar estados
        if "country" in self.data:
            try:
                country_id = int(self.data.get("country"))
                self.fields["state"].queryset = State.objects.filter(
                    country_id=country_id, is_active=True
                ).order_by("name")
            except (ValueError, TypeError):
                pass

        # Si hay un estado seleccionado, cargar ciudades
        if "state" in self.data:
            try:
                state_id = int(self.data.get("state"))
                self.fields["city"].queryset = City.objects.filter(
                    state_id=state_id, is_active=True
                ).order_by("name")
            except (ValueError, TypeError):
                pass

    def generate_username(self, first_name, last_name, last_name2=None):
        """Genera un username único basado en nombre y apellidos"""
        # Limpiar y normalizar nombres
        first_name = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ]", "", first_name.strip().lower())
        last_name = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ]", "", last_name.strip().lower())
        last_name2 = (
            re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ]", "", last_name2.strip().lower())
            if last_name2 and last_name2.strip()
            else None
        )

        # Reemplazar acentos y caracteres especiales
        replacements = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "Á": "a",
            "É": "e",
            "Í": "i",
            "Ó": "o",
            "Ú": "u",
            "ñ": "n",
            "Ñ": "n",
        }
        for old, new in replacements.items():
            first_name = first_name.replace(old, new)
            last_name = last_name.replace(old, new)
            if last_name2:
                last_name2 = last_name2.replace(old, new)

        # Generar base del username
        if first_name and last_name:
            if last_name2:
                # Si hay segundo apellido, usar solo la primera letra del segundo apellido
                base_username = f"{first_name}.{last_name}{last_name2[0]}"
            else:
                base_username = f"{first_name}.{last_name}"
        elif first_name:
            base_username = first_name
        elif last_name:
            base_username = last_name
        else:
            base_username = "usuario"

        # Limitar longitud
        base_username = base_username[:25]  # Dejar espacio para números

        # Verificar si existe y generar variante única
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            suffix = str(counter)
            # Asegurar que no exceda 30 caracteres (límite de Django)
            max_base_len = 30 - len(suffix) - 1
            username = f"{base_username[:max_base_len]}{suffix}"
            counter += 1
            # Prevenir loops infinitos
            if counter > 9999:
                import random

                username = f"{base_username[:20]}{random.randint(1000, 9999)}"
                break

        return username

    def clean_email(self):
        """Validar que el email sea único"""
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("This email is already registered. Please use another email.")
            )
        return email

    def clean_first_name(self):
        """Validar que el nombre no esté vacío"""
        first_name = self.cleaned_data.get("first_name")
        if not first_name or not first_name.strip():
            raise forms.ValidationError(_("First name is required."))
        return first_name.strip()

    def clean_last_name(self):
        """Validar que el apellido no esté vacío"""
        last_name = self.cleaned_data.get("last_name")
        if not last_name or not last_name.strip():
            raise forms.ValidationError(_("Last name is required."))
        return last_name.strip()

    def clean_last_name2(self):
        """Validar y limpiar el segundo apellido"""
        last_name2 = self.cleaned_data.get("last_name2", "")
        if last_name2:
            return last_name2.strip()
        return ""

    def clean_password1(self):
        """Validar que la contraseña sea segura"""
        password = self.cleaned_data.get("password1")

        if not password:
            return password

        # Verificar longitud mínima
        if len(password) < 8:
            raise forms.ValidationError(
                _("Password must be at least 8 characters long.")
            )

        # Verificar que tenga al menos una letra mayúscula
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError(
                _("Password must contain at least one uppercase letter.")
            )

        # Verificar que tenga al menos una letra minúscula
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError(
                _("Password must contain at least one lowercase letter.")
            )

        # Verificar que tenga al menos un número
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError(
                _("Password must contain at least one number.")
            )

        # Verificar que tenga al menos un carácter especial
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            raise forms.ValidationError(
                _("Password must contain at least one special character (!@#$%^&*).")
            )

        # Verificar que no sea demasiado común o similar al email/nombre
        email = self.cleaned_data.get("email", "")
        first_name = self.cleaned_data.get("first_name", "")
        last_name = self.cleaned_data.get("last_name", "")

        # No permitir que la contraseña sea similar al email
        if email and password.lower() in email.lower():
            raise forms.ValidationError(
                _("Password cannot be too similar to your email address.")
            )

        # No permitir que la contraseña sea similar al nombre
        if first_name and password.lower() in first_name.lower():
            raise forms.ValidationError(
                _("Password cannot be too similar to your first name.")
            )

        if last_name and password.lower() in last_name.lower():
            raise forms.ValidationError(
                _("Password cannot be too similar to your last name.")
            )

        return password

    def save(self, commit=True):
        # Generar username automáticamente
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        last_name2 = self.cleaned_data.get("last_name2", "")
        username = self.generate_username(first_name, last_name, last_name2)

        # Combinar apellidos para el campo last_name de User
        if last_name2:
            full_last_name = f"{last_name} {last_name2}"
        else:
            full_last_name = last_name

        # Crear usuario con username generado
        user = User.objects.create_user(
            username=username,
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            first_name=first_name,
            last_name=full_last_name,
        )

        if commit:
            # Combinar prefijo con número de teléfono
            phone_prefix = self.cleaned_data.get("phone_prefix", "")
            phone_number = self.cleaned_data.get("phone", "")
            full_phone = (
                f"{phone_prefix} {phone_number}".strip()
                if phone_prefix and phone_number
                else phone_number
            )

            # Crear perfil de usuario
            profile = UserProfile.objects.create(
                user=user,
                user_type=self.cleaned_data["user_type"],
                phone=full_phone,
                phone_secondary=self.cleaned_data.get("phone_secondary", ""),
                birth_date=self.cleaned_data.get("birth_date"),
                profile_picture=self.cleaned_data.get("profile_picture"),
                country=self.cleaned_data.get("country"),
                state=self.cleaned_data.get("state"),
                city=self.cleaned_data.get("city"),
                address=self.cleaned_data.get("address", ""),
                address_line_2=self.cleaned_data.get("address_line_2", ""),
                postal_code=self.cleaned_data.get("postal_code", ""),
                bio=self.cleaned_data.get("bio", ""),
                website=self.cleaned_data.get("website", ""),
                social_media=self.cleaned_data.get("social_media", ""),
            )
            # No crear perfil de jugador aquí - los padres lo harán desde el dashboard

        return user


class UserProfileForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""

    class Meta:
        model = UserProfile
        fields = [
            "phone",
            "address",
            "country",
            "state",
            "city",
            "postal_code",
            "birth_date",
            "profile_picture",
            "bio",
        ]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "profile_picture": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                    "style": "display: none;",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Campos de ubicación con ModelChoiceField
        self.fields["country"] = forms.ModelChoiceField(
            queryset=Country.objects.filter(is_active=True).order_by("name"),
            required=False,
            empty_label=_("Select a country"),
            widget=forms.Select(attrs={"class": "form-select", "id": "id_country"}),
        )

        self.fields["state"] = forms.ModelChoiceField(
            queryset=State.objects.none(),
            required=False,
            empty_label=_("Select a state"),
            widget=forms.Select(attrs={"class": "form-select", "id": "id_state"}),
        )

        self.fields["city"] = forms.ModelChoiceField(
            queryset=City.objects.none(),
            required=False,
            empty_label=_("Select a city"),
            widget=forms.Select(attrs={"class": "form-select", "id": "id_city"}),
        )

        # Si hay una instancia (edición), cargar estados y ciudades
        if self.instance and self.instance.pk:
            if self.instance.country:
                self.fields["state"].queryset = State.objects.filter(
                    country=self.instance.country, is_active=True
                ).order_by("name")
            if self.instance.state:
                self.fields["city"].queryset = City.objects.filter(
                    state=self.instance.state, is_active=True
                ).order_by("name")

        # Si hay datos en POST, cargar dinámicamente
        if "country" in self.data:
            try:
                country_id = int(self.data.get("country"))
                self.fields["state"].queryset = State.objects.filter(
                    country_id=country_id, is_active=True
                ).order_by("name")
            except (ValueError, TypeError):
                pass

        if "state" in self.data:
            try:
                state_id = int(self.data.get("state"))
                self.fields["city"].queryset = City.objects.filter(
                    state_id=state_id, is_active=True
                ).order_by("name")
            except (ValueError, TypeError):
                pass


class UserCreateForm(UserCreationForm):
    """Formulario para crear usuarios"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nombre"}
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Apellido"}
        ),
    )
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Tipo de Usuario",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a los campos de contraseña
        if "password1" in self.fields:
            self.fields["password1"].widget.attrs.update(
                {"class": "form-control", "placeholder": "Contraseña"}
            )
        if "password2" in self.fields:
            self.fields["password2"].widget.attrs.update(
                {"class": "form-control", "placeholder": "Confirmar contraseña"}
            )

    is_staff = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Es Staff",
    )
    is_superuser = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Es Administrador",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "user_type",
            "is_staff",
            "is_superuser",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre de usuario"}
            ),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_staff = self.cleaned_data.get("is_staff", False)
        user.is_superuser = self.cleaned_data.get("is_superuser", False)
        if commit:
            user.save()
            # Crear perfil de usuario
            UserProfile.objects.create(
                user=user, user_type=self.cleaned_data["user_type"]
            )
        return user


class UserUpdateForm(forms.ModelForm):
    """Formulario para actualizar información básica del usuario"""

    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Tipo de Usuario",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "user_type",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, "profile"):
            self.fields["user_type"].initial = self.instance.profile.user_type

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit and hasattr(user, "profile"):
            user.profile.user_type = self.cleaned_data.get("user_type", "player")
            user.profile.save()
        return user


class TeamForm(forms.ModelForm):
    """Formulario para crear/editar equipos"""

    class Meta:
        model = Team
        fields = [
            "name",
            "description",
            "logo",
            "country",
            "state",
            "city",
            "website",
            "contact_email",
            "contact_phone",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
            "logo": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-control"}),
            "contact_phone": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Campos de ubicación con ModelChoiceField
        self.fields["country"] = forms.ModelChoiceField(
            queryset=Country.objects.filter(is_active=True).order_by("name"),
            required=False,
            empty_label=_("Select a country"),
            widget=forms.Select(
                attrs={"class": "form-select", "id": "id_team_country"}
            ),
        )

        self.fields["state"] = forms.ModelChoiceField(
            queryset=State.objects.none(),
            required=False,
            empty_label=_("Select a state"),
            widget=forms.Select(attrs={"class": "form-select", "id": "id_team_state"}),
        )

        self.fields["city"] = forms.ModelChoiceField(
            queryset=City.objects.none(),
            required=False,
            empty_label=_("Select a city"),
            widget=forms.Select(attrs={"class": "form-select", "id": "id_team_city"}),
        )

        # Si hay una instancia (edición), cargar estados y ciudades
        if self.instance and self.instance.pk:
            if self.instance.country:
                self.fields["state"].queryset = State.objects.filter(
                    country=self.instance.country, is_active=True
                ).order_by("name")
            if self.instance.state:
                self.fields["city"].queryset = City.objects.filter(
                    state=self.instance.state, is_active=True
                ).order_by("name")

        # Si hay datos en POST, cargar dinámicamente
        if "country" in self.data:
            try:
                country_id = int(self.data.get("country"))
                self.fields["state"].queryset = State.objects.filter(
                    country_id=country_id, is_active=True
                ).order_by("name")
            except (ValueError, TypeError):
                pass

        if "state" in self.data:
            try:
                state_id = int(self.data.get("state"))
                self.fields["city"].queryset = City.objects.filter(
                    state_id=state_id, is_active=True
                ).order_by("name")
            except (ValueError, TypeError):
                pass


class PlayerRegistrationForm(forms.ModelForm):
    """Formulario para que managers registren jugadores"""

    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name2 = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text=_("The player will be able to change their password later"),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    class Meta:
        model = Player
        fields = [
            "team",
            "jersey_number",
            "position",
            "secondary_position",
            "is_pitcher",
            "height",
            "weight",
            "batting_hand",
            "throwing_hand",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relation",
            "medical_conditions",
            "jersey_size",
            "hat_size",
            "batting_glove_size",
            "batting_helmet_size",
            "shorts_size",
            "grade",
            "division",
            "age_verification_document",
        ]
        widgets = {
            "team": forms.Select(attrs={"class": "form-select"}),
            "jersey_number": forms.NumberInput(attrs={"class": "form-control"}),
            "position": forms.Select(attrs={"class": "form-select"}),
            "secondary_position": forms.Select(attrs={"class": "form-select"}),
            "is_pitcher": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "height": forms.TextInput(attrs={"class": "form-control"}),
            "weight": forms.NumberInput(attrs={"class": "form-control"}),
            "batting_hand": forms.Select(attrs={"class": "form-select"}),
            "throwing_hand": forms.Select(attrs={"class": "form-select"}),
            "emergency_contact_name": forms.TextInput(attrs={"class": "form-control"}),
            "emergency_contact_phone": forms.TextInput(attrs={"class": "form-control"}),
            "emergency_contact_relation": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "medical_conditions": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "jersey_size": forms.Select(attrs={"class": "form-select"}),
            "hat_size": forms.Select(attrs={"class": "form-select"}),
            "batting_glove_size": forms.Select(attrs={"class": "form-select"}),
            "batting_helmet_size": forms.Select(attrs={"class": "form-select"}),
            "shorts_size": forms.Select(attrs={"class": "form-select"}),
            "grade": forms.Select(attrs={"class": "form-select"}),
            "division": forms.Select(attrs={"class": "form-select"}),
            "age_verification_document": forms.FileInput(
                attrs={"class": "form-control", "accept": ".pdf,.jpg,.jpeg,.png"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.manager = kwargs.pop("manager", None)
        super().__init__(*args, **kwargs)
        self.fields["age_verification_document"].required = False
        if self.manager:
            # Solo mostrar equipos que el manager gestiona
            self.fields["team"].queryset = Team.objects.filter(manager=self.manager)

    def generate_username(self, first_name, last_name, last_name2=None):
        """Genera un username único basado en nombre y apellidos"""
        first_name = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ]", "", first_name.strip().lower())
        last_name = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ]", "", last_name.strip().lower())
        last_name2 = (
            re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ]", "", last_name2.strip().lower())
            if last_name2 and last_name2.strip()
            else None
        )

        replacements = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "Á": "a",
            "É": "e",
            "Í": "i",
            "Ó": "o",
            "Ú": "u",
            "ñ": "n",
            "Ñ": "n",
        }
        for old, new in replacements.items():
            first_name = first_name.replace(old, new)
            last_name = last_name.replace(old, new)
            if last_name2:
                last_name2 = last_name2.replace(old, new)

        if first_name and last_name:
            if last_name2:
                base_username = f"{first_name}.{last_name}{last_name2[0]}"
            else:
                base_username = f"{first_name}.{last_name}"
        elif first_name:
            base_username = first_name
        elif last_name:
            base_username = last_name
        else:
            base_username = "usuario"

        base_username = base_username[:25]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            suffix = str(counter)
            max_base_len = 30 - len(suffix)
            if max_base_len < 1:
                max_base_len = 1
            username = f"{base_username[:max_base_len]}{suffix}"
            counter += 1
            if counter > 9999:
                import random

                username = f"{base_username[:20]}{random.randint(1000, 9999)}"
                break

        return username

    def clean_email(self):
        """Validar que el email sea único"""
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("This email is already registered. Please use another email.")
            )
        return email

    def clean_first_name(self):
        """Validar que el nombre no esté vacío"""
        first_name = self.cleaned_data.get("first_name")
        if not first_name or not first_name.strip():
            raise forms.ValidationError(_("First name is required."))
        return first_name.strip()

    def clean_last_name(self):
        """Validar que el apellido no esté vacío"""
        last_name = self.cleaned_data.get("last_name")
        if not last_name or not last_name.strip():
            raise forms.ValidationError(_("Last name is required."))
        return last_name.strip()

    def clean_last_name2(self):
        """Validar y limpiar el segundo apellido"""
        last_name2 = self.cleaned_data.get("last_name2", "")
        if last_name2:
            return last_name2.strip()
        return ""

    def save(self, commit=True):
        # Generar username automáticamente
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        last_name2 = self.cleaned_data.get("last_name2", "")
        username = self.generate_username(first_name, last_name, last_name2)

        # Combinar apellidos para el campo last_name de User
        if last_name2:
            full_last_name = f"{last_name} {last_name2}"
        else:
            full_last_name = last_name

        # Crear usuario primero
        user = User.objects.create_user(
            username=username,
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=first_name,
            last_name=full_last_name,
        )

        # Crear perfil de usuario
        profile = UserProfile.objects.create(
            user=user,
            user_type="player",
            phone=self.cleaned_data.get("phone", ""),
            birth_date=self.cleaned_data.get("birth_date"),
        )
        # Guardar last_name2 si existe (usando setattr por si el campo no existe en el modelo)
        if last_name2:
            setattr(profile, "last_name2", last_name2)
            profile.save()

        # Crear perfil de jugador directamente (no usar super().save() porque requiere user)
        # Obtener secondary_position e is_pitcher explícitamente
        secondary_position = self.cleaned_data.get("secondary_position", "") or ""
        is_pitcher = bool(self.cleaned_data.get("is_pitcher", False))

        player = Player.objects.create(
            user=user,
            team=self.cleaned_data.get("team"),
            jersey_number=self.cleaned_data.get("jersey_number"),
            position=self.cleaned_data.get("position"),
            secondary_position=secondary_position,
            is_pitcher=is_pitcher,
            height=self.cleaned_data.get("height"),
            weight=self.cleaned_data.get("weight"),
            batting_hand=self.cleaned_data.get("batting_hand"),
            throwing_hand=self.cleaned_data.get("throwing_hand"),
            emergency_contact_name=self.cleaned_data.get("emergency_contact_name"),
            emergency_contact_phone=self.cleaned_data.get("emergency_contact_phone"),
            emergency_contact_relation=self.cleaned_data.get(
                "emergency_contact_relation"
            ),
            medical_conditions=self.cleaned_data.get("medical_conditions"),
            jersey_size=self.cleaned_data.get("jersey_size"),
            hat_size=self.cleaned_data.get("hat_size"),
            batting_glove_size=self.cleaned_data.get("batting_glove_size"),
            batting_helmet_size=self.cleaned_data.get("batting_helmet_size"),
            shorts_size=self.cleaned_data.get("shorts_size"),
            grade=self.cleaned_data.get("grade"),
            division=self.cleaned_data.get("division"),
            age_verification_document=self.cleaned_data.get(
                "age_verification_document"
            ),
        )

        return player


class ParentPlayerRegistrationForm(forms.ModelForm):
    """Formulario para que padres registren jugadores

    Nota: Los jugadores NO pueden iniciar sesión. Todo es gestionado por el padre/acudiente.
    El equipo y número de jersey serán asignados por un administrador o manager.
    """

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name2 = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    birth_date = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date", "data-format": "yyyy-MM-dd"}
        ),
        help_text=_("Player's date of birth"),
    )
    relationship = forms.ChoiceField(
        choices=[
            ("father", _("Father")),
            ("mother", _("Mother")),
            ("guardian", _("Guardian")),
            ("other", _("Other")),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Relationship to the player"),
        initial="guardian",
    )
    is_primary = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label=_("Primary Contact"),
        help_text=_("Check if you are the primary contact for the player"),
    )

    class Meta:
        model = Player
        fields = [
            "position",
            "secondary_position",
            "is_pitcher",
            "height",
            "weight",
            "batting_hand",
            "throwing_hand",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relation",
            "medical_conditions",
            "jersey_size",
            "hat_size",
            "batting_glove_size",
            "batting_helmet_size",
            "shorts_size",
            "grade",
            "division",
            "age_verification_document",
        ]
        widgets = {
            "position": forms.Select(attrs={"class": "form-select", "required": True}),
            "secondary_position": forms.Select(attrs={"class": "form-select"}),
            "is_pitcher": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "height": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "weight": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "batting_hand": forms.Select(
                attrs={"class": "form-select", "required": True}
            ),
            "throwing_hand": forms.Select(
                attrs={"class": "form-select", "required": True}
            ),
            "emergency_contact_name": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "emergency_contact_phone": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "emergency_contact_relation": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "medical_conditions": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "required": True}
            ),
            "jersey_size": forms.Select(attrs={"class": "form-select"}),
            "hat_size": forms.Select(attrs={"class": "form-select"}),
            "batting_glove_size": forms.Select(attrs={"class": "form-select"}),
            "batting_helmet_size": forms.Select(attrs={"class": "form-select"}),
            "shorts_size": forms.Select(attrs={"class": "form-select"}),
            "grade": forms.Select(attrs={"class": "form-select", "required": True}),
            "division": forms.Select(attrs={"class": "form-select", "required": True}),
            "age_verification_document": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.jpg,.jpeg,.png",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        # Los padres NO pueden seleccionar equipo - será asignado por admin o manager
        # El campo 'team' no está en los fields del Meta, así que no aparecerá en el formulario

        # Hacer todos los campos obligatorios excepto last_name2 y phone
        # Los campos que ya están en el Meta se configuran en los widgets
        # Campos adicionales que necesitan ser obligatorios:
        self.fields["position"].required = True
        self.fields["batting_hand"].required = True
        self.fields["throwing_hand"].required = True
        self.fields["emergency_contact_name"].required = True
        self.fields["emergency_contact_phone"].required = True
        self.fields["emergency_contact_relation"].required = True
        self.fields["medical_conditions"].required = True
        self.fields["grade"].required = True
        self.fields["division"].required = True
        self.fields["age_verification_document"].required = False

        # Tallas de uniformes también son obligatorias
        self.fields["jersey_size"].required = True
        self.fields["hat_size"].required = True
        self.fields["batting_glove_size"].required = True
        self.fields["batting_helmet_size"].required = True
        self.fields["shorts_size"].required = True

        # last_name2 y phone ya están como required=False, no los cambiamos

        if self.parent:
            # Pre-llenar los campos de contacto de emergencia con los datos del padre
            # El padre puede modificar estos valores si quiere poner otros datos
            parent_name = (
                self.parent.get_full_name()
                or f"{self.parent.first_name} {self.parent.last_name}".strip()
            )
            if parent_name:
                self.fields["emergency_contact_name"].initial = parent_name

            # Usar el teléfono principal, o el secundario si el principal no está disponible
            if hasattr(self.parent, "profile"):
                parent_phone = (
                    self.parent.profile.phone or self.parent.profile.phone_secondary
                )
                if parent_phone:
                    self.fields["emergency_contact_phone"].initial = parent_phone

            # Pre-llenar la relación basada en el campo relationship del formulario
            # El valor inicial de relationship es 'guardian' por defecto
            relationship_map = {
                "father": "Padre",
                "mother": "Madre",
                "guardian": "Acudiente",
                "other": "Otro",
            }
            # Usar el valor inicial del campo relationship si está disponible
            relationship_value = self.initial.get(
                "relationship", self.fields["relationship"].initial or "guardian"
            )
            self.fields["emergency_contact_relation"].initial = relationship_map.get(
                relationship_value, "Acudiente"
            )

    def generate_username(self, first_name, last_name, last_name2=None):
        """Genera un username único basado en nombre y apellidos"""
        first_name = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ]", "", first_name.strip().lower())
        last_name = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ]", "", last_name.strip().lower())
        last_name2 = (
            re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ]", "", last_name2.strip().lower())
            if last_name2 and last_name2.strip()
            else None
        )

        replacements = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "Á": "a",
            "É": "e",
            "Í": "i",
            "Ó": "o",
            "Ú": "u",
            "ñ": "n",
            "Ñ": "n",
        }
        for old, new in replacements.items():
            first_name = first_name.replace(old, new)
            last_name = last_name.replace(old, new)
            if last_name2:
                last_name2 = last_name2.replace(old, new)

        if first_name and last_name:
            if last_name2:
                base_username = f"{first_name}.{last_name}{last_name2[0]}"
            else:
                base_username = f"{first_name}.{last_name}"
        elif first_name:
            base_username = first_name
        elif last_name:
            base_username = last_name
        else:
            base_username = "jugador"

        base_username = base_username[:25]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            suffix = str(counter)
            max_base_len = 30 - len(suffix) - 1
            if max_base_len < 1:
                max_base_len = 1
            username = f"{base_username[:max_base_len]}{suffix}"
            counter += 1
            if counter > 9999:
                import random

                username = f"{base_username[:20]}{random.randint(1000, 9999)}"
                break

        return username

    def clean_email(self):
        """Validar que el email sea único si se proporciona"""
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("This email is already registered. Please use another email.")
            )
        return email

    def clean_division(self):
        """Validar que la división asignada sea válida según las reglas de elegibilidad"""
        division = self.cleaned_data.get("division")
        if not division:
            return division

        # Necesitamos birth_date y grade para calcular la división elegible
        birth_date = self.cleaned_data.get("birth_date")
        grade = self.cleaned_data.get("grade")

        if not birth_date and not grade:
            # Si no hay birth_date ni grade, permitir asignar división de todas formas
            return division

        # Calcular la división basada en edad directamente sin crear instancia completa
        # Esto evita problemas con la verificación de edad
        age_division = None
        if birth_date:
            try:
                from datetime import date
                # Calcular edad al 30 de abril
                cutoff_date = date(date.today().year, 4, 30)
                if cutoff_date < date.today():
                    cutoff_date = date(date.today().year + 1, 4, 30)

                age = cutoff_date.year - birth_date.year
                if (cutoff_date.month, cutoff_date.day) < (birth_date.month, birth_date.day):
                    age -= 1

                # Mapeo de edad a división
                division_map = {
                    5: "05U", 6: "06U", 7: "07U", 8: "08U", 9: "09U",
                    10: "10U", 11: "11U", 12: "12U", 13: "13U", 14: "14U",
                    15: "15U", 16: "16U", 17: "17U", 18: "18U",
                }

                if age < 5:
                    age_division = None
                elif age >= 18:
                    age_division = "18U"
                else:
                    age_division = division_map.get(age)
            except Exception:
                age_division = None

        if not age_division:
            # Si no se puede determinar división basada en edad, permitir asignar
            return division

        # Obtener el número de la división objetivo
        try:
            target_num = int(division.replace("U", ""))
        except (ValueError, AttributeError):
            return division

        try:
            age_division_num = int(age_division.replace("U", ""))
        except (ValueError, AttributeError):
            return division

        # No puede jugar "down" (en una división menor)
        if target_num < age_division_num:
            raise forms.ValidationError(
                f"El jugador no puede jugar en una división menor ({division}). División mínima elegible: {age_division}"
            )

        # Puede jugar "up" máximo 2 divisiones
        if target_num > age_division_num + 2:
            raise forms.ValidationError(
                f"El jugador solo puede jugar hasta 2 divisiones arriba de su división basada en edad ({age_division}). División solicitada: {division}"
            )

        return division

    def clean_first_name(self):
        """Validar que el nombre no esté vacío"""
        first_name = self.cleaned_data.get("first_name")
        if not first_name or not first_name.strip():
            raise forms.ValidationError(_("First name is required."))
        return first_name.strip()

    def clean_last_name(self):
        """Validar que el apellido no esté vacío"""
        last_name = self.cleaned_data.get("last_name")
        if not last_name or not last_name.strip():
            raise forms.ValidationError(_("Last name is required."))
        return last_name.strip()

    def clean_division(self):
        """Validar que la división asignada sea válida según las reglas de elegibilidad"""
        division = self.cleaned_data.get("division")
        if not division:
            return division

        # Necesitamos birth_date y grade para calcular la división elegible
        birth_date = self.cleaned_data.get("birth_date")
        grade = self.cleaned_data.get("grade")

        if not birth_date and not grade:
            # Si no hay birth_date ni grade, permitir asignar división de todas formas
            return division

        # Calcular la división basada en edad directamente sin crear instancia completa
        # Esto evita problemas con la verificación de edad
        age_division = None
        if birth_date:
            try:
                from datetime import date
                # Calcular edad al 30 de abril
                cutoff_date = date(date.today().year, 4, 30)
                if cutoff_date < date.today():
                    cutoff_date = date(date.today().year + 1, 4, 30)

                age = cutoff_date.year - birth_date.year
                if (cutoff_date.month, cutoff_date.day) < (birth_date.month, birth_date.day):
                    age -= 1

                # Mapeo de edad a división
                division_map = {
                    5: "05U", 6: "06U", 7: "07U", 8: "08U", 9: "09U",
                    10: "10U", 11: "11U", 12: "12U", 13: "13U", 14: "14U",
                    15: "15U", 16: "16U", 17: "17U", 18: "18U",
                }

                if age < 5:
                    age_division = None
                elif age >= 18:
                    age_division = "18U"
                else:
                    age_division = division_map.get(age)
            except Exception:
                age_division = None

        if not age_division:
            # Si no se puede determinar división basada en edad, permitir asignar
            return division

        # Obtener el número de la división objetivo
        try:
            target_num = int(division.replace("U", ""))
        except (ValueError, AttributeError):
            return division

        try:
            age_division_num = int(age_division.replace("U", ""))
        except (ValueError, AttributeError):
            return division

        # No puede jugar "down" (en una división menor)
        if target_num < age_division_num:
            raise forms.ValidationError(
                f"El jugador no puede jugar en una división menor ({division}). División mínima elegible: {age_division}"
            )

        # Puede jugar "up" máximo 2 divisiones
        if target_num > age_division_num + 2:
            raise forms.ValidationError(
                f"El jugador solo puede jugar hasta 2 divisiones arriba de su división basada en edad ({age_division}). División solicitada: {division}"
            )

        return division

    def clean_birth_date(self):
        """Validar que la fecha de nacimiento sea válida"""
        birth_date = self.cleaned_data.get("birth_date")
        if not birth_date:
            raise forms.ValidationError("La fecha de nacimiento es requerida.")
        return birth_date

    def save(self, commit=True):
        import secrets
        import string

        from django.contrib.auth.models import User

        # Generar username automáticamente
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        last_name2 = self.cleaned_data.get("last_name2", "")
        username = self.generate_username(first_name, last_name, last_name2)

        # Generar contraseña aleatoria segura (no se usará para login, solo para la cuenta)
        alphabet = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabet) for i in range(20))

        # Combinar apellidos para el campo last_name de User
        if last_name2:
            full_last_name = f"{last_name} {last_name2}"
        else:
            full_last_name = last_name

        # Email temporal (no real, solo para cumplir con el modelo)
        email = f"{username}@nsc-temp.local"

        # Crear usuario INACTIVO - Los jugadores NO pueden iniciar sesión
        # Todo es gestionado por el padre/acudiente
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=full_last_name,
            is_active=False,  # IMPORTANTE: Cuenta inactiva, no puede iniciar sesión
        )

        # Crear perfil de usuario
        profile = UserProfile.objects.create(
            user=user,
            user_type="player",
            phone=self.cleaned_data.get("phone", ""),
            birth_date=self.cleaned_data.get("birth_date"),
        )

        # Crear perfil de jugador
        # NOTA: El equipo y número de jersey NO se asignan aquí - serán asignados por un administrador o manager
        # Obtener secondary_position e is_pitcher explícitamente
        secondary_position = self.cleaned_data.get("secondary_position", "") or ""
        is_pitcher = bool(self.cleaned_data.get("is_pitcher", False))

        player = Player.objects.create(
            user=user,
            team=None,  # El equipo se asignará posteriormente por admin o manager
            jersey_number=None,  # El número de jersey se asignará posteriormente por admin o manager
            position=self.cleaned_data.get("position"),
            secondary_position=secondary_position,
            is_pitcher=is_pitcher,
            height=self.cleaned_data.get("height"),
            weight=self.cleaned_data.get("weight"),
            batting_hand=self.cleaned_data.get("batting_hand"),
            throwing_hand=self.cleaned_data.get("throwing_hand"),
            emergency_contact_name=self.cleaned_data.get("emergency_contact_name"),
            emergency_contact_phone=self.cleaned_data.get("emergency_contact_phone"),
            emergency_contact_relation=self.cleaned_data.get(
                "emergency_contact_relation"
            ),
            medical_conditions=self.cleaned_data.get("medical_conditions"),
            jersey_size=self.cleaned_data.get("jersey_size"),
            hat_size=self.cleaned_data.get("hat_size"),
            batting_glove_size=self.cleaned_data.get("batting_glove_size"),
            batting_helmet_size=self.cleaned_data.get("batting_helmet_size"),
            shorts_size=self.cleaned_data.get("shorts_size"),
            grade=self.cleaned_data.get("grade"),
            division=self.cleaned_data.get("division"),
            age_verification_document=self.cleaned_data.get(
                "age_verification_document"
            ),
        )

        # Crear relación padre-jugador
        if self.parent:
            PlayerParent.objects.create(
                parent=self.parent,
                player=player,
                relationship=self.cleaned_data.get("relationship", "guardian"),
                is_primary=self.cleaned_data.get("is_primary", False),
            )

        return player


class PlayerUpdateForm(forms.ModelForm):
    """Formulario para actualizar información de jugador"""

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "accept": "image/*",
                "id": "id_profile_picture",
                "style": "display: none;",
            }
        ),
        help_text="Sube una nueva foto de perfil",
    )

    # Campos de User
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name2 = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    class Meta:
        model = Player
        fields = [
            "team",
            "jersey_number",
            "position",
            "secondary_position",
            "is_pitcher",
            "height",
            "weight",
            "batting_hand",
            "throwing_hand",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relation",
            "medical_conditions",
            "is_active",
            "jersey_size",
            "hat_size",
            "batting_glove_size",
            "batting_helmet_size",
            "shorts_size",
            "grade",
            "division",
            "age_verification_document",
            "age_verification_status",
            "age_verification_notes",
        ]
        # team_hidden no está en fields porque se agrega dinámicamente en __init__
        widgets = {
            "team": forms.Select(attrs={"class": "form-select"}),
            "jersey_number": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Número de jersey"}
            ),
            "position": forms.Select(attrs={"class": "form-select"}),
            "secondary_position": forms.Select(attrs={"class": "form-select"}),
            "is_pitcher": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "height": forms.TextInput(attrs={"class": "form-control"}),
            "weight": forms.NumberInput(attrs={"class": "form-control"}),
            "batting_hand": forms.Select(attrs={"class": "form-select"}),
            "throwing_hand": forms.Select(attrs={"class": "form-select"}),
            "emergency_contact_name": forms.TextInput(attrs={"class": "form-control"}),
            "emergency_contact_phone": forms.TextInput(attrs={"class": "form-control"}),
            "emergency_contact_relation": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "medical_conditions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "jersey_size": forms.Select(attrs={"class": "form-select"}),
            "hat_size": forms.Select(attrs={"class": "form-select"}),
            "batting_glove_size": forms.Select(attrs={"class": "form-select"}),
            "batting_helmet_size": forms.Select(attrs={"class": "form-select"}),
            "shorts_size": forms.Select(attrs={"class": "form-select"}),
            "grade": forms.Select(attrs={"class": "form-select"}),
            "division": forms.Select(attrs={"class": "form-select"}),
            "age_verification_document": forms.FileInput(
                attrs={"class": "form-control", "accept": ".pdf,.jpg,.jpeg,.png"}
            ),
            "age_verification_status": forms.Select(attrs={"class": "form-select"}),
            "age_verification_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Verificar si el usuario es padre/acudiente del jugador
        is_parent = False
        if (
            self.user
            and hasattr(self.user, "profile")
            and self.user.profile.is_parent
            and self.instance
        ):
            from .models import PlayerParent

            is_parent = PlayerParent.objects.filter(
                parent=self.user, player=self.instance
            ).exists()

        # Verificar si es manager o staff
        is_manager = False
        is_staff = False
        if self.user:
            if hasattr(self.user, "profile"):
                is_manager = self.user.profile.is_team_manager
            is_staff = self.user.is_staff or self.user.is_superuser

        # Si es padre, NO puede cambiar equipo ni número de jersey (solo admin/manager)
        if is_parent and not is_staff:
            # Campo team (Select) - deshabilitar pero mantener valor con hidden
            if self.instance and self.instance.team:
                self.fields["team"].widget.attrs["disabled"] = True
                self.fields["team"].widget.attrs["class"] = (
                    self.fields["team"].widget.attrs.get("class", "") + " bg-light"
                )
                # Agregar campo hidden para mantener el valor del team (disabled no envía valor en POST)
                from django import forms as django_forms

                self.fields["team_hidden"] = django_forms.CharField(
                    widget=django_forms.HiddenInput(),
                    required=False,
                    initial=self.instance.team.pk,
                )
            elif self.instance:
                # Si no tiene equipo, también deshabilitar
                self.fields["team"].widget.attrs["disabled"] = True
                self.fields["team"].widget.attrs["class"] = (
                    self.fields["team"].widget.attrs.get("class", "") + " bg-light"
                )
            self.fields["team"].required = False
            # Campo jersey_number - usar readonly (sí envía valor en POST)
            self.fields["jersey_number"].widget.attrs["readonly"] = True
            self.fields["jersey_number"].widget.attrs["class"] = (
                self.fields["jersey_number"].widget.attrs.get("class", "") + " bg-light"
            )
            self.fields["jersey_number"].required = False
            # Campo is_active - deshabilitar (no se puede cambiar)
            self.fields["is_active"].widget.attrs["disabled"] = True
            self.fields["is_active"].required = False

        # Si es manager, permitir cambiar el equipo (solo sus equipos)
        if is_manager and self.instance and self.instance.team:
            # Solo mostrar equipos del manager del equipo actual
            if hasattr(self.instance.team, "manager"):
                self.fields["team"].queryset = Team.objects.filter(
                    manager=self.instance.team.manager
                )

        # Si es padre, ocultar campos de verificación de edad (solo admins/managers pueden aprobar)
        if is_parent and not is_staff:
            self.fields["age_verification_status"].widget = forms.HiddenInput()
            self.fields["age_verification_notes"].widget = forms.HiddenInput()
            self.fields["age_verification_status"].required = False
            self.fields["age_verification_notes"].required = False

        # El documento de verificación de edad no es requerido
        self.fields["age_verification_document"].required = False

        # Inicializar campos de Player (secondary_position e is_pitcher)
        if self.instance and self.instance.pk:
            self.fields["secondary_position"].initial = self.instance.secondary_position
            self.fields["is_pitcher"].initial = self.instance.is_pitcher

        # Inicializar campos de User si hay una instancia
        if self.instance and hasattr(self.instance, "user"):
            user = self.instance.user
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

            # Campos de UserProfile
            if hasattr(user, "profile"):
                profile = user.profile
                self.fields["last_name2"].initial = getattr(profile, "last_name2", "")
                self.fields["phone"].initial = getattr(profile, "phone", "")
                self.fields["birth_date"].initial = getattr(profile, "birth_date", None)

                # Cargar la foto de perfil actual si existe
                if profile.profile_picture:
                    self.fields["profile_picture"].initial = profile.profile_picture

    def clean_is_pitcher(self):
        """Asegurar que is_pitcher siempre tenga un valor booleano"""
        # Obtener el valor del campo desde los datos originales
        # Django puede recibir múltiples valores si hay un checkbox y un hidden con el mismo name
        # Tomar el último valor (que será el del checkbox si está marcado, o el hidden si no)

        # Primero verificar si el campo está en los datos originales
        if "is_pitcher" not in self.data:
            # Si no está presente, retornar False
            return False

        # Obtener el valor desde cleaned_data (ya procesado por Django)
        value = self.cleaned_data.get("is_pitcher", False)

        # Si es una lista (múltiples valores), tomar el último
        if isinstance(value, list):
            value = value[-1] if value else False

        # Convertir a booleano
        # Si el valor es '1', 'on', True, o cualquier valor truthy, retornar True
        # Si es '0', False, '', None, o cualquier valor falsy, retornar False
        if value in (True, '1', 'on', 1, 'True', 'true'):
            return True
        elif value in (False, '0', '', None, 0, 'False', 'false'):
            return False
        # Por defecto, convertir a booleano
        return bool(value)

    def clean_secondary_position(self):
        """Asegurar que secondary_position siempre tenga un valor (puede ser vacío)"""
        # Si el campo no está en cleaned_data, retornar cadena vacía
        if "secondary_position" not in self.cleaned_data:
            return ""
        value = self.cleaned_data.get("secondary_position", "")
        return value or ""

    def clean(self):
        """Asegurar que secondary_position e is_pitcher siempre estén en cleaned_data"""
        cleaned_data = super().clean()
        # Asegurar que is_pitcher siempre esté en cleaned_data
        if "is_pitcher" not in cleaned_data:
            cleaned_data["is_pitcher"] = False
        # Asegurar que secondary_position siempre esté en cleaned_data
        if "secondary_position" not in cleaned_data:
            cleaned_data["secondary_position"] = ""
        return cleaned_data

    def save(self, commit=True):
        """Guardar los cambios, manteniendo los valores originales de campos deshabilitados para padres"""
        # Obtener el player (nuevo o existente)
        player = self.instance

        # Verificar si el usuario es padre/acudiente del jugador
        is_parent = False
        is_staff = False
        if hasattr(self, "user") and self.user:
            if hasattr(self.user, "profile") and self.user.profile.is_parent:
                from .models import PlayerParent
                is_parent = PlayerParent.objects.filter(
                    parent=self.user, player=player
                ).exists()
            is_staff = self.user.is_staff or self.user.is_superuser

        # Establecer TODOS los campos del Player explícitamente desde cleaned_data
        for field_name in self.Meta.fields:
            if field_name in self.cleaned_data:
                value = self.cleaned_data[field_name]
                # Para ForeignKey y FileField, establecer solo si hay valor
                if field_name in ["team", "age_verification_document"]:
                    if value is not None:
                        setattr(player, field_name, value)
                else:
                    # Para otros campos, establecer el valor directamente
                    setattr(player, field_name, value)

        # IMPORTANTE: Establecer secondary_position e is_pitcher DESPUÉS del bucle
        # y ANTES de las restricciones de padre, para asegurar que siempre se guarden
        # Usar cleaned_data directamente ya que clean() asegura que estén presentes
        player.secondary_position = self.cleaned_data.get("secondary_position", "") or ""
        player.is_pitcher = bool(self.cleaned_data.get("is_pitcher", False))

        # Si es padre (no staff), mantener los valores originales de campos restringidos
        if is_parent and not is_staff and player.pk:
            # Mantener valores originales de campos que no puede cambiar
            if "team_hidden" in self.cleaned_data and self.cleaned_data.get("team_hidden"):
                try:
                    from .models import Team
                    team_id = int(self.cleaned_data["team_hidden"])
                    player.team = Team.objects.get(pk=team_id)
                except (ValueError, Team.DoesNotExist, TypeError):
                    player.team = self.instance.team
            else:
                player.team = self.instance.team
            player.jersey_number = self.instance.jersey_number
            player.is_active = self.instance.is_active

            # Si se sube un nuevo documento, resetear el estado a "pending"
            if "age_verification_document" in self.cleaned_data and self.cleaned_data.get("age_verification_document"):
                if self.instance.age_verification_document != self.cleaned_data["age_verification_document"]:
                    player.age_verification_status = "pending"
                    player.age_verification_approved_date = None
                    player.age_verification_notes = ""
            else:
                # Mantener el estado original si no se sube documento nuevo
                player.age_verification_status = self.instance.age_verification_status
                player.age_verification_approved_date = self.instance.age_verification_approved_date
                player.age_verification_notes = self.instance.age_verification_notes

        # Guardar campos de User
        if hasattr(player, "user"):
            user = player.user
            user.first_name = self.cleaned_data.get("first_name", user.first_name)
            user.last_name = self.cleaned_data.get("last_name", user.last_name)
            user.email = self.cleaned_data.get("email", user.email)

            # Guardar campos de UserProfile
            if hasattr(user, "profile"):
                profile = user.profile
                profile.last_name2 = self.cleaned_data.get("last_name2", getattr(profile, "last_name2", ""))
                profile.phone = self.cleaned_data.get("phone", getattr(profile, "phone", ""))
                profile.birth_date = self.cleaned_data.get("birth_date", getattr(profile, "birth_date", None))

                # Guardar foto de perfil si se proporciona
                if self.cleaned_data.get("profile_picture"):
                    profile.profile_picture = self.cleaned_data["profile_picture"]

                if commit:
                    profile.save()

            if commit:
                user.save()

        # Guardar el Player
        # Asegurar una última vez que secondary_position e is_pitcher estén correctos antes de guardar
        # Esto es crítico porque estos campos podrían no guardarse si Django no los detecta como "changed"
        secondary_pos_value = self.cleaned_data.get("secondary_position", "") or ""
        is_pitcher_value = bool(self.cleaned_data.get("is_pitcher", False))

        # Establecer los valores explícitamente
        player.secondary_position = secondary_pos_value
        player.is_pitcher = is_pitcher_value

        if commit:
            # Guardar primero todos los campos normalmente
            player.save()

            # CRÍTICO: Forzar el guardado de estos campos específicos usando update_fields
            # Esto asegura que se guarden incluso si Django no detecta cambios
            player.secondary_position = secondary_pos_value
            player.is_pitcher = is_pitcher_value
            player.save(update_fields=["secondary_position", "is_pitcher"])

            # Verificar que se guardaron correctamente
            player.refresh_from_db()

            # Si aún no se guardaron correctamente, intentar una vez más
            if player.secondary_position != secondary_pos_value or player.is_pitcher != is_pitcher_value:
                player.secondary_position = secondary_pos_value
                player.is_pitcher = is_pitcher_value
                # Usar update() directamente en la base de datos como último recurso
                from django.db.models import F
                from .models import Player as PlayerModel
                PlayerModel.objects.filter(pk=player.pk).update(
                    secondary_position=secondary_pos_value,
                    is_pitcher=is_pitcher_value
                )
                player.refresh_from_db()

        return player


class HomeBannerForm(forms.ModelForm):
    """Formulario para crear/editar banners del home"""

    class Meta:
        model = HomeBanner
        fields = [
            "title",
            "description",
            "banner_type",
            "image",
            "gradient_color_1",
            "gradient_color_2",
            "gradient_color_3",
            "button_text",
            "button_url",
            "button_text_2",
            "button_url_2",
            "icon_class",
            "is_active",
            "order",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Banner title (optional)"),
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción del banner (opcional)",
                }
            ),
            "banner_type": forms.Select(attrs={"class": "form-select"}),
            "image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "gradient_color_1": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "color",
                    "placeholder": "#0d2c54",
                }
            ),
            "gradient_color_2": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "color",
                    "placeholder": "#132448",
                }
            ),
            "gradient_color_3": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "color",
                    "placeholder": "#64b5f6 (opcional)",
                }
            ),
            "button_text": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Texto del botón principal",
                }
            ),
            "button_url": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "/events/ o URL completa",
                }
            ),
            "button_text_2": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Texto del botón secundario",
                }
            ),
            "button_url_2": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "/accounts/panel/ o URL completa",
                }
            ),
            "icon_class": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "fa-trophy, fa-baseball-ball, etc.",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }

    def clean(self):
        cleaned_data = super().clean()
        banner_type = cleaned_data.get("banner_type")
        image = cleaned_data.get("image")

        # Si es tipo imagen, la imagen es requerida
        if banner_type == "image" and not image and not self.instance.pk:
            raise forms.ValidationError(
                {"image": 'La imagen es requerida para banners de tipo "Imagen".'}
            )

        # Si es tipo imagen y no hay imagen en la instancia existente, requerir imagen
        if banner_type == "image" and not image:
            if self.instance and not self.instance.image:
                raise forms.ValidationError(
                    {"image": 'La imagen es requerida para banners de tipo "Imagen".'}
                )

        return cleaned_data


class SiteSettingsForm(forms.ModelForm):
    """Formulario para configuraciones del sitio con soporte multiidioma"""

    class Meta:
        model = SiteSettings
        fields = [
            "schedule_image",
            # Schedule - English
            "schedule_title_en",
            "schedule_subtitle_en",
            "schedule_description_en",
            # Schedule - Spanish
            "schedule_title_es",
            "schedule_subtitle_es",
            "schedule_description_es",
            # Showcase
            "showcase_image",
            # Showcase - English
            "showcase_title_en",
            "showcase_subtitle_en",
            "showcase_description_en",
            # Showcase - Spanish
            "showcase_title_es",
            "showcase_subtitle_es",
            "showcase_description_es",
            # Contact Information
            "contact_email",
            "contact_phone",
            "contact_address",
        ]
        widgets = {
            "schedule_image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            # Schedule English
            "schedule_title_en": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "2026 EVENT CALENDAR",
                    "rows": 2,
                }
            ),
            "schedule_subtitle_en": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "REGIONAL EXPANSION AND NEW NATIONAL...",
                    "rows": 2,
                }
            ),
            "schedule_description_en": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Schedule description in English...",
                }
            ),
            # Schedule Spanish
            "schedule_title_es": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "CALENDARIO DE EVENTOS 2026",
                    "rows": 2,
                }
            ),
            "schedule_subtitle_es": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "EXPANSIÓN REGIONAL Y NUEVOS CAMPEONATOS...",
                    "rows": 2,
                }
            ),
            "schedule_description_es": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Descripción del Schedule en español...",
                }
            ),
            # Showcase
            "showcase_image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            # Showcase English
            "showcase_title_en": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "SHOWCASES AND PROSPECT GATEWAYS",
                    "rows": 2,
                }
            ),
            "showcase_subtitle_en": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "REGIONAL AND NATIONAL SHOWCASES",
                    "rows": 2,
                }
            ),
            "showcase_description_en": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Showcase description in English...",
                }
            ),
            # Showcase Spanish
            "showcase_title_es": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "SHOWCASES Y PORTALES DE PROSPECTO",
                    "rows": 2,
                }
            ),
            "showcase_subtitle_es": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "SHOWCASES REGIONALES Y NACIONALES",
                    "rows": 2,
                }
            ),
            "showcase_description_es": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Descripción del Showcase en español...",
                }
            ),
            # Contact Information
            "contact_email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "info@nscinternational.com",
                }
            ),
            "contact_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+1 (555) 123-4567",
                }
            ),
            "contact_address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "México",
                }
            ),
        }


class ContactSettingsForm(forms.ModelForm):
    """Formulario para editar solo la información de contacto"""

    class Meta:
        model = SiteSettings
        fields = [
            "contact_email",
            "contact_phone",
            "contact_address",
        ]
        widgets = {
            "contact_email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "info@nscinternational.com",
                }
            ),
            "contact_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+1 (555) 123-4567",
                }
            ),
            "contact_address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "México",
                }
            ),
        }


class ScheduleSettingsForm(forms.ModelForm):
    """Formulario para editar solo la sección Schedule"""

    class Meta:
        model = SiteSettings
        fields = [
            "schedule_image",
            "schedule_title_en",
            "schedule_subtitle_en",
            "schedule_description_en",
            "schedule_title_es",
            "schedule_subtitle_es",
            "schedule_description_es",
        ]
        widgets = {
            "schedule_image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "schedule_title_en": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "2026 EVENT CALENDAR",
                    "rows": 2,
                }
            ),
            "schedule_subtitle_en": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "REGIONAL EXPANSION AND NEW NATIONAL...",
                    "rows": 2,
                }
            ),
            "schedule_description_en": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Schedule description in English...",
                }
            ),
            "schedule_title_es": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "CALENDARIO DE EVENTOS 2026",
                    "rows": 2,
                }
            ),
            "schedule_subtitle_es": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "EXPANSIÓN REGIONAL Y NUEVOS CAMPEONATOS...",
                    "rows": 2,
                }
            ),
            "schedule_description_es": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Descripción del Schedule en español...",
                }
            ),
        }


class ShowcaseSettingsForm(forms.ModelForm):
    """Formulario para editar solo la sección Showcase"""

    class Meta:
        model = SiteSettings
        fields = [
            "showcase_image",
            "showcase_title_en",
            "showcase_subtitle_en",
            "showcase_description_en",
            "showcase_title_es",
            "showcase_subtitle_es",
            "showcase_description_es",
        ]
        widgets = {
            "showcase_image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "showcase_title_en": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "SHOWCASES AND PROSPECT GATEWAYS",
                    "rows": 2,
                }
            ),
            "showcase_subtitle_en": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "REGIONAL AND NATIONAL SHOWCASES",
                    "rows": 2,
                }
            ),
            "showcase_description_en": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Showcase description in English...",
                }
            ),
            "showcase_title_es": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "SHOWCASES Y PORTALES DE PROSPECTO",
                    "rows": 2,
                }
            ),
            "showcase_subtitle_es": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "SHOWCASES REGIONALES Y NACIONALES",
                    "rows": 2,
                }
            ),
            "showcase_description_es": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Descripción del Showcase en español...",
                }
            ),
        }


class SponsorForm(forms.ModelForm):
    """Formulario para crear/editar sponsors"""

    class Meta:
        model = Sponsor
        fields = [
            "name",
            "logo",
            "website_url",
            "is_active",
            "order",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del sponsor"}
            ),
            "logo": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "website_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://www.ejemplo.com",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }
