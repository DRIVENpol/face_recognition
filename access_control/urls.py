"""
Configurare URL-uri pentru aplicația de Control Acces

Acest fișier definește toate rutele (endpoint-urile) disponibile în
aplicația de control acces. Fiecare rută mapează un URL la o funcție view.

Rute API disponibile:
    /                       -> Dashboard-ul web de administrare
    /api/attempt           -> Înregistrare încercare nouă (POST)
    /api/attempts          -> Lista tuturor încercărilor (GET)
    /api/attempt/<id>      -> Detalii încercare specifică (GET)
    /api/decide/<id>       -> Aprobare/Respingere încercare (POST)
    /captures/<filename>   -> Servire fotografii capturate (GET)

Autor: Bascacov Alexandra
Versiune: 1.0
"""

from django.urls import path
from . import views

# Lista pattern-urilor URL pentru aplicația access_control
urlpatterns = [
    # =========================================================================
    # PAGINA PRINCIPALĂ (DASHBOARD)
    # =========================================================================
    # URL: /
    # Metodă: GET
    # Descriere: Afișează interfața web pentru administrator
    path('', views.dashboard, name='dashboard'),

    # =========================================================================
    # API ENDPOINT-URI
    # =========================================================================

    # Înregistrare încercare nouă de acces
    # URL: /api/attempt
    # Metodă: POST
    # Corp: {"folder_path": "...", "access_type": "...", "photo_path": "..."}
    # Răspuns: {"id": X, "status": "pending"}
    # Folosit de: monitor.py când detectează acces la folder
    path('api/attempt', views.new_attempt, name='new_attempt'),

    # Lista tuturor încercărilor de acces
    # URL: /api/attempts
    # Metodă: GET
    # Răspuns: Lista JSON cu ultimele 50 de încercări
    # Folosit de: Dashboard pentru a afișa istoricul
    path('api/attempts', views.get_attempts, name='get_attempts'),

    # Detalii despre o încercare specifică
    # URL: /api/attempt/<id>
    # Metodă: GET
    # Răspuns: Obiect JSON cu detaliile încercării
    # Folosit de: monitor.py pentru a verifica dacă s-a luat o decizie
    path('api/attempt/<int:attempt_id>', views.get_attempt, name='get_attempt'),

    # Aprobare sau respingere încercare
    # URL: /api/decide/<id>
    # Metodă: POST
    # Corp: {"decision": "approved"} sau {"decision": "denied"}
    # Răspuns: {"id": X, "status": "approved/denied"}
    # Folosit de: Dashboard când administratorul apasă Aprobă/Respinge
    path('api/decide/<int:attempt_id>', views.decide, name='decide'),

    # =========================================================================
    # SERVIRE FIȘIERE
    # =========================================================================
    # Servire fotografii capturate
    # URL: /captures/<filename>
    # Metodă: GET
    # Răspuns: Imaginea JPEG
    # Folosit de: Dashboard pentru a afișa fotografiile
    path('captures/<str:filename>', views.serve_capture, name='serve_capture'),
]
