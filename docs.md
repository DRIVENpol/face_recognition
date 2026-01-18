# Sistem de Control al Accesului la Foldere

## Cuprins
1. [Introducere](#1-introducere)
2. [Cum funcționează](#2-cum-funcționează)
3. [Componente principale](#3-componente-principale)
4. [Tehnologii folosite](#4-tehnologii-folosite)
5. [Structura proiectului](#5-structura-proiectului)
6. [Instalare și configurare](#6-instalare-și-configurare)
7. [Cum se folosește](#7-cum-se-folosește)
8. [Întrebări frecvente](#8-întrebări-frecvente)

---

## 1. Introducere

### Ce este acest proiect?

Sistemul de Control al Accesului la Foldere este o aplicație de securitate pentru macOS care protejează un folder confidențial prin monitorizare în timp real și aprobare de la distanță.

### Pentru ce este folosit?

Acest sistem este util în următoarele scenarii:

- **Protecția fișierelor confidențiale**: Păstrează documente importante în siguranță
- **Monitorizarea accesului**: Știi exact cine încearcă să acceseze folderul protejat
- **Control de la distanță**: Poți aproba sau respinge accesul direct de pe telefon
- **Audit și evidență**: Păstrează un istoric al tuturor încercărilor de acces

### Caracteristici principale

- Monitorizare în timp real a folderului protejat
- Captură foto automată cu camera web la detectarea accesului
- Notificări instant pe telefon prin dashboard web
- Aprobare/Respingere acces de la distanță
- Blocare automată a ecranului în caz de acces neautorizat
- Acces de pe telefon prin cod QR (ngrok)

---

## 2. Cum funcționează

### Diagrama fluxului

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FLUX DE FUNCȚIONARE                               │
└─────────────────────────────────────────────────────────────────────────┘

     Utilizator                  Mac (Monitor)               Admin (Telefon)
         │                            │                            │
         │ 1. Deschide folder         │                            │
         │ ─────────────────────────► │                            │
         │                            │                            │
         │                   2. Detectează acces                   │
         │                   3. Capturează foto                    │
         │                   4. Închide fereastra                  │
         │                            │                            │
         │                   5. Afișează "Așteptare..."            │
         │                            │                            │
         │                            │ 6. Trimite notificare      │
         │                            │ ─────────────────────────► │
         │                            │                            │
         │                            │        7. Vede cererea     │
         │                            │        + fotografia        │
         │                            │                            │
         │                            │ 8. Aprobă/Respinge         │
         │                            │ ◄───────────────────────── │
         │                            │                            │
         │   9a. APROBAT:             │                            │
         │       Deschide folder      │                            │
         │ ◄───────────────────────── │                            │
         │                            │                            │
         │   9b. RESPINS:             │                            │
         │       Blochează ecranul    │                            │
         │ ◄───────────────────────── │                            │
         │                            │                            │
```

### Explicație pas cu pas

1. **Utilizatorul deschide folderul** - Cineva încearcă să deschidă folderul protejat în Finder

2. **Sistemul detectează accesul** - Monitorul verifică constant ferestrele Finder și detectează accesul

3. **Se capturează o fotografie** - Camera web face automat o poză pentru identificare

4. **Fereastra este închisă** - Folderul este închis imediat pentru a preveni accesul

5. **Apare mesaj de așteptare** - Utilizatorul vede un dialog "Se așteaptă aprobarea..."

6. **Se trimite notificarea** - Cererea ajunge la serverul de administrare

7. **Administratorul vede cererea** - Pe telefon apare notificarea cu fotografia

8. **Se ia decizia** - Administratorul apasă "Aprobă" sau "Respinge"

9. **Se execută acțiunea**:
   - **Dacă aprobat**: Folderul se deschide automat
   - **Dacă respins**: Ecranul se blochează după 5 secunde

---

## 3. Componente principale

### 3.1 Monitorul (`monitor.py`)

Componenta care rulează pe Mac și monitorizează folderul protejat.

**Responsabilități:**
- Detectează când se deschide folderul în Finder
- Capturează fotografii cu camera web
- Comunică cu serverul de administrare
- Gestionează ferestrele și notificările macOS
- Blochează ecranul când accesul este respins

**Clase principale:**
- `FinderWindowMonitor` - Verifică ferestrele Finder la fiecare 0.5 secunde
- `FolderAccessHandler` - Gestionează întregul flux de aprobare

### 3.2 Dashboard-ul Web (`admin_dashboard/`)

Interfața web care permite administratorului să gestioneze cererile de acces.

**Responsabilități:**
- Afișează lista încercărilor de acces
- Arată fotografiile capturate
- Permite aprobarea sau respingerea cererilor
- Actualizează în timp real (polling)

**Tehnologie:** Django (Python web framework)

### 3.3 Baza de Date

Stochează toate încercările de acces pentru audit și istoric.

**Model principal: `AccessAttempt`**
- `timestamp` - Când s-a detectat accesul
- `access_path` - Ce folder/fișier a fost accesat
- `access_type` - Tipul accesului (folder deschis, fișier creat, etc.)
- `photo_path` - Calea către fotografia capturată
- `status` - Starea: pending (în așteptare), approved (aprobat), denied (respins)
- `decided_at` - Când s-a luat decizia

---

## 4. Tehnologii folosite

### Limbaje de programare
- **Python 3** - Limbajul principal pentru tot proiectul

### Framework-uri și biblioteci

| Bibliotecă | Versiune | Utilizare |
|------------|----------|-----------|
| Django | 4.2+ | Framework web pentru dashboard |
| AVFoundation | (nativ) | Capturare foto de la camera web (framework macOS nativ) |
| watchdog | 3.x | Monitorizare modificări fișiere |
| requests | 2.x | Comunicare HTTP cu serverul |
| pyngrok | 5.x | Tunel pentru acces de la distanță |
| qrcode | 7.x | Generare cod QR pentru acces rapid |

### Sistem de operare
- **macOS** - Proiectul folosește AppleScript pentru interacțiunea cu Finder

### Bază de date
- **SQLite** - Bază de date locală, nu necesită server separat

---

## 5. Structura proiectului

```
face_recognition/
│
├── monitor.py              # Monitorul principal - detectează accesul
├── config.py               # Configurări (folder protejat, timeout, etc.)
├── run_server.py           # Pornește serverul Django + ngrok
├── manage.py               # Utilitarul Django
├── docs.md                 # Această documentație
├── requirements.txt        # Dependențele Python
│
├── admin_dashboard/        # Configurări Django
│   ├── __init__.py
│   ├── settings.py         # Setări Django (bază de date, aplicații, etc.)
│   ├── urls.py             # Rutele URL principale
│   └── wsgi.py             # Configurare pentru servere de producție
│
├── access_control/         # Aplicația principală
│   ├── __init__.py
│   ├── models.py           # Modelul AccessAttempt (baza de date)
│   ├── views.py            # Endpoint-urile API
│   ├── urls.py             # Rutele URL pentru API
│   └── templates/
│       └── access_control/
│           └── dashboard.html  # Interfața web
│
├── captures/               # Fotografiile capturate (creat automat)
│   └── capture_*.jpg
│
├── .camera_capture         # Binar compilat pentru captură foto (creat automat)
│
└── db.sqlite3              # Baza de date SQLite (creat automat)
```

### Descrierea fișierelor

| Fișier | Descriere |
|--------|-----------|
| `monitor.py` | Scriptul principal care monitorizează folderul și gestionează fluxul de aprobare |
| `config.py` | Toate setările configurabile (folder protejat, timeout, server, etc.) |
| `run_server.py` | Pornește serverul web Django și optional tunelul ngrok |
| `requirements.txt` | Lista dependențelor Python necesare |
| `.camera_capture` | Binar Swift compilat automat pentru captura foto (AVFoundation) |
| `settings.py` | Configurările framework-ului Django |
| `models.py` | Definește structura bazei de date (modelul AccessAttempt) |
| `views.py` | Funcțiile care răspund la cereri HTTP (endpoint-uri API) |
| `urls.py` | Maparea URL-urilor la funcțiile corespunzătoare |

---

## 6. Instalare și configurare

### Cerințe preliminare

- macOS (10.14 sau mai recent)
- Python 3.8 sau mai recent
- Xcode Command Line Tools (pentru compilarea camerei)
- Cameră web funcțională (opțional, pentru captură foto)

### Pași de instalare

#### Pasul 1: Clonează sau descarcă proiectul

```bash
cd ~/Desktop
# Proiectul ar trebui să fie deja în face_recognition/
```

#### Pasul 2: Instalează dependențele

```bash
cd face_recognition
pip3 install -r requirements.txt
```

Sau manual:
```bash
pip3 install django watchdog requests pyngrok qrcode
```

> **Notă**: Nu este nevoie de mediu virtual (venv). Camera folosește AVFoundation (framework macOS nativ) - nu necesită instalare separată. La prima rulare, sistemul compilează automat un mic binar Swift pentru captura foto.

#### Pasul 3: Inițializează baza de date

```bash
python3 manage.py migrate
```

#### Pasul 4: Configurează folderul protejat

Editează `config.py` și setează:

```python
# Varianta 1: Doar numele folderului (va fi căutat automat)
PROTECTED_FOLDER = "Confidential"

# Varianta 2: Calea completă
PROTECTED_FOLDER = "/Users/numeletău/Desktop/FolderSecret"
```

#### Pasul 5: Configurează ngrok (opțional, pentru acces de pe telefon)

1. Creează un cont pe [ngrok.com](https://ngrok.com)
2. Copiază token-ul de autentificare
3. Rulează: `ngrok config add-authtoken TOKENUL_TĂU`

### Verificare instalare

```bash
# Verifică că Python funcționează
python3 --version

# Verifică că Django funcționează
python3 manage.py check

# Verifică că Swift (pentru cameră) funcționează
swiftc --version
```

---

## 7. Cum se folosește

### Pornirea sistemului

Trebuie să pornești **ambele componente** în terminale separate:

#### Terminal 1: Serverul web

```bash
cd ~/Desktop/face_recognition
python3 run_server.py
```

Vei vedea:
- URL-ul local: `http://localhost:5000`
- URL-ul public (dacă ngrok este activat)
- Codul QR pentru acces de pe telefon

#### Terminal 2: Monitorul

```bash
cd ~/Desktop/face_recognition
python3 monitor.py
```

Vei vedea:
- Folderul monitorizat
- Mesaj "Se așteaptă încercări de acces..."

### Utilizare pas cu pas

1. **Pornește ambele componente** (server + monitor)

2. **Accesează dashboard-ul** de pe telefon:
   - Scanează codul QR cu camera telefonului
   - SAU deschide URL-ul ngrok în browser

3. **Testează sistemul**:
   - Deschide folderul protejat în Finder
   - Observă cum:
     - Fereastra se închide automat
     - Apare un dialog "Se așteaptă aprobarea..."
     - În dashboard apare o nouă cerere cu fotografia

4. **Ia o decizie**:
   - Apasă "Aprobă" - folderul se deschide
   - Apasă "Respinge" - ecranul se blochează după 5 secunde

### Oprirea sistemului

- **Monitor**: Apasă `Ctrl+C` în terminal
- **Server**: Apasă `Ctrl+C` în terminal

---

## 8. Întrebări frecvente

### Q: Ce se întâmplă dacă serverul nu răspunde?

**A:** Dacă serverul nu este disponibil sau nu răspunde în timpul limită (30 secunde implicit), accesul este respins automat și ecranul se blochează.

### Q: Pot folosi sistemul fără cameră web?

**A:** Da! Dacă camera nu este disponibilă sau nu ai acordat permisiunea de acces, sistemul funcționează normal, dar fără captură foto. Camera folosește framework-ul nativ macOS AVFoundation - nu necesită software extern.

### Q: Cum schimb timpul de așteptare pentru aprobare?

**A:** Editează `config.py` și modifică:
```python
APPROVAL_TIMEOUT = 60  # 60 secunde în loc de 30
```

### Q: Pot proteja mai multe foldere?

**A:** În versiunea curentă, poți proteja doar un folder (și toate subfolderele sale). Pentru mai multe foldere, ai nevoie de instanțe separate ale monitorului.

### Q: Funcționează pe Windows sau Linux?

**A:** Nu. Proiectul folosește AppleScript pentru interacțiunea cu Finder, deci funcționează doar pe macOS.

### Q: Este sigur pentru date sensibile?

**A:** Sistemul oferă un strat suplimentar de securitate, dar nu înlocuiește criptarea. Pentru date foarte sensibile, recomandăm și criptarea folderului.

### Q: Cum văd istoricul accesărilor?

**A:** În dashboard-ul web vezi toate încercările de acces (aprobate, respinse și în așteptare). Datele sunt stocate în baza de date SQLite.

### Q: Pot folosi sistemul fără ngrok?

**A:** Da! Setează `USE_NGROK = False` în `run_server.py`. Vei putea accesa dashboard-ul doar de pe același calculator la `http://localhost:5000`.

### Q: Cât timp rămâne validă o aprobare?

**A:** După aprobare, utilizatorul are 5 minute să acceseze folderul fără a mai necesita aprobare. Acest timp poate fi modificat în `monitor.py` (variabila `APPROVAL_CACHE_DURATION`).

---

## Suport și contact

Pentru întrebări sau probleme, verifică:
1. Această documentație
2. Comentariile din cod (toate fișierele sunt documentate în română)
3. Mesajele de debug din terminal (prefixate cu `[DEBUG]`)

---

**Autor:** Bascacov Alexandra
**Versiune:** 1.0
**Ultima actualizare:** Ianuarie 2025
