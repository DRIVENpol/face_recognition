"""
Modele de date pentru aplicația de Control Acces

Acest fișier definește structura bazei de date folosind ORM-ul Django.
Fiecare clasă reprezintă un tabel în baza de date SQLite.

Autor: Paul Socarde
Versiune: 1.0
"""

from django.db import models


class AccessAttempt(models.Model):
    """
    Model pentru stocarea încercărilor de acces la folderul protejat.

    Fiecare înregistrare reprezintă o încercare de a accesa folderul protejat
    și conține informații despre momentul accesului, tipul accesului, fotografia
    capturată și decizia administratorului.

    Acest model este folosit pentru:
    - Înregistrarea încercărilor de acces în timp real
    - Afișarea listei de încercări în dashboard
    - Urmărirea deciziilor (aprobat/respins)
    - Păstrarea istoricului accesărilor

    Atribute:
        timestamp (DateTimeField): Data și ora când s-a detectat accesul
        access_path (CharField): Calea completă către folderul/fișierul accesat
        access_type (CharField): Tipul accesului ('folder_opened', 'file_created', etc.)
        photo_path (CharField): Calea către fotografia capturată (poate fi null)
        status (CharField): Starea curentă ('pending', 'approved', 'denied')
        decided_at (DateTimeField): Momentul când s-a luat decizia (poate fi null)
    """

    # Opțiunile posibile pentru statusul unei încercări de acces
    STATUS_CHOICES = [
        ('pending', 'În așteptare'),   # Încă nu s-a luat o decizie
        ('approved', 'Aprobat'),        # Administratorul a aprobat accesul
        ('denied', 'Respins'),          # Administratorul a respins accesul
    ]

    # Câmpurile bazei de date (coloanele tabelului)

    # Data și ora când s-a detectat încercarea de acces
    # auto_now_add=True înseamnă că se completează automat la creare
    timestamp = models.DateTimeField(auto_now_add=True)

    # Calea către folderul sau fișierul accesat
    # max_length=500 pentru a permite căi lungi
    access_path = models.CharField(max_length=500)

    # Tipul accesului (ex: 'folder_opened', 'file_created', 'file_modified')
    access_type = models.CharField(max_length=50, default='folder')

    # Numele fișierului foto capturat (dacă există)
    # null=True și blank=True permit valori goale
    photo_path = models.CharField(max_length=255, null=True, blank=True)

    # Starea curentă a încercării de acces
    # choices=STATUS_CHOICES limitează valorile posibile
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Momentul când administratorul a luat decizia
    # Rămâne null până când se aprobă sau se respinge
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """
        Metadate pentru model.

        ordering: Sortează înregistrările după timestamp descrescător
                  (cele mai recente primele)
        """
        ordering = ['-timestamp']

    def __str__(self):
        """
        Reprezentarea text a unei încercări de acces.

        Afișează tipul, statusul și timestamp-ul în format citibil.
        Folosit în interfața de administrare Django.
        """
        return f"{self.access_type} - {self.status} - {self.timestamp}"
