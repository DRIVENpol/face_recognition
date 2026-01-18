"""
Configurări Django pentru proiectul admin_dashboard

Acest fișier conține toate setările pentru framework-ul Django care
alimentează dashboard-ul de administrare web.

Documentație Django:
    https://docs.djangoproject.com/en/4.2/topics/settings/
    https://docs.djangoproject.com/en/4.2/ref/settings/

Autor: Bascacov Alexandra
Versiune: 1.0
"""

from pathlib import Path

# ============================================================================
# CĂILE DE BAZĂ
# ============================================================================
# Construiește căile în proiect astfel: BASE_DIR / 'subdirector'
# BASE_DIR este directorul rădăcină al proiectului
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================================
# SETĂRI DE SECURITATE
# ============================================================================
# ATENȚIE: Păstrează cheia secretă... secretă în producție!
# Această cheie este folosită pentru criptare și semnături
SECRET_KEY = 'django-insecure-p7i4_-^p0k!5r@71xi-y6-(p8vk)a(p4yceicbd6$&^sl=y8#2'

# ATENȚIE: Nu rula cu debug=True în producție!
# Modul debug afișează informații sensibile în caz de eroare
DEBUG = True

# Lista gazdelor permise să acceseze aplicația
# '*' permite orice gazdă - necesar pentru acces mobil/ngrok
ALLOWED_HOSTS = ['*']


# ============================================================================
# APLICAȚII INSTALATE
# ============================================================================
# Lista aplicațiilor Django care sunt activate în acest proiect
INSTALLED_APPS = [
    'django.contrib.admin',        # Interfața de administrare Django
    'django.contrib.auth',         # Sistem de autentificare
    'django.contrib.contenttypes', # Framework pentru tipuri de conținut
    'django.contrib.sessions',     # Gestionarea sesiunilor
    'django.contrib.messages',     # Framework pentru mesaje
    'django.contrib.staticfiles',  # Servirea fișierelor statice
    'access_control',              # Aplicația noastră de control acces
]

# ============================================================================
# SETĂRI CONTROL ACCES
# ============================================================================
# Timpul (în secunde) înainte de respingere automată
APPROVAL_TIMEOUT = 30

# ============================================================================
# MIDDLEWARE
# ============================================================================
# Middleware-ul procesează cererile și răspunsurile
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================================
# CONFIGURARE URL
# ============================================================================
# Modulul principal de configurare a URL-urilor
ROOT_URLCONF = 'admin_dashboard.urls'

# ============================================================================
# CONFIGURARE TEMPLATE-URI
# ============================================================================
# Setări pentru sistemul de template-uri Django (HTML)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],           # Directoare suplimentare pentru template-uri
        'APP_DIRS': True,     # Caută template-uri în folderele aplicațiilor
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Aplicația WSGI pentru servere de producție
WSGI_APPLICATION = 'admin_dashboard.wsgi.application'


# ============================================================================
# CONFIGURARE BAZĂ DE DATE
# ============================================================================
# Folosim SQLite pentru simplitate - baza de date este un fișier local
# Documentație: https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Motor SQLite
        'NAME': BASE_DIR / 'db.sqlite3',         # Calea către fișierul DB
    }
}


# ============================================================================
# VALIDARE PAROLE
# ============================================================================
# Validatori pentru parolele utilizatorilor (pentru admin Django)
# Documentație: https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ============================================================================
# INTERNAȚIONALIZARE
# ============================================================================
# Setări pentru limbi și zone orare
# Documentație: https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'  # Codul limbii (engleză SUA)

TIME_ZONE = 'UTC'        # Zona orară (Timp Universal Coordonat)

USE_I18N = True          # Activează sistemul de internaționalizare

USE_TZ = True            # Folosește zone orare în date


# ============================================================================
# FIȘIERE STATICE (CSS, JavaScript, Imagini)
# ============================================================================
# URL-ul de bază pentru fișierele statice
# Documentație: https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'

# ============================================================================
# CONFIGURARE MODEL
# ============================================================================
# Tipul implicit pentru câmpul cheie primară
# BigAutoField = număr întreg mare cu auto-incrementare
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
