from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroForm(UserCreationForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingresá tu contraseña',
            'id': 'password',
            'required': True
        })
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repetí la contraseña',
            'id': 'confirmPassword',
            'required': True
        })
    )
    correo = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingresá tu usuario',
            'id': 'correo',
            'required': True,
            'minlength': 8
        })
    )

    class Meta:
        model = User
        fields = ['correo', 'password1', 'password2']