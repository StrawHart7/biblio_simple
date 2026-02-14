# ui/main_window.py
import tkinter as tk
from tkinter import messagebox
from database import db
from models import Emprunt

class MainWindow:
    """Fenêtre principale de l'application"""
    
    def __init__(self, bibliothecaire_id):
        self.root = tk.Tk()
        self.root.title("Gestion Bibliothèque - Menu Principal")
        self.root.geometry("900x600")
        
        self.bibliothecaire_id = bibliothecaire_id
        
        # Récupérer les infos du bibliothécaire
        query = "SELECT * FROM Bibliothecaire WHERE idBibliothecaire = %s"
        self.bibliothecaire = db.fetch_one(query, (bibliothecaire_id,))
        
        # Centrer la fenêtre
        self.center_window()
        
        # Interface
        self.create_widgets()
        
        # Rafraîchir les stats toutes les 5 secondes
        self.refresh_stats()
    
    def center_window(self):
        """Centrer la fenêtre"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Créer l'interface"""
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=80)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="🏛️ SYSTÈME DE GESTION DE BIBLIOTHÈQUE",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=15)
        
        tk.Label(
            header,
            text=f"Connecté : {self.bibliothecaire['prenom']} {self.bibliothecaire['nom']}",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#ecf0f1"
        ).pack()
        
        # Container principal
        container = tk.Frame(self.root, bg="#ecf0f1")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Frame gauche : Boutons principaux
        left_frame = tk.Frame(container, bg="#ecf0f1")
        left_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            left_frame,
            text="ACTIONS PRINCIPALES",
            font=("Arial", 14, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=(0, 20))
        
        # Boutons d'actions
        buttons_config = [
            ("📤 EMPRUNTER", "#27ae60", self.open_emprunt),
            ("📥 RETOURNER", "#e74c3c", self.open_retour),
            ("👥 GÉRER ADHÉRENTS", "#3498db", self.open_adherents),
            ("📚 GÉRER LIVRES", "#9b59b6", self.open_livres),
        ]
        
        for text, color, command in buttons_config:
            btn = tk.Button(
                left_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 14, "bold"),
                width=25,
                height=2,
                cursor="hand2",
                relief="raised",
                bd=3
            )
            btn.pack(pady=10)
        
        # Frame droite : Statistiques
        right_frame = tk.Frame(container, bg="white", relief="solid", bd=2)
        right_frame.pack(side="right", fill="both", padx=(20, 0))
        
        tk.Label(
            right_frame,
            text="📊 TABLEAU DE BORD",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=15)
        
        # Frame pour les stats
        self.stats_frame = tk.Frame(right_frame, bg="white")
        self.stats_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Bouton Déconnexion
        tk.Button(
            self.root,
            text="🚪 DÉCONNEXION",
            command=self.logout,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10),
            cursor="hand2"
        ).pack(side="bottom", pady=10)
    
    def refresh_stats(self):
        """Rafraîchir les statistiques"""
        # Nettoyer le frame
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Récupérer les stats
        stats = Emprunt.get_statistiques()
        retards = db.fetch_one("SELECT COUNT(*) as count FROM Emprunt WHERE statut = 'EN_COURS' AND dateRetourPrevue < NOW()")
        livres_dispo = db.fetch_one("SELECT SUM(nombreDisponibles) as count FROM Livre")
        adherents_actifs = db.fetch_one("SELECT COUNT(*) as count FROM Adherent WHERE statut = 'ACTIF'")
        
        stats_data = [
            ("Emprunts en cours", stats['en_cours'], "#3498db"),
            ("Livres en retard", retards['count'], "#e74c3c"),
            ("Livres disponibles", livres_dispo['count'], "#27ae60"),
            ("Adhérents actifs", adherents_actifs['count'], "#9b59b6"),
        ]
        
        for label, value, color in stats_data:
            frame = tk.Frame(self.stats_frame, bg="white")
            frame.pack(fill="x", pady=10)
            
            tk.Label(
                frame,
                text=str(value),
                font=("Arial", 28, "bold"),
                fg=color,
                bg="white"
            ).pack()
            
            tk.Label(
                frame,
                text=label,
                font=("Arial", 10),
                fg="#7f8c8d",
                bg="white"
            ).pack()
        
        # Rafraîchir toutes les 10 secondes
        self.root.after(10000, self.refresh_stats)
    
    def open_emprunt(self):
        """Ouvrir le module d'emprunt"""
        messagebox.showinfo("Info", "Module Emprunt - À implémenter")
        # TODO: Ouvrir la fenêtre d'emprunt
    
    def open_retour(self):
        """Ouvrir le module de retour"""
        messagebox.showinfo("Info", "Module Retour - À implémenter")
        # TODO: Ouvrir la fenêtre de retour
    
    def open_adherents(self):
        """Ouvrir la gestion des adhérents"""
        messagebox.showinfo("Info", "Gestion Adhérents - À implémenter")
        # TODO: Ouvrir la fenêtre de gestion adhérents
    
    def open_livres(self):
        """Ouvrir la gestion des livres"""
        messagebox.showinfo("Info", "Gestion Livres - À implémenter")
        # TODO: Ouvrir la fenêtre de gestion livres
    
    def logout(self):
        """Déconnexion"""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment vous déconnecter ?"):
            db.disconnect()
            self.root.destroy()
    
    def run(self):
        """Lancer la fenêtre"""
        self.root.mainloop()