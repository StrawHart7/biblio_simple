# api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db
from models import Adherent, Livre, Emprunt
from services.emprunt_service import EmpruntService
from datetime import datetime

app = Flask(__name__)

# Configuration CORS pour React
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Connexion à la BDD au démarrage
def initialize():
    if not db.connect():
        print("❌ Erreur de connexion à la base de données")

# Gestion des erreurs
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Ressource non trouvée'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erreur serveur'}), 500

# Route racine
@app.route("/")
def home():
    return {"status": "API Bibliothèque active"}

# ============================================================
# ROUTES AUTHENTIFICATION
# ============================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Connexion bibliothécaire"""
    data = request.json
    login_user = data.get('login')
    password = data.get('motDePasse')
    
    if not login_user or not password:
        return jsonify({'error': 'Login et mot de passe requis'}), 400
    
    query = "SELECT * FROM Bibliothecaire WHERE login = %s AND motDePasse = %s"
    bibliothecaire = db.fetch_one(query, (login_user, password))
    
    if bibliothecaire:
        return jsonify({
            'success': True,
            'bibliothecaire': {
                'id': bibliothecaire['idBibliothecaire'],
                'nom': bibliothecaire['nom'],
                'prenom': bibliothecaire['prenom'],
                'login': bibliothecaire['login']
            }
        }), 200
    
    return jsonify({'error': 'Identifiants incorrects'}), 401

# ============================================================
# ROUTES ADHÉRENTS
# ============================================================

@app.route('/api/adherents', methods=['GET'])
def get_adherents():
    """Récupérer tous les adhérents"""
    adherents = Adherent.get_all()
    
    # Ajouter le quota pour chaque adhérent
    for adh in adherents:
        emprunts_en_cours = Adherent.get_emprunts_en_cours(adh['idAdherent'])
        quota_max = 5 if adh['typeAdherent'] == 'ENSEIGNANT' else 3
        adh['empruntsEnCours'] = emprunts_en_cours
        adh['quotaMax'] = quota_max
        adh['quotaDisponible'] = quota_max - emprunts_en_cours
    
    return jsonify(adherents), 200

@app.route('/api/adherents/search', methods=['GET'])
def search_adherents():
    """Rechercher des adhérents"""
    keyword = request.args.get('q', '')
    
    if not keyword:
        return jsonify([]), 200
    
    results = Adherent.search(keyword)
    
    # Ajouter le quota
    for adh in results:
        emprunts_en_cours = Adherent.get_emprunts_en_cours(adh['idAdherent'])
        quota_max = 5 if adh['typeAdherent'] == 'ENSEIGNANT' else 3
        adh['empruntsEnCours'] = emprunts_en_cours
        adh['quotaMax'] = quota_max
        adh['quotaDisponible'] = quota_max - emprunts_en_cours
    
    return jsonify(results), 200

@app.route('/api/adherents/<int:id>', methods=['GET'])
def get_adherent(id):
    """Récupérer un adhérent par ID"""
    adherent = Adherent.get_by_id(id)
    
    if not adherent:
        return jsonify({'error': 'Adhérent non trouvé'}), 404
    
    # Ajouter infos supplémentaires
    emprunts_en_cours = Adherent.get_emprunts_en_cours(id)
    quota_max = 5 if adherent['typeAdherent'] == 'ENSEIGNANT' else 3
    adherent['empruntsEnCours'] = emprunts_en_cours
    adherent['quotaMax'] = quota_max
    adherent['quotaDisponible'] = quota_max - emprunts_en_cours
    
    return jsonify(adherent), 200

@app.route('/api/adherents', methods=['POST'])
def create_adherent():
    """Créer un nouvel adhérent"""
    data = request.json
    
    # Validation
    required = ['nom', 'prenom', 'email']
    if not all(field in data for field in required):
        return jsonify({'error': 'Champs requis manquants'}), 400
    
    adherent = Adherent(
        nom=data['nom'],
        prenom=data['prenom'],
        email=data['email'],
        telephone=data.get('telephone', ''),
        typeAdherent=data.get('typeAdherent', 'ETUDIANT'),
        statut=data.get('statut', 'ACTIF')
    )
    
    if adherent.save():
        return jsonify({
            'success': True,
            'id': adherent.idAdherent,
            'message': 'Adhérent créé avec succès'
        }), 201
    
    return jsonify({'error': 'Erreur lors de la création'}), 400

@app.route('/api/adherents/<int:id>', methods=['PUT'])
def update_adherent(id):
    """Modifier un adhérent"""
    data = request.json
    adherent_data = Adherent.get_by_id(id)
    
    if not adherent_data:
        return jsonify({'error': 'Adhérent non trouvé'}), 404
    
    adherent = Adherent(**adherent_data)
    adherent.nom = data.get('nom', adherent.nom)
    adherent.prenom = data.get('prenom', adherent.prenom)
    adherent.email = data.get('email', adherent.email)
    adherent.telephone = data.get('telephone', adherent.telephone)
    adherent.typeAdherent = data.get('typeAdherent', adherent.typeAdherent)
    adherent.statut = data.get('statut', adherent.statut)
    
    if adherent.update():
        return jsonify({
            'success': True,
            'message': 'Adhérent modifié avec succès'
        }), 200
    
    return jsonify({'error': 'Erreur lors de la modification'}), 400

