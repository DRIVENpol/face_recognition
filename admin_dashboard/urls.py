"""
Configurare URL-uri principale pentru proiectul admin_dashboard

Acest fișier definește rutele URL principale ale aplicației.
Toate cererile HTTP sunt direcționate către view-urile corespunzătoare.

Rute disponibile:
    /admin/  -> Interfața de administrare Django (pentru dezvoltatori)
    /        -> Dashboard-ul de control acces (aplicația principală)

Autor: Bascacov Alexandra
Versiune: 1.0
"""

from django.contrib import admin
from django.urls import path, include

# Lista pattern-urilor URL pentru întreaga aplicație
urlpatterns = [
    # Interfața de administrare Django - pentru gestionare avansată
    # Accesibilă la: http://localhost:5000/admin/
    path('admin/', admin.site.urls),

    # Include toate URL-urile din aplicația access_control
    # Aceasta este aplicația principală pentru controlul accesului
    # Redirecționează către dashboard-ul web
    path('', include('access_control.urls')),
]
