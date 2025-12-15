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
            "country": forms.TextInput(
                attrs={
                    "class": "form-control autocomplete-input",
                    "required": True,
                    "placeholder": "Buscar país...",
                    "autocomplete": "off",
                    "data-field": "country",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "class": "form-control autocomplete-input",
                    "required": True,
                    "placeholder": "Buscar estado...",
                    "autocomplete": "off",
                    "data-field": "state",
                    "disabled": True,
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control autocomplete-input",
                    "required": True,
                    "placeholder": "Buscar ciudad...",
                    "autocomplete": "off",
                    "data-field": "city",
                    "disabled": True,
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
                },
                format="%Y-%m-%d",
            ),
            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "required": False,
                },
                format="%Y-%m-%d",
            ),
            "entry_deadline": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "required": False,
                },
                format="%Y-%m-%d",
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
                },
                format="%Y-%m-%d",
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
            "event_contact": forms.CheckboxSelectMultiple(
                attrs={
                    "class": "form-check-input",
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
            "event_contact": "Contactos",
            "image": "Logo del Evento",
            "video_url": "Video del Evento",
            "email_welcome_body": "Cuerpo del Correo de Bienvenida (HTML)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Asegurar que las fechas se formateen correctamente para inputs type="date"
        if self.instance and self.instance.pk:
            if self.instance.start_date:
                self.fields["start_date"].initial = self.instance.start_date.strftime(
                    "%Y-%m-%d"
                )
            if self.instance.end_date:
                self.fields["end_date"].initial = self.instance.end_date.strftime(
                    "%Y-%m-%d"
                )
            if self.instance.entry_deadline:
                self.fields["entry_deadline"].initial = (
                    self.instance.entry_deadline.strftime("%Y-%m-%d")
                )
            if self.instance.payment_deadline:
                self.fields["payment_deadline"].initial = (
                    self.instance.payment_deadline.strftime("%Y-%m-%d")
                )

            # Asegurar que primary_site y additional_sites estén en el queryset
            if self.instance.primary_site:
                # Agregar el sitio actual al queryset si no está incluido
                current_site = self.instance.primary_site
                if current_site not in self.fields["primary_site"].queryset:
                    self.fields["primary_site"].queryset = Site.objects.filter(
                        is_active=True
                    ).order_by("site_name") | Site.objects.filter(id=current_site.id)

            # Asegurar que hotel esté en el queryset y establecer el valor inicial
            if self.instance.hotel:
                # Agregar el hotel actual al queryset si no está incluido
                current_hotel = self.instance.hotel
                if current_hotel not in self.fields["hotel"].queryset:
                    self.fields["hotel"].queryset = Hotel.objects.filter(
                        is_active=True
                    ).order_by("hotel_name") | Hotel.objects.filter(id=current_hotel.id)
                # Establecer el valor inicial explícitamente
                if not self.data:  # Solo si no hay POST (primera carga)
                    self.fields["hotel"].initial = current_hotel

            if self.instance.additional_sites.exists():
                # Agregar los sitios actuales al queryset si no están incluidos
                current_sites = self.instance.additional_sites.all()
                current_site_ids = set(current_sites.values_list("id", flat=True))
                queryset_site_ids = set(
                    self.fields["additional_sites"].queryset.values_list(
                        "id", flat=True
                    )
                )
                missing_site_ids = current_site_ids - queryset_site_ids
                if missing_site_ids:
                    self.fields["additional_sites"].queryset = self.fields[
                        "additional_sites"
                    ].queryset | Site.objects.filter(id__in=missing_site_ids)

        # Configurar querysets - Optimizado para rendimiento
        # Season: generalmente pocos registros
        # No limitar el queryset para evitar problemas de validación
        self.fields["season"].queryset = Season.objects.filter(is_active=True).order_by(
            "name"
        )

        if not self.fields["season"].empty_label:
            self.fields["season"].empty_label = "Seleccione una temporada"

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

        # Country, State, City: Ahora son campos de texto con autocomplete
        # Los valores reales se guardan en campos hidden que se crean en el template
        # No necesitamos configurar querysets para estos campos

        # Rule: generalmente pocos registros
        # No limitar el queryset para evitar problemas de validación
        self.fields["rule"].queryset = Rule.objects.filter(is_active=True).order_by(
            "name"
        )

        if not self.fields["rule"].empty_label:
            self.fields["rule"].empty_label = "Seleccione un reglamento"

        # Gate Fee Type: configurar queryset
        self.fields["gate_fee_type"].queryset = GateFeeType.objects.filter(
            is_active=True
        ).order_by("name")

        if not self.fields["gate_fee_type"].empty_label:
            self.fields["gate_fee_type"].empty_label = "Seleccione un tipo de gate fee"

        # Primary Site: configurar queryset
        # Filtrar sitios activos - sin límite para evitar problemas de validación
        self.fields["primary_site"].queryset = Site.objects.filter(
            is_active=True
        ).order_by("site_name")

        if not self.fields["primary_site"].empty_label:
            self.fields["primary_site"].empty_label = "Seleccione un sitio"

        # Additional Sites: configurar queryset (selección múltiple)
        # Filtrar sitios activos - sin límite para evitar problemas de validación
        self.fields["additional_sites"].queryset = Site.objects.filter(
            is_active=True
        ).order_by("site_name")

        # Hotel Sede: configurar queryset
        # Filtrar hoteles activos - sin límite para evitar problemas de validación
        self.fields["hotel"].queryset = Hotel.objects.filter(is_active=True).order_by(
            "hotel_name"
        )

        if not self.fields["hotel"].empty_label:
            self.fields["hotel"].empty_label = "Seleccione un hotel"

        # Additional Hotels: configurar queryset (selección múltiple)
        # Filtrar hoteles activos - No limitar para evitar problemas de validación
        self.fields["additional_hotels"].queryset = Hotel.objects.filter(
            is_active=True
        ).order_by("hotel_name")

        # Event Contact: configurar queryset (selección múltiple)
        # Filtrar contactos activos - No limitar para evitar problemas de validación
        self.fields["event_contact"].queryset = EventContact.objects.filter(
            is_active=True
        ).order_by("name")

        # Divisions: configurar queryset (selección múltiple)
        # Filtrar divisiones activas - No limitar para evitar problemas de validación
        self.fields["divisions"].queryset = Division.objects.filter(
            is_active=True
        ).order_by("name")

        # Establecer valores por defecto - Optimizado
        if not self.instance.pk:
            # Usar filter().first() en lugar de get() para evitar excepciones
            us_country = Country.objects.filter(
                name="United States", is_active=True
            ).first()
            if us_country:
                self.fields["country"].initial = us_country

    def clean_season(self):
        season = self.cleaned_data.get("season")
        if season:
            # Verificar que la temporada esté activa (sin límite de queryset)
            allowed_seasons = Season.objects.filter(is_active=True, id=season.id)
            if not allowed_seasons.exists():
                raise forms.ValidationError(
                    "La temporada seleccionada no es válida o no está activa."
                )
        elif self.fields["season"].required:
            raise forms.ValidationError("Debe seleccionar una temporada.")
        return season

    def clean_rule(self):
        rule = self.cleaned_data.get("rule")
        if rule:
            # Verificar que el reglamento esté activo (sin límite de queryset)
            allowed_rules = Rule.objects.filter(is_active=True, id=rule.id)
            if not allowed_rules.exists():
                raise forms.ValidationError(
                    "El reglamento seleccionado no es válido o no está activo."
                )
        elif self.fields["rule"].required:
            raise forms.ValidationError("Debe seleccionar un reglamento.")
        return rule

    def clean_divisions(self):
        divisions = self.cleaned_data.get("divisions")
        if divisions:
            # Verificar sin límite de queryset
            allowed_divisions = Division.objects.filter(is_active=True)
            allowed_division_ids = set(allowed_divisions.values_list("id", flat=True))

            # Filtrar solo las divisiones válidas
            if hasattr(divisions, "__iter__") and not isinstance(divisions, str):
                valid_divisions = [
                    d
                    for d in divisions
                    if hasattr(d, "id") and d.id in allowed_division_ids
                ]
                if len(valid_divisions) != len(list(divisions)):
                    invalid_count = len(list(divisions)) - len(valid_divisions)
                    raise forms.ValidationError(
                        f"{invalid_count} división(es) no son válidas o no están activas. Por favor, seleccione solo divisiones activas."
                    )
                return valid_divisions
        return divisions

    def clean_event_contact(self):
        event_contacts = self.cleaned_data.get("event_contact")
        if event_contacts:
            # Verificar sin límite de queryset
            allowed_contacts = EventContact.objects.filter(is_active=True)
            allowed_contact_ids = set(allowed_contacts.values_list("id", flat=True))

            # Filtrar solo los contactos válidos
            if hasattr(event_contacts, "__iter__") and not isinstance(
                event_contacts, str
            ):
                valid_contacts = [
                    c
                    for c in event_contacts
                    if hasattr(c, "id") and c.id in allowed_contact_ids
                ]
                if len(valid_contacts) != len(list(event_contacts)):
                    invalid_count = len(list(event_contacts)) - len(valid_contacts)
                    raise forms.ValidationError(
                        f"{invalid_count} contacto(s) no son válidos o no están activos. Por favor, seleccione solo contactos activos."
                    )
                return valid_contacts
        return event_contacts

    def clean_additional_hotels(self):
        additional_hotels = self.cleaned_data.get("additional_hotels")
        if additional_hotels:
            # Verificar sin límite de queryset
            allowed_hotels = Hotel.objects.filter(is_active=True)
            allowed_hotel_ids = set(allowed_hotels.values_list("id", flat=True))

            # Filtrar solo los hoteles válidos
            if hasattr(additional_hotels, "__iter__") and not isinstance(
                additional_hotels, str
            ):
                valid_hotels = [
                    h
                    for h in additional_hotels
                    if hasattr(h, "id") and h.id in allowed_hotel_ids
                ]
                if len(valid_hotels) != len(list(additional_hotels)):
                    invalid_count = len(list(additional_hotels)) - len(valid_hotels)
                    raise forms.ValidationError(
                        f"{invalid_count} hotel(es) adicional(es) no son válidos o no están activos. Por favor, seleccione solo hoteles activos."
                    )
                return valid_hotels
        return additional_hotels

    def clean_primary_site(self):
        primary_site = self.cleaned_data.get("primary_site")
        if primary_site:
            # Verificar que el sitio esté activo (sin límite de queryset)
            allowed_sites = Site.objects.filter(is_active=True, id=primary_site.id)
            if not allowed_sites.exists():
                raise forms.ValidationError(
                    "El sitio seleccionado no es válido o no está activo."
                )
        return primary_site

    def clean_additional_sites(self):
        additional_sites = self.cleaned_data.get("additional_sites")
        if additional_sites:
            # Verificar sin límite de queryset
            allowed_sites = Site.objects.filter(is_active=True)
            allowed_site_ids = set(allowed_sites.values_list("id", flat=True))

            # Filtrar solo los sitios válidos
            if hasattr(additional_sites, "__iter__") and not isinstance(
                additional_sites, str
            ):
                valid_sites = [s for s in additional_sites if s.id in allowed_site_ids]
                invalid_count = len(additional_sites) - len(valid_sites)
                if invalid_count > 0:
                    raise forms.ValidationError(
                        f"{invalid_count} sitio(s) seleccionado(s) no son válidos o no están activos."
                    )
                return valid_sites
        return additional_sites

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
            "position",
            "organization",
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
            "position": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Director Ejecutivo, Coordinador, Manager...",
                }
            ),
            "organization": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: NSC International, Baseball Academy...",
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
            "position": "Cargo",
            "organization": "Organización",
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
        """Obtener el país del campo hidden"""
        # El valor real viene del campo hidden
        country_id = self.data.get("country")
        if not country_id:
            raise forms.ValidationError("Debe seleccionar un país.")

        try:
            country_id = int(country_id)
            country_obj = Country.objects.filter(pk=country_id, is_active=True).first()
            if not country_obj:
                raise forms.ValidationError("El país seleccionado no es válido.")
            return country_obj
        except (ValueError, TypeError):
            raise forms.ValidationError("El país seleccionado no es válido.")

    def clean_state(self):
        """Obtener el estado del campo hidden"""
        # El valor real viene del campo hidden
        state_id = self.data.get("state")
        if not state_id:
            raise forms.ValidationError("Debe seleccionar un estado.")

        try:
            state_id = int(state_id)
            state_obj = State.objects.filter(pk=state_id, is_active=True).first()
            if not state_obj:
                raise forms.ValidationError("El estado seleccionado no es válido.")
            return state_obj
        except (ValueError, TypeError):
            raise forms.ValidationError("El estado seleccionado no es válido.")

    def clean_city(self):
        """Obtener la ciudad del campo hidden"""
        # El valor real viene del campo hidden
        city_id = self.data.get("city")
        if not city_id:
            raise forms.ValidationError("Debe seleccionar una ciudad.")

        try:
            city_id = int(city_id)
            city_obj = City.objects.filter(pk=city_id, is_active=True).first()
            if not city_obj:
                raise forms.ValidationError("La ciudad seleccionada no es válida.")
            return city_obj
        except (ValueError, TypeError):
            raise forms.ValidationError("La ciudad seleccionada no es válida.")


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
