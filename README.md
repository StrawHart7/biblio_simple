# 📚 SYSTÈME DE GESTION DE BIBLIOTHÈQUE - DOCUMENTATION ÉQUIPE

## 👥 RÉPARTITION DU PROJET

- **Backend** : Python + MySQL + Flask API
- **Frontend** : React + Axios

---

## 📦 STRUCTURE DU BACKEND

```
backend/
├── 📁 database/
│   ├── __init__.py
│   └── connection.py          # Connexion MySQL
│
├── 📁 models/
│   ├── __init__.py
│   ├── adherent.py            # Modèle Adhérent (CRUD)
│   ├── livre.py               # Modèle Livre (CRUD)
│   └── emprunt.py             # Modèle Emprunt (CRUD)
│
├── 📁 services/
│   ├── __init__.py
│   └── emprunt_service.py     # Logique métier (emprunter, retourner)
│
├── api.py                      # 🌟 API REST Flask (point d'entrée)
├── config.py                   # Configuration (BDD, règles métier)
├── requirements.txt            # Dépendances Python
└── biblio_simple.sql           # Script de création BDD
```

---

## 🚀 INSTALLATION BACKEND

### 1. Prérequis
- Python 3.8+
- MySQL 8.0+

### 2. Installation

```bash
# Cloner le projet
git clone <url-repo>
cd backend

# Créer environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration MySQL

```bash
# Se connecter à MySQL
mysql -u root -p

# Exécuter le script
source biblio_simple.sql
```

### 4. Configuration de l'application

Éditer `config.py` :
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'VOTRE_MOT_DE_PASSE',  # ⚠️ MODIFIER
    'database': 'biblio_simple',
    'port': 3306
}
```

### 5. Lancer l'API

```bash
python api.py
```

**Résultat attendu :**
```
🚀 Démarrage de l'API Bibliothèque...
📡 Serveur : http://localhost:5000
 * Running on http://0.0.0.0:5000
```

### 6. Tester l'API

Ouvrir : http://localhost:5000/api/health

---

## 🔌 API ENDPOINTS

### Base URL : `http://localhost:5000/api`

### **Authentification**
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/login` | Connexion bibliothécaire |

### **Adhérents**
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/adherents` | Liste complète |
| GET | `/adherents/search?q=keyword` | Recherche |
| GET | `/adherents/:id` | Détails |
| POST | `/adherents` | Créer |
| PUT | `/adherents/:id` | Modifier |
| DELETE | `/adherents/:id` | Supprimer |

### **Livres**
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/livres` | Liste complète |
| GET | `/livres/disponibles` | Livres disponibles |
| GET | `/livres/search?q=keyword` | Recherche |
| GET | `/livres/:id` | Détails |
| GET | `/livres/isbn/:isbn` | Par ISBN |
| POST | `/livres` | Créer |
| PUT | `/livres/:id` | Modifier |
| DELETE | `/livres/:id` | Supprimer |

### **Emprunts**
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/emprunts` | Tous les emprunts |
| GET | `/emprunts/en-cours` | En cours |
| GET | `/emprunts/retards` | En retard |
| GET | `/emprunts/adherent/:id` | Par adhérent |
| POST | `/emprunts` | Créer emprunt |
| POST | `/emprunts/retour` | Retourner livre |

### **Catégories**
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/categories` | Liste complète |

### **Pénalités**
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/penalites` | Toutes |
| GET | `/penalites/impayees` | Impayées |
| PUT | `/penalites/:id/payer` | Marquer payée |

### **Statistiques**
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/stats` | Stats globales |

---

## 📱 EXEMPLES DE REQUÊTES

### Authentification
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "motDePasse": "admin123"}'
```

### Rechercher des livres
```bash
curl http://localhost:5000/api/livres/search?q=Python
```

### Créer un emprunt
```bash
curl -X POST http://localhost:5000/api/emprunts \
  -H "Content-Type: application/json" \
  -d '{
    "idLivre": 1,
    "idAdherent": 1,
    "idBibliothecaire": 1
  }'
```

### Retourner un livre
```bash
curl -X POST http://localhost:5000/api/emprunts/retour \
  -H "Content-Type: application/json" \
  -d '{"isbn": "978-1234567890"}'
```

---

## 🎨 INTÉGRATION REACT

Voir le fichier `GUIDE_REACT_AXIOS.md` pour :
- Configuration Axios
- Création des services
- Exemples de composants

---

## 🗄️ BASE DE DONNÉES

### Tables (7)
1. **Bibliothecaire** - Comptes bibliothécaires
2. **Adherent** - Étudiants/Enseignants
3. **Categorie** - Catégories de livres
4. **Livre** - Catalogue
5. **Emprunt** - Transactions d'emprunt
6. **Reservation** - Réservations
7. **Penalite** - Amendes

### Règles Métier
- Étudiants : **3 livres max**, **15 jours**
- Enseignants : **5 livres max**, **30 jours**
- Pénalité : **0,50€ par jour de retard**

---

## ⚙️ CONFIGURATION

### Variables dans `config.py`

```python
# Base de données
DB_CONFIG = {...}

# Quotas
QUOTA_ETUDIANT = 3
QUOTA_ENSEIGNANT = 5

# Durées
DUREE_EMPRUNT_ETUDIANT = 15  # jours
DUREE_EMPRUNT_ENSEIGNANT = 30  # jours

# Pénalités
PENALITE_PAR_JOUR = 0.50  # euros
```

---

## 🧪 TESTS

### Test manuel de l'API

1. **Health check** : `GET /api/health`
2. **Statistiques** : `GET /api/stats`
3. **Recherche** : `GET /api/livres/search?q=Python`

### Données de test

- **Bibliothécaires** :
  - Login: `admin` / Mot de passe: `admin123`
  - Login: `sophie` / Mot de passe: `pass123`

- **Adhérents** : 4 adhérents (voir BDD)
- **Livres** : 5 livres dans le catalogue
- **Emprunts** : 2 emprunts en cours

---

## 🐛 DÉPANNAGE

### Erreur : "Connection refused"
→ MySQL n'est pas lancé

### Erreur : "Access denied"
→ Mot de passe incorrect dans `config.py`

### Erreur : "Unknown database"
→ Exécuter `biblio_simple.sql`

### Erreur CORS dans React
→ Vérifier que Flask-CORS est installé et configuré

---

## 📞 CONTACT

**Backend** : [Ton nom]
**Frontend** : [Nom collègue]

---

## 📝 TODO

- [ ] Backend API fonctionnelle ✅
- [ ] Documentation API ✅
- [ ] Tests unitaires ⏳
- [ ] Frontend React ⏳
- [ ] Intégration Backend/Frontend ⏳
- [ ] Tests d'intégration ⏳
- [ ] Déploiement ⏳

---

**Date de création** : Février 2026
**Version** : 1.0
