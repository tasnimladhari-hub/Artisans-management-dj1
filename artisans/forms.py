from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Artisan, Material, Sale

class ArtisanForm(forms.ModelForm):
    class Meta:
        model = Artisan
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'specialty', 'experience_years', 'profile_image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['material_type', 'quantity', 'unit', 'purchase_date', 'cost_per_unit']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product_name', 'quantity_sold', 'unit_price', 'sale_date', 'customer_name']
        widgets = {
            'sale_date': forms.DateInput(attrs={'type': 'date'}),
            'customer_name': forms.TextInput(attrs={'placeholder': 'Customer name (optional)'}),
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user