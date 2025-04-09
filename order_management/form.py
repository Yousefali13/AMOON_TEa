from django import forms
from .models import OrderItem, Order

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product_name', 'quantity', 'unit_price']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
