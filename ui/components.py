# ui/components.py
"""
Composants UI réutilisables avec design moderne
"""
import tkinter as tk
from tkinter import ttk

# Palette de couleurs
COLORS = {
    'primary': '#2c3e50',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'info': '#3498db',
    'warning': '#f39c12',
    'purple': '#9b59b6',
    'background': '#ecf0f1',
    'white': '#ffffff',
    'text': '#2c3e50',
    'text_light': '#7f8c8d',
    'border': '#bdc3c7'
}

class StyledButton(tk.Button):
    """Bouton stylé avec couleurs personnalisées"""
    
    def __init__(self, parent, text, command, color='info', **kwargs):
        # Couleur selon le type
        bg_color = COLORS.get(color, COLORS['info'])
        
        # Configuration par défaut
        default_config = {
            'text': text,
            'command': command,
            'bg': bg_color,
            'fg': 'white',
            'font': ('Arial', 12, 'bold'),
            'cursor': 'hand2',
            'relief': 'flat',
            'bd': 0,
            'padx': 20,
            'pady': 10
        }
        
        # Fusionner avec les kwargs
        default_config.update(kwargs)
        
        super().__init__(parent, **default_config)
        
        # Effet hover
        self.bind('<Enter>', lambda e: self.config(bg=self._darken_color(bg_color)))
        self.bind('<Leave>', lambda e: self.config(bg=bg_color))
    
    def _darken_color(self, hex_color):
        """Assombrir une couleur de 10%"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darker = tuple(int(c * 0.85) for c in rgb)
        return f"#{darker[0]:02x}{darker[1]:02x}{darker[2]:02x}"


class Card(tk.Frame):
    """Carte avec ombre et bordure arrondie (simulée)"""
    
    def __init__(self, parent, title=None, **kwargs):
        super().__init__(
            parent,
            bg=COLORS['white'],
            relief='solid',
            bd=1,
            highlightbackground=COLORS['border'],
            highlightthickness=1,
            **kwargs
        )
        
        if title:
            title_label = tk.Label(
                self,
                text=title,
                font=('Arial', 14, 'bold'),
                bg=COLORS['white'],
                fg=COLORS['text']
            )
            title_label.pack(anchor='w', padx=15, pady=(15, 10))
            
            # Séparateur
            separator = tk.Frame(self, height=2, bg=COLORS['border'])
            separator.pack(fill='x', padx=15, pady=(0, 15))


class SearchBar(tk.Frame):
    """Barre de recherche stylée"""
    
    def __init__(self, parent, placeholder="Rechercher...", on_search=None, **kwargs):
        super().__init__(parent, bg=COLORS['background'], **kwargs)
        
        self.on_search = on_search
        self.search_var = tk.StringVar()
        
        # Icône de recherche (emoji)
        icon = tk.Label(self, text="🔍", font=('Arial', 14), bg=COLORS['background'])
        icon.pack(side='left', padx=(0, 5))
        
        # Champ de recherche
        self.entry = tk.Entry(
            self,
            textvariable=self.search_var,
            font=('Arial', 12),
            relief='solid',
            bd=1,
            width=30
        )
        self.entry.pack(side='left', padx=5)
        self.entry.insert(0, placeholder)
        self.entry.config(fg=COLORS['text_light'])
        
        # Placeholder behavior
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.placeholder = placeholder
        
        # Bouton rechercher
        search_btn = StyledButton(
            self,
            text="Chercher",
            command=self._search,
            color='info',
            width=10
        )
        search_btn.pack(side='left', padx=5)
        
        # Bind Enter key
        self.entry.bind('<Return>', lambda e: self._search())
    
    def _on_focus_in(self, event):
        """Effacer le placeholder au focus"""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=COLORS['text'])
    
    def _on_focus_out(self, event):
        """Remettre le placeholder si vide"""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=COLORS['text_light'])
    
    def _search(self):
        """Déclencher la recherche"""
        value = self.search_var.get()
        if value and value != self.placeholder and self.on_search:
            self.on_search(value)
    
    def get(self):
        """Récupérer la valeur"""
        value = self.search_var.get()
        return value if value != self.placeholder else ""
    
    def clear(self):
        """Vider la recherche"""
        self.search_var.set("")
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg=COLORS['text_light'])


class StyledTable(ttk.Treeview):
    """Tableau stylé avec alternance de couleurs"""
    
    def __init__(self, parent, columns, headings, **kwargs):
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuration du style
        style.configure(
            "Custom.Treeview",
            background=COLORS['white'],
            foreground=COLORS['text'],
            rowheight=35,
            fieldbackground=COLORS['white'],
            font=('Arial', 11)
        )
        
        style.configure(
            "Custom.Treeview.Heading",
            background=COLORS['primary'],
            foreground='white',
            font=('Arial', 11, 'bold'),
            relief='flat'
        )
        
        style.map('Custom.Treeview', background=[('selected', COLORS['info'])])
        
        # Créer le tableau
        super().__init__(
            parent,
            columns=columns,
            show='tree headings',
            style="Custom.Treeview",
            selectmode='browse',
            **kwargs
        )
        
        # Masquer la première colonne (tree)
        self.column('#0', width=0, stretch=False)
        
        # Configurer les colonnes
        for col, heading in zip(columns, headings):
            self.heading(col, text=heading, anchor='w')
            self.column(col, anchor='w', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.yview)
        self.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.pack(side='left', fill='both', expand=True)
        
        # Alternance de couleurs
        self.tag_configure('oddrow', background='#f8f9fa')
        self.tag_configure('evenrow', background=COLORS['white'])
    
    def insert_row(self, values, index=None):
        """Insérer une ligne avec alternance de couleur"""
        if index is None:
            index = len(self.get_children())
        
        tag = 'evenrow' if index % 2 == 0 else 'oddrow'
        return self.insert('', 'end', values=values, tags=(tag,))
    
    def clear(self):
        """Vider le tableau"""
        for item in self.get_children():
            self.delete(item)
    
    def get_selected(self):
        """Récupérer la ligne sélectionnée"""
        selection = self.selection()
        if selection:
            return self.item(selection[0])['values']
        return None


class FormPopup(tk.Toplevel):
    """Fenêtre popup pour formulaires"""
    
    def __init__(self, parent, title, width=500, height=400):
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(bg=COLORS['background'])
        
        # Centrer la fenêtre
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Container
        self.container = tk.Frame(self, bg=COLORS['white'], padx=30, pady=30)
        self.container.pack(fill='both', expand=True, padx=20, pady=20)
    
    def add_field(self, label_text, field_type='entry', options=None, row=0):
        """Ajouter un champ au formulaire"""
        # Label
        label = tk.Label(
            self.container,
            text=label_text,
            font=('Arial', 11, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        )
        label.grid(row=row, column=0, sticky='w', pady=10)
        
        # Champ
        if field_type == 'entry':
            var = tk.StringVar()
            field = tk.Entry(
                self.container,
                textvariable=var,
                font=('Arial', 11),
                width=25
            )
            field.grid(row=row, column=1, sticky='ew', pady=10)
            return var
        
        elif field_type == 'combobox':
            var = tk.StringVar()
            field = ttk.Combobox(
                self.container,
                textvariable=var,
                values=options or [],
                state='readonly',
                font=('Arial', 11),
                width=23
            )
            field.grid(row=row, column=1, sticky='ew', pady=10)
            if options:
                field.current(0)
            return var
        
        elif field_type == 'text':
            field = tk.Text(
                self.container,
                font=('Arial', 11),
                width=25,
                height=4
            )
            field.grid(row=row, column=1, sticky='ew', pady=10)
            return field
    
    def add_buttons(self, on_validate, on_cancel, row=10):
        """Ajouter les boutons de validation"""
        btn_frame = tk.Frame(self.container, bg=COLORS['white'])
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        StyledButton(
            btn_frame,
            text="✓ Valider",
            command=on_validate,
            color='success',
            width=12
        ).pack(side='left', padx=10)
        
        StyledButton(
            btn_frame,
            text="✗ Annuler",
            command=on_cancel,
            color='danger',
            width=12
        ).pack(side='left', padx=10)


class InfoCard(tk.Frame):
    """Carte d'information avec icône et détails"""
    
    def __init__(self, parent, icon, title, details, color='info'):
        super().__init__(
            parent,
            bg=COLORS['white'],
            relief='solid',
            bd=2,
            highlightbackground=COLORS.get(color, COLORS['info']),
            highlightthickness=2
        )
        
        # Icône
        icon_label = tk.Label(
            self,
            text=icon,
            font=('Arial', 24),
            bg=COLORS['white']
        )
        icon_label.pack(pady=(15, 5))
        
        # Titre
        title_label = tk.Label(
            self,
            text=title,
            font=('Arial', 13, 'bold'),
            bg=COLORS['white'],
            fg=COLORS['text']
        )
        title_label.pack(pady=5)
        
        # Détails
        for detail in details:
            detail_label = tk.Label(
                self,
                text=detail,
                font=('Arial', 10),
                bg=COLORS['white'],
                fg=COLORS['text_light']
            )
            detail_label.pack(pady=2)
        
        self.pack(padx=10, pady=10, fill='both', expand=True)