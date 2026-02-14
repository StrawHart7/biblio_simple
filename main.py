# main.py
"""
Point d'entrée de l'application Bibliothèque
Lancement de l'interface graphique
"""
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def main():
    """Fonction principale"""
    # 1. Afficher l'écran de connexion
    login_window = LoginWindow()
    bibliothecaire_id = login_window.run()
    
    # 2. Si connexion réussie, afficher le menu principal
    if bibliothecaire_id:
        main_window = MainWindow(bibliothecaire_id)
        main_window.run()
    else:
        print("Connexion annulée")

if __name__ == "__main__":
    main()