# ui/emprunt_window.py
import tkinter as tk
from tkinter import messagebox
from ui.components import *
from models import Adherent, Livre
from services.emprunt_service import EmpruntService

class EmpruntWindow:
    """Module d'emprunt avec interface soignée"""
    
    def __init__(self, parent, bibliothecaire_id):
        self.window = tk.Toplevel(parent)
        self.window.title("📤 Emprunter un Livre")
        self.window.geometry("900x700")
        self.window.configure(bg=COLORS['background'])
        
        self.bibliothecaire_id = bibliothecaire_id
        self.adherent_selectionne = None
        self.livre_selectionne = None
        
        # Centrer
        self.center_window()
        
        # Interface
        self.create_widgets()
    
    def center_window(self):
        """Centrer la fenêtre"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Créer l'interface"""
        # Header (fixe)
        header = tk.Frame(self.window, bg=COLORS['success'], height=70)
        header.pack(fill='x')
        
        tk.Label(
            header,
            text="📤 EMPRUNTER UN LIVRE",
            font=('Arial', 20, 'bold'),
            bg=COLORS['success'],
            fg='white'
        ).pack(pady=20)
        
        # Frame avec scrollbar
        main_frame = tk.Frame(self.window, bg=COLORS['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Canvas pour le scroll
        canvas = tk.Canvas(main_frame, bg=COLORS['background'], highlightthickness=0)
        canvas.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Container scrollable
        container = tk.Frame(canvas, bg=COLORS['background'])
        canvas_frame = canvas.create_window((0, 0), window=container, anchor='nw')
        
        # Ajuster la zone scrollable
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            # Ajuster la largeur du container
            canvas.itemconfig(canvas_frame, width=event.width)
        
        container.bind('<Configure>', configure_scroll)
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        
        # Scroll avec la molette
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Padding
        content = tk.Frame(container, bg=COLORS['background'])
        content.pack(padx=30, pady=20, fill='both', expand=True)
        
        # === SECTION ADHÉRENT ===
        adherent_card = Card(content, title="👤 SÉLECTION DE L'ADHÉRENT")
        adherent_card.pack(fill='x', pady=(0, 20))
        
        # Recherche adhérent
        search_frame = tk.Frame(adherent_card, bg=COLORS['white'])
        search_frame.pack(fill='x', padx=15, pady=10)
        
        self.adherent_search = SearchBar(
            search_frame,
            placeholder="Nom, prénom ou email...",
            on_search=self.search_adherent
        )
        self.adherent_search.pack(fill='x')
        
        # Résultat adhérent
        self.adherent_result_frame = tk.Frame(adherent_card, bg=COLORS['white'])
        self.adherent_result_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # === SECTION LIVRE ===
        livre_card = Card(content, title="📚 SÉLECTION DU LIVRE")
        livre_card.pack(fill='x', pady=(0, 20))
        
        # Recherche livre
        search_frame2 = tk.Frame(livre_card, bg=COLORS['white'])
        search_frame2.pack(fill='x', padx=15, pady=10)
        
        self.livre_search = SearchBar(
            search_frame2,
            placeholder="Titre, auteur ou ISBN...",
            on_search=self.search_livre
        )
        self.livre_search.pack(fill='x')
        
        # Résultat livre
        self.livre_result_frame = tk.Frame(livre_card, bg=COLORS['white'])
        self.livre_result_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # === BOUTON VALIDATION ===
        btn_frame = tk.Frame(content, bg=COLORS['background'])
        btn_frame.pack(pady=20)
        
        self.validate_btn = StyledButton(
            btn_frame,
            text="✅ VALIDER L'EMPRUNT",
            command=self.valider_emprunt,
            color='success',
            width=25,
            height=2,
            font=('Arial', 14, 'bold'),
            state='disabled'
        )
        self.validate_btn.pack()

    def search_adherent(self, keyword):
        """Rechercher un adhérent"""
        # Nettoyer les résultats précédents
        for widget in self.adherent_result_frame.winfo_children():
            widget.destroy()
        
        # Rechercher
        resultats = Adherent.search(keyword)
        
        if not resultats:
            tk.Label(
                self.adherent_result_frame,
                text="Aucun adhérent trouvé",
                font=('Arial', 11),
                fg=COLORS['text_light'],
                bg=COLORS['white']
            ).pack(pady=10)
            return
        
        # Afficher les résultats
        for adh in resultats[:5]:  # Max 5 résultats
            self.create_adherent_card(adh)
    
    def create_adherent_card(self, adherent):
        """Créer une carte adhérent cliquable"""
        # Vérifier si peut emprunter
        emprunts_en_cours = Adherent.get_emprunts_en_cours(adherent['idAdherent'])
        quota_max = 5 if adherent['typeAdherent'] == 'ENSEIGNANT' else 3
        quota_dispo = quota_max - emprunts_en_cours
        peut_emprunter = adherent['statut'] == 'ACTIF' and quota_dispo > 0
        
        # Couleur selon statut
        border_color = COLORS['success'] if peut_emprunter else COLORS['danger']
        
        card = tk.Frame(
            self.adherent_result_frame,
            bg=COLORS['white'],
            relief='solid',
            bd=2,
            highlightbackground=border_color,
            highlightthickness=2,
            cursor='hand2' if peut_emprunter else 'arrow'
        )
        card.pack(fill='x', pady=5)
        
        # Nom
        nom_label = tk.Label(
            card,
            text=f"✓ {adherent['nom']} {adherent['prenom']}",
            font=('Arial', 13, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        )
        nom_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        # Détails
        details = f"📧 {adherent['email']} | 🎓 {adherent['typeAdherent']} | Quota: {quota_dispo}/{quota_max}"
        
        if adherent['statut'] != 'ACTIF':
            details += f" | ⚠️ {adherent['statut']}"
        
        detail_label = tk.Label(
            card,
            text=details,
            font=('Arial', 10),
            bg=COLORS['white'],
            fg=COLORS['text_light']
        )
        detail_label.pack(anchor='w', padx=15, pady=(0, 10))
        
        # Rendre cliquable si peut emprunter
        if peut_emprunter:
            card.bind('<Button-1>', lambda e: self.select_adherent(adherent, card))
            nom_label.bind('<Button-1>', lambda e: self.select_adherent(adherent, card))
            detail_label.bind('<Button-1>', lambda e: self.select_adherent(adherent, card))
        else:
            avertissement = tk.Label(
                card,
                text="❌ Ne peut pas emprunter actuellement",
                font=('Arial', 10, 'bold'),
                bg=COLORS['white'],
                fg=COLORS['danger']
            )
            avertissement.pack(anchor='w', padx=15, pady=(0, 10))
    
    def select_adherent(self, adherent, card):
        """Sélectionner un adhérent"""
        # Désélectionner les autres
        for widget in self.adherent_result_frame.winfo_children():
            widget.config(bg=COLORS['white'])
        
        # Sélectionner celui-ci
        card.config(bg='#e8f8f5')
        self.adherent_selectionne = adherent
        
        # Vérifier si on peut valider
        self.check_can_validate()
    
    def search_livre(self, keyword):
        """Rechercher un livre"""
        # Nettoyer les résultats précédents
        for widget in self.livre_result_frame.winfo_children():
            widget.destroy()
        
        # Rechercher
        resultats = Livre.search(keyword)
        
        if not resultats:
            tk.Label(
                self.livre_result_frame,
                text="Aucun livre trouvé",
                font=('Arial', 11),
                fg=COLORS['text_light'],
                bg=COLORS['white']
            ).pack(pady=10)
            return
        
        # Afficher les résultats
        for livre in resultats[:5]:  # Max 5 résultats
            self.create_livre_card(livre)
    
    def create_livre_card(self, livre):
        """Créer une carte livre cliquable"""
        disponible = livre['nombreDisponibles'] > 0
        border_color = COLORS['success'] if disponible else COLORS['danger']
        
        card = tk.Frame(
            self.livre_result_frame,
            bg=COLORS['white'],
            relief='solid',
            bd=2,
            highlightbackground=border_color,
            highlightthickness=2,
            cursor='hand2' if disponible else 'arrow'
        )
        card.pack(fill='x', pady=5)
        
        # Titre
        titre_label = tk.Label(
            card,
            text=f"✓ {livre['titre']}",
            font=('Arial', 13, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        )
        titre_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        # Détails
        details = f"👤 {livre['auteur']} | 📦 Disponibles: {livre['nombreDisponibles']}/{livre['nombreExemplaires']}"
        if livre.get('isbn'):
            details += f" | 🔢 {livre['isbn']}"
        
        detail_label = tk.Label(
            card,
            text=details,
            font=('Arial', 10),
            bg=COLORS['white'],
            fg=COLORS['text_light']
        )
        detail_label.pack(anchor='w', padx=15, pady=(0, 10))
        
        # Rendre cliquable si disponible
        if disponible:
            card.bind('<Button-1>', lambda e: self.select_livre(livre, card))
            titre_label.bind('<Button-1>', lambda e: self.select_livre(livre, card))
            detail_label.bind('<Button-1>', lambda e: self.select_livre(livre, card))
        else:
            indispo = tk.Label(
                card,
                text="❌ Aucun exemplaire disponible",
                font=('Arial', 10, 'bold'),
                bg=COLORS['white'],
                fg=COLORS['danger']
            )
            indispo.pack(anchor='w', padx=15, pady=(0, 10))
    
    def select_livre(self, livre, card):
        """Sélectionner un livre"""
        # Désélectionner les autres
        for widget in self.livre_result_frame.winfo_children():
            widget.config(bg=COLORS['white'])
        
        # Sélectionner celui-ci
        card.config(bg='#e8f4f8')
        self.livre_selectionne = livre
        
        # Vérifier si on peut valider
        self.check_can_validate()
    
    def check_can_validate(self):
        """Vérifier si on peut valider l'emprunt"""
        if self.adherent_selectionne and self.livre_selectionne:
            self.validate_btn.config(state='normal')
        else:
            self.validate_btn.config(state='disabled')
    
    def valider_emprunt(self):
        """Valider l'emprunt"""
        if not self.adherent_selectionne or not self.livre_selectionne:
            return
        
        # Confirmer
        message = f"Confirmer l'emprunt ?\n\n"
        message += f"👤 {self.adherent_selectionne['nom']} {self.adherent_selectionne['prenom']}\n"
        message += f"📚 {self.livre_selectionne['titre']}"
        
        if not messagebox.askyesno("Confirmation", message):
            return
        
        # Enregistrer l'emprunt
        success, msg, emprunt_id = EmpruntService.emprunter_livre(
            self.livre_selectionne['idLivre'],
            self.adherent_selectionne['idAdherent'],
            self.bibliothecaire_id
        )
        
        if success:
            messagebox.showinfo("Succès", f"✅ {msg}")
            self.window.destroy()
        else:
            messagebox.showerror("Erreur", f"❌ {msg}")