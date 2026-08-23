from django import forms

from .models import Reservation


INPUT_CLASSES = (
    'w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 '
    'focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900'
)


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['customer_name', 'customer_phone', 'quantity']
        widgets = {
            'customer_name': forms.TextInput(attrs={'placeholder': 'Tu nombre completo', 'class': INPUT_CLASSES}),
            'customer_phone': forms.TextInput(attrs={'placeholder': 'Tu número de WhatsApp', 'class': INPUT_CLASSES}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': INPUT_CLASSES}),
        }
        labels = {
            'customer_name': 'Nombre completo',
            'customer_phone': 'Teléfono / WhatsApp',
            'quantity': 'Cantidad',
        }
