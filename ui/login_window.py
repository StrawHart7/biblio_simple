# ui/login_window.py
import tkinter as tk
from tkinter import messagebox
from database import db

class LoginWindow:
    """Fenêtre de connexion pour le bibliothécaire"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connexion - Bibliothèque")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Centrer la fenêtre
        self.center_window()
        
        # Variables
        self.login_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.bibliothecaire_id = None
        
        # Interface
        self.create_widgets()
        
        # Connexion à la BDD
        if not db.connect():
            messagebox.showerror("Erreur", "Impossible de se connecter à la base de données")
            self.root.destroy()
    
    def center_window(self):
        """Centrer la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Créer les widgets de l'interface"""
        # Titre
        title = tk.Label(
            self.root,
            text="🏛️ BIBLIOTHÈQUE UNIVERSITAIRE",
            font=("Arial", 16, "bold"),
            fg="#2c3e50"
        )
        title.pack(pady=30)
        
        # Frame pour le formulaire
        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=20)
        
        # Login
        tk.Label(form_frame, text="Login :", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=10)
        login_entry = tk.Entry(form_frame, textvariable=self.login_var, font=("Arial", 11), width=25)
        login_entry.grid(row=0, column=1, pady=10)
        login_entry.focus()
        
        # Mot de passe
        tk.Label(form_frame, text="Mot de passe :", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=10)
        password_entry = tk.Entry(form_frame, textvariable=self.password_var, show="●", font=("Arial", 11), width=25)
        password_entry.grid(row=1, column=1, pady=10)
        
        # Bouton connexion
        login_btn = tk.Button(
            self.root,
            text="SE CONNECTER",
            command=self.login,
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            cursor="hand2"
        )
        login_btn.pack(pady=20)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Vérifier les identifiants"""
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()
        
        if not login or not password:
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs")
            return
        
        # Vérifier dans la base de données
        query = "SELECT * FROM Bibliothecaire WHERE login = %s AND motDePasse = %s"
        result = db.fetch_one(query, (login, password))
        
        if result:
            self.bibliothecaire_id = result['idBibliothecaire']
            messagebox.showinfo("Succès", f"Bienvenue {result['prenom']} {result['nom']} !")
            self.root.destroy()  # Fermer la fenêtre de connexion
        else:
            messagebox.showerror("Erreur", "Login ou mot de passe incorrect")
            self.password_var.set("")  # Vider le mot de passe
    
    def run(self):
        """Lancer la fenêtre"""
        self.root.mainloop()
        return self.bibliothecaire_id