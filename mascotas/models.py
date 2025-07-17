from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
import re
import os
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

def validar_rut_chileno(rut):
    """Valida que el RUT sea un RUT chileno válido"""
    # Limpiar el RUT (solo números y K)
    rut_limpio = re.sub(r'[^\dkK]', '', rut).upper()
    
    # Verificar formato básico
    if len(rut_limpio) < 8 or len(rut_limpio) > 9:
        raise ValidationError('El RUT debe tener entre 8 y 9 caracteres')
    
    # Separar número del dígito verificador
    if len(rut_limpio) == 8:
        numero = rut_limpio[:-1]
        dv = rut_limpio[-1]
    else:
        numero = rut_limpio[:-1]
        dv = rut_limpio[-1]
    
    # Verificar que el número sea válido
    try:
        numero_int = int(numero)
    except ValueError:
        raise ValidationError('El número del RUT debe contener solo dígitos')
    
    # Calcular dígito verificador
    suma = 0
    multiplicador = 2
    
    for digito in reversed(numero):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador == 8:
            multiplicador = 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
    
    if dv != dv_calculado:
        raise ValidationError('El RUT ingresado no es válido')
    
    return True

def validar_email_chileno(email):
    """Validador personalizado para emails que funciona bien con dominios chilenos"""
    # Usar el validador base de Django primero
    email_validator = EmailValidator()
    try:
        email_validator(email)
    except ValidationError:
        raise ValidationError('Ingrese un correo electrónico válido')
    
    # Validaciones adicionales para emails chilenos comunes
    email_lower = email.lower()
    
    # Lista de dominios comunes en Chile
    dominios_validos = [
        'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
        'uc.cl', 'puc.cl', 'usach.cl', 'uchile.cl', 'uv.cl',
        'utem.cl', 'unab.cl', 'udp.cl', 'uai.cl', 'udd.cl',
        'live.cl', 'hotmail.cl', 'vtr.net', 'tie.cl', 'entel.cl'
    ]
    
    dominio = email_lower.split('@')[1] if '@' in email_lower else ''
    
    # Verificar longitud del nombre de usuario
    nombre_usuario = email_lower.split('@')[0] if '@' in email_lower else ''
    if len(nombre_usuario) < 2:
        raise ValidationError('El nombre de usuario del correo debe tener al menos 2 caracteres')
    
    # El email pasó todas las validaciones
    return True

class Mascota(models.Model):
    # Validador para teléfonos chilenos
    telefono_validator = RegexValidator(
        regex=r'^(\+56)?9[0-9]{8}$',
        message='Ingrese un número de teléfono chileno válido (ej: +56912345678 o 912345678)'
    )
    
    nfc_id = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='fotos_mascotas/')
    vacunado_rabia = models.BooleanField(default=False)
    nombre_dueno = models.CharField(max_length=100)
    rut_dueno = models.CharField(
        max_length=12, 
        verbose_name='RUT del dueño',
        validators=[validar_rut_chileno],
        help_text='Formato: 12345678-9 o 12.345.678-9'
    )
    email_dueno = models.EmailField(
        max_length=254, 
        verbose_name='Correo del dueño',
        validators=[validar_email_chileno],
        help_text='Formato: ejemplo@gmail.com'
    )
    telefono_dueno = models.CharField(
        max_length=12, 
        null=True, 
        blank=True,
        validators=[telefono_validator],
        help_text='Formato: +56912345678 o 912345678'
    )

    def __str__(self):
        return f"{self.nombre} ({self.nfc_id})"
    
    def rut_formateado(self):
        """Retorna el RUT en formato chileno estándar con puntos y guión"""
        if not self.rut_dueno:
            return None
        
        # Limpiar el RUT (solo números y K)
        rut_limpio = re.sub(r'[^\dkK]', '', self.rut_dueno).upper()
        
        if len(rut_limpio) < 8:
            return self.rut_dueno
        
        # Separar número del dígito verificador
        numero = rut_limpio[:-1]
        dv = rut_limpio[-1]
        
        # Formatear con puntos
        numero_formateado = ''
        for i, digito in enumerate(reversed(numero)):
            if i > 0 and i % 3 == 0:
                numero_formateado = '.' + numero_formateado
            numero_formateado = digito + numero_formateado
        
        return f"{numero_formateado}-{dv}"
    
    def telefono_formateado(self):
        """Retorna el teléfono en formato chileno estándar"""
        if not self.telefono_dueno:
            return None
        
        # Limpiar el número (solo dígitos)
        numero_limpio = re.sub(r'[^\d]', '', self.telefono_dueno)
        
        # Si tiene 11 dígitos y empieza con 56, remover el 56
        if len(numero_limpio) == 11 and numero_limpio.startswith('56'):
            numero_limpio = numero_limpio[2:]
        
        # Si tiene 9 dígitos y empieza con 9, formatear
        if len(numero_limpio) == 9 and numero_limpio.startswith('9'):
            return f"+569 {numero_limpio[1:5]} {numero_limpio[5:]}"
        
        return self.telefono_dueno
    
    def telefono_whatsapp(self):
        """Retorna el número de teléfono en formato para WhatsApp (solo dígitos con código de país)"""
        if not self.telefono_dueno:
            return None
        
        # Limpiar el número (solo dígitos)
        numero_limpio = re.sub(r'[^\d]', '', self.telefono_dueno)
        
        # Si tiene 11 dígitos y empieza con 56, remover el 56
        if len(numero_limpio) == 11 and numero_limpio.startswith('56'):
            numero_limpio = numero_limpio[2:]
        
        # Si tiene 9 dígitos y empieza con 9, agregar código de país
        if len(numero_limpio) == 9 and numero_limpio.startswith('9'):
            return f"56{numero_limpio}"
        
        return numero_limpio
    
    def save(self, *args, **kwargs):
        """Normalizar el teléfono y RUT antes de guardar"""
        # Normalizar teléfono
        if self.telefono_dueno:
            # Limpiar el número (solo dígitos)
            numero_limpio = re.sub(r'[^\d]', '', self.telefono_dueno)
            
            # Si tiene 11 dígitos y empieza con 56, remover el 56
            if len(numero_limpio) == 11 and numero_limpio.startswith('56'):
                numero_limpio = numero_limpio[2:]
            
            # Guardar con formato +56
            if len(numero_limpio) == 9 and numero_limpio.startswith('9'):
                self.telefono_dueno = f"+56{numero_limpio}"
        
        # Normalizar RUT
        if self.rut_dueno:
            # Limpiar el RUT (solo números y K) y guardarlo sin formato
            rut_limpio = re.sub(r'[^\dkK]', '', self.rut_dueno).upper()
            self.rut_dueno = rut_limpio
        
        super().save(*args, **kwargs)

# Borrar la foto del sistema de archivos cuando se elimina la mascota
@receiver(post_delete, sender=Mascota)
def eliminar_foto_mascota(sender, instance, **kwargs):
    if instance.foto and instance.foto.name:
        foto_path = instance.foto.path
        if os.path.isfile(foto_path):
            os.remove(foto_path)



class Ubicacion(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    latitud = models.FloatField()
    longitud = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)
