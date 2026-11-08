

import tkinter as tk

from donnees import MONTANT_PARRAINAGE, parrains, credit_photo
from style import (BEIGE, CREME, NOIR, VERT_CLAIR, VERT_PALE, BEIGE_FONCE,
                   TITRE, SOUS_TITRE, TEXTE, GRAS, PETIT, POLICE,
                   Bouton, carte, vignette_animal, pastille_sante)


class FenetreFiche(tk.Frame):

    def __init__(self, app, animal):
        super().__init__(app, bg=BEIGE)
        self.app = app

        entete = tk.Frame(self, bg=VERT_PALE)
        entete.pack(fill="x")
        tk.Frame(entete, bg=VERT_CLAIR, height=8).pack(fill="x")
        ligne = tk.Frame(entete, bg=VERT_PALE)
        ligne.pack(fill="x", padx=20, pady=10)
        Bouton(ligne, "Retour à la liste", app.afficher_animaux,
               couleur=BEIGE_FONCE).pack(side="left")
        tk.Label(ligne, text=f"Fiche de {animal.nom}", font=SOUS_TITRE, bg=VERT_PALE,
                 fg=NOIR).pack(side="left", padx=20)

        fiche = carte(self, padx=30, pady=24)
        fiche.pack(pady=24)

        # à gauche : la photo et son auteur
        gauche = tk.Frame(fiche, bg=CREME)
        gauche.grid(row=0, column=0, sticky="n", padx=(0, 30))
        vignette_animal(gauche, animal, grande=True).pack()
        tk.Label(gauche, text=credit_photo(animal.chemin_photo()), font=PETIT, bg=CREME,
                 fg=NOIR, wraplength=380, justify="left").pack(anchor="w", pady=(4, 0))

        # à droite : les informations
        droite = tk.Frame(fiche, bg=CREME)
        droite.grid(row=0, column=1, sticky="n")
        tk.Label(droite, text=animal.nom, font=TITRE, bg=CREME, fg=NOIR).pack(anchor="w")
        tk.Label(droite, text=f"{animal.espece} ({animal.nom_scientifique})",
                 font=(POLICE, 12, "italic"), bg=CREME, fg=NOIR).pack(anchor="w")
        pastille_sante(droite, animal.sante).pack(anchor="w", pady=(6, 12))

        infos = tk.Frame(droite, bg=CREME)
        infos.pack(anchor="w")
        lignes = [("Classification", animal.classification),
                  ("Âge", f"{animal.age} an(s)"),
                  ("Nombre au zoo", animal.nombre),
                  ("Régime", animal.regime),
                  ("Origine", animal.origine),
                  ("Poids", animal.poids),
                  ("Statut UICN", animal.statut_uicn)]
        for i, (titre, valeur) in enumerate(lignes):
            tk.Label(infos, text=titre, font=GRAS, bg=CREME, fg=NOIR).grid(
                row=i, column=0, sticky="w", pady=2)
            tk.Label(infos, text=valeur, font=TEXTE, bg=CREME, fg=NOIR).grid(
                row=i, column=1, sticky="w", padx=(16, 0), pady=2)

        tk.Label(droite, text=animal.description, font=TEXTE, bg=CREME, fg=NOIR,
                 wraplength=420, justify="left").pack(anchor="w", pady=(14, 0))

        # en bas : le parrainage
        bas = tk.Frame(fiche, bg=VERT_PALE, padx=16, pady=12)
        bas.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(22, 0))
        tk.Label(bas, text=f"Parrainez {animal.nom} pour {MONTANT_PARRAINAGE} € par mois",
                 font=GRAS, bg=VERT_PALE, fg=NOIR).pack(side="left")
        tk.Label(bas, text=f"({len(parrains(animal))} parrain(s) pour l'instant)", font=PETIT,
                 bg=VERT_PALE, fg=NOIR).pack(side="left", padx=10)
        Bouton(bas, "Parrainer cet animal",
               lambda: app.afficher_parrainage(animal)).pack(side="right")
