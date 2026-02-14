# config.py
# Configuration de l'application

# Configuration de la base de données
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mugiwara7!#',
    'database': 'biblio_simple',
    'port': 3306
}

# Règles métier
QUOTA_ETUDIANT = 3
QUOTA_ENSEIGNANT = 5

DUREE_EMPRUNT_ETUDIANT = 15  # jours
DUREE_EMPRUNT_ENSEIGNANT = 30  # jours

PENALITE_PAR_JOUR = 50  # FCFA

# Configuration de l'interface
APP_TITLE = "Système de Gestion de Bibliothèque"
APP_WIDTH = 1000
APP_HEIGHT = 700
