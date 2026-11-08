

import tkinter as tk

from donnees import NOM_DU_ZOO, CLASSIFICATIONS
from style import (BEIGE, CREME, NOIR, VERT_CLAIR, VERT_PALE, BEIGE_FONCE,
                   TITRE, SOUS_TITRE, TEXTE, PETIT, POLICE,
                   Bouton, carte, dessiner_logo)


class FenetreAccueil(tk.Frame):
    

    def __init__(self, app):
        super().__init__(app, bg=BEIGE)
        self.app = app

        # 
        tk.Frame(self, bg=VERT_CLAIR, height=14).pack(fill="x")
        tk.Frame(self, bg=VERT_PALE, height=6).pack(fill="x")

        # 
        haut = tk.Frame(self, bg=BEIGE)
        haut.pack(fill="x", padx=20, pady=(10, 0))
        Bouton(haut, "Espace administrateur", app.afficher_connexion, couleur=BEIGE_FONCE,
               police=PETIT).pack(side="right")

        # 
        centre = carte(self, padx=60, pady=30)
        centre.place(relx=0.5, rely=0.5, anchor="center")

        logo = tk.Canvas(centre, width=130, height=130, bg=CREME, highlightthickness=0)
        dessiner_logo(logo, 65, 65, 60)
        logo.pack()

        tk.Label(centre, text=NOM_DU_ZOO, font=TITRE, bg=CREME, fg=NOIR).pack(pady=(10, 0))
        tk.Label(centre, text="Parc zoologique · Conservation · Découverte",
                 font=(POLICE, 11, "italic"), bg=CREME, fg=NOIR).pack()

        tk.Frame(centre, bg=VERT_CLAIR, height=3, width=380).pack(pady=18)

        tk.Label(centre, text="Merci de votre visite !", font=SOUS_TITRE,
                 bg=CREME, fg=NOIR).pack()
        tk.Label(centre, font=TEXTE, bg=CREME, fg=NOIR, justify="center",
                 text="Nous vous donnons l'occasion de donner votre avis sur le zoo,\n"
                      "de parrainer l'un de nos animaux ou de faire un don.").pack(pady=(8, 22))

        boutons = tk.Frame(centre, bg=CREME)
        boutons.pack()
        Bouton(boutons, " Donner mon avis", app.afficher_saisie,
               police=(POLICE, 14, "bold")).pack(side="left", padx=10)
        Bouton(boutons, "Voir les animaux", app.afficher_animaux,
               police=(POLICE, 14, "bold")).pack(side="left", padx=10)
        Bouton(boutons, "Faire un don", app.afficher_don,
               police=(POLICE, 14, "bold")).pack(side="left", padx=10)

       