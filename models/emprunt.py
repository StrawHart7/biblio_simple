# models/emprunt.py
from datetime import datetime, timedelta
from database import db
from config import DUREE_EMPRUNT_ETUDIANT, DUREE_EMPRUNT_ENSEIGNANT

class Emprunt:
    """Classe représentant un emprunt"""
    
    def __init__(self, idEmprunt=None, dateEmprunt=None, dateRetourPrevue=None,
                 dateRetourEffective=None, statut='EN_COURS', 
                 idLivre=None, idAdherent=None, idBibliothecaire=None):
        self.idEmprunt = idEmprunt
        self.dateEmprunt = dateEmprunt or datetime.now()
        self.dateRetourPrevue = dateRetourPrevue
        self.dateRetourEffective = dateRetourEffective
        self.statut = statut
        self.idLivre = idLivre
        self.idAdherent = idAdherent
        self.idBibliothecaire = idBibliothecaire
    
    @staticmethod
    def get_all():
        """Récupérer tous les emprunts avec détails"""
        query = """
            SELECT 
                e.*,
                CONCAT(a.nom, ' ', a.prenom) as adherent,
                a.typeAdherent,
                l.titre,
                l.auteur,
                CONCAT(b.nom, ' ', b.prenom) as bibliothecaire
            FROM Emprunt e
            JOIN Adherent a ON e.idAdherent = a.idAdherent
            JOIN Livre l ON e.idLivre = l.idLivre
            JOIN Bibliothecaire b ON e.idBibliothecaire = b.idBibliothecaire
            ORDER BY e.dateEmprunt DESC
        """
        return db.fetch_all(query)
    
    @staticmethod
    def get_en_cours():
        """Récupérer les emprunts en cours"""
        query = """
            SELECT 
                e.*,
                CONCAT(a.nom, ' ', a.prenom) as adherent,
                a.email,
                l.titre,
                l.auteur,
                l.isbn
            FROM Emprunt e
            JOIN Adherent a ON e.idAdherent = a.idAdherent
            JOIN Livre l ON e.idLivre = l.idLivre
            WHERE e.statut IN ('EN_COURS', 'EN_RETARD')
            ORDER BY e.dateRetourPrevue
        """
        return db.fetch_all(query)
    
    @staticmethod
    def get_en_retard():
        """Récupérer les emprunts en retard"""
        query = """
            SELECT 
                e.*,
                CONCAT(a.nom, ' ', a.prenom) as adherent,
                a.email,
                a.telephone,
                l.titre,
                l.auteur,
                DATEDIFF(NOW(), e.dateRetourPrevue) as joursRetard
            FROM Emprunt e
            JOIN Adherent a ON e.idAdherent = a.idAdherent
            JOIN Livre l ON e.idLivre = l.idLivre
            WHERE e.statut = 'EN_COURS' AND e.dateRetourPrevue < NOW()
            ORDER BY joursRetard DESC
        """
        return db.fetch_all(query)
    
    @staticmethod
    def get_by_livre_isbn(isbn):
        """Trouver l'emprunt en cours pour un livre (par ISBN)"""
        query = """
            SELECT 
                e.*,
                CONCAT(a.nom, ' ', a.prenom) as adherent,
                a.email,
                l.titre,
                l.auteur
            FROM Emprunt e
            JOIN Adherent a ON e.idAdherent = a.idAdherent
            JOIN Livre l ON e.idLivre = l.idLivre
            WHERE l.isbn = %s AND e.statut = 'EN_COURS'
        """
        return db.fetch_one(query, (isbn,))
    
    @staticmethod
    def get_by_adherent(idAdherent):
        """Récupérer les emprunts d'un adhérent"""
        query = """
            SELECT 
                e.*,
                l.titre,
                l.auteur
            FROM Emprunt e
            JOIN Livre l ON e.idLivre = l.idLivre
            WHERE e.idAdherent = %s
            ORDER BY e.dateEmprunt DESC
        """
        return db.fetch_all(query, (idAdherent,))
    
    @staticmethod
    def calculer_date_retour(typeAdherent):
        """Calculer la date de retour selon le type d'adhérent"""
        if typeAdherent == 'ENSEIGNANT':
            duree = DUREE_EMPRUNT_ENSEIGNANT
        else:
            duree = DUREE_EMPRUNT_ETUDIANT
        
        return datetime.now() + timedelta(days=duree)
    
    def save(self):
        """Enregistrer un nouvel emprunt"""
        query = """
            INSERT INTO Emprunt (dateEmprunt, dateRetourPrevue, statut,
                               idLivre, idAdherent, idBibliothecaire)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (self.dateEmprunt, self.dateRetourPrevue, self.statut,
                  self.idLivre, self.idAdherent, self.idBibliothecaire)
        
        if db.execute_query(query, params):
            self.idEmprunt = db.get_last_insert_id()
            return True
        return False
    
    @staticmethod
    def retourner(idEmprunt):
        """Marquer un emprunt comme retourné"""
        query = """
            UPDATE Emprunt 
            SET dateRetourEffective = NOW(), statut = 'RETOURNE'
            WHERE idEmprunt = %s
        """
        return db.execute_query(query, (idEmprunt,))
    
    @staticmethod
    def calculer_retard(dateRetourPrevue):
        """Calculer le nombre de jours de retard"""
        if isinstance(dateRetourPrevue, str):
            dateRetourPrevue = datetime.strptime(dateRetourPrevue, '%Y-%m-%d %H:%M:%S')
        
        if dateRetourPrevue < datetime.now():
            return (datetime.now() - dateRetourPrevue).days
        return 0
    
    @staticmethod
    def get_statistiques():
        """Récupérer les statistiques des emprunts"""
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN statut = 'EN_COURS' THEN 1 ELSE 0 END) as en_cours,
                SUM(CASE WHEN statut = 'EN_RETARD' THEN 1 ELSE 0 END) as en_retard,
                SUM(CASE WHEN statut = 'RETOURNE' THEN 1 ELSE 0 END) as retournes
            FROM Emprunt
        """
        return db.fetch_one(query)
    
    def __str__(self):
        return f"Emprunt #{self.idEmprunt} - {self.statut}"
