"""
Monitor pentru Accesul la Foldere - Sistem de Securitate

Descriere:
    Acest modul monitorizează un folder protejat și solicită aprobarea
    administratorului înainte de a permite accesul. Când cineva încearcă
    să deschidă folderul protejat, sistemul:
    1. Detectează accesul prin monitorizarea ferestrelor Finder
    2. Capturează o fotografie cu camera web
    3. Închide fereastra și afișează un mesaj de așteptare
    4. Trimite cererea către serverul de administrare
    5. Așteaptă decizia administratorului (aprobare/respingere)
    6. Dacă este aprobat, deschide folderul; dacă nu, blochează ecranul

Autor: Paul Socarde
Versiune: 1.0
"""

import os
import time
import subprocess
import requests
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import (
    PROTECTED_FOLDER, SEARCH_ROOT, SERVER_URL, APPROVAL_TIMEOUT, ACCESS_COOLDOWN
)

# Încercăm să importăm OpenCV pentru capturarea fotografiilor
# OpenCV este o bibliotecă pentru procesarea imaginilor și video
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("Avertisment: OpenCV nu este instalat. Captura foto este dezactivată. Rulează: pip install opencv-python")

# Directorul unde se salvează fotografiile capturate
CAPTURES_DIR = os.path.join(os.path.dirname(__file__), 'captures')


def capture_photo():
    """
    Capturează o fotografie de la camera web și o salvează.

    Această funcție este apelată automat când cineva încearcă să acceseze
    folderul protejat. Fotografia este trimisă către administrator pentru
    a verifica identitatea persoanei care solicită accesul.

    Returnează:
        str: Numele fișierului salvat (ex: 'capture_20250117_143052.jpg')
        None: Dacă captura a eșuat sau OpenCV nu este disponibil
    """
    if not OPENCV_AVAILABLE:
        print("[DEBUG] OpenCV nu este disponibil - se omite captura foto")
        return None

    # Ne asigurăm că directorul pentru capturi există
    os.makedirs(CAPTURES_DIR, exist_ok=True)

    # Generăm numele fișierului cu marca temporală (timestamp)
    # Format: capture_YYYYMMDD_HHMMSS.jpg
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'capture_{timestamp}.jpg'
    filepath = os.path.join(CAPTURES_DIR, filename)

    print(f"[DEBUG] Se capturează fotografia...")

    try:
        # Deschidem camera web (0 = camera implicită/principală)
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("[DEBUG] Nu s-a putut deschide camera web")
            return None

        # Așteptăm puțin pentru ca camera să se inițializeze
        time.sleep(0.5)

        # Capturăm un cadru (frame) de la cameră
        ret, frame = cap.read()

        # Eliberăm camera pentru alte aplicații
        cap.release()

        if ret:
            # Salvăm imaginea pe disc
            cv2.imwrite(filepath, frame)
            print(f"[DEBUG] Fotografie salvată: {filename}")
            return filename
        else:
            print("[DEBUG] Eșec la capturarea cadrului")
            return None

    except Exception as e:
        print(f"[DEBUG] Eroare la capturarea fotografiei: {e}")
        return None


