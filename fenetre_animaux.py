

import tkinter as tk
from tkinter import ttk

from donnees import CLASSIFICATIONS, ETATS_SANTE
from sons import cri_animal
from style import (BEIGE, CREME, NOIR, VERT_CLAIR, VERT_PALE, BEIGE_FONCE,
                   SOUS_TITRE, TEXTE, GRAS, PETIT, Bouton, carte,
                   vignette_animal, pastille_sante)

NB_COLONNES = 5         
TOUS = "Tous"
TOUS_ETATS = "Tous les états"


PLURIELS = {"Mammifère": "Mammifères", "Oiseau": "Oiseaux", "Reptile": "Reptiles",
            "Amphibien": "Amphibiens", "Poisson": "Poissons"}


class FenetreAnimaux(tk.Frame):
    

    def __init__(self, app):
        super().__init__(app, bg=BEIGE)
        self.app = app
        self.classe_choisie = TOUS

       
        entete = tk.Frame(self, bg=VERT_PALE)
        entete.pack(fill="x")
        tk.Frame(entete, bg=VERT_CLAIR, height=8).pack(fill="x")
        ligne = tk.Frame(entete, bg=VERT_PALE)
        ligne.pack(fill="x", padx=20, pady=10)
        Bouton(ligne, "Retour", app.afficher_accueil, couleur=BEIGE_FONCE).pack(side="left")
        tk.Label(ligne, text="Nos animaux", font=SOUS_TITRE, bg=VERT_PALE,
                 fg=NOIR).pack(side="left", padx=20)
        

        
        filtres = tk.Frame(self, bg=BEIGE)
        filtres.pack(fill="x", padx=20, pady=(12, 4))

        self.boutons_classes = {}
        for classe in [TOUS] + CLASSIFICATIONS:
            b = Bouton(filtres, PLURIELS.get(classe, classe),
                       lambda c=classe: self.choisir_classe(c),
                       couleur=CREME, police=PETIT)
            b.pack(side="left", padx=(0, 6))
            self.boutons_classes[classe] = b

        
        self.filtre_sante = ttk.Combobox(filtres, values=[TOUS_ETATS] + ETATS_SANTE,
                                         state="readonly", width=16)
        self.filtre_sante.set(TOUS_ETATS)
        self.filtre_sante.bind("<<ComboboxSelected>>", lambda e: self.afficher_grille())
        self.filtre_sante.pack(side="right")

        self.compteur = tk.Label(self, font=PETIT, bg=BEIGE, fg=NOIR, anchor="w")
        self.compteur.pack(fill="x", padx=22)

       


        self.canvas = tk.Canvas(self, bg=BEIGE, highlightthickness=0)
        barre = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=barre.set)
        barre.pack(side="right", fill="y", padx=(0, 14), pady=(4, 12))
        self.canvas.pack(fill="both", expand=True, padx=14, pady=(4, 12))

        self.grille = tk.Frame(self.canvas, bg=BEIGE)
        self.canvas.create_window(0, 0, window=self.grille, anchor="nw")

        self.choisir_classe(TOUS)

   
    def choisir_classe(self, classe):
       
        self.classe_choisie = classe
        self.afficher_grille()

    def animaux_filtres(self):
        
        classe = None if self.classe_choisie == TOUS else self.classe_choisie
        sante = None if self.filtre_sante.get() == TOUS_ETATS else self.filtre_sante.get()
        return self.app.zoo.filtrer(classe, sante)

    def afficher_grille(self):
        
        for widget in self.grille.winfo_children():
            widget.destroy()

        animaux = self.animaux_filtres()
        titre = PLURIELS.get(self.classe_choisie, "Tous les animaux")
        self.compteur.config(text=f"{titre} : {len(animaux)} animal affiché")
        if not animaux:
            tk.Label(self.grille, text="none",
                     font=TEXTE, bg=BEIGE, fg=NOIR).grid(row=0, column=0, pady=40, padx=20)
            return

        for i, animal in enumerate(animaux):
            c = self.creer_carte(animal)
            c.grid(row=i // NB_COLONNES, column=i % NB_COLONNES, padx=15, pady=6, sticky="n")

       
        self.grille.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)         

    def creer_carte(self, animal):
       
        c = carte(self.grille, padx=6, pady=6)
        photo = vignette_animal(c, animal)
        photo.pack()
        nom = tk.Label(c, text=animal.nom, font=GRAS, bg=CREME, fg=NOIR, cursor="hand2")
        nom.pack(pady=(6, 0))
        tk.Label(c, text=animal.espece, font=PETIT, bg=CREME, fg=NOIR,
                 wraplength=170).pack()
        pastille_sante(c, animal.sante).pack(pady=(2, 0))

       
        photo.bind("<Button-1>", lambda e: self.ouvrir_fiche(animal))
        nom.bind("<Button-1>", lambda e: self.ouvrir_fiche(animal))
        return c

    def ouvrir_fiche(self, animal):
        cri_animal(animal)
        self.app.afficher_fiche(animal)
