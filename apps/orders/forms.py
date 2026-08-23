from django import forms

from .models import Order

INPUT_CLASSES = (
    'w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 '
    'focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900'
)


class ContactForm(forms.Form):
    customer_name = forms.CharField(
        max_length=120, label='Nombre completo',
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES}),
    )
    customer_phone = forms.CharField(
        max_length=30, label='Teléfono / WhatsApp',
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES}),
    )
    customer_email = forms.EmailField(
        required=False, label='Correo (opcional)',
        widget=forms.EmailInput(attrs={'class': INPUT_CLASSES}),
    )


class CheckoutForm(ContactForm):
    quantity = forms.IntegerField(
        min_value=1, initial=1, label='Cantidad',
        widget=forms.NumberInput(attrs={'min': 1, 'class': INPUT_CLASSES}),
    )


class CartCheckoutForm(ContactForm):
    pass


class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_proof']
        widgets = {
            'payment_proof': forms.ClearableFileInput(attrs={
                'class': 'text-sm text-slate-700', 'accept': 'image/*',
            }),
        }
        labels = {'payment_proof': 'Foto o captura del comprobante'}

    def clean_payment_proof(self):
        proof = self.cleaned_data['payment_proof']
        if not proof:
            raise forms.ValidationError('Sube una foto o captura de tu comprobante de pago.')
        return proof
