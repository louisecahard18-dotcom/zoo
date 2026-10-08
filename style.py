"""
Charte graphique de l'application : couleurs (vert et beige, textes en noir),
polices et widgets personnalisés réutilisés dans toutes les fenêtres.
"""

import os
import tkinter as tk
from tkinter import ttk

# ----------------------------------------------------------------------------
# Couleurs
# ----------------------------------------------------------------------------
VERT_FONCE = "#3E6B48"     # bordures, logo, détails
VERT = "#7FAE7F"           # survol des boutons
VERT_CLAIR = "#A9CBA4"     # boutons
VERT_PALE = "#D7E7D0"      # fonds de bandeaux
BEIGE = "#F3ECDC"          # fond des fenêtres
BEIGE_FONCE = "#E3D5B8"    # bordures des cartes
CREME = "#FCF9F2"          # fond des cartes et des champs
NOIR = "#1C1C1C"           # tous les textes
ETOILE = "#D9A520"         # étoiles des notes

# Couleur de fond des vignettes selon la classification
COULEURS_CLASSES = {
    "Mammifère": "#C9DDB8",
    "Oiseau": "#E8DCB5",
    "Reptile": "#B9D5BF",
    "Amphibien": "#D8E8C2",
    "Poisson": "#C4DDD5",
}

# Pastille de couleur selon l'état de santé (le texte, lui, reste noir)
COULEURS_SANTE = {
    "Bonne santé": "#5E9E5E",
    "Sous surveillance": "#E0B341",
    "Malade": "#C9573F",
    "Blessé": "#C9573F",
    "En convalescence": "#E08D41",
    "Gestante": "#8E7CC3",
}

# ----------------------------------------------------------------------------
# Polices
# ----------------------------------------------------------------------------
POLICE = "Helvetica"
TITRE = (POLICE, 30, "bold")
SOUS_TITRE = (POLICE, 18, "bold")
TEXTE = (POLICE, 12)
GRAS = (POLICE, 12, "bold")
PETIT = (POLICE, 10)
PETIT_GRAS = (POLICE, 10, "bold")
CONSOLE = ("Courier", 11)


def configurer_ttk(fenetre):
    """Applique les couleurs du zoo aux widgets ttk (listes déroulantes, onglets...)."""
    s = ttk.Style(fenetre)
    s.theme_use("clam")
    s.configure(".", background=BEIGE, foreground=NOIR, font=TEXTE)
    s.configure("TCombobox", fieldbackground=CREME, background=VERT_CLAIR,
                arrowcolor=NOIR, bordercolor=VERT_FONCE, padding=4)
    s.map("TCombobox", fieldbackground=[("readonly", CREME)],
          selectbackground=[("readonly", CREME)],
          selectforeground=[("readonly", NOIR)])
    s.configure("TSpinbox", fieldbackground=CREME, background=VERT_CLAIR,
                arrowcolor=NOIR, bordercolor=VERT_FONCE, padding=4)
    s.configure("TNotebook", background=BEIGE, bordercolor=BEIGE_FONCE)
    s.configure("TNotebook.Tab", background=BEIGE_FONCE, foreground=NOIR,
                padding=(16, 6), font=GRAS)
    s.map("TNotebook.Tab", background=[("selected", VERT_CLAIR)])
    s.configure("TCheckbutton", background=CREME, foreground=NOIR, font=TEXTE)
    s.map("TCheckbutton", background=[("active", CREME)])
    s.configure("Vertical.TScrollbar", background=VERT_CLAIR,
                troughcolor=BEIGE, bordercolor=BEIGE, arrowcolor=NOIR)
    # Couleurs de la liste qui s'ouvre sous les Combobox
    fenetre.option_add("*TCombobox*Listbox.background", CREME)
    fenetre.option_add("*TCombobox*Listbox.foreground", NOIR)
    fenetre.option_add("*TCombobox*Listbox.selectBackground", VERT_CLAIR)
    fenetre.option_add("*TCombobox*Listbox.selectForeground", NOIR)
    fenetre.option_add("*TCombobox*Listbox.font", TEXTE)


