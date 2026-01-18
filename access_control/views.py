"""
View-uri (Endpoint-uri API) pentru aplicația de Control Acces

Acest fișier conține toate funcțiile care răspund la cereri HTTP.
Fiecare funcție este un endpoint API care procesează cereri și returnează răspunsuri.

Endpoint-uri disponibile:
    GET  /              -> dashboard()      - Afișează pagina web principală
    POST /api/attempt   -> new_attempt()    - Înregistrează o nouă încercare de acces
    GET  /api/attempts  -> get_attempts()   - Listează toate încercările
    GET  /api/attempt/X -> get_attempt()    - Obține detalii despre o încercare
    POST /api/decide/X  -> decide()         - Aprobă sau respinge o încercare
    GET  /captures/X    -> serve_capture()  - Servește fotografiile capturate

Autor: Bascacov Alexandra
Versiune: 1.0
"""

import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from django.db.models import Case, When, Value, IntegerField
import json

from .models import AccessAttempt


def dashboard(request):
    """
    Afișează dashboard-ul de administrare.

    Aceasta este pagina principală pe care o vede administratorul.
    Afișează lista încercărilor de acces și permite aprobarea/respingerea lor.

    Parametri:
        request: Cererea HTTP de la browser

    Returnează:
        HttpResponse: Pagina HTML a dashboard-ului
    """
    return render(request, 'access_control/dashboard.html', {
        'timeout': settings.APPROVAL_TIMEOUT  # Trimite timeout-ul către template
    })


@csrf_exempt  # Dezactivează protecția CSRF (necesar pentru API)
@require_http_methods(["POST"])  # Acceptă doar cereri POST
def new_attempt(request):
    """
    Primește și înregistrează o nouă încercare de acces la folder.

    Acest endpoint este apelat de monitor.py când detectează un acces
    la folderul protejat. Creează o înregistrare în baza de date și
    returnează ID-ul pentru urmărire.

    Parametri cerere (JSON):
        folder_path (str): Calea către folderul accesat (obligatoriu)
        access_type (str): Tipul accesului (opțional, default: 'folder')
        photo_path (str): Calea către fotografia capturată (opțional)

    Returnează:
        JsonResponse: {'id': <id>, 'status': 'pending'} la succes
        JsonResponse: {'error': <mesaj>} la eroare (status 400)
    """
    # Parsăm corpul cererii ca JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalid'}, status=400)

    # Extragem datele din cerere
    folder_path = data.get('folder_path')
    access_type = data.get('access_type', 'folder')
    photo_path = data.get('photo_path')

    # Validăm că avem calea folderului
    if not folder_path:
        return JsonResponse({'error': 'folder_path este obligatoriu'}, status=400)

    # Creăm înregistrarea în baza de date
    attempt = AccessAttempt.objects.create(
        access_path=folder_path,
        access_type=access_type,
        photo_path=photo_path,
        status='pending'  # Toate încercările încep cu statusul "în așteptare"
    )

    return JsonResponse({'id': attempt.id, 'status': 'pending'})


def get_attempts(request):
    """
    Obține lista tuturor încercărilor de acces.

    Returnează ultimele 50 de încercări, sortate cu cele în așteptare
    primele, apoi cele recente.

    Parametri:
        request: Cererea HTTP de la browser

    Returnează:
        JsonResponse: Lista încercărilor în format JSON
    """
    # Obținem toate încercările, sortate cu pending primele (folosind Case pentru ordine corectă)
    # Ordinea alfabetică nu funcționează: 'approved' < 'denied' < 'pending'
    # Folosim Case pentru a defini ordinea dorită: pending=0, denied=1, approved=2
    attempts = AccessAttempt.objects.all().annotate(
        status_order=Case(
            When(status='pending', then=Value(0)),
            When(status='denied', then=Value(1)),
            When(status='approved', then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        )
    ).order_by('status_order', '-timestamp')[:50]

    ordered = list(attempts)

    # Construim lista de rezultate în format JSON-serializabil
    result = []
    for a in ordered:
        result.append({
            'id': a.id,
            'timestamp': a.timestamp.isoformat(),
            'access_path': a.access_path,
            'access_type': a.access_type,
            'photo_path': a.photo_path,
            'status': a.status,
            'decided_at': a.decided_at.isoformat() if a.decided_at else None,
        })

    return JsonResponse(result, safe=False)  # safe=False permite liste


def get_attempt(request, attempt_id):
    """
    Obține statusul unei încercări specifice de acces.

    Acest endpoint este folosit de monitor.py pentru a verifica periodic
    dacă administratorul a luat o decizie.

    Parametri:
        request: Cererea HTTP
        attempt_id (int): ID-ul încercării de acces

    Returnează:
        JsonResponse: Detaliile încercării în format JSON
        Http404: Dacă încercarea nu există
    """
    # get_object_or_404 returnează obiectul sau ridică eroare 404
    attempt = get_object_or_404(AccessAttempt, id=attempt_id)

    return JsonResponse({
        'id': attempt.id,
        'timestamp': attempt.timestamp.isoformat(),
        'access_path': attempt.access_path,
        'access_type': attempt.access_type,
        'photo_path': attempt.photo_path,
        'status': attempt.status,
        'decided_at': attempt.decided_at.isoformat() if attempt.decided_at else None,
    })


@csrf_exempt  # Dezactivează protecția CSRF pentru API
@require_http_methods(["POST"])  # Acceptă doar cereri POST
def decide(request, attempt_id):
    """
    Aprobă sau respinge o încercare de acces.

    Acest endpoint este apelat din dashboard când administratorul
    apasă butonul "Aprobă" sau "Respinge".

    Parametri:
        request: Cererea HTTP
        attempt_id (int): ID-ul încercării de acces

    Parametri cerere (JSON):
        decision (str): 'approved' sau 'denied'

    Returnează:
        JsonResponse: {'id': <id>, 'status': <decizie>} la succes
        JsonResponse: {'error': <mesaj>} la eroare (status 400)
    """
    # Parsăm corpul cererii ca JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalid'}, status=400)

    decision = data.get('decision')

    # Validăm decizia
    if decision not in ['approved', 'denied']:
        return JsonResponse({'error': 'Decizie invalidă'}, status=400)

    # Găsim încercarea și actualizăm statusul
    attempt = get_object_or_404(AccessAttempt, id=attempt_id)
    attempt.status = decision
    attempt.decided_at = timezone.now()  # Înregistrăm momentul deciziei
    attempt.save()

    return JsonResponse({'id': attempt.id, 'status': decision})


def serve_capture(request, filename):
    """
    Servește fotografiile capturate.

    Acest endpoint permite afișarea fotografiilor în dashboard.
    Fotografiile sunt stocate în folderul 'captures'.

    Parametri:
        request: Cererea HTTP
        filename (str): Numele fișierului foto (ex: 'capture_20250117_143052.jpg')

    Returnează:
        FileResponse: Fișierul imagine JPEG
        Http404: Dacă fotografia nu există
    """
    # Construim calea completă către fișier
    captures_dir = os.path.join(settings.BASE_DIR, 'captures')
    file_path = os.path.join(captures_dir, filename)

    # Verificăm dacă fișierul există
    if not os.path.exists(file_path):
        raise Http404("Fotografia nu a fost găsită")

    # Returnăm fișierul cu tipul MIME corect
    return FileResponse(open(file_path, 'rb'), content_type='image/jpeg')