@app.route('/api/adherents/<int:id>', methods=['DELETE'])
def delete_adherent(id):
    """Supprimer un adhérent"""
    if Adherent.delete(id):
        return jsonify({
            'success': True,
            'message': 'Adhérent supprimé avec succès'
        }), 200
    
    return jsonify({'error': 'Impossible de supprimer (emprunts en cours)'}), 400

# ============================================================
# ROUTES LIVRES
# ============================================================

@app.route('/api/livres', methods=['GET'])
def get_livres():
    """Récupérer tous les livres"""
    livres = Livre.get_all()
    return jsonify(livres), 200

@app.route('/api/livres/disponibles', methods=['GET'])
def get_livres_disponibles():
    """Récupérer les livres disponibles"""
    livres = Livre.get_disponibles()
    return jsonify(livres), 200

@app.route('/api/livres/search', methods=['GET'])
def search_livres():
    """Rechercher des livres"""
    keyword = request.args.get('q', '')
    
    if not keyword:
        return jsonify([]), 200
    
    results = Livre.search(keyword)
    return jsonify(results), 200

@app.route('/api/livres/<int:id>', methods=['GET'])
def get_livre(id):
    """Récupérer un livre par ID"""
    livre = Livre.get_by_id(id)
    
    if not livre:
        return jsonify({'error': 'Livre non trouvé'}), 404
    
    return jsonify(livre), 200

@app.route('/api/livres/isbn/<isbn>', methods=['GET'])
def get_livre_by_isbn(isbn):
    """Récupérer un livre par ISBN"""
    livre = Livre.get_by_isbn(isbn)
    
    if not livre:
        return jsonify({'error': 'Livre non trouvé'}), 404
    
    return jsonify(livre), 200

@app.route('/api/livres', methods=['POST'])
def create_livre():
    """Créer un nouveau livre"""
    data = request.json
    
    # Validation
    required = ['titre', 'auteur', 'idCategorie']
    if not all(field in data for field in required):
        return jsonify({'error': 'Champs requis manquants'}), 400
    
    livre = Livre(
        isbn=data.get('isbn', ''),
        titre=data['titre'],
        auteur=data['auteur'],
        nombreExemplaires=data.get('nombreExemplaires', 1),
        nombreDisponibles=data.get('nombreDisponibles', 1),
        idCategorie=data['idCategorie']
    )
    
    if livre.save():
        return jsonify({
            'success': True,
            'id': livre.idLivre,
            'message': 'Livre créé avec succès'
        }), 201
    
    return jsonify({'error': 'Erreur lors de la création'}), 400

@app.route('/api/livres/<int:id>', methods=['PUT'])
def update_livre(id):
    """Modifier un livre"""
    data = request.json
    livre_data = Livre.get_by_id(id)
    
    if not livre_data:
        return jsonify({'error': 'Livre non trouvé'}), 404
    
    livre = Livre(**livre_data)
    livre.isbn = data.get('isbn', livre.isbn)
    livre.titre = data.get('titre', livre.titre)
    livre.auteur = data.get('auteur', livre.auteur)
    livre.nombreExemplaires = data.get('nombreExemplaires', livre.nombreExemplaires)
    livre.nombreDisponibles = data.get('nombreDisponibles', livre.nombreDisponibles)
    livre.idCategorie = data.get('idCategorie', livre.idCategorie)
    
    if livre.update():
        return jsonify({
            'success': True,
            'message': 'Livre modifié avec succès'
        }), 200
    
    return jsonify({'error': 'Erreur lors de la modification'}), 400

@app.route('/api/livres/<int:id>', methods=['DELETE'])
def delete_livre(id):
    """Supprimer un livre"""
    if Livre.delete(id):
        return jsonify({
            'success': True,
            'message': 'Livre supprimé avec succès'
        }), 200
    
    return jsonify({'error': 'Impossible de supprimer (emprunts en cours)'}), 400

# ============================================================
# ROUTES EMPRUNTS
# ============================================================

@app.route('/api/emprunts', methods=['GET'])
def get_emprunts():
    """Récupérer tous les emprunts"""
    emprunts = Emprunt.get_all()
    return jsonify(emprunts), 200

@app.route('/api/emprunts/en-cours', methods=['GET'])
def get_emprunts_en_cours():
    """Récupérer les emprunts en cours"""
    emprunts = Emprunt.get_en_cours()
    return jsonify(emprunts), 200

@app.route('/api/emprunts/retards', methods=['GET'])
def get_emprunts_retards():
    """Récupérer les emprunts en retard"""
    retards = Emprunt.get_en_retard()
    return jsonify(retards), 200

@app.route('/api/emprunts/adherent/<int:id>', methods=['GET'])
def get_emprunts_adherent(id):
    """Récupérer les emprunts d'un adhérent"""
    emprunts = Emprunt.get_by_adherent(id)
    return jsonify(emprunts), 200

