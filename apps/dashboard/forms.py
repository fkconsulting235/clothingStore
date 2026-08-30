from django import forms
from django.forms import inlineformset_factory

from apps.catalog.models import Category, Product, ProductImage, ProductVariant
from apps.orders.models import BankAccount

INPUT_CLASSES = (
    'w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 '
    'focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900'
)
CHECKBOX_CLASSES = 'h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900'


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'code', 'name', 'description', 'base_price', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': INPUT_CLASSES}),
            'code': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Se genera solo si lo dejas vacío'}),
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 4}),
            'base_price': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'step': '0.01', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
        }
        labels = {
            'category': 'Categoría',
            'code': 'Código',
            'name': 'Nombre',
            'description': 'Descripción',
            'base_price': 'Precio base',
            'is_active': 'Publicada en la tienda',
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
        }
        labels = {
            'name': 'Nombre',
            'order': 'Orden de aparición',
            'is_active': 'Visible en la tienda',
        }


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['bank_name', 'account_type', 'account_number', 'holder_name', 'order', 'is_active']
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej. BAC Credomatic'}),
            'account_type': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ej. Cuenta de ahorro'}),
            'account_number': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'holder_name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
        }
        labels = {
            'bank_name': 'Banco',
            'account_type': 'Tipo de cuenta',
            'account_number': 'Número de cuenta',
            'holder_name': 'A nombre de',
            'order': 'Orden de aparición',
            'is_active': 'Visible en el checkout',
        }


VariantFormSet = inlineformset_factory(
    Product, ProductVariant,
    fields=['color', 'size', 'price_override', 'stock'],
    widgets={
        'color': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Color'}),
        'size': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Talla'}),
        'price_override': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'step': '0.01', 'placeholder': 'Precio especial'}),
        'stock': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 0}),
    },
    extra=3, can_delete=True,
)

ImageFormSet = inlineformset_factory(
    Product, ProductImage,
    fields=['image', 'order'],
    widgets={
        'image': forms.ClearableFileInput(attrs={'class': 'text-sm text-slate-700'}),
        'order': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 0}),
    },
    extra=3, can_delete=True,
)