# ----------------------------------------------------------------------------
# Widgets personnalisés
# ----------------------------------------------------------------------------
class Bouton(tk.Label):
    """
    Bouton vert à texte noir. On utilise un Label cliquable plutôt qu'un
    tk.Button car, sous macOS, tk.Button ignore la couleur de fond.
    """

    def __init__(self, parent, texte, commande, couleur=VERT_CLAIR,
                 survol=VERT, police=GRAS, **options):
        super().__init__(parent, text=texte, bg=couleur, fg=NOIR, font=police,
                         padx=18, pady=8, cursor="hand2",
                         highlightthickness=1, highlightbackground=VERT_FONCE,
                         **options)
        self.commande = commande
        self.couleur = couleur
        self.survol = survol
        self.bind("<Enter>", lambda e: self.config(bg=self.survol))
        self.bind("<Leave>", lambda e: self.config(bg=self.couleur))
        self.bind("<Button-1>", lambda e: self.commande())

    def changer_couleur(self, couleur):
        """Change la couleur au repos (utile pour les boutons de filtre actifs)."""
        self.couleur = couleur
        self.config(bg=couleur)


def carte(parent, **options):
    """Cadre crème avec une fine bordure beige : sert de « carte » pour regrouper des éléments."""
    return tk.Frame(parent, bg=CREME, highlightthickness=1,
                    highlightbackground=BEIGE_FONCE, highlightcolor=BEIGE_FONCE,
                    **options)


def champ_texte(parent, largeur=24, **options):
    """Zone de saisie aux couleurs du zoo."""
    return tk.Entry(parent, width=largeur, font=TEXTE, bg=CREME, fg=NOIR,
                    relief="flat", highlightthickness=1,
                    highlightbackground=BEIGE_FONCE, highlightcolor=VERT_FONCE,
                    insertbackground=NOIR, **options)


class NoteEtoiles(tk.Frame):
    """Note de 1 à 5 sous forme d'étoiles cliquables. self.note vaut 0 tant que rien n'est choisi."""

    def __init__(self, parent, fond=CREME):
        super().__init__(parent, bg=fond)
        self.note = 0
        self.etoiles = []
        for i in range(1, 6):
            lbl = tk.Label(self, text="☆", font=(POLICE, 22), bg=fond,
                           fg=ETOILE, cursor="hand2")
            lbl.pack(side="left")
            lbl.bind("<Enter>", lambda e, n=i: self.colorier(n))
            lbl.bind("<Leave>", lambda e: self.colorier(self.note))
            lbl.bind("<Button-1>", lambda e, n=i: self.choisir(n))
            self.etoiles.append(lbl)
        self.legende = tk.Label(self, text="", font=PETIT, bg=fond, fg=NOIR, width=12,
                                anchor="w")
        self.legende.pack(side="left", padx=8)

    def colorier(self, n):
        for i, lbl in enumerate(self.etoiles):
            lbl.config(text="★" if i < n else "☆")

    def choisir(self, n):
        self.note = n
        self.colorier(n)
        self.legende.config(text=["", "Très mauvais", "Mauvais", "Moyen",
                                  "Bien", "Excellent"][n])


