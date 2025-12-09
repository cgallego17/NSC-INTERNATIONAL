from django import forms
from django.db.models import Q
import unicodedata
from apps.locations.models import Country, Season, State, City, Rule, Site, Hotel
from .models import (
    Event,
    EventCategory,
    EventType,
    GateFeeType,
    EventContact,
    Division,
)


class EventForm(forms.ModelForm):
    """Formulario para crear eventos"""

    class Meta:
        model = Event
        fields = [
            "season",  # TEMPORADA DEL EVENTO SELECT
            "title",  # NOMBRE DEL EVENTO
            "description",  # DESCRIPCION DEL EVENTO HTML
            "country",  # PAIS SELECT
            "state",  # ESTADO SELECT
            "city",  # CIUDAD SELECT
            "rule",  # REGLAMENTO DEL EVENTO SELECT
            "event_type",  # TIPO DE EVENTO SELECT (LIGA, SHOWCASES, TORNEO, WORLD SERIES)
            "divisions",  # DIVISIONES SELECT MULTIPLE
            "start_date",  # INICIO EVENTO DATE
            "end_date",  # FINAL EVENTO DATE
            "entry_deadline",  # DIA LIMITE DE REGISTRO DATE
            "default_entry_fee",  # PRECIO EVENTO
            "payment_deadline",  # DIA LIMITE DE PAGO DATE
            "gate_fee_type",  # TIPO DE GATE FEE
            "gate_fee_amount",  # PRECIO GATE FEE
            "primary_site",  # SITIO DEL EVENTO PRIMARY SELECT
            "additional_sites",  # SITIO DEL EVENTO ADICIONALES SELECT MULTIPLE
            "hotel",  # HOTEL SEDE SELECT
            "additional_hotels",  # HOTELES ADICIONALES SELECT MULTIPLE
            "event_contact",  # CONTACTO EVENTO SELECT
            "image",  # LOGO EVENTO
            "video_url",  # VIDEO EVENTO
            "email_welcome_body",  # BODY DEL CORREO HTML
        ]
        widgets = {
            "season": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": True,
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                    "placeholder": "Nombre del Evento",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "required": False,
                    "placeholder": "Descripción detallada del evento (HTML permitido)",
                }
            ),
            "country": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": True,
                }
            ),
            "state": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": True,
                }
            ),
            "city": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": True,
                }
            ),
            "rule": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": True,
                }
            ),
            "event_type": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": True,
                }
            ),
            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "required": False,
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "required": False,
                }
            ),
            "entry_deadline": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "required": False,
                }
            ),
            "default_entry_fee": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                    "required": False,
                }
            ),
            "payment_deadline": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "required": False,
                }
            ),
            "gate_fee_type": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": False,
                }
            ),
            "gate_fee_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                    "required": False,
                }
            ),
            "primary_site": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": False,
                }
            ),
            "additional_sites": forms.CheckboxSelectMultiple(
                attrs={
                    "class": "form-check-input",
                    "required": False,
                }
            ),
            "hotel": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": False,
                }
            ),
            "additional_hotels": forms.CheckboxSelectMultiple(
                attrs={
                    "class": "form-check-input",
                    "required": False,
                }
            ),
            "event_contact": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": False,
                }
            ),
            "divisions": forms.CheckboxSelectMultiple(
                attrs={
                    "class": "form-check-input",
                    "required": False,
                }
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                    "required": False,
                }
            ),
            "video_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://youtube.com/watch?v=... o https://vimeo.com/...",
                    "required": False,
                }
            ),
            "email_welcome_body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 10,
                    "required": False,
                    "placeholder": "Contenido HTML del correo de bienvenida...",
                }
            ),
        }
        labels = {
            "season": "Temporada del Evento *",
            "title": "Nombre del Evento *",
            "description": "Descripción del Evento (HTML)",
            "country": "País *",
            "state": "Estado *",
            "city": "Ciudad *",
            "rule": "Reglamento del Evento *",
            "event_type": "Tipo de Evento *",
            "divisions": "Divisiones",
            "start_date": "Inicio Evento",
            "end_date": "Final Evento",
            "entry_deadline": "Día Límite de Registro",
            "default_entry_fee": "Precio Evento",
            "payment_deadline": "Día Límite de Pago",
            "gate_fee_type": "Tipo de Gate Fee",
            "gate_fee_amount": "Precio Gate Fee",
            "primary_site": "Sitio del Evento (Primary)",
            "additional_sites": "Sitios del Evento (Adicionales)",
            "hotel": "Hotel Sede",
            "additional_hotels": "Hoteles Adicionales",
            "event_contact": "Contacto del Evento",
            "image": "Logo del Evento",
            "video_url": "Video del Evento",
            "email_welcome_body": "Cuerpo del Correo de Bienvenida (HTML)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configurar querysets - Optimizado para rendimiento
        # Season: generalmente pocos registros
        self.fields["season"].queryset = Season.objects.filter(is_active=True).order_by(
            "name"
        )[
            :100
        ]  # Limitar por seguridad

        # Event Type: Configuración simple y directa
        # Obtener todos los tipos activos
        event_types = EventType.objects.filter(is_active=True)

        # Ordenar según el orden específico: LIGA, SHOWCASES, TORNEO, WORLD SERIES
        event_type_order = ["LIGA", "SHOWCASES", "TORNEO", "WORLD SERIES"]

        # Obtener todos los tipos activos
        all_types = list(event_types)

        if all_types:
            # Crear diccionario para acceso rápido (case-insensitive)
            types_dict = {et.name.upper(): et for et in all_types}

            # Ordenar según el orden especificado
            ordered_types = []
            for name in event_type_order:
                name_upper = name.upper()
                if name_upper in types_dict:
                    ordered_types.append(types_dict[name_upper])

            # Agregar cualquier tipo que no esté en la lista de orden
            for et in all_types:
                if et not in ordered_types:
                    ordered_types.append(et)

            # Crear lista de IDs en el orden deseado
            ordered_ids = [et.id for et in ordered_types]

            # Usar queryset con anotación para mantener el orden
            from django.db.models import Case, When, IntegerField

            when_conditions = [
                When(id=id_val, then=pos) for pos, id_val in enumerate(ordered_ids)
            ]
            self.fields["event_type"].queryset = (
                EventType.objects.filter(id__in=ordered_ids)
                .annotate(
                    sort_order=Case(
                        *when_conditions,
                        default=999,
                        output_field=IntegerField(),
                    )
                )
                .order_by("sort_order")
            )
        else:
            # Si no hay tipos, usar queryset vacío
            self.fields["event_type"].queryset = EventType.objects.none()

        if not self.fields["event_type"].empty_label:
            self.fields["event_type"].empty_label = "Seleccione un tipo de evento"

        # Country: generalmente pocos registros
        # Filtrar duplicados normalizando nombres (sin acentos)
        all_countries = Country.objects.filter(is_active=True).order_by("name")

        # Normalizar nombres y eliminar duplicados
        seen_normalized = set()
        unique_countries = []
        for country in all_countries:
            # Normalizar nombre (remover acentos)
            nfd = unicodedata.normalize("NFD", country.name.lower().strip())
            normalized = "".join(c for c in nfd if unicodedata.category(c) != "Mn")

            if normalized not in seen_normalized:
                seen_normalized.add(normalized)
                unique_countries.append(country.id)

        self.fields["country"].queryset = Country.objects.filter(
            id__in=unique_countries
        ).order_by("name")[
            :200
        ]  # Limitar por seguridad

        # State: QUERYSET VACÍO INICIALMENTE - Se carga dinámicamente con JavaScript cuando se selecciona un país
        # Esto es crítico para el rendimiento y para filtrar correctamente por país
        self.fields["state"].queryset = State.objects.none()
        self.fields["state"].widget.attrs["disabled"] = True
        self.fields["state"].required = False

        # City: QUERYSET VACÍO INICIALMENTE - Se carga dinámicamente con JavaScript cuando se selecciona un estado
        # Esto es crítico para el rendimiento si hay miles de ciudades
        # El campo se hace required en el método clean() cuando se envía el formulario
        self.fields["city"].queryset = City.objects.none()
        self.fields["city"].widget.attrs["disabled"] = True
        self.fields["city"].required = False

        # Rule: generalmente pocos registros
        self.fields["rule"].queryset = Rule.objects.filter(is_active=True).order_by(
            "name"
        )[
            :100
        ]  # Limitar por seguridad

        # Gate Fee Type: configurar queryset
        self.fields["gate_fee_type"].queryset = GateFeeType.objects.filter(
            is_active=True
        ).order_by("name")

        if not self.fields["gate_fee_type"].empty_label:
            self.fields["gate_fee_type"].empty_label = "Seleccione un tipo de gate fee"

        # Primary Site: configurar queryset
        # Filtrar sitios activos
        self.fields["primary_site"].queryset = Site.objects.filter(
            is_active=True
        ).order_by("site_name")[
            :500
        ]  # Limitar por seguridad

        if not self.fields["primary_site"].empty_label:
            self.fields["primary_site"].empty_label = "Seleccione un sitio"

        # Additional Sites: configurar queryset (selección múltiple)
        # Filtrar sitios activos
        self.fields["additional_sites"].queryset = Site.objects.filter(
            is_active=True
        ).order_by("site_name")[
            :500
        ]  # Limitar por seguridad

        # Hotel Sede: configurar queryset
        # Filtrar hoteles activos
        self.fields["hotel"].queryset = Hotel.objects.filter(is_active=True).order_by(
            "hotel_name"
        )[
            :500
        ]  # Limitar por seguridad

        if not self.fields["hotel"].empty_label:
            self.fields["hotel"].empty_label = "Seleccione un hotel"

        # Additional Hotels: configurar queryset (selección múltiple)
        # Filtrar hoteles activos
        self.fields["additional_hotels"].queryset = Hotel.objects.filter(
            is_active=True
        ).order_by("hotel_name")[
            :500
        ]  # Limitar por seguridad

        # Event Contact: configurar queryset
        # Filtrar contactos activos
        self.fields["event_contact"].queryset = EventContact.objects.filter(
            is_active=True
        ).order_by("name")[
            :500
        ]  # Limitar por seguridad

        if not self.fields["event_contact"].empty_label:
            self.fields["event_contact"].empty_label = "Seleccione un contacto"

        # Divisions: configurar queryset (selección múltiple)
        # Filtrar divisiones activas
        self.fields["divisions"].queryset = Division.objects.filter(
            is_active=True
        ).order_by("name")[
            :500
        ]  # Limitar por seguridad

        # Establecer valores por defecto - Optimizado
        if not self.instance.pk:
            # Usar filter().first() en lugar de get() para evitar excepciones
            us_country = Country.objects.filter(
                name="United States", is_active=True
            ).first()
            if us_country:
                self.fields["country"].initial = us_country

    def clean(self):
        cleaned_data = super().clean()

        # Validar que city esté seleccionado si state está seleccionado
        state = cleaned_data.get("state")
        city = cleaned_data.get("city")

        if state and not city:
            self.add_error(
                "city", "Debe seleccionar una ciudad cuando se selecciona un estado."
            )

        # Validar fechas
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        entry_deadline = cleaned_data.get("entry_deadline")

        # Validar que end_date sea posterior a start_date
        if start_date and end_date:
            if end_date < start_date:
                self.add_error(
                    "end_date",
                    "La fecha de finalización debe ser posterior a la fecha de inicio.",
                )

        # Validar que entry_deadline sea anterior o igual a start_date
        if entry_deadline and start_date:
            if entry_deadline > start_date:
                self.add_error(
                    "entry_deadline",
                    "El día límite de registro debe ser anterior o igual a la fecha de inicio del evento.",
                )

        # Validar payment_deadline
        payment_deadline = cleaned_data.get("payment_deadline")

        # Validar que payment_deadline sea anterior o igual a start_date
        if payment_deadline and start_date:
            if payment_deadline > start_date:
                self.add_error(
                    "payment_deadline",
                    "El día límite de pago debe ser anterior o igual a la fecha de inicio del evento.",
                )

        # Validar que default_entry_fee sea positivo si está presente
        default_entry_fee = cleaned_data.get("default_entry_fee")
        if default_entry_fee is not None and default_entry_fee < 0:
            self.add_error(
                "default_entry_fee",
                "El precio del evento no puede ser negativo.",
            )

        # Validar que gate_fee_amount sea positivo si está presente
        gate_fee_amount = cleaned_data.get("gate_fee_amount")
        if gate_fee_amount is not None and gate_fee_amount < 0:
            self.add_error(
                "gate_fee_amount",
                "El precio del gate fee no puede ser negativo.",
            )

        return cleaned_data


# ===== FORMULARIOS PARA GESTIÓN DE DATOS =====


class EventContactForm(forms.ModelForm):
    """Formulario personalizado para EventContact"""

    class Meta:
        model = EventContact
        fields = [
            "name",
            "photo",
            "phone",
            "email",
            "country",
            "state",
            "city",
            "information",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre completo del contacto",
                    "required": True,
                }
            ),
            "photo": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: +1 234 567 8900",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "correo@ejemplo.com",
                }
            ),
            "country": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "state": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "city": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "information": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Información adicional sobre el contacto...",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
        labels = {
            "name": "Nombre",
            "photo": "Foto",
            "phone": "Teléfono",
            "email": "Email",
            "country": "País",
            "state": "Estado",
            "city": "Ciudad",
            "information": "Información Adicional",
            "is_active": "Activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.locations.models import Country, State, City

        # Optimizar queryset de países - aumentar límite para evitar problemas de validación
        # Si hay datos POST, primero intentar actualizar el queryset con el país seleccionado
        if self.data:
            country_id = self.data.get("country") or self.data.get("country_hidden")
            if country_id:
                try:
                    country_id = int(country_id)
                    country_obj = Country.objects.filter(
                        pk=country_id, is_active=True
                    ).first()
                    if country_obj:
                        # Si hay un país seleccionado en POST, incluirlo en el queryset
                        all_countries = Country.objects.filter(
                            Q(pk=country_obj.pk) | Q(is_active=True)
                        ).order_by("name")
                    else:
                        all_countries = Country.objects.filter(is_active=True).order_by(
                            "name"
                        )
                except (ValueError, TypeError):
                    all_countries = Country.objects.filter(is_active=True).order_by(
                        "name"
                    )
            else:
                all_countries = Country.objects.filter(is_active=True).order_by("name")
        else:
            # Sin datos POST, usar queryset normal pero con límite mayor
            all_countries = Country.objects.filter(is_active=True).order_by("name")

        # Normalizar nombres y eliminar duplicados
        seen_normalized = set()
        unique_countries = []
        for country in all_countries:
            # Normalizar nombre (remover acentos)
            nfd = unicodedata.normalize("NFD", country.name.lower().strip())
            normalized = "".join(c for c in nfd if unicodedata.category(c) != "Mn")

            if normalized not in seen_normalized:
                seen_normalized.add(normalized)
                unique_countries.append(country.id)

        self.fields["country"].queryset = Country.objects.filter(
            id__in=unique_countries
        ).order_by("name")[:500]

        self.fields["country"].empty_label = "Seleccione un país"
        self.fields["country"].required = False

        # Si hay datos POST, actualizar querysets ANTES de la validación de Django
        # Esto es crítico porque Django valida el queryset antes de clean_*
        if self.data:
            # Actualizar queryset del país si hay un valor seleccionado
            country_id = self.data.get("country") or self.data.get("country_hidden")
            state_id = self.data.get("state") or self.data.get("state_hidden")
            city_id = self.data.get("city") or self.data.get("city_hidden")

            if country_id:
                try:
                    country_id = int(country_id)
                    country_obj = Country.objects.filter(
                        pk=country_id, is_active=True
                    ).first()
                    if country_obj:
                        # Actualizar queryset para incluir este país
                        self.fields["country"].queryset = Country.objects.filter(
                            pk=country_obj.pk
                        )
                        self.fields["country"].empty_label = "Seleccione un país"
                        # Asegurar que el campo no esté disabled
                        if "disabled" in self.fields["country"].widget.attrs:
                            del self.fields["country"].widget.attrs["disabled"]
                except (ValueError, TypeError):
                    pass

            if state_id:
                try:
                    state_id = int(state_id)
                    state_obj = State.objects.filter(
                        pk=state_id, is_active=True
                    ).first()
                    if state_obj:
                        # Actualizar queryset para incluir este estado
                        self.fields["state"].queryset = State.objects.filter(
                            pk=state_obj.pk
                        )
                        self.fields["state"].empty_label = "Seleccione un estado"
                        # Asegurar que el campo no esté disabled
                        if "disabled" in self.fields["state"].widget.attrs:
                            del self.fields["state"].widget.attrs["disabled"]
                except (ValueError, TypeError):
                    pass

            if city_id:
                try:
                    city_id = int(city_id)
                    city_obj = City.objects.filter(pk=city_id, is_active=True).first()
                    if city_obj:
                        # Actualizar queryset para incluir esta ciudad
                        self.fields["city"].queryset = City.objects.filter(
                            pk=city_obj.pk
                        )
                        self.fields["city"].empty_label = "Seleccione una ciudad"
                        # Asegurar que el campo no esté disabled
                        if "disabled" in self.fields["city"].widget.attrs:
                            del self.fields["city"].widget.attrs["disabled"]
                except (ValueError, TypeError):
                    pass

        # Estados y ciudades se cargarán dinámicamente
        if self.instance and self.instance.pk:
            # Modo edición: cargar datos relacionados si existen
            if self.instance.country:
                if not self.data:  # Solo si no hay POST (primera carga)
                    self.fields["state"].queryset = State.objects.filter(
                        country=self.instance.country, is_active=True
                    ).order_by("name")[:100]
                    self.fields["state"].empty_label = "Seleccione un estado"
            else:
                if not self.data:  # Solo si no hay POST
                    self.fields["state"].queryset = State.objects.none()
                    self.fields["state"].empty_label = "Seleccione un país primero"
                    self.fields["state"].widget.attrs["disabled"] = True

            if self.instance.state:
                if not self.data:  # Solo si no hay POST (primera carga)
                    self.fields["city"].queryset = City.objects.filter(
                        state=self.instance.state, is_active=True
                    ).order_by("name")[:200]
                    self.fields["city"].empty_label = "Seleccione una ciudad"
            else:
                if not self.data:  # Solo si no hay POST
                    self.fields["city"].queryset = City.objects.none()
                    self.fields["city"].empty_label = "Seleccione un estado primero"
                    self.fields["city"].widget.attrs["disabled"] = True
        else:
            # Modo creación: campos vacíos
            if not self.data:  # Solo si no hay POST
                self.fields["state"].queryset = State.objects.none()
                self.fields["state"].empty_label = "Seleccione un país primero"
                self.fields["state"].widget.attrs["disabled"] = True
                self.fields["state"].required = False

                self.fields["city"].queryset = City.objects.none()
                self.fields["city"].empty_label = "Seleccione un estado primero"
                self.fields["city"].widget.attrs["disabled"] = True
                self.fields["city"].required = False

    def clean_country(self):
        """Permitir cualquier país válido, incluso si no está en el queryset inicial limitado"""
        country = self.cleaned_data.get("country")
        if not country:
            # Intentar obtener del POST directamente
            country_id = self.data.get("country") or self.data.get("country_hidden")
            if country_id:
                try:
                    from apps.locations.models import Country

                    country_id = int(country_id)
                    country_obj = Country.objects.filter(
                        pk=country_id, is_active=True
                    ).first()
                    if country_obj:
                        # Actualizar el queryset para que Django acepte el valor
                        self.fields["country"].queryset = Country.objects.filter(
                            pk=country_obj.pk
                        )
                        return country_obj
                except (ValueError, TypeError):
                    pass
            return None
        # Si el país está en cleaned_data, verificar que sea válido
        from apps.locations.models import Country

        try:
            country_obj = Country.objects.get(pk=country.pk, is_active=True)
            return country_obj
        except Country.DoesNotExist:
            # Si no existe, intentar obtener del POST
            country_id = self.data.get("country") or self.data.get("country_hidden")
            if country_id:
                try:
                    country_id = int(country_id)
                    country_obj = Country.objects.filter(
                        pk=country_id, is_active=True
                    ).first()
                    if country_obj:
                        self.fields["country"].queryset = Country.objects.filter(
                            pk=country_obj.pk
                        )
                        return country_obj
                except (ValueError, TypeError):
                    pass
            raise forms.ValidationError("El país seleccionado no es válido.")


class EventTypeForm(forms.ModelForm):
    """Formulario personalizado para EventType"""

    class Meta:
        model = EventType
        fields = ["name", "description", "color", "icon", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: LIGA, SHOWCASES, TORNEO",
                    "required": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción del tipo de evento...",
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "text",
                    "placeholder": "#0d2c54",
                    "pattern": "^#[0-9A-Fa-f]{6}$",
                }
            ),
            "icon": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: fas fa-calendar, bi bi-trophy",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
        labels = {
            "name": "Nombre",
            "description": "Descripción",
            "color": "Color",
            "icon": "Icono",
            "is_active": "Activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            # Valores por defecto para nuevos tipos
            self.fields["color"].initial = "#0d2c54"
            self.fields["icon"].initial = "fas fa-calendar"
            self.fields["is_active"].initial = True


class GateFeeTypeForm(forms.ModelForm):
    """Formulario personalizado para GateFeeType"""

    class Meta:
        model = GateFeeType
        fields = ["name", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Por Persona, Por Día, Por Evento",
                    "required": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción del tipo de tarifa...",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
        labels = {
            "name": "Nombre",
            "description": "Descripción",
            "is_active": "Activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["is_active"].initial = True
