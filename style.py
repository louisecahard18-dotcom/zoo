

import calendar
import os
import tkinter as tk
from tkinter import ttk
from datetime import date


VERT_FONCE = "#3E6B48"    
VERT_CLAIR = "#A9CBA4"     
VERT_PALE = "#D7E7D0"      
BEIGE = "#F3ECDC"          
BEIGE_FONCE = "#E3D5B8"    
CREME = "#FCF9F2"          
NOIR = "#1C1C1C"           
ETOILE = "#D9A520"         


COULEURS_CLASSES = {
    "Mammifère": "#C9DDB8",
    "Oiseau": "#E8DCB5",
    "Reptile": "#B9D5BF",
    "Amphibien": "#D8E8C2",
    "Poisson": "#C4DDD5",
}


COULEURS_SANTE = {
    "Bonne santé": "#5E9E5E",
    "Sous surveillance": "#E0B341",
    "Malade": "#C9573F",
    "Blessé": "#C9573F",
    "En convalescence": "#E08D41",
    "Gestante": "#8E7CC3",
}


POLICE = "Helvetica"
TITRE = (POLICE, 30, "bold")
SOUS_TITRE = (POLICE, 18, "bold")
TEXTE = (POLICE, 12)
GRAS = (POLICE, 12, "bold")
PETIT = (POLICE, 10)
PETIT_GRAS = (POLICE, 10, "bold")


def configurer_ttk(fenetre):
    
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

    fenetre.option_add("*TCombobox*Listbox.background", CREME)
    fenetre.option_add("*TCombobox*Listbox.foreground", NOIR)
    fenetre.option_add("*TCombobox*Listbox.selectBackground", VERT_CLAIR)
    fenetre.option_add("*TCombobox*Listbox.selectForeground", NOIR)
    fenetre.option_add("*TCombobox*Listbox.font", TEXTE)



class Bouton(tk.Label):
  

    def __init__(self, parent, texte, commande, couleur=VERT_CLAIR, police=GRAS, **options):
        super().__init__(parent, text=texte, bg=couleur, fg=NOIR, font=police,
                         padx=18, pady=8, cursor="hand2",
                         highlightthickness=1, highlightbackground=VERT_FONCE,
                         **options)
        self.bind("<Button-1>", lambda e: commande())


def carte(parent, **options):

    return tk.Frame(parent, bg=CREME, highlightthickness=1,
                    highlightbackground=BEIGE_FONCE, highlightcolor=BEIGE_FONCE,
                    **options)


def champ_texte(parent, largeur=24, **options):

    return tk.Entry(parent, width=largeur, font=TEXTE, bg=CREME, fg=NOIR,
                    relief="flat", highlightthickness=1,
                    highlightbackground=BEIGE_FONCE, highlightcolor=VERT_FONCE,
                    insertbackground=NOIR, **options)


class NoteEtoiles(tk.Frame):


    def __init__(self, parent, fond=CREME):
        super().__init__(parent, bg=fond)
        self.note = 0
        self.etoiles = []
        for i in range(1, 6):
            lbl = tk.Label(self, text="☆", font=(POLICE, 22), bg=fond,
                           fg=ETOILE, cursor="hand2")
            lbl.pack(side="left")
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



NOMS_MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
             "août", "septembre", "octobre", "novembre", "décembre"]


