from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify
import re

from apps.locations.models import Country, State, City

from .models import UserProfile, Team, Player


class PublicRegistrationForm(UserCreationForm):
    """Formulario de registro público completo"""
    
    USER_TYPE_CHOICES = [
        ('player', 'Jugador'),
        ('team_manager', 'Manager de Equipo'),
    ]
    
    # Información básica de usuario
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer Apellido'})
    )
    last_name2 = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo Apellido (opcional)'})
    )
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(),
        label='Tipo de Registro'
    )
    
    # Información de contacto
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'})
    )
    phone_secondary = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono Secundario (opcional)'})
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    # Foto de perfil
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    
    # Ubicación
    country = forms.ModelChoiceField(
        queryset=Country.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label='Selecciona un país',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_country'})
    )
    state = forms.ModelChoiceField(
        queryset=State.objects.none(),
        required=False,
        empty_label='Selecciona un estado',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_state'})
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.none(),
        required=False,
        empty_label='Selecciona una ciudad',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_city'})
    )
    
    # Dirección
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'})
    )
    address_line_2 = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartamento, suite, etc. (opcional)'})
    )
    postal_code = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'})
    )
    
    # Información adicional
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Cuéntanos sobre ti...'})
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://tu-sitio-web.com'})
    )
    social_media = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@usuario_instagram, @usuario_twitter'})
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar el campo username del formulario
        if 'username' in self.fields:
            del self.fields['username']
        
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
        
        # Si hay un país seleccionado, cargar estados
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_id, is_active=True).order_by('name')
            except (ValueError, TypeError):
                pass
        
        # Si hay un estado seleccionado, cargar ciudades
        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(state_id=state_id, is_active=True).order_by('name')
            except (ValueError, TypeError):
                pass
    
    def generate_username(self, first_name, last_name, last_name2=None):
        """Genera un username único basado en nombre y apellidos"""
        # Limpiar y normalizar nombres
        first_name = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ]', '', first_name.strip().lower())
        last_name = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ]', '', last_name.strip().lower())
        last_name2 = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ]', '', last_name2.strip().lower()) if last_name2 and last_name2.strip() else None
        
        # Reemplazar acentos y caracteres especiales
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
            'ñ': 'n', 'Ñ': 'n'
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
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado. Por favor, usa otro email.')
        return email
    
    def clean_first_name(self):
        """Validar que el nombre no esté vacío"""
        first_name = self.cleaned_data.get('first_name')
        if not first_name or not first_name.strip():
            raise forms.ValidationError('El nombre es requerido.')
        return first_name.strip()
    
    def clean_last_name(self):
        """Validar que el apellido no esté vacío"""
        last_name = self.cleaned_data.get('last_name')
        if not last_name or not last_name.strip():
            raise forms.ValidationError('El primer apellido es requerido.')
        return last_name.strip()
    
    def clean_last_name2(self):
        """Validar y limpiar el segundo apellido"""
        last_name2 = self.cleaned_data.get('last_name2', '')
        if last_name2:
            return last_name2.strip()
        return ''
    
    def save(self, commit=True):
        # Generar username automáticamente
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        last_name2 = self.cleaned_data.get('last_name2', '')
        username = self.generate_username(first_name, last_name, last_name2)
        
        # Combinar apellidos para el campo last_name de User
        if last_name2:
            full_last_name = f"{last_name} {last_name2}"
        else:
            full_last_name = last_name
        
        # Crear usuario con username generado
        user = User.objects.create_user(
            username=username,
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=first_name,
            last_name=full_last_name
        )
        
        if commit:
            # Crear perfil de usuario
            profile = UserProfile.objects.create(
                user=user,
                user_type=self.cleaned_data['user_type'],
                phone=self.cleaned_data.get('phone', ''),
                phone_secondary=self.cleaned_data.get('phone_secondary', ''),
                birth_date=self.cleaned_data.get('birth_date'),
                profile_picture=self.cleaned_data.get('profile_picture'),
                country=self.cleaned_data.get('country'),
                state=self.cleaned_data.get('state'),
                city=self.cleaned_data.get('city'),
                address=self.cleaned_data.get('address', ''),
                address_line_2=self.cleaned_data.get('address_line_2', ''),
                postal_code=self.cleaned_data.get('postal_code', ''),
                bio=self.cleaned_data.get('bio', ''),
                website=self.cleaned_data.get('website', ''),
                social_media=self.cleaned_data.get('social_media', ''),
            )
            # Si es jugador, crear perfil de jugador
            if self.cleaned_data['user_type'] == 'player':
                Player.objects.create(user=user)
        
        return user


class UserProfileForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""
    
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'address', 'country', 'state', 'city', 'postal_code',
            'birth_date', 'profile_picture', 'bio'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'style': 'display: none;'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Cuéntanos sobre ti...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos de ubicación con ModelChoiceField
        self.fields['country'] = forms.ModelChoiceField(
            queryset=Country.objects.filter(is_active=True).order_by('name'),
            required=False,
            empty_label='Selecciona un país',
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_country'})
        )
        
        self.fields['state'] = forms.ModelChoiceField(
            queryset=State.objects.none(),
            required=False,
            empty_label='Selecciona un estado',
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_state'})
        )
        
        self.fields['city'] = forms.ModelChoiceField(
            queryset=City.objects.none(),
            required=False,
            empty_label='Selecciona una ciudad',
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_city'})
        )
        
        # Si hay una instancia (edición), cargar estados y ciudades
        if self.instance and self.instance.pk:
            if self.instance.country:
                self.fields['state'].queryset = State.objects.filter(
                    country=self.instance.country, is_active=True
                ).order_by('name')
            if self.instance.state:
                self.fields['city'].queryset = City.objects.filter(
                    state=self.instance.state, is_active=True
                ).order_by('name')
        
        # Si hay datos en POST, cargar dinámicamente
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(
                    country_id=country_id, is_active=True
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        
        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(
                    state_id=state_id, is_active=True
                ).order_by('name')
            except (ValueError, TypeError):
                pass


class UserUpdateForm(forms.ModelForm):
    """Formulario para actualizar información básica del usuario"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class TeamForm(forms.ModelForm):
    """Formulario para crear/editar equipos"""
    
    class Meta:
        model = Team
        fields = [
            'name', 'description', 'logo', 'country', 'state', 'city',
            'website', 'contact_email', 'contact_phone'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del equipo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción del equipo'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://tu-sitio-web.com'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ejemplo.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Campos de ubicación con ModelChoiceField
        self.fields['country'] = forms.ModelChoiceField(
            queryset=Country.objects.filter(is_active=True).order_by('name'),
            required=False,
            empty_label='Selecciona un país',
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_team_country'})
        )
        
        self.fields['state'] = forms.ModelChoiceField(
            queryset=State.objects.none(),
            required=False,
            empty_label='Selecciona un estado',
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_team_state'})
        )
        
        self.fields['city'] = forms.ModelChoiceField(
            queryset=City.objects.none(),
            required=False,
            empty_label='Selecciona una ciudad',
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_team_city'})
        )
        
        # Si hay una instancia (edición), cargar estados y ciudades
        if self.instance and self.instance.pk:
            if self.instance.country:
                self.fields['state'].queryset = State.objects.filter(
                    country=self.instance.country, is_active=True
                ).order_by('name')
            if self.instance.state:
                self.fields['city'].queryset = City.objects.filter(
                    state=self.instance.state, is_active=True
                ).order_by('name')
        
        # Si hay datos en POST, cargar dinámicamente
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(
                    country_id=country_id, is_active=True
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        
        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(
                    state_id=state_id, is_active=True
                ).order_by('name')
            except (ValueError, TypeError):
                pass


class PlayerRegistrationForm(forms.ModelForm):
    """Formulario para que managers registren jugadores"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer Apellido'})
    )
    last_name2 = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo Apellido (opcional)'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña temporal'}),
        help_text='El jugador podrá cambiar su contraseña después'
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'})
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    class Meta:
        model = Player
        fields = [
            'team', 'jersey_number', 'position', 'height', 'weight',
            'batting_hand', 'throwing_hand', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relation', 'medical_conditions'
        ]
        widgets = {
            'team': forms.Select(attrs={'class': 'form-select'}),
            'jersey_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ej: 5'10\""}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'batting_hand': forms.Select(attrs={'class': 'form-select'}),
            'throwing_hand': forms.Select(attrs={'class': 'form-select'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Padre, Madre, etc.'}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)
        if self.manager:
            # Solo mostrar equipos que el manager gestiona
            self.fields['team'].queryset = Team.objects.filter(manager=self.manager)
    
    def generate_username(self, first_name, last_name, last_name2=None):
        """Genera un username único basado en nombre y apellidos"""
        first_name = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ]', '', first_name.strip().lower())
        last_name = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ]', '', last_name.strip().lower())
        last_name2 = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ]', '', last_name2.strip().lower()) if last_name2 and last_name2.strip() else None
        
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
            'ñ': 'n', 'Ñ': 'n'
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
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado. Por favor, usa otro email.')
        return email
    
    def clean_first_name(self):
        """Validar que el nombre no esté vacío"""
        first_name = self.cleaned_data.get('first_name')
        if not first_name or not first_name.strip():
            raise forms.ValidationError('El nombre es requerido.')
        return first_name.strip()
    
    def clean_last_name(self):
        """Validar que el apellido no esté vacío"""
        last_name = self.cleaned_data.get('last_name')
        if not last_name or not last_name.strip():
            raise forms.ValidationError('El primer apellido es requerido.')
        return last_name.strip()
    
    def clean_last_name2(self):
        """Validar y limpiar el segundo apellido"""
        last_name2 = self.cleaned_data.get('last_name2', '')
        if last_name2:
            return last_name2.strip()
        return ''
    
    def save(self, commit=True):
        # Generar username automáticamente
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        last_name2 = self.cleaned_data.get('last_name2', '')
        username = self.generate_username(first_name, last_name, last_name2)
        
        # Combinar apellidos para el campo last_name de User
        if last_name2:
            full_last_name = f"{last_name} {last_name2}"
        else:
            full_last_name = last_name
        
        # Crear usuario primero
        user = User.objects.create_user(
            username=username,
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=first_name,
            last_name=full_last_name
        )
        
        # Crear perfil de usuario
        profile = UserProfile.objects.create(
            user=user,
            user_type='player',
            phone=self.cleaned_data.get('phone', ''),
            birth_date=self.cleaned_data.get('birth_date')
        )
        
        # Crear perfil de jugador directamente (no usar super().save() porque requiere user)
        player = Player.objects.create(
            user=user,
            team=self.cleaned_data.get('team'),
            jersey_number=self.cleaned_data.get('jersey_number'),
            position=self.cleaned_data.get('position'),
            height=self.cleaned_data.get('height'),
            weight=self.cleaned_data.get('weight'),
            batting_hand=self.cleaned_data.get('batting_hand'),
            throwing_hand=self.cleaned_data.get('throwing_hand'),
            emergency_contact_name=self.cleaned_data.get('emergency_contact_name'),
            emergency_contact_phone=self.cleaned_data.get('emergency_contact_phone'),
            emergency_contact_relation=self.cleaned_data.get('emergency_contact_relation'),
            medical_conditions=self.cleaned_data.get('medical_conditions'),
        )
        
        return player


