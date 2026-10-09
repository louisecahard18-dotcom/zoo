"""Fenêtre 3 : liste des animaux avec filtres."""

import tkinter as tk
from tkinter import ttk

from donnees import CLASSIFICATIONS, ETATS_SANTE
from style import (BEIGE, CREME, NOIR, VERT_CLAIR, VERT_PALE, BEIGE_FONCE,
                   SOUS_TITRE, TEXTE, GRAS, PETIT, Bouton, carte,
                   vignette_animal, pastille_sante)

NB_COLONNES = 5          # nombre de cartes par ligne
TOUS = "Tous"
TOUS_ETATS = "Tous les états"

# Nom des classifications au pluriel pour les boutons de filtre
PLURIELS = {"Mammifère": "Mammifères", "Oiseau": "Oiseaux", "Reptile": "Reptiles",
            "Amphibien": "Amphibiens", "Poisson": "Poissons"}


class FenetreAnimaux(tk.Frame):
    """Grille de tous les animaux (photo + nom), filtrable par classification."""

    def __init__(self, app):
        super().__init__(app, bg=BEIGE)
        self.app = app
        self.classe_choisie = TOUS

        # --- En-tête ---------------------------------------------------------
        entete = tk.Frame(self, bg=VERT_PALE)
        entete.pack(fill="x")
        tk.Frame(entete, bg=VERT_CLAIR, height=8).pack(fill="x")
        ligne = tk.Frame(entete, bg=VERT_PALE)
        ligne.pack(fill="x", padx=20, pady=10)
        Bouton(ligne, "←  Retour", app.afficher_accueil, couleur=BEIGE_FONCE).pack(side="left")
        tk.Label(ligne, text="Nos animaux", font=SOUS_TITRE, bg=VERT_PALE,
                 fg=NOIR).pack(side="left", padx=20)
        tk.Label(ligne, text="Cliquez sur un animal pour découvrir sa fiche et le parrainer",
                 font=TEXTE, bg=VERT_PALE, fg=NOIR).pack(side="right")

        # --- Barre de filtres ------------------------------------------------
        filtres = tk.Frame(self, bg=BEIGE)
        filtres.pack(fill="x", padx=20, pady=(12, 4))

        self.boutons_classes = {}
        for classe in [TOUS] + CLASSIFICATIONS:
            b = Bouton(filtres, PLURIELS.get(classe, classe),
                       lambda c=classe: self.choisir_classe(c),
                       couleur=CREME, police=PETIT)
            b.pack(side="left", padx=(0, 6))
            self.boutons_classes[classe] = b

        # Filtre supplémentaire par état de santé
        self.filtre_sante = ttk.Combobox(filtres, values=[TOUS_ETATS] + ETATS_SANTE,
                                         state="readonly", width=16)
        self.filtre_sante.set(TOUS_ETATS)
        self.filtre_sante.bind("<<ComboboxSelected>>", lambda e: self.afficher_grille())
        self.filtre_sante.pack(side="right")

        self.compteur = tk.Label(self, font=PETIT, bg=BEIGE, fg=NOIR, anchor="w")
        self.compteur.pack(fill="x", padx=22)

        # --- Zone qui défile : un Canvas qui contient un Frame (la grille) ----
        cadre = tk.Frame(self, bg=BEIGE)
        cadre.pack(fill="both", expand=True, padx=14, pady=(4, 12))
        self.canvas = tk.Canvas(cadre, bg=BEIGE, highlightthickness=0)
        barre = ttk.Scrollbar(cadre, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=barre.set)
        barre.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.grille = tk.Frame(self.canvas, bg=BEIGE)
        id_grille = self.canvas.create_window(0, 0, window=self.grille, anchor="nw")
        # La zone à faire défiler correspond à la taille de la grille
        self.grille.bind("<Configure>",
                         lambda e: self.canvas.config(scrollregion=self.canvas.bbox("all")))
        # La grille prend toute la largeur du Canvas
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(id_grille, width=e.width))
        # La molette de la souris fait défiler la liste
        self.bind_all("<MouseWheel>", self.molette)

        self.choisir_classe(TOUS)

    # ------------------------------------------------------------------------
    def choisir_classe(self, classe):
        """Retient la classification choisie et met à jour la grille."""
        self.classe_choisie = classe
        self.afficher_grille()

    def molette(self, event):
        """Fait défiler la liste (event.delta > 0 quand on tourne la molette vers le haut)."""
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")

    def destroy(self):
        # Quand on quitte la page, on arrête d'écouter la molette
        self.unbind_all("<MouseWheel>")
        super().destroy()

    def animaux_filtres(self):
        classe = None if self.classe_choisie == TOUS else self.classe_choisie
        sante = None if self.filtre_sante.get() == TOUS_ETATS else self.filtre_sante.get()
        return self.app.zoo.filtrer(classe, sante)

    def afficher_grille(self):
        """(Re)construit la grille de cartes selon les filtres choisis."""
        for widget in self.grille.winfo_children():
            widget.destroy()

        animaux = self.animaux_filtres()
        titre = PLURIELS.get(self.classe_choisie, "Tous les animaux")
        self.compteur.config(text=f"{titre} : {len(animaux)} animal(aux) affiché(s)")
        if not animaux:
            tk.Label(self.grille, text="Aucun animal ne correspond à ces filtres.",
                     font=TEXTE, bg=BEIGE, fg=NOIR).grid(row=0, column=0, pady=40, padx=20)
            return

        for col in range(NB_COLONNES):
            self.grille.columnconfigure(col, weight=1)
        for i, animal in enumerate(animaux):
            c = self.creer_carte(animal)
            c.grid(row=i // NB_COLONNES, column=i % NB_COLONNES, padx=4, pady=6, sticky="n")
        self.canvas.yview_moveto(0)          # on revient en haut de la liste

    def creer_carte(self, animal):
        """Crée la carte d'un animal : photo, nom, espèce et état de santé."""
        c = carte(self.grille, padx=6, pady=6, cursor="hand2")
        vignette_animal(c, animal).pack()
        tk.Label(c, text=animal.nom, font=GRAS, bg=CREME, fg=NOIR).pack(pady=(6, 0))
        tk.Label(c, text=animal.espece, font=PETIT, bg=CREME, fg=NOIR,
                 wraplength=170).pack()
        pastille_sante(c, animal.sante).pack(pady=(2, 0))

        # Toute la carte (et tout ce qu'elle contient) est cliquable
        def lier(widget):
            widget.bind("<Button-1>", lambda e: self.app.ouvrir_fiche(animal))
            for enfant in widget.winfo_children():
                lier(enfant)

        lier(c)
        return c