class Calendrier(tk.Frame):
    # petit calendrier : on clique sur un jour pour le choisir, self.date contient le jour choisi

    def __init__(self, parent, fond=CREME):
        super().__init__(parent, bg=fond, highlightthickness=1, highlightbackground=BEIGE_FONCE)
        self.fond = fond
        self.date = date.today()
        self.annee = self.date.year
        self.mois = self.date.month

        haut = tk.Frame(self, bg=VERT_PALE)
        haut.pack(fill="x")
        Bouton(haut, "◀", self.mois_precedent, couleur=VERT_PALE, police=PETIT_GRAS).pack(side="left")
        Bouton(haut, "▶", self.mois_suivant, couleur=VERT_PALE, police=PETIT_GRAS).pack(side="right")
        self.titre = tk.Label(haut, font=GRAS, bg=VERT_PALE, fg=NOIR)
        self.titre.pack(side="left", expand=True)

        self.grille = tk.Frame(self, bg=fond)
        self.grille.pack(padx=6, pady=6)
        self.afficher()

    def afficher(self):
        for widget in self.grille.winfo_children():
            widget.destroy()
        self.titre.config(text=f"{NOMS_MOIS[self.mois - 1]} {self.annee}")

        for col, nom in enumerate(["L", "M", "M", "J", "V", "S", "D"]):
            tk.Label(self.grille, text=nom, font=PETIT_GRAS, width=3, bg=self.fond,
                     fg=NOIR).grid(row=0, column=col)

        # monthcalendar donne les semaines du mois, avec 0 pour les cases vides
        for ligne, semaine in enumerate(calendar.monthcalendar(self.annee, self.mois), start=1):
            for col, jour in enumerate(semaine):
                if jour == 0:
                    continue
                ce_jour = date(self.annee, self.mois, jour)
                couleur = VERT_CLAIR if ce_jour == self.date else self.fond
                police = PETIT_GRAS if ce_jour == date.today() else PETIT
                case = tk.Label(self.grille, text=jour, font=police, width=3, bg=couleur, fg=NOIR,
                                cursor="hand2")
                case.grid(row=ligne, column=col, padx=1, pady=1)
                case.bind("<Button-1>", lambda e, d=ce_jour: self.choisir(d))

    def choisir(self, jour):
        self.date = jour
        self.afficher()

    def mois_precedent(self):
        if self.mois == 1:
            self.mois = 12
            self.annee = self.annee - 1
        else:
            self.mois = self.mois - 1
        self.afficher()

    def mois_suivant(self):
        # on ne va pas plus loin que le mois actuel : la visite ne peut pas être dans le futur
        if (self.annee, self.mois) >= (date.today().year, date.today().month):
            return
        if self.mois == 12:
            self.mois = 1
            self.annee = self.annee + 1
        else:
            self.mois = self.mois + 1
        self.afficher()


def dessiner_logo(canvas, x, y, r):
    
    canvas.create_oval(x - r, y - r, x + r, y + r, fill=VERT_PALE,
                       outline=VERT_FONCE, width=3)
   
    
    canvas.create_oval(x - 0.38 * r, y - 0.05 * r, x + 0.38 * r, y + 0.55 * r,
                       fill=VERT_FONCE, outline="")
    # quatre doigts
    for dx, dy in [(-0.52, -0.25), (-0.2, -0.55), (0.2, -0.55), (0.52, -0.25)]:
        cx, cy = x + dx * r, y + dy * r
        canvas.create_oval(cx - 0.15 * r, cy - 0.19 * r, cx + 0.15 * r,
                           cy + 0.19 * r, fill=VERT_FONCE, outline="")



_photos = {}


def charger_photo(chemin):
    
    if chemin not in _photos:
        try:
            _photos[chemin] = tk.PhotoImage(file=chemin) if os.path.exists(chemin) else None
        except tk.TclError:
            _photos[chemin] = None
    return _photos[chemin]


def vignette_animal(parent, animal, grande=False, fond=CREME):
    # petite photo pour la liste des animaux, grande photo pour la fiche
    if grande:
        largeur, hauteur, chemin = 380, 268, animal.chemin_grande_photo()
    else:
        largeur, hauteur, chemin = 176, 124, animal.chemin_photo()
    c = tk.Canvas(parent, width=largeur, height=hauteur, bg=fond,
                  highlightthickness=0, cursor="hand2")
    photo = charger_photo(chemin)
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
   
    cadre = tk.Frame(parent, bg=fond)
    tk.Label(cadre, text="●", fg=COULEURS_SANTE.get(sante, NOIR), bg=fond,
             font=PETIT).pack(side="left")
    tk.Label(cadre, text=sante, fg=NOIR, bg=fond, font=PETIT).pack(side="left")
    return cadre
