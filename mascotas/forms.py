from django import forms
from mascotas.models import Mascota

class MascotaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vacunado_rabia'].label = '¿Vacunado contra la rabia?'
        
        # Configurar campo de teléfono
        self.fields['telefono_dueno'].widget.attrs.update({
            'placeholder': 'Ej: +56912345678 o 912345678',
            'pattern': r'^(\+56)?9[0-9]{8}$',
            'title': 'Ingrese un número de teléfono chileno válido'
        })
        
        # Configurar campo de RUT
        self.fields['rut_dueno'].widget.attrs.update({
            'placeholder': 'Ej: 12345678-9 o 12.345.678-9',
            'title': 'Ingrese un RUT chileno válido con dígito verificador',
            'maxlength': '12',
            'oninput': 'formatearRUT(this)'
        })
        
        # Configurar campo de email
        self.fields['email_dueno'].widget.attrs.update({
            'placeholder': 'Ej: usuario@gmail.com',
            'type': 'email',
            'title': 'Ingrese un correo electrónico válido',
            'oninput': 'validarEmail(this)'
        })
    
    class Meta:
        model = Mascota
        fields = [
            'nfc_id',
            'nombre',
            'foto',
            'vacunado_rabia',
            'nombre_dueno',
            'rut_dueno',
            'email_dueno',
            'telefono_dueno',
        ]
        widgets = {
            'telefono_dueno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: +56912345678 o 912345678'
            }),
            'rut_dueno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678-9 o 12.345.678-9'
            }),
            'email_dueno': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: usuario@gmail.com'
            })
        }