@app.route('/api/emprunts', methods=['POST'])
def create_emprunt():
    """Créer un emprunt"""
    data = request.json
    
    # Validation
    required = ['idLivre', 'idAdherent', 'idBibliothecaire']
    if not all(field in data for field in required):
        return jsonify({'error': 'Champs requis manquants'}), 400
    
    success, message, emprunt_id = EmpruntService.emprunter_livre(
        data['idLivre'],
        data['idAdherent'],
        data['idBibliothecaire']
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'id': emprunt_id
        }), 201
    
    return jsonify({'error': message}), 400

@app.route('/api/emprunts/retour', methods=['POST'])
def retourner_livre():
    """Retourner un livre"""
    data = request.json
    
    if 'isbn' not in data:
        return jsonify({'error': 'ISBN requis'}), 400
    
    success, message, penalite = EmpruntService.retourner_livre(data['isbn'])
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'penalite': float(penalite) if penalite else 0
        }), 200
    
    return jsonify({'error': message}), 400

# ============================================================
# ROUTES CATÉGORIES
# ============================================================

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Récupérer toutes les catégories"""
    query = "SELECT * FROM Categorie ORDER BY nomCategorie"
    categories = db.fetch_all(query)
    return jsonify(categories), 200

# ============================================================
# ROUTES PÉNALITÉS
# ============================================================

@app.route('/api/penalites', methods=['GET'])
def get_penalites():
    """Récupérer toutes les pénalités"""
    query = """
        SELECT 
            p.*,
            CONCAT(a.nom, ' ', a.prenom) as adherent,
            l.titre as livre
        FROM Penalite p
        JOIN Emprunt e ON p.idEmprunt = e.idEmprunt
        JOIN Adherent a ON e.idAdherent = a.idAdherent
        JOIN Livre l ON e.idLivre = l.idLivre
        ORDER BY p.dateCreation DESC
    """
    penalites = db.fetch_all(query)
    return jsonify(penalites), 200

@app.route('/api/penalites/impayees', methods=['GET'])
def get_penalites_impayees():
    """Récupérer les pénalités impayées"""
    query = """
        SELECT 
            p.*,
            CONCAT(a.nom, ' ', a.prenom) as adherent,
            l.titre as livre
        FROM Penalite p
        JOIN Emprunt e ON p.idEmprunt = e.idEmprunt
        JOIN Adherent a ON e.idAdherent = a.idAdherent
        JOIN Livre l ON e.idLivre = l.idLivre
        WHERE p.statut = 'IMPAYEE'
        ORDER BY p.dateCreation DESC
    """
    penalites = db.fetch_all(query)
    return jsonify(penalites), 200

@app.route('/api/penalites/<int:id>/payer', methods=['PUT'])
def payer_penalite(id):
    """Marquer une pénalité comme payée"""
    query = "UPDATE Penalite SET statut = 'PAYEE' WHERE idPenalite = %s"
    
    if db.execute_query(query, (id,)):
        return jsonify({
            'success': True,
            'message': 'Pénalité marquée comme payée'
        }), 200
    
    return jsonify({'error': 'Erreur lors du paiement'}), 400

# ============================================================
# ROUTES STATISTIQUES
# ============================================================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Récupérer les statistiques globales"""
    stats = Emprunt.get_statistiques()
    
    # Stats supplémentaires
    retards = db.fetch_one("SELECT COUNT(*) as count FROM Emprunt WHERE statut = 'EN_COURS' AND dateRetourPrevue < NOW()")
    livres_dispo = db.fetch_one("SELECT SUM(nombreDisponibles) as count FROM Livre")
    adherents_actifs = db.fetch_one("SELECT COUNT(*) as count FROM Adherent WHERE statut = 'ACTIF'")
    penalites_impayees = db.fetch_one("SELECT COALESCE(SUM(montant), 0) as total FROM Penalite WHERE statut = 'IMPAYEE'")
    
    return jsonify({
        'empruntsTotal': stats['total'],
        'empruntsEnCours': stats['en_cours'],
        'empruntsEnRetard': retards['count'],
        'empruntsRetournes': stats['retournes'],
        'livresDisponibles': livres_dispo['count'],
        'adherentsActifs': adherents_actifs['count'],
        'penalitesImpayees': float(penalites_impayees['total'])
    }), 200

# ============================================================
# ROUTE DE TEST
# ============================================================

@app.route("/api/health")
def health_check():
    return jsonify({
        "status": "OK",
        "message": "API Bibliothèque fonctionnelle",
        "timestamp": datetime.now().isoformat()
    })

# ============================================================
# LANCEMENT DU SERVEUR
# ============================================================

if __name__ == "__main__":
    print("🚀 Démarrage de l'API Bibliothèque...")
    print("📡 Serveur : http://localhost:5000")
    print("📚 Documentation : http://localhost:5000/api/health")
    initialize()
    app.run(debug=True, host="0.0.0.0", port=5000)