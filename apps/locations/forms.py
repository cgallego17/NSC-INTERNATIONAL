from django import forms

from .models import City, Country, Hotel, HotelRoom, HotelRoomTax, Season, State


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ["name", "code", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del país"}
            ),
            "code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Código del país (ej: US, MX, CO)",
                    "maxlength": "3",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if code:
            code = code.upper()
        return code


class StateForm(forms.ModelForm):
    class Meta:
        model = State
        fields = ["country", "name", "code", "is_active"]
        widgets = {
            "country": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del estado"}
            ),
            "code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Código del estado",
                    "maxlength": "10",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if code:
            code = code.upper()
        return code


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ["state", "name", "is_active"]
        widgets = {
            "state": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre de la ciudad"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = [
            "name",
            "year",
            "start_date",
            "end_date",
            "status",
            "description",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre de la temporada"}
            ),
            "year": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Año de la temporada",
                    "min": "1900",
                    "max": "2100",
                }
            ),
            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción de la temporada",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError(
                "La fecha de fin debe ser posterior a la fecha de inicio."
            )

        return cleaned_data


class HotelForm(forms.ModelForm):
    """Formulario para crear/editar hoteles con autocomplete para país, estado y ciudad"""

    class Meta:
        model = Hotel
        fields = [
            "hotel_name",
            "address",
            "country",
            "state",
            "city",
            "photo",
            "information",
            "registration_url",
            "capacity",
            "buy_out_fee",
            "contact_name",
            "contact_email",
            "contact_phone",
            "is_active",
        ]
        widgets = {
            "hotel_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Hotel Grand Plaza",
                    "required": True,
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Dirección completa del hotel",
                    "required": True,
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "class": "form-control autocomplete-input",
                    "placeholder": "Buscar país...",
                    "autocomplete": "off",
                    "data-field": "country",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "class": "form-control autocomplete-input",
                    "placeholder": "Buscar estado...",
                    "autocomplete": "off",
                    "data-field": "state",
                    "disabled": True,
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control autocomplete-input",
                    "placeholder": "Buscar ciudad...",
                    "autocomplete": "off",
                    "data-field": "city",
                    "disabled": True,
                }
            ),
            "photo": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
            "information": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Información adicional sobre el hotel",
                }
            ),
            "registration_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://ejemplo.com/registro",
                }
            ),
            "capacity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Número de habitaciones o personas",
                }
            ),
            "buy_out_fee": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "Ej: 1000.00",
                }
            ),
            "contact_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del contacto",
                }
            ),
            "contact_email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "contacto@hotel.com",
                }
            ),
            "contact_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+1 (555) 123-4567",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
        labels = {
            "hotel_name": "Nombre del Hotel",
            "address": "Dirección",
            "country": "País",
            "state": "Estado",
            "city": "Ciudad",
            "photo": "Foto del Hotel",
            "information": "Información Adicional",
            "registration_url": "URL de Registro",
            "capacity": "Capacidad",
            "buy_out_fee": "Buy Out Fee (Cargo por no Hospedarse)",
            "contact_name": "Nombre de Contacto",
            "contact_email": "Email de Contacto",
            "contact_phone": "Teléfono de Contacto",
            "is_active": "Activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Country, State, City: Ahora son campos de texto con autocomplete
        # Los valores reales se guardan en campos hidden que se crean en el template
        # No necesitamos configurar querysets para estos campos

    def clean_country(self):
        """Obtener el país del campo hidden"""
        country_id = self.data.get("country")
        if not country_id:
            return None

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
        state_id = self.data.get("state")
        if not state_id:
            return None

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
        city_id = self.data.get("city")
        if not city_id:
            return None

        try:
            city_id = int(city_id)
            city_obj = City.objects.filter(pk=city_id, is_active=True).first()
            if not city_obj:
                raise forms.ValidationError("La ciudad seleccionada no es válida.")
            return city_obj
        except (ValueError, TypeError):
            raise forms.ValidationError("La ciudad seleccionada no es válida.")


class HotelRoomForm(forms.ModelForm):
    """Formulario para crear/editar habitaciones de hotel"""

    class Meta:
        model = HotelRoom
        fields = [
            "hotel",
            "room_number",
            "name",
            "room_type",
            "capacity",
            "price_per_night",
            "price_includes_guests",
            "additional_guest_price",
            "breakfast_included",
            "stock",
            "taxes",
            "description",
            "is_available",
        ]
        widgets = {
            "hotel": forms.Select(attrs={"class": "form-select"}),
            "room_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ej: 101, 205, Suite A"}
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Suite Presidencial, Habitación con Vista al Mar",
                }
            ),
            "room_type": forms.Select(attrs={"class": "form-select"}),
            "capacity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Total de personas",
                }
            ),
            "price_per_night": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "price_includes_guests": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "placeholder": "1"}
            ),
            "additional_guest_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "breakfast_included": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "Cantidad disponible",
                }
            ),
            "taxes": forms.CheckboxSelectMultiple(),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Descripción de la habitación (amenidades, vista, etc.)",
                }
            ),
            "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Taxes: incluir activos + los ya asignados a la habitación (aunque estén inactivos),
        # para evitar que el formulario sea inválido al editar.
        taxes_qs = HotelRoomTax.objects.filter(is_active=True)
        if getattr(self.instance, "pk", None):
            try:
                taxes_qs = taxes_qs | self.instance.taxes.all()
            except Exception:
                pass
        self.fields["taxes"].queryset = taxes_qs.distinct()
        self.fields["taxes"].required = False

        # Hotel: incluir activos + el hotel actual (aunque esté inactivo), para no romper edición.
        try:
            from .models import Hotel

            hotel_qs = Hotel.objects.filter(is_active=True)
            if getattr(self.instance, "pk", None) and getattr(
                self.instance, "hotel_id", None
            ):
                hotel_qs = hotel_qs | Hotel.objects.filter(pk=self.instance.hotel_id)
            self.fields["hotel"].queryset = hotel_qs.distinct()
        except Exception:
            # Si algo falla, dejamos el queryset por defecto del ModelChoiceField.
            pass
