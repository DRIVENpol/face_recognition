#!/usr/bin/env python3
"""
Lansator Server Django - Pornește dashboard-ul de administrare

Acest script pornește serverul web Django care oferă interfața de administrare.
Opțional, poate crea un tunel ngrok pentru acces de la distanță (de pe telefon).

Funcționalități:
    - Pornește serverul Django pe portul configurat
    - Creează tunel ngrok pentru acces public (opțional)
    - Generează și afișează cod QR pentru acces rapid de pe telefon

Utilizare:
    python run_server.py

Autor: Paul Socarde
Versiune: 1.0
"""

import os
import sys

# Configurăm modulul de setări Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_dashboard.settings')

# ============================================================================
# CONFIGURĂRI SERVER
# ============================================================================
# '0.0.0.0' permite conexiuni de pe orice dispozitiv din rețea
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000

# Activează/dezactivează tunelul ngrok pentru acces de la distanță
USE_NGROK = True  # Setează False pentru a dezactiva ngrok

# Verificăm dacă bibliotecile pentru ngrok sunt disponibile
if USE_NGROK:
    try:
        from pyngrok import ngrok
        import qrcode
        NGROK_AVAILABLE = True
    except ImportError:
        NGROK_AVAILABLE = False
        print("Avertisment: pyngrok sau qrcode nu sunt instalate. Rulează: pip install pyngrok qrcode")
else:
    NGROK_AVAILABLE = False


def print_qr_code(url):
    """
    Generează și afișează un cod QR în format ASCII în terminal.

    Codul QR poate fi scanat cu telefonul pentru a accesa rapid
    dashboard-ul de administrare.

    Parametri:
        url (str): URL-ul de codificat în QR
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)


def start_ngrok_tunnel():
    """
    Pornește tunelul ngrok și returnează URL-ul public.

    ngrok creează un tunel securizat care permite accesul la serverul
    local de pe internet. Util pentru a accesa dashboard-ul de pe telefon.

    Returnează:
        str: URL-ul public ngrok (ex: https://abc123.ngrok.io)
        None: Dacă tunelul nu a putut fi creat
    """
    print("\nSe pornește tunelul ngrok...")
    try:
        public_url = ngrok.connect(SERVER_PORT, "http").public_url
        return public_url
    except Exception as e:
        print(f"Eroare la pornirea ngrok: {e}")
        print("Asigură-te că ngrok este configurat. Rulează: ngrok config add-authtoken <token-ul-tău>")
        return None


# ============================================================================
# PUNCTUL DE INTRARE - EXECUȚIA PRINCIPALĂ
# ============================================================================
if __name__ == '__main__':
    public_url = None

    # Încercăm să pornim tunelul ngrok dacă este activat și disponibil
    if USE_NGROK and NGROK_AVAILABLE:
        public_url = start_ngrok_tunnel()
        if public_url:
            print(f"\nURL Public: {public_url}")
            print("\nScanează acest cod QR cu telefonul:\n")
            print_qr_code(public_url)

    # Afișăm informațiile despre server
    print("\n" + "=" * 50)
    print("Control Acces Folder - Dashboard Administrare (Django)")
    print("=" * 50)
    print(f"  Local:  http://localhost:{SERVER_PORT}")
    if public_url:
        print(f"  Public: {public_url}")
    print("=" * 50)
    print("\nSe așteaptă încercări de acces la folder...")

    # Pornim serverul de dezvoltare Django
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', f'{SERVER_HOST}:{SERVER_PORT}'])
