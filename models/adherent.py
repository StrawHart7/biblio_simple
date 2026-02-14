# models/adherent.py
from database import db

class Adherent:
    """Classe représentant un adhérent"""
    
    def __init__(self, idAdherent=None, nom='', prenom='', email='', 
                 telephone='', typeAdherent='ETUDIANT', statut='ACTIF'):
        self.idAdherent = idAdherent
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.telephone = telephone
        self.typeAdherent = typeAdherent
        self.statut = statut
    
    @staticmethod
    def get_all():
        """Récupérer tous les adhérents"""
        query = "SELECT * FROM Adherent ORDER BY nom, prenom"
        return db.fetch_all(query)
    
    @staticmethod
    def get_by_id(idAdherent):
        """Récupérer un adhérent par son ID"""
        query = "SELECT * FROM Adherent WHERE idAdherent = %s"
        return db.fetch_one(query, (idAdherent,))
    
    @staticmethod
    def search(keyword):
        """Rechercher des adhérents par nom, prénom ou email"""
        query = """
            SELECT * FROM Adherent 
            WHERE nom LIKE %s OR prenom LIKE %s OR email LIKE %s
            ORDER BY nom, prenom
        """
        search_term = f"%{keyword}%"
        return db.fetch_all(query, (search_term, search_term, search_term))
    
    def save(self):
        """Enregistrer un nouvel adhérent"""
        query = """
            INSERT INTO Adherent (nom, prenom, email, telephone, typeAdherent, statut)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (self.nom, self.prenom, self.email, self.telephone, 
                  self.typeAdherent, self.statut)
        
        if db.execute_query(query, params):
            self.idAdherent = db.get_last_insert_id()
            return True
        return False
    
    def update(self):
        """Mettre à jour un adhérent existant"""
        query = """
            UPDATE Adherent 
            SET nom=%s, prenom=%s, email=%s, telephone=%s, 
                typeAdherent=%s, statut=%s
            WHERE idAdherent=%s
        """
        params = (self.nom, self.prenom, self.email, self.telephone,
                  self.typeAdherent, self.statut, self.idAdherent)
        return db.execute_query(query, params)
    
    @staticmethod
    def delete(idAdherent):
        """Supprimer un adhérent (si pas d'emprunts en cours)"""
        # Vérifier d'abord s'il n'a pas d'emprunts en cours
        check_query = """
            SELECT COUNT(*) as count FROM Emprunt 
            WHERE idAdherent = %s AND statut = 'EN_COURS'
        """
        result = db.fetch_one(check_query, (idAdherent,))
        
        if result and result['count'] > 0:
            print("✗ Impossible de supprimer : l'adhérent a des emprunts en cours")
            return False
        
        query = "DELETE FROM Adherent WHERE idAdherent = %s"
        return db.execute_query(query, (idAdherent,))
    
    @staticmethod
    def get_emprunts_en_cours(idAdherent):
        """Compter le nombre d'emprunts en cours d'un adhérent"""
        query = """
            SELECT COUNT(*) as count 
            FROM Emprunt 
            WHERE idAdherent = %s AND statut = 'EN_COURS'
        """
        result = db.fetch_one(query, (idAdherent,))
        return result['count'] if result else 0
    
    def get_quota_disponible(self):
        """Calculer le quota disponible"""
        quota_max = 5 if self.typeAdherent == 'ENSEIGNANT' else 3
        emprunts_en_cours = self.get_emprunts_en_cours(self.idAdherent)
        return quota_max - emprunts_en_cours
    
    def peut_emprunter(self):
        """Vérifier si l'adhérent peut emprunter"""
        return self.statut == 'ACTIF' and self.get_quota_disponible() > 0
    
    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.typeAdherent})"