class FinderWindowMonitor:
    """
    Monitor pentru Ferestrele Finder - Detectează deschiderea folderului protejat.

    Această clasă verifică periodic (la fiecare 0.5 secunde) toate ferestrele
    Finder deschise pentru a detecta dacă utilizatorul încearcă să acceseze
    folderul protejat sau oricare subfolder al acestuia.

    Funcționare:
        - Folosește AppleScript pentru a interoga aplicația Finder
        - Obține lista tuturor căilor deschise în ferestre Finder
        - Compară căile cu folderul protejat
        - Declanșează fluxul de aprobare când detectează acces

    Atribute:
        protected_path (str): Calea completă către folderul protejat
        handler (FolderAccessHandler): Obiectul care gestionează evenimentele
        running (bool): Indicator dacă monitorul este activ
    """

    def __init__(self, protected_path, handler):
        """
        Inițializează monitorul pentru ferestre Finder.

        Parametri:
            protected_path (str): Calea către folderul de monitorizat
            handler (FolderAccessHandler): Handler-ul pentru evenimente
        """
        self.protected_path = protected_path
        self.handler = handler
        self.running = False

    def check_finder_windows(self):
        """
        Verifică dacă Finder are folderul protejat deschis.

        Folosește AppleScript pentru a obține lista tuturor ferestrelor Finder
        și verifică dacă vreuna dintre ele afișează folderul protejat.

        Returnează:
            bool: True dacă folderul protejat este deschis, False altfel
        """
        # Script AppleScript pentru a obține toate căile ferestrelor Finder
        # Folosește 'folder of' pentru a gestiona ferestrele de folder obișnuite
        script = '''
        tell application "Finder"
            set windowPaths to {}
            set windowCount to count of windows
            repeat with i from 1 to windowCount
                try
                    set w to window i
                    set t to target of w
                    set p to POSIX path of (t as alias)
                    set end of windowPaths to p
                on error errMsg
                    -- Window might be a special view (Recents, Tags, etc.)
                    log "Window " & i & " error: " & errMsg
                end try
            end repeat
            return windowPaths
        end tell
        '''
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True
        )
        # Log raw output for debugging
        raw_out = result.stdout.strip()
        raw_err = result.stderr.strip()
        if raw_out or raw_err:
            print(f"[DEBUG] AppleScript output: '{raw_out}' | stderr: '{raw_err}'")
        if result.returncode != 0:
            print(f"[DEBUG] AppleScript FAILED: rc={result.returncode}, stderr='{result.stderr.strip()}'")
        if result.returncode == 0:
            # Parse the output - it's a comma-separated list
            paths = result.stdout.strip()
            if paths:
                print(f"[DEBUG] Finder windows detected: {paths}")
                print(f"[DEBUG] Looking for: {self.protected_path} (or subfolders)")
                # Check if our protected folder OR any subfolder is open
                # Normalize paths for comparison
                protected_normalized = self.protected_path.rstrip('/') + '/'
                for path in paths.split(', '):
                    path_normalized = path.strip().rstrip('/') + '/'
                    # Check if path is the protected folder OR inside it
                    if path_normalized.startswith(protected_normalized) or path_normalized == protected_normalized:
                        print(f"[DEBUG] MATCH FOUND: '{path_normalized}' is within protected area")
                        return True
        return False

    def start(self):
        """
        Pornește monitorizarea ferestrelor Finder.

        Creează un fir de execuție (thread) separat care verifică periodic
        toate ferestrele Finder pentru a detecta accesul la folderul protejat.
        """
        import threading
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Oprește monitorizarea ferestrelor Finder."""
        self.running = False

    def _poll_loop(self):
        """
        Buclă de verificare periodică - rulează în fundal.

        Verifică ferestrele Finder la fiecare 0.5 secunde. Dacă detectează
        că folderul protejat este deschis, declanșează fluxul de aprobare.
        """
        print("[DEBUG] _poll_loop STARTED")
        poll_num = 0
        while self.running:
            poll_num += 1
            if self.handler.pending_approval:
                if poll_num % 10 == 1:
                    print(f"[DEBUG] Poll #{poll_num} - skipped (pending_approval=True)")
            elif self.handler.is_approval_cached(path=self.protected_path, log=True):  # Always log
                pass  # Skip - approval cached
            else:
                if poll_num % 10 == 1:  # Print every 5 seconds (10 * 0.5s)
                    print(f"[DEBUG] Poll #{poll_num} - checking Finder windows...")
                is_open = self.check_finder_windows()
                if is_open:
                    print(f"[DEBUG] Protected folder detected in Finder!")
                    print("\n[Finder window detected for protected folder]")
                    self.handler.handle_access(self.protected_path, 'folder_opened')
            time.sleep(0.5)


class FolderAccessHandler(FileSystemEventHandler):
    """
    Handler pentru Evenimente de Acces la Folder - Gestionează fluxul de aprobare.

    Această clasă este componenta principală care:
    - Detectează evenimentele de acces la fișiere/foldere
    - Capturează fotografii ale utilizatorului
    - Comunică cu serverul de administrare
    - Gestionează aprobările și respingerile
    - Blochează ecranul în caz de acces neautorizat

    Funcționare:
        1. Primește eveniment de acces (folder deschis sau fișier accesat)
        2. Verifică dacă trebuie să declanșeze fluxul de aprobare
        3. Capturează fotografie, închide fereastra, arată mesaj de așteptare
        4. Trimite cererea la server și așteaptă decizia
        5. Acționează conform deciziei (deschide folder sau blochează ecran)

    Atribute:
        protected_path (str): Calea către folderul protejat
        last_access_time (float): Timestamp-ul ultimului acces detectat
        pending_approval (bool): True dacă așteptăm o decizie
        approved_until (float): Timestamp până când aprobarea este validă
        APPROVAL_CACHE_DURATION (int): Durata în secunde cât rămâne validă aprobarea
    """

    # Cât timp (secunde) după aprobare înainte de a necesita re-aprobare
    APPROVAL_CACHE_DURATION = 300  # 5 minute

    def __init__(self, protected_path):
        """
        Inițializează handler-ul pentru evenimente de acces.

        Parametri:
            protected_path (str): Calea completă către folderul protejat
        """
        super().__init__()
        self.protected_path = protected_path
        self.last_access_time = 0
        self.pending_approval = False
        self.approved_until = 0  # Timestamp când expiră aprobarea
        self.approved_path = None  # Track which path was approved

    def is_approval_cached(self, path=None, log=False):
        """
        Verifică dacă suntem în perioada de cache pentru aprobare.

        După ce administratorul aprobă accesul, utilizatorul are 5 minute
        în care poate accesa folderul fără a mai necesita aprobare.

        Parametri:
            path (str, optional): Calea de verificat (fișier sau folder)
            log (bool): Dacă să afișeze mesaje de debug

        Returnează:
            bool: True dacă aprobarea este încă validă, False altfel
        """
        current = time.time()
        if current < self.approved_until and self.approved_path:
            # Check if the given path is the approved path OR inside it
            if path:
                path_normalized = os.path.normpath(path)
                approved_normalized = os.path.normpath(self.approved_path)
                # Path is approved if it IS the approved path or STARTS WITH it
                if path_normalized == approved_normalized or path_normalized.startswith(approved_normalized + os.sep):
                    if log:
                        remaining = int(self.approved_until - current)
                        print(f"[DEBUG] Approval VALID for {path} - {remaining}s remaining")
                    return True
            else:
                # No path specified, just check time
                if log:
                    remaining = int(self.approved_until - current)
                    print(f"[DEBUG] Approval VALID - {remaining}s remaining")
                return True
        if log:
            print(f"[DEBUG] Approval EXPIRED or path not covered")
        return False

    def should_trigger(self, event):
        """
        Verifică dacă acest eveniment trebuie să declanșeze fluxul de aprobare.

        Filtrează evenimentele pentru a evita declanșări multiple sau inutile.
        Nu declanșează dacă:
        - Avem deja o aprobare validă (în cache)
        - Suntem în perioada de cooldown (pauză între alertă)
        - Deja așteptăm o aprobare
        - Este un fișier ascuns sau de sistem

        Parametri:
            event: Evenimentul de sistem de fișiere detectat

        Returnează:
            bool: True dacă trebuie să declanșăm fluxul, False altfel
        """
        # Verificăm dacă suntem în perioada de cache pentru aprobare
        if self.is_approval_cached(path=event.src_path, log=True):
            return False

        # Verificăm perioada de cooldown (pauză între alerte)
        current_time = time.time()
        if current_time - self.last_access_time < ACCESS_COOLDOWN:
            return False

        # Nu declanșăm dacă deja așteptăm o aprobare
        if self.pending_approval:
            return False

        # Obținem numele fișierului
        basename = os.path.basename(event.src_path) if event.src_path else ""

        # Ignorăm fișierele ascunse (inclusiv .DS_Store - deschiderea folderului
        # este gestionată de FinderWindowMonitor)
        if basename.startswith('.'):
            return False

        # Ignorăm alte fișiere de sistem comune
        if basename in ['Thumbs.db', 'desktop.ini']:
            return False

        return True

    def get_display_info(self, event):
        """
        Obține informații de afișare pentru eveniment.

        Determină calea și tipul de acces pentru a le afișa utilizatorului
        și a le trimite la server.

        Parametri:
            event: Evenimentul de sistem de fișiere

        Returnează:
            tuple: (cale_afișare, tip_acces)
        """
        basename = os.path.basename(event.src_path) if event.src_path else ""

        # .DS_Store indică faptul că Finder a deschis folderul
        if basename == '.DS_Store':
            return self.protected_path, 'folder_opened'

        return event.src_path, f'file_{event.event_type}'

    def on_any_event(self, event):
        """
        Gestionează orice eveniment de sistem de fișiere.

        Această metodă este apelată automat de biblioteca watchdog
        când se detectează orice modificare în folderul monitorizat.

        Parametri:
            event: Evenimentul detectat (creare, modificare, ștergere, etc.)
        """
        # Debug: afișăm TOATE evenimentele
        print(f"[DEBUG] Eveniment: {event.event_type} - {event.src_path}")

        if not self.should_trigger(event):
            return

        # Update last access time
        self.last_access_time = time.time()

        # Get display info
        display_path, access_type = self.get_display_info(event)

        print(f"\n{'='*50}")
        print(f"ACCESS DETECTED: {access_type}")
        print(f"Path: {display_path}")
        print(f"{'='*50}")

        self.handle_access(display_path, access_type)

    def handle_access(self, path, access_type):
        """
        Gestionează accesul la folder - trimite la server și așteaptă decizia.

        Aceasta este metoda principală care orchestrează întregul flux de aprobare:
        1. Capturează fotografie cu camera web
        2. Închide fereastra Finder
        3. Afișează popup de așteptare
        4. Trimite cererea la server (cu fotografia)
        5. Așteaptă decizia administratorului
        6. Execută acțiunea corespunzătoare (deschide folder sau blochează)

        Parametri:
            path (str): Calea folderului/fișierului accesat
            access_type (str): Tipul accesului ('folder_opened', 'file_created', etc.)
        """
        print(f"[DEBUG] handle_access START - cale={path}, tip={access_type}")
        self.pending_approval = True

        try:
            # FIRST: Capture photo of who is accessing
            print("[DEBUG] Step 0: Capturing photo...")
            photo_filename = capture_photo()
            print(f"[DEBUG] Step 0 DONE - photo={photo_filename}")

            # Close the Finder window
            print("[DEBUG] Step 1: Closing Finder window...")
            print("Closing Finder window - awaiting approval...")
            self.close_finder_window(self.protected_path)
            print("[DEBUG] Step 1 DONE")

            # Show waiting popup
            print("[DEBUG] Step 2: Showing waiting popup...")
            self.show_waiting_popup()
            print("[DEBUG] Step 2 DONE")

            # Send to server (with photo)
            print("[DEBUG] Step 3: Sending to server...")
            attempt_id = self.send_to_server(path, access_type, photo_filename)
            print(f"[DEBUG] Step 3 DONE - attempt_id={attempt_id}")
            if not attempt_id:
                print("[DEBUG] No attempt_id - server failed")
                print("Failed to contact server - denying access")
                self.close_waiting_popup()
                self.show_warning_and_lock()
                return

            # Wait for decision
            print("[DEBUG] Step 4: Waiting for decision...")
            decision = self.wait_for_decision(attempt_id)
            print(f"[DEBUG] Step 4 DONE - decision={decision}")

            # Close waiting popup
            self.close_waiting_popup()

            # Act on decision
            if decision == 'approved':
                print("[DEBUG] Decision is APPROVED - opening folder")
                # Cache the approval for 5 minutes
                self.approved_until = time.time() + self.APPROVAL_CACHE_DURATION
                self.approved_path = self.protected_path  # Always approve the root protected folder
                print(f"[DEBUG] APPROVAL SET: approved_until = {self.approved_until} (current={time.time()})")
                print("ACCESS GRANTED - Opening folder...")
                self.show_approved_notification()
                self.open_folder(self.protected_path)
            else:
                print("[DEBUG] Decision is DENIED - showing warning and locking")
                self.show_warning_and_lock()
        finally:
            print("[DEBUG] handle_access FINALLY - resetting state")
            self.pending_approval = False
            # Delete .DS_Store again so we can detect next open
            delete_ds_store(self.protected_path)

    def send_to_server(self, path, access_type, photo_filename=None):
        """
        Trimite încercarea de acces la serverul de administrare.

        Creează o cerere HTTP POST către server cu informațiile despre
        încercarea de acces, inclusiv fotografia capturată.

        Parametri:
            path (str): Calea folderului/fișierului accesat
            access_type (str): Tipul accesului
            photo_filename (str, optional): Numele fișierului foto capturat

        Returnează:
            int: ID-ul încercării înregistrate pe server
            None: Dacă comunicarea cu serverul a eșuat
        """
        try:
            payload = {
                'folder_path': path,
                'access_type': access_type
            }
            if photo_filename:
                payload['photo_path'] = photo_filename

            response = requests.post(
                f"{SERVER_URL}/api/attempt",
                json=payload,
                timeout=10
            )
            data = response.json()
            print(f"Attempt registered with ID: {data['id']}")
            return data['id']
        except requests.exceptions.ConnectionError:
            print("ERROR: Could not connect to admin server")
            print(f"Make sure admin_server.py is running at {SERVER_URL}")
            return None
        except Exception as e:
            print(f"ERROR: {e}")
            return None

    def wait_for_decision(self, attempt_id):
        """
        Așteaptă decizia administratorului cu timeout.

        Interoghează periodic serverul pentru a verifica dacă administratorul
        a luat o decizie. Dacă timeout-ul expiră fără decizie, accesul este
        refuzat automat.

        Parametri:
            attempt_id (int): ID-ul încercării de acces

        Returnează:
            str: 'approved' sau 'denied'
        """
        print(f"[DEBUG] wait_for_decision START - attempt_id={attempt_id}")
        print(f"Waiting for admin approval (timeout: {APPROVAL_TIMEOUT}s)...")

        start_time = time.time()
        poll_count = 0
        while time.time() - start_time < APPROVAL_TIMEOUT:
            try:
                poll_count += 1
                elapsed = time.time() - start_time
                print(f"[DEBUG] Polling server (#{poll_count}, elapsed={elapsed:.1f}s)...")
                response = requests.get(f"{SERVER_URL}/api/attempt/{attempt_id}")
                data = response.json()
                print(f"[DEBUG] Server response: status={data.get('status')}")

                if data['status'] == 'approved':
                    print("[DEBUG] wait_for_decision returning 'approved'")
                    return 'approved'
                elif data['status'] == 'denied':
                    print("[DEBUG] wait_for_decision returning 'denied'")
                    return 'denied'

                # Still pending, wait and retry
                time.sleep(1)

            except Exception as e:
                print(f"[DEBUG] Poll error: {e}")
                print(f"Error checking status: {e}")
                time.sleep(1)

        # Timeout reached
        print("[DEBUG] wait_for_decision TIMEOUT")
        print("Timeout reached - auto-denying")
        return 'denied'

    def close_finder_window(self, folder_path):
        """
        Închide fereastra Finder și fereastra aplicației din prim-plan.

        Folosește AppleScript pentru a închide toate ferestrele Finder și
        fereastra aplicației active (cu excepția Terminal și editorilor de cod).
        """
        print("[DEBUG] close_finder_window apelat")
        time.sleep(0.3)  # Let window render

        # Get the frontmost app and close its windows (except Terminal/Code)
        close_frontmost_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
        end tell
        return frontApp
        '''
        result_front = subprocess.run(
            ['osascript', '-e', close_frontmost_script],
            capture_output=True,
            text=True
        )
        frontmost_app = result_front.stdout.strip()
        print(f"[DEBUG] Frontmost app: '{frontmost_app}'")

        # Close that app's windows if it's not our terminal/editor
        excluded_apps = ['Terminal', 'Code', 'iTerm2', 'iTerm', 'python', 'Python']
        if frontmost_app and frontmost_app not in excluded_apps:
            close_app_script = f'tell application "{frontmost_app}" to close every window'
            result_close = subprocess.run(
                ['osascript', '-e', close_app_script],
                capture_output=True,
                text=True
            )
            print(f"[DEBUG] Close {frontmost_app} windows result: rc={result_close.returncode}, stderr={result_close.stderr}")

        # Also close ALL Finder windows
        result = subprocess.run(
            ['osascript', '-e', 'tell application "Finder" to close every window'],
            capture_output=True,
            text=True
        )
        print(f"[DEBUG] close Finder windows result: rc={result.returncode}, stderr={result.stderr}")

    def show_waiting_popup(self):
        """
        Afișează un popup de notificare că accesul așteaptă aprobare.

        Creează un dialog AppleScript care informează utilizatorul că
        cererea de acces a fost trimisă și așteaptă decizia administratorului.
        """
        print("[DEBUG] Se lansează popup-ul de așteptare...")
        script = '''
        display dialog "Protected folder access detected.

Awaiting admin approval..." buttons {} giving up after 300 with title "Access Control" with icon caution
        '''
        # Run in background so it doesn't block
        self.popup_process = subprocess.Popen(
            ['osascript', '-e', script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"[DEBUG] Popup process started: pid={self.popup_process.pid}")

    def close_waiting_popup(self):
        """
        Închide popup-ul de așteptare.

        Termină procesul AppleScript care afișează dialogul de așteptare.
        """
        if hasattr(self, 'popup_process') and self.popup_process:
            self.popup_process.terminate()
            self.popup_process = None
        # Oprim orice dialog osascript
        subprocess.run(['pkill', '-f', 'osascript.*display dialog'], capture_output=True)

    def show_approved_notification(self):
        """
        Afișează notificarea de aprobare.

        Arată un mesaj macOS care informează utilizatorul că accesul a fost aprobat.
        """
        subprocess.run([
            'osascript', '-e',
            'display notification "Folder access approved by admin" with title "Access Granted" sound name "Glass"'
        ])

    def open_folder(self, folder_path):
        """
        Deschide folderul în Finder.

        Parametri:
            folder_path (str): Calea completă către folder
        """
        subprocess.run(['open', folder_path])

    def lock_screen(self):
        """
        Blochează ecranul Mac-ului pornind screen saver-ul.

        Dacă opțiunea "Solicită parolă" este activată în Preferințe Sistem,
        aceasta blochează efectiv ecranul și necesită autentificare.
        """
        print("SE BLOCHEAZĂ ECRANUL - Acces refuzat!")
        # Pornește screen saver-ul - dacă "require password" este activat
        # în System Preferences, aceasta blochează efectiv ecranul
        subprocess.run([
            'open', '-a', 'ScreenSaverEngine'
        ])

    def show_warning_and_lock(self):
        """
        Afișează un avertisment și blochează ecranul după 5 secunde.

        Arată o notificare de avertizare pentru acces neautorizat și
        apoi blochează ecranul pentru a proteja sistemul.
        """
        # Show non-blocking notification
        subprocess.Popen([
            'osascript', '-e',
            'display notification "Screen will lock in 5 seconds..." with title "ACCESS DENIED" subtitle "Unauthorized folder access detected!" sound name "Basso"'
        ])

        # Wait 5 seconds
        print("[DEBUG] Warning shown - locking in 5 seconds...")
        time.sleep(5)

        # Lock the screen
        self.lock_screen()


def find_folder(name, search_root):
    """
    Caută un folder după nume în directorul specificat.

    Parcurge recursiv toate subdirectoarele pentru a găsi un folder
    cu numele specificat.

    Parametri:
        name (str): Numele folderului de căutat
        search_root (str): Directorul rădăcină unde să caute

    Returnează:
        str: Calea completă către folder dacă a fost găsit
        None: Dacă folderul nu a fost găsit
    """
    print(f"Se caută folderul '{name}' în {search_root}...")

    for root, dirs, files in os.walk(search_root):
        # Omitem directoarele ascunse
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        if name in dirs:
            found_path = os.path.join(root, name)
            print(f"Găsit: {found_path}")
            return found_path

    return None


def get_protected_folder_path():
    """
    Obține calea completă către folderul protejat.

    Verifică dacă PROTECTED_FOLDER din config este o cale completă sau
    doar un nume de folder. Dacă este doar un nume, caută folderul
    în directorul SEARCH_ROOT.

    Returnează:
        str: Calea completă către folderul protejat
        None: Dacă folderul nu poate fi găsit sau validat
    """
    # Verificăm dacă PROTECTED_FOLDER este deja o cale completă
    if os.path.isabs(PROTECTED_FOLDER):
        if os.path.isdir(PROTECTED_FOLDER):
            return PROTECTED_FOLDER
        else:
            print(f"EROARE: Calea specificată nu există: {PROTECTED_FOLDER}")
            return None

    # Căutăm folderul după nume
    found_path = find_folder(PROTECTED_FOLDER, SEARCH_ROOT)
    if found_path:
        return found_path

    print(f"EROARE: Nu s-a putut găsi folderul '{PROTECTED_FOLDER}' în {SEARCH_ROOT}")
    return None


def delete_ds_store(folder_path):
    """
    Șterge fișierul .DS_Store pentru ca Finder să îl recreeze la deschidere.

    Fișierul .DS_Store este creat de Finder când se deschide un folder.
    Prin ștergerea lui, putem detecta următoarea deschidere a folderului.

    Parametri:
        folder_path (str): Calea către folder
    """
    ds_store = os.path.join(folder_path, '.DS_Store')
    try:
        if os.path.exists(ds_store):
            os.remove(ds_store)
            print(f"S-a șters .DS_Store pentru a permite detectarea deschiderii")
    except Exception as e:
        print(f"Avertisment: Nu s-a putut șterge .DS_Store: {e}")


def main():
    """
    Funcția principală - punctul de intrare al aplicației.

    Această funcție:
    1. Validează și găsește folderul protejat
    2. Inițializează monitorul de sistem de fișiere (watchdog)
    3. Inițializează monitorul de ferestre Finder
    4. Rulează în buclă până la întrerupere (Ctrl+C)

    Monitorizarea funcționează pe două canale:
    - Watchdog: Detectează modificări de fișiere în folder
    - FinderWindowMonitor: Detectează deschiderea folderului în Finder
    """
    print("=" * 50)
    print("  MONITOR ACCES FOLDER")
    print("=" * 50)

    # Găsim sau validăm folderul protejat
    protected_path = get_protected_folder_path()
    if not protected_path:
        print("\nFailed to locate protected folder.")
        print("Please check your config.py settings:")
        print(f"  PROTECTED_FOLDER = '{PROTECTED_FOLDER}'")
        print(f"  SEARCH_ROOT = '{SEARCH_ROOT}'")
        return

    # Delete .DS_Store so we can detect when Finder opens the folder
    delete_ds_store(protected_path)

    print(f"\nMonitoring folder: {protected_path}")
    print(f"Cooldown: {ACCESS_COOLDOWN} seconds")
    print(f"Approval timeout: {APPROVAL_TIMEOUT} seconds")
    print(f"\nServer: {SERVER_URL}")
    print("\nWaiting for folder access events...")
    print("(Opens in Finder + file operations will trigger alerts)")
    print("(Press Ctrl+C to stop)\n")

    # Set up watchdog observer for file events
    event_handler = FolderAccessHandler(protected_path)
    observer = Observer()
    observer.schedule(event_handler, protected_path, recursive=True)
    observer.start()

    # Set up Finder window monitor for folder opens
    finder_monitor = FinderWindowMonitor(protected_path, event_handler)
    finder_monitor.start()
    print("Finder window polling active (checks every 0.5s)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        finder_monitor.stop()
        observer.stop()

    observer.join()
    print("Monitor stopped.")


if __name__ == '__main__':
    main()
