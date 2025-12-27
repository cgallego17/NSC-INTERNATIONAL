"""
Formularios para banners del dashboard
"""

from django import forms
from .models import DashboardBanner


class DashboardBannerForm(forms.ModelForm):
    """Formulario para crear/editar banners del dashboard"""

    class Meta:
        model = DashboardBanner
        fields = [
            "title",
            "description",
            "banner_type",
            "image",
            "gradient_color_1",
            "gradient_color_2",
            "gradient_color_3",
            "is_active",
            "order",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Título del banner (opcional)",
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




