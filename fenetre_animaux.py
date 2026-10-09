"""Fenêtre 3 : liste des animaux avec filtres."""

import tkinter as tk
from tkinter import ttk

from donnees import CLASSIFICATIONS, ETATS_SANTE
from style import (BEIGE, CREME, NOIR, VERT_CLAIR, VERT_PALE, BEIGE_FONCE,
                   SOUS_TITRE, TEXTE, GRAS, PETIT, Bouton, carte,
                   ZoneDefilante, vignette_animal, pastille_sante)

LARGEUR_CARTE = 200      # largeur d'une carte animal (en pixels, marges comprises)
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
        self.nb_colonnes = 0

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

        # --- Grille défilante ------------------------------------------------
        self.zone = ZoneDefilante(self)
        self.zone.pack(fill="both", expand=True, padx=14, pady=(4, 12))
        # On recalcule le nombre de colonnes quand la fenêtre change de taille
        self.zone.canvas.bind("<Configure>", self.redimensionner, add="+")

        self.choisir_classe(TOUS)

    # ------------------------------------------------------------------------
    def choisir_classe(self, classe):
        """Retient la classification choisie et met à jour la grille."""
        self.classe_choisie = classe
        self.afficher_grille()

    def redimensionner(self, event):
        colonnes = max(1, event.width // LARGEUR_CARTE)
        if colonnes != self.nb_colonnes:
            self.nb_colonnes = colonnes
            self.afficher_grille()

    def animaux_filtres(self):
        classe = None if self.classe_choisie == TOUS else self.classe_choisie
        sante = None if self.filtre_sante.get() == TOUS_ETATS else self.filtre_sante.get()
        return self.app.zoo.filtrer(classe, sante)

    def afficher_grille(self):
        """(Re)construit la grille de cartes selon les filtres choisis."""
        for widget in self.zone.interieur.winfo_children():
            widget.destroy()

        animaux = self.animaux_filtres()
        titre = PLURIELS.get(self.classe_choisie, "Tous les animaux")
        self.compteur.config(text=f"{titre} : {len(animaux)} animal(aux) affiché(s)")
        if not animaux:
            tk.Label(self.zone.interieur, text="Aucun animal ne correspond à ces filtres.",
                     font=TEXTE, bg=BEIGE, fg=NOIR).grid(row=0, column=0, pady=40, padx=20)
            return

        colonnes = max(1, self.nb_colonnes)
        for col in range(colonnes):
            self.zone.interieur.columnconfigure(col, weight=1)
        for i, animal in enumerate(animaux):
            c = self.creer_carte(animal)
            c.grid(row=i // colonnes, column=i % colonnes, padx=6, pady=6, sticky="n")
        self.zone.remonter()

    def creer_carte(self, animal):
        """Crée la carte d'un animal : photo, nom, espèce et état de santé."""
        c = carte(self.zone.interieur, padx=6, pady=6, cursor="hand2")
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
