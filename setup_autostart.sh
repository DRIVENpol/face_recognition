#!/bin/bash

# =============================================================================
# Script pentru configurarea pornirii automate a Sistemului de Securitate
#
# Acest script instalează/dezinstalează două servicii macOS LaunchAgent:
#   1. com.security.monitor - Monitorul care detectează accesul la folder
#   2. com.security.server  - Serverul web Django pentru dashboard
#
# Utilizare:
#   ./setup_autostart.sh install   - Activează pornirea automată
#   ./setup_autostart.sh uninstall - Dezactivează pornirea automată
#   ./setup_autostart.sh status    - Verifică statusul serviciilor
#
# Autor: Paul Socarde
# =============================================================================

# Nume fișiere plist
MONITOR_PLIST="com.security.monitor.plist"
SERVER_PLIST="com.security.server.plist"

# Căi sursă (unde se află scriptul)
SCRIPT_DIR="$(dirname "$0")"
MONITOR_SOURCE="$SCRIPT_DIR/$MONITOR_PLIST"
SERVER_SOURCE="$SCRIPT_DIR/$SERVER_PLIST"

# Căi destinație (LaunchAgents)
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
MONITOR_DEST="$LAUNCH_AGENTS_DIR/$MONITOR_PLIST"
SERVER_DEST="$LAUNCH_AGENTS_DIR/$SERVER_PLIST"

# Culori pentru output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funcție pentru afișarea mesajelor
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

case "$1" in
    install)
        echo ""
        echo "======================================================"
        echo "  Instalare Pornire Automată - Sistem de Securitate"
        echo "======================================================"
        echo ""

        # Verificăm că fișierele sursă există
        if [ ! -f "$MONITOR_SOURCE" ]; then
            print_error "Fișierul $MONITOR_PLIST nu a fost găsit!"
            exit 1
        fi
        if [ ! -f "$SERVER_SOURCE" ]; then
            print_error "Fișierul $SERVER_PLIST nu a fost găsit!"
            exit 1
        fi

        # Creăm directorul LaunchAgents dacă nu există
        if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
            mkdir -p "$LAUNCH_AGENTS_DIR"
            print_status "Director LaunchAgents creat"
        fi

        # Instalăm Monitor
        echo ""
        echo "Instalare Monitor..."
        cp "$MONITOR_SOURCE" "$MONITOR_DEST"
        launchctl load "$MONITOR_DEST" 2>/dev/null
        print_status "Monitor instalat și pornit"

        # Instalăm Server
        echo ""
        echo "Instalare Server..."
        cp "$SERVER_SOURCE" "$SERVER_DEST"
        launchctl load "$SERVER_DEST" 2>/dev/null
        print_status "Server instalat și pornit"

        echo ""
        echo "======================================================"
        print_status "Instalare completă!"
        echo "======================================================"
        echo ""
        echo "Ambele servicii vor porni automat la login."
        echo ""
        echo "Pentru a testa acum:"
        echo "  launchctl start com.security.monitor"
        echo "  launchctl start com.security.server"
        echo ""
        echo "Log-uri disponibile în:"
        echo "  /tmp/security_monitor.log"
        echo "  /tmp/security_server.log"
        echo ""
        ;;

    uninstall)
        echo ""
        echo "======================================================"
        echo "  Dezinstalare Pornire Automată"
        echo "======================================================"
        echo ""

        # Dezinstalăm Monitor
        echo "Dezinstalare Monitor..."
        launchctl unload "$MONITOR_DEST" 2>/dev/null
        rm -f "$MONITOR_DEST"
        print_status "Monitor dezinstalat"

        # Dezinstalăm Server
        echo ""
        echo "Dezinstalare Server..."
        launchctl unload "$SERVER_DEST" 2>/dev/null
        rm -f "$SERVER_DEST"
        print_status "Server dezinstalat"

        echo ""
        echo "======================================================"
        print_status "Dezinstalare completă!"
        echo "======================================================"
        echo ""
        echo "Serviciile nu vor mai porni automat la login."
        echo ""
        ;;

    status)
        echo ""
        echo "======================================================"
        echo "  Status Servicii"
        echo "======================================================"
        echo ""

        # Verificăm Monitor
        echo "Monitor (com.security.monitor):"
        if [ -f "$MONITOR_DEST" ]; then
            print_status "Instalat pentru pornire automată"
            if launchctl list | grep -q "com.security.monitor"; then
                print_status "Rulează în prezent"
            else
                print_warning "Nu rulează în prezent"
            fi
        else
            print_error "NU este instalat"
        fi

        echo ""

        # Verificăm Server
        echo "Server (com.security.server):"
        if [ -f "$SERVER_DEST" ]; then
            print_status "Instalat pentru pornire automată"
            if launchctl list | grep -q "com.security.server"; then
                print_status "Rulează în prezent"
            else
                print_warning "Nu rulează în prezent"
            fi
        else
            print_error "NU este instalat"
        fi

        echo ""
        echo "======================================================"
        echo ""
        ;;

    start)
        echo "Pornire manuală servicii..."
        launchctl start com.security.monitor 2>/dev/null && print_status "Monitor pornit" || print_error "Monitor - eroare la pornire"
        launchctl start com.security.server 2>/dev/null && print_status "Server pornit" || print_error "Server - eroare la pornire"
        echo ""
        echo "Dashboard disponibil la: http://localhost:5000"
        ;;

    stop)
        echo "Oprire servicii..."
        launchctl stop com.security.monitor 2>/dev/null && print_status "Monitor oprit" || print_warning "Monitor nu rula"
        launchctl stop com.security.server 2>/dev/null && print_status "Server oprit" || print_warning "Server nu rula"
        ;;

    restart)
        echo "Repornire servicii..."
        launchctl stop com.security.monitor 2>/dev/null
        launchctl stop com.security.server 2>/dev/null
        sleep 1
        launchctl start com.security.monitor 2>/dev/null && print_status "Monitor repornit"
        launchctl start com.security.server 2>/dev/null && print_status "Server repornit"
        ;;

    logs)
        echo "======================================================"
        echo "  Log-uri în timp real (Ctrl+C pentru a opri)"
        echo "======================================================"
        echo ""
        tail -f /tmp/security_monitor.log /tmp/security_server.log
        ;;

    *)
        echo ""
        echo "======================================================"
        echo "  Setup Autostart - Sistem de Securitate"
        echo "======================================================"
        echo ""
        echo "Utilizare: $0 {comandă}"
        echo ""
        echo "Comenzi disponibile:"
        echo ""
        echo "  install   - Instalează și activează pornirea automată la login"
        echo "  uninstall - Dezinstalează și dezactivează pornirea automată"
        echo "  status    - Afișează statusul serviciilor"
        echo ""
        echo "  start     - Pornește manual ambele servicii"
        echo "  stop      - Oprește ambele servicii"
        echo "  restart   - Repornește ambele servicii"
        echo ""
        echo "  logs      - Afișează log-urile în timp real"
        echo ""
        exit 1
        ;;
esac
