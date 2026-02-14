# services/emprunt_service.py
from datetime import datetime
from models import Adherent, Livre, Emprunt
from models.livre import Livre as LivreModel
from models.adherent import Adherent as AdherentModel
from database import db
from config import PENALITE_PAR_JOUR

class EmpruntService:
    """Service gérant la logique métier des emprunts"""
    
    @staticmethod
    def emprunter_livre(idLivre, idAdherent, idBibliothecaire):
        """
        Emprunter un livre avec toutes les vérifications
        Retourne : (success: bool, message: str, emprunt_id: int ou None)
        """
        # 1. Vérifier que le livre existe et est disponible
        livre = Livre.get_by_id(idLivre)
        if not livre:
            return False, "Livre introuvable", None
        
        if livre['nombreDisponibles'] <= 0:
            return False, "Aucun exemplaire disponible", None
        
        # 2. Vérifier que l'adhérent existe et peut emprunter
        adherent = Adherent.get_by_id(idAdherent)
        if not adherent:
            return False, "Adhérent introuvable", None
        
        if adherent['statut'] != 'ACTIF':
            return False, f"Adhérent {adherent['statut'].lower()} - Emprunt impossible", None
        
        # 3. Vérifier le quota
        emprunts_en_cours = Adherent.get_emprunts_en_cours(idAdherent)
        quota_max = 5 if adherent['typeAdherent'] == 'ENSEIGNANT' else 3
        
        if emprunts_en_cours >= quota_max:
            return False, f"Quota atteint ({emprunts_en_cours}/{quota_max})", None
        
        # 4. Calculer la date de retour
        date_retour = Emprunt.calculer_date_retour(adherent['typeAdherent'])
        
        # 5. Créer l'emprunt
        emprunt = Emprunt(
            dateRetourPrevue=date_retour,
            idLivre=idLivre,
            idAdherent=idAdherent,
            idBibliothecaire=idBibliothecaire
        )
        
        if not emprunt.save():
            return False, "Erreur lors de l'enregistrement de l'emprunt", None
        
        # 6. Décrémenter la disponibilité
        if not LivreModel.decrementer_disponibilite(idLivre):
            return False, "Erreur lors de la mise à jour de la disponibilité", None
        
        message = f"Emprunt enregistré ! Retour prévu le {date_retour.strftime('%d/%m/%Y')}"
        return True, message, emprunt.idEmprunt
    
    @staticmethod
    def retourner_livre(isbn):
        """
        Retourner un livre avec calcul automatique de pénalité
        Retourne : (success: bool, message: str, penalite: float ou None)
        """
        # 1. Trouver l'emprunt en cours pour ce livre
        emprunt = Emprunt.get_by_livre_isbn(isbn)
        if not emprunt:
            return False, "Aucun emprunt en cours pour ce livre", None
        
        # 2. Calculer le retard éventuel
        jours_retard = Emprunt.calculer_retard(emprunt['dateRetourPrevue'])
        montant_penalite = 0
        
        if jours_retard > 0:
            montant_penalite = jours_retard * PENALITE_PAR_JOUR
            
            # Créer la pénalité
            query_penalite = """
                INSERT INTO Penalite (montant, motif, idEmprunt)
                VALUES (%s, %s, %s)
            """
            motif = f"Retard de {jours_retard} jour(s) à {PENALITE_PAR_JOUR}€/jour"
            db.execute_query(query_penalite, (montant_penalite, motif, emprunt['idEmprunt']))
        
        # 3. Marquer l'emprunt comme retourné
        if not Emprunt.retourner(emprunt['idEmprunt']):
            return False, "Erreur lors du retour", None
        
        # 4. Incrémenter la disponibilité
        livre = Livre.get_by_isbn(isbn)
        if not LivreModel.incrementer_disponibilite(livre['idLivre']):
            return False, "Erreur lors de la mise à jour de la disponibilité", None
        
        # 5. Vérifier s'il y a des réservations en attente
        EmpruntService._notifier_reservations(livre['idLivre'])
        
        # Message de confirmation
        if jours_retard > 0:
            message = f"Retour enregistré. RETARD : {jours_retard} jour(s) - Pénalité : {montant_penalite:.2f}€"
        else:
            message = "Retour enregistré avec succès"
        
        return True, message, montant_penalite
    
    @staticmethod
    def _notifier_reservations(idLivre):
        """Vérifier et notifier les réservations en attente (privé)"""
        query = """
            SELECT r.*, CONCAT(a.nom, ' ', a.prenom) as adherent
            FROM Reservation r
            JOIN Adherent a ON r.idAdherent = a.idAdherent
            WHERE r.idLivre = %s AND r.statut = 'EN_ATTENTE'
            ORDER BY r.position
            LIMIT 1
        """
        reservation = db.fetch_one(query, (idLivre,))
        
        if reservation:
            print(f"📢 NOTIFICATION : Le livre est réservé par {reservation['adherent']}")
            # TODO: Marquer la réservation comme notifiée
            # TODO: Envoyer email/SMS (optionnel pour projet étudiant)
    
    @staticmethod
    def get_emprunts_adherent(idAdherent):
        """Récupérer l'historique des emprunts d'un adhérent"""
        return Emprunt.get_by_adherent(idAdherent)
    
    @staticmethod
    def prolonger_emprunt(idEmprunt, jours=7):
        """Prolonger un emprunt (optionnel)"""
        query = """
            UPDATE Emprunt 
            SET dateRetourPrevue = DATE_ADD(dateRetourPrevue, INTERVAL %s DAY)
            WHERE idEmprunt = %s AND statut = 'EN_COURS'
        """
        if db.execute_query(query, (jours, idEmprunt)):
            return True, f"Emprunt prolongé de {jours} jours"
        return False, "Erreur lors de la prolongation"