class PlayerUpdateForm(forms.ModelForm):
    """Formulario para actualizar información de jugador"""
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'id_profile_picture',
            'style': 'display: none;'
        }),
        help_text='Sube una nueva foto de perfil'
    )
    
    class Meta:
        model = Player
        fields = [
            'team', 'jersey_number', 'position', 'height', 'weight',
            'batting_hand', 'throwing_hand', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relation', 'medical_conditions', 'is_active'
        ]
        widgets = {
            'team': forms.Select(attrs={'class': 'form-select'}),
            'jersey_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número de jersey'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ej: 6'2\""}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Peso en libras'}),
            'batting_hand': forms.Select(attrs={'class': 'form-select'}),
            'throwing_hand': forms.Select(attrs={'class': 'form-select'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del contacto'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono del contacto'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Padre, Madre, etc.'}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Especifica condiciones médicas o "Ninguna"'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es manager, permitir cambiar el equipo
        if self.instance and self.instance.team:
            # Solo mostrar equipos del manager del equipo actual
            if hasattr(self.instance.team, 'manager'):
                self.fields['team'].queryset = Team.objects.filter(
                    manager=self.instance.team.manager
                )
        
        # Cargar la foto de perfil actual si existe
        if self.instance and hasattr(self.instance, 'user'):
            if hasattr(self.instance.user, 'profile'):
                if self.instance.user.profile.profile_picture:
                    self.fields['profile_picture'].initial = self.instance.user.profile.profile_picture

