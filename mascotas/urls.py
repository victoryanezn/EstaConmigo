
from django.urls import path
from . import views

urlpatterns = [
    path('moderador/mascotas/', views.moderador_listar_mascotas, name='moderador_listar_mascotas'),
    path('moderador/mascotas/crear/', views.moderador_crear_mascota, name='moderador_crear_mascota'),
    path('moderador/mascotas/<int:pk>/editar/', views.moderador_editar_mascota, name='moderador_editar_mascota'),
    path('moderador/mascotas/<int:pk>/eliminar/', views.moderador_eliminar_mascota, name='moderador_eliminar_mascota'),
    path('moderador/mascotas/ajax/', views.moderador_listar_mascotas_ajax, name='moderador_listar_mascotas_ajax'),
    path('guardar_ubicacion/', views.guardar_ubicacion, name='guardar_ubicacion'),
    path('<str:nfc_id>/', views.vista_nfc, name='vista_nfc'),
]
