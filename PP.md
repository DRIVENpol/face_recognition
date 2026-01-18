# Sistem de Control al Accesului la Foldere
## Slide-uri Prezentare

---

## Slide 1: Titlu

**Sistem de Control al Accesului la Foldere**

O Soluție de Securitate în Timp Real pentru macOS

*Bascacov Alexandra*

---

## Slide 2: Problema

**Provocarea**

- Fișierele sensibile necesită protecție dincolo de simple parole
- Nu există modalitate de a ști CINE accesează folderele confidențiale
- Securitatea tradițională nu oferă monitorizare în timp real
- Aprobarea de la distanță nu este posibilă cu instrumentele standard

---

## Slide 3: Soluția Propusă

**Ce Am Construit**

Un sistem de protecție a folderelor în timp real care:

- Monitorizează un folder confidențial 24/7
- Capturează dovezi foto ale încercărilor de acces
- Notifică proprietarul instant pe telefon
- Permite decizii de aprobare/respingere de la distanță
- Blochează ecranul dacă accesul este respins

---

## Slide 4: Arhitectura Sistemului

**Design de Nivel Înalt**

```
+-------------+        +--------------+        +---------------+
|   Monitor   | <----> |  Server Web  | <----> |   Dashboard   |
|    (Mac)    |        |   (Django)   |        |   (Mobil)     |
+-------------+        +--------------+        +---------------+
      |                       |                       |
  Detectează &           Procesează             Admin vede &
  Capturează             Cererile               Decide
```

Trei componente interconectate care lucrează împreună

---

## Slide 5: Cum Funcționează

**Fluxul de Acces (5 Pași)**

1. Cineva deschide folderul protejat
2. Sistemul detectează accesul și capturează o fotografie
3. Folderul se închide, apare mesaj de așteptare
4. Administratorul primește notificare cu fotografia
5. Adminul aprobă (folderul se deschide) sau respinge (ecranul se blochează)

---

## Slide 6: Funcționalități Cheie

**Ce Îl Face Special**

- Monitorizare folder în timp real
- Captură foto automată cu camera web
- Notificări instant pe mobil
- Aprobare/respingere de oriunde
- Blocare automată ecran la respingere
- Cod QR pentru acces mobil rapid
- Istoric complet al accesărilor

---

## Slide 7: Componenta Monitor

**Paznicul**

**Scop:** Rulează pe Mac, monitorizează folderul protejat

**Ce face:**
- Verifică ferestrele Finder la fiecare 0.5 secunde
- Capturează foto folosind camera macOS (AVFoundation)
- Închide fereastra folderului imediat
- Afișează dialog "Se așteaptă aprobarea"
- Comunică cu serverul pentru decizie
- Execută acțiunea (deschide folder sau blochează ecran)

---

## Slide 8: Dashboard-ul Web

**Centrul de Comandă**

**Scop:** Interfață admin accesibilă de pe orice dispozitiv

**Funcționalități:**
- Vizualizare toate încercările de acces
- Afișare fotografii capturate
- Aprobare sau respingere cu un click
- Actualizări în timp real
- Istoric accesări și jurnal de audit
- Design responsive pentru mobil

---

## Slide 9: Diagrama Fluxului de Securitate

**Rezultatele Deciziei**

```
                    +--------------------+
                    | Încercare de Acces |
                    |   + Foto Captată   |
                    +---------+----------+
                              |
                    +---------v----------+
                    |  Decizia Adminului |
                    +---------+----------+
                              |
              +---------------+---------------+
              |                               |
     +--------v--------+             +--------v--------+
     |     APROBAT     |             |     RESPINS     |
     +-----------------+             +-----------------+
     |                 |             |                 |
     | Folderul se     |             | Ecranul se      |
     | deschide        |             | blochează în    |
     | Acces acordat   |             | 5 secunde       |
     +-----------------+             +-----------------+
```

---

## Slide 10: Tehnologii Folosite

**Stack Tehnologic**

| Componentă | Tehnologie |
|------------|------------|
| Limbaj | Python 3 |
| Framework Web | Django |
| Cameră | AVFoundation (nativ macOS) |
| Monitorizare Fișiere | watchdog |
| Acces la Distanță | tunel ngrok |
| Generare QR | biblioteca qrcode |
| Bază de Date | SQLite |
| Platformă | doar macOS |

---

## Slide 11: Experiența Utilizatorului

**Din perspectiva utilizatorului:**
- Vede folderul închizându-se automat
- Primește mesaj "Se așteaptă aprobarea"
- Primește acces sau ecranul se blochează

**Din perspectiva adminului:**
- Scanează codul QR o dată pentru acces mobil
- Primește notificări instant
- Vede fotografia celui care a încercat accesul
- O singură apăsare pentru aprobare sau respingere

---

## Slide 12: Provocări și Soluții

**Probleme Întâmpinate**

| Provocare | Soluție |
|-----------|---------|
| Permisiuni cameră macOS | Binar Swift cu AVFoundation |
| Acces mobil de la distanță | Tunel ngrok cu cod QR |
| Notificări în timp real | Dashboard cu polling |
| Detectare fereastră Finder | Integrare AppleScript |
| Prevenire alerte multiple | Timer cooldown (5 sec) |

---

## Slide 13: Îmbunătățiri Viitoare

**Posibile Dezvoltări**

- Recunoaștere facială pentru aprobare automată
- Protecție foldere multiple
- Notificări push (în loc de polling)
- Suport Windows/Linux
- Integrare criptare
- Conturi multiple de admin
- Autentificare în doi pași

---

## Slide 14: Concluzii

**Rezumat**

- Am construit o soluție completă de securitate pentru foldere
- Monitorizare în timp real cu captură foto
- Control de la distanță de pe dispozitivul mobil
- Aplicație practică a Python, Django și API-urilor macOS
- Echilibru între securitate și ușurință în utilizare

---

## Slide 15: Întrebări

**Întrebări?**

*Vă mulțumesc pentru atenție*

---

### Note pentru Prezentator

**Slide 4:** Subliniază arhitectura pe trei nivele și cum fiecare componentă are un rol specific.

**Slide 5:** Acesta este fluxul principal - parcurge un scenariu real.

**Slide 9:** Arată cum sistemul gestionează ambele rezultate în mod decisiv.

**Slide 12:** Împărtășește experiențe reale de dezvoltare și cum au fost rezolvate problemele.
