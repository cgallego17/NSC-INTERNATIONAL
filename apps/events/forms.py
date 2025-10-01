from django import forms

from apps.locations.models import Country, Season, State

from .models import Event, Division


class EventForm(forms.ModelForm):
    """Formulario para crear y editar eventos"""

    class Meta:
        model = Event
        fields = [
            "season",
            "title",
            "short_name",
            "description",
            "tags",
            "division",
            "city",
            "state",
            "country",
            "primary_site",
            "additional_sites",
            "rule",
            "stature",
            "start_date",
            "end_date",
            "entry_deadline",
            "allow_withdrawals",
            "withdraw_deadline",
            "freeze_rosters",
            "roster_freeze_date",
            "default_entry_fee",
            "payment_deadline",
            "accept_deposits",
            "default_deposit_amount",
            "allow_online_pay",
            "has_gate_fee",
            "gate_fee_type",
            "gate_fee_amount",
            "send_payment_reminders",
            "payment_reminder_date",
            "accept_schedule_requests",
            "schedule_request_deadline",
        ]
        widgets = {
            "season": forms.Select(attrs={"class": "form-select", "required": True, "placeholder": "Select Season"}),
            "title": forms.TextInput(attrs={"class": "form-control", "required": True, "placeholder": "Event Name"}),
            "short_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Event Short Name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Short Description"}),
            "tags": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tags"}),
            "division": forms.Select(attrs={"class": "form-select", "placeholder": "Select Division"}),
            "city": forms.Select(attrs={"class": "form-select", "required": True, "placeholder": "Select City"}),
            "state": forms.Select(attrs={"class": "form-select", "required": True, "placeholder": "Select State"}),
            "country": forms.Select(attrs={"class": "form-select", "required": True, "placeholder": "Select Country"}),
            "primary_site": forms.Select(attrs={"class": "form-select", "placeholder": "Select Primary Site"}),
            "additional_sites": forms.CheckboxSelectMultiple(attrs={"class": "additional-sites-checkbox-list"}),
            "rule": forms.Select(attrs={"class": "form-select", "required": True, "placeholder": "Select Rule Set"}),
            "stature": forms.Select(attrs={"class": "form-select", "required": True}),
            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "required": True, "placeholder": "dd/mm/aaaa"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "required": True, "placeholder": "dd/mm/aaaa"}
            ),
            "entry_deadline": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "required": True, "placeholder": "dd/mm/aaaa"}
            ),
            "allow_withdrawals": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "withdraw_deadline": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "freeze_rosters": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "roster_freeze_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "default_entry_fee": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}),
            "payment_deadline": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "accept_deposits": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "default_deposit_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}
            ),
            "allow_online_pay": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "has_gate_fee": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "gate_fee_type": forms.Select(attrs={"class": "form-select"}),
            "gate_fee_amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}),
            "send_payment_reminders": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "payment_reminder_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "accept_schedule_requests": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "schedule_request_deadline": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
        labels = {
            "season": "Season *",
            "title": "Event Name *",
            "short_name": "Event Short Name",
            "description": "Short Description",
            "tags": "Tags",
            "division": "División",
            "city": "City *",
            "state": "State *",
            "country": "Country *",
            "rule": "Rule Set *",
            "stature": "Stature *",
            "start_date": "Start Date *",
            "end_date": "End Date *",
            "entry_deadline": "Entry Deadline *",
            "allow_withdrawals": "Allow Withdrawals",
            "withdraw_deadline": "Withdraw Deadline",
            "freeze_rosters": "Freeze Rosters",
            "roster_freeze_date": "Roster Freeze Date",
            "default_entry_fee": "Default Entry Fee",
            "payment_deadline": "Payment Deadline",
            "accept_deposits": "Accept Deposits",
            "default_deposit_amount": "Default Deposit Amount",
            "allow_online_pay": "Allow Online Pay",
            "has_gate_fee": "Has Gate Fee",
            "gate_fee_type": "Gate Fee Type",
            "gate_fee_amount": "Gate Fee Amount",
            "send_payment_reminders": "Send Payment Reminders",
            "payment_reminder_date": "Payment Reminder Date",
            "accept_schedule_requests": "Accept Schedule Requests",
            "schedule_request_deadline": "Schedule Request Deadline",
        }
        help_texts = {
            "short_name": "If provided, the short name will be used in event notifications sent via SMS.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configurar opciones para los campos de selección
        self.fields["season"].queryset = Season.objects.filter(is_active=True).order_by("name")
        self.fields["division"].queryset = Division.objects.filter(is_active=True).order_by("name")
        self.fields["state"].queryset = State.objects.filter(is_active=True).order_by("name")
        self.fields["country"].queryset = Country.objects.filter(is_active=True).order_by("name")

        # Establecer valores por defecto
        if not self.instance.pk:
            # Para nuevos eventos, establecer país por defecto como Estados Unidos
            try:
                us_country = Country.objects.get(name="United States")
                self.fields["country"].initial = us_country
            except Country.DoesNotExist:
                pass

            # Establecer stature por defecto
            self.fields["stature"].initial = "single_points"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        entry_deadline = cleaned_data.get("entry_deadline")

        # Validar que la fecha de fin sea posterior a la de inicio
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

        # Validar que la fecha límite de inscripción sea anterior a la fecha de inicio
        if entry_deadline and start_date and entry_deadline >= start_date:
            raise forms.ValidationError("La fecha límite de inscripción debe ser anterior a la fecha de inicio del evento.")

        return cleaned_data