class ZoneDefilante(tk.Frame):
    """
    Cadre avec barre de défilement verticale. Les widgets doivent être placés
    dans self.interieur. Gère la molette de la souris (Windows, macOS, Linux).
    """

    def __init__(self, parent, fond=BEIGE):
        super().__init__(parent, bg=fond)
        self.canvas = tk.Canvas(self, bg=fond, highlightthickness=0)
        barre = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=barre.set)
        barre.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.interieur = tk.Frame(self.canvas, bg=fond)
        self.fenetre_id = self.canvas.create_window((0, 0), window=self.interieur,
                                                    anchor="nw")
        self.interieur.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(
            self.fenetre_id, width=e.width))
        # La molette n'est active que lorsque la souris est au-dessus de la zone
        self.canvas.bind("<Enter>", self.activer_molette)
        self.canvas.bind("<Leave>", self.desactiver_molette)

    def activer_molette(self, event=None):
        self.canvas.bind_all("<MouseWheel>", self.molette)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def desactiver_molette(self, event=None):
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.unbind_all(sequence)

    def molette(self, event):
        # Sous Windows delta vaut ±120 par cran, sous macOS ±1
        pas = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(pas, "units")

    def remonter(self):
        self.canvas.yview_moveto(0)

    def destroy(self):
        self.desactiver_molette()
        super().destroy()


# ----------------------------------------------------------------------------
# Dessins (logo et vignettes d'animaux)
# ----------------------------------------------------------------------------
def dessiner_logo(canvas, x, y, r):
    """Dessine le logo du zoo (une empreinte de patte dans un cercle) centré en (x, y)."""
    canvas.create_oval(x - r, y - r, x + r, y + r, fill=VERT_PALE,
                       outline=VERT_FONCE, width=3)
    # coussinet principal
    canvas.create_oval(x - 0.38 * r, y - 0.05 * r, x + 0.38 * r, y + 0.55 * r,
                       fill=VERT_FONCE, outline="")
    # quatre doigts
    for dx, dy in [(-0.52, -0.25), (-0.2, -0.55), (0.2, -0.55), (0.52, -0.25)]:
        cx, cy = x + dx * r, y + dy * r
        canvas.create_oval(cx - 0.15 * r, cy - 0.19 * r, cx + 0.15 * r,
                           cy + 0.19 * r, fill=VERT_FONCE, outline="")


# Cache des photos déjà chargées (Tkinter oublie une image qui n'est plus
# référencée par une variable : il faut donc les garder en mémoire).
_photos = {}


def charger_photo(animal):
    """Renvoie la photo de l'animal (tk.PhotoImage) ou None si elle n'existe pas."""
    chemin = animal.chemin_photo()
    if chemin not in _photos:
        try:
            _photos[chemin] = tk.PhotoImage(file=chemin) if os.path.exists(chemin) else None
        except tk.TclError:
            _photos[chemin] = None
    return _photos[chemin]


def vignette_animal(parent, animal, largeur=176, hauteur=124, fond=CREME):
    """
    Renvoie un Canvas montrant la photo de l'animal. S'il n'y a pas de photo
    dans images/, on dessine une vignette de remplacement (initiale de
    l'animal sur un fond de la couleur de sa classe).
    """
    c = tk.Canvas(parent, width=largeur, height=hauteur, bg=fond,
                  highlightthickness=0, cursor="hand2")
    photo = charger_photo(animal)
    if photo is not None:
        c.create_image(largeur // 2, hauteur // 2, image=photo)
    else:
        couleur = COULEURS_CLASSES.get(animal.classification, VERT_PALE)
        c.create_rectangle(0, 0, largeur, hauteur, fill=couleur, outline="")
        r = min(largeur, hauteur) // 4
        cx, cy = largeur // 2, hauteur // 2 - 10
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=CREME, outline=VERT_FONCE, width=2)
        c.create_text(cx, cy, text=animal.nom[0].upper(), font=(POLICE, int(r * 0.9), "bold"),
                      fill=NOIR)
        c.create_text(cx, hauteur - 14, text=animal.classification, font=PETIT, fill=NOIR)
    return c


def pastille_sante(parent, sante, fond=CREME):
    """Petit cadre « ● état de santé » (pastille colorée, texte noir)."""
    cadre = tk.Frame(parent, bg=fond)
    tk.Label(cadre, text="●", fg=COULEURS_SANTE.get(sante, NOIR), bg=fond,
             font=PETIT).pack(side="left")
    tk.Label(cadre, text=sante, fg=NOIR, bg=fond, font=PETIT).pack(side="left")
    return cadre
