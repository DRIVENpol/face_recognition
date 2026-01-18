"""
Configurări pentru Sistemul de Control al Accesului la Foldere

Acest fișier conține toate setările configurabile ale sistemului.
Modificați valorile de mai jos pentru a personaliza comportamentul aplicației.

Autor: Bascacov Alexandra
Versiune: 1.0
"""

import os

# ============================================================================
# DIRECTORUL DE BAZĂ
# ============================================================================
# Calea către directorul unde se află acest fișier de configurare
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# SETĂRI SERVER WEB
# ============================================================================
# Adresa IP pe care rulează serverul de administrare
# "127.0.0.1" = doar acces local (de pe același calculator)
# "0.0.0.0" = acces din rețea (de pe orice dispozitiv)
SERVER_HOST = "127.0.0.1"

# Portul pe care ascultă serverul
SERVER_PORT = 5000

# URL-ul complet al serverului (generat automat)
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# ============================================================================
# SETĂRI TIMEOUT
# ============================================================================
# Timpul (în secunde) de așteptare pentru decizia administratorului
# Dacă nu se primește nicio decizie în acest timp, accesul este refuzat automat
APPROVAL_TIMEOUT = 30  # Respingere automată după 30 de secunde fără răspuns

# ============================================================================
# SETĂRI NGROK (ACCES DE LA DISTANȚĂ)
# ============================================================================
# ngrok creează un tunel public pentru a permite accesul de pe telefon
# True = activat (generează cod QR pentru acces mobil)
# False = dezactivat (doar acces local)
USE_NGROK = True

# ============================================================================
# SETĂRI PROTECȚIE FOLDER
# ============================================================================
# Folderul care va fi protejat poate fi specificat în două moduri:
# 1. Doar numele folderului: "Confidential"
#    (va fi căutat automat în SEARCH_ROOT)
# 2. Calea completă: "~/Desktop/SecretFolder"
#    (se folosește exact această cale)
PROTECTED_FOLDER = "Confidential"

# Directorul rădăcină unde se caută folderul protejat
# (folosit doar dacă PROTECTED_FOLDER este un nume, nu o cale completă)
SEARCH_ROOT = os.path.expanduser("~")

# ============================================================================
# SETĂRI ALERTĂ
# ============================================================================
# Timpul minim (în secunde) între două alerte consecutive
# Previne notificări multiple pentru același acces
ACCESS_COOLDOWN = 5

# ============================================================================
# CĂILE FIȘIERELOR
# ============================================================================
# Calea către baza de date SQLite (nu mai este folosită - s-a migrat la Django)
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")
