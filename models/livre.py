# models/livre.py
from database import db

class Livre:
    """Classe représentant un livre"""
    
    def __init__(self, idLivre=None, isbn='', titre='', auteur='', 
                 nombreExemplaires=1, nombreDisponibles=1, idCategorie=None):
        self.idLivre = idLivre
        self.isbn = isbn
        self.titre = titre
        self.auteur = auteur
        self.nombreExemplaires = nombreExemplaires
        self.nombreDisponibles = nombreDisponibles
        self.idCategorie = idCategorie
    
    @staticmethod
    def get_all():
        """Récupérer tous les livres avec leur catégorie"""
        query = """
            SELECT l.*, c.nomCategorie 
            FROM Livre l
            JOIN Categorie c ON l.idCategorie = c.idCategorie
            ORDER BY l.titre
        """
        return db.fetch_all(query)
    
    @staticmethod
    def get_by_id(idLivre):
        """Récupérer un livre par son ID"""
        query = """
            SELECT l.*, c.nomCategorie 
            FROM Livre l
            JOIN Categorie c ON l.idCategorie = c.idCategorie
            WHERE l.idLivre = %s
        """
        return db.fetch_one(query, (idLivre,))
    
    @staticmethod
    def get_by_isbn(isbn):
        """Récupérer un livre par son ISBN"""
        query = """
            SELECT l.*, c.nomCategorie 
            FROM Livre l
            JOIN Categorie c ON l.idCategorie = c.idCategorie
            WHERE l.isbn = %s
        """
        return db.fetch_one(query, (isbn,))
    
    @staticmethod
    def search(keyword):
        """Rechercher des livres par titre, auteur ou ISBN"""
        query = """
            SELECT l.*, c.nomCategorie 
            FROM Livre l
            JOIN Categorie c ON l.idCategorie = c.idCategorie
            WHERE l.titre LIKE %s OR l.auteur LIKE %s OR l.isbn LIKE %s
            ORDER BY l.titre
        """
        search_term = f"%{keyword}%"
        return db.fetch_all(query, (search_term, search_term, search_term))
    
    @staticmethod
    def get_disponibles():
        """Récupérer les livres disponibles"""
        query = """
            SELECT l.*, c.nomCategorie 
            FROM Livre l
            JOIN Categorie c ON l.idCategorie = c.idCategorie
            WHERE l.nombreDisponibles > 0
            ORDER BY l.titre
        """
        return db.fetch_all(query)
    
    def save(self):
        """Enregistrer un nouveau livre"""
        query = """
            INSERT INTO Livre (isbn, titre, auteur, nombreExemplaires, 
                             nombreDisponibles, idCategorie)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (self.isbn, self.titre, self.auteur, self.nombreExemplaires,
                  self.nombreDisponibles, self.idCategorie)
        
        if db.execute_query(query, params):
            self.idLivre = db.get_last_insert_id()
            return True
        return False
    
    def update(self):
        """Mettre à jour un livre existant"""
        query = """
            UPDATE Livre 
            SET isbn=%s, titre=%s, auteur=%s, nombreExemplaires=%s, 
                nombreDisponibles=%s, idCategorie=%s
            WHERE idLivre=%s
        """
        params = (self.isbn, self.titre, self.auteur, self.nombreExemplaires,
                  self.nombreDisponibles, self.idCategorie, self.idLivre)
        return db.execute_query(query, params)
    
    @staticmethod
    def delete(idLivre):
        """Supprimer un livre (si pas d'emprunts en cours)"""
        # Vérifier d'abord s'il n'y a pas d'emprunts en cours
        check_query = """
            SELECT COUNT(*) as count FROM Emprunt 
            WHERE idLivre = %s AND statut = 'EN_COURS'
        """
        result = db.fetch_one(check_query, (idLivre,))
        
        if result and result['count'] > 0:
            print("✗ Impossible de supprimer : le livre a des emprunts en cours")
            return False
        
        query = "DELETE FROM Livre WHERE idLivre = %s"
        return db.execute_query(query, (idLivre,))
    
    @staticmethod
    def decrementer_disponibilite(idLivre):
        """Décrémenter le nombre de livres disponibles (lors d'un emprunt)"""
        query = """
            UPDATE Livre 
            SET nombreDisponibles = nombreDisponibles - 1 
            WHERE idLivre = %s AND nombreDisponibles > 0
        """
        return db.execute_query(query, (idLivre,))
    
    @staticmethod
    def incrementer_disponibilite(idLivre):
        """Incrémenter le nombre de livres disponibles (lors d'un retour)"""
        query = """
            UPDATE Livre 
            SET nombreDisponibles = nombreDisponibles + 1 
            WHERE idLivre = %s
        """
        return db.execute_query(query, (idLivre,))
    
    def est_disponible(self):
        """Vérifier si le livre est disponible"""
        return self.nombreDisponibles > 0
    
    def __str__(self):
        return f"{self.titre} - {self.auteur}"
