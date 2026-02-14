# main.py
"""
Point d'entrée de l'application Bibliothèque
"""
from database import db
from models import Adherent, Livre, Emprunt
from services.emprunt_service import EmpruntService

def test_backend():
    """Tester les fonctionnalités du backend"""
    
    print("="*60)
    print("TEST DU BACKEND - SYSTÈME DE BIBLIOTHÈQUE")
    print("="*60)
    
    # Connexion à la base de données
    if not db.connect():
        print("✗ Impossible de se connecter à la base de données")
        return
    
    try:
        # 1. TESTER LA RÉCUPÉRATION DES ADHÉRENTS
        print("\n📋 LISTE DES ADHÉRENTS:")
        print("-" * 60)
        adherents = Adherent.get_all()
        for adh in adherents:
            quota_dispo = Adherent.get_emprunts_en_cours(adh['idAdherent'])
            print(f"  • {adh['nom']} {adh['prenom']} ({adh['typeAdherent']}) - {adh['statut']}")
            print(f"    Email: {adh['email']}")
            print(f"    Emprunts en cours: {quota_dispo}")
        
        # 2. TESTER LA RÉCUPÉRATION DES LIVRES
        print("\n📚 LIVRES DISPONIBLES:")
        print("-" * 60)
        livres = Livre.get_disponibles()
        for livre in livres[:5]:  # Afficher les 5 premiers
            print(f"  • {livre['titre']}")
            print(f"    Auteur: {livre['auteur']}")
            print(f"    ISBN: {livre['isbn']}")
            print(f"    Disponibles: {livre['nombreDisponibles']}/{livre['nombreExemplaires']}")
        
        # 3. TESTER LA RECHERCHE
        print("\n🔍 RECHERCHE DE LIVRES (mot-clé: 'Python'):")
        print("-" * 60)
        resultats = Livre.search('Python')
        for livre in resultats:
            print(f"  • {livre['titre']} - {livre['auteur']}")
        
        # 4. TESTER UN EMPRUNT
        print("\n📤 TEST D'EMPRUNT:")
        print("-" * 60)
        success, message, emprunt_id = EmpruntService.emprunter_livre(
            idLivre=1,
            idAdherent=1,
            idBibliothecaire=1
        )
        if success:
            print(f"  ✓ {message}")
            print(f"  ID Emprunt: {emprunt_id}")
        else:
            print(f"  ✗ {message}")
        
        # 5. AFFICHER LES EMPRUNTS EN COURS
        print("\n📊 EMPRUNTS EN COURS:")
        print("-" * 60)
        emprunts = Emprunt.get_en_cours()
        for emp in emprunts:
            print(f"  • {emp['adherent']}")
            print(f"    Livre: {emp['titre']}")
            print(f"    Retour prévu: {emp['dateRetourPrevue']}")
            print(f"    Statut: {emp['statut']}")
        
        # 6. AFFICHER LES RETARDS
        print("\n⚠️  LIVRES EN RETARD:")
        print("-" * 60)
        retards = Emprunt.get_en_retard()
        if retards:
            for ret in retards:
                print(f"  • {ret['adherent']} - {ret['titre']}")
                print(f"    Retard: {ret['joursRetard']} jour(s)")
                print(f"    Pénalité estimée: {ret['joursRetard'] * 0.50:.2f}€")
        else:
            print("  ✓ Aucun retard")
        
        # 7. STATISTIQUES
        print("\n📈 STATISTIQUES:")
        print("-" * 60)
        stats = Emprunt.get_statistiques()
        print(f"  • Total emprunts: {stats['total']}")
        print(f"  • En cours: {stats['en_cours']}")
        print(f"  • En retard: {stats['en_retard']}")
        print(f"  • Retournés: {stats['retournes']}")
        
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
    
    finally:
        # Déconnexion
        db.disconnect()
    
    print("\n" + "="*60)
    print("FIN DU TEST")
    print("="*60)


def main():
    """Fonction principale"""
    print("\n🏛️  SYSTÈME DE GESTION DE BIBLIOTHÈQUE UNIVERSITAIRE")
    print("=" * 60)
    
    # Pour l'instant, on teste le backend
    test_backend()
    
    # TODO: Lancer l'interface graphique Tkinter
    # from ui.main_window import BibliothequeApp
    # app = BibliothequeApp()
    # app.run()


if __name__ == "__main__":
    main()
