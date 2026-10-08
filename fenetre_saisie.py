"""Fenêtre 2 : saisie de l'avis du visiteur."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from donnees import GENRES, TRANCHES_AGE, PAYS, REGIONS, enregistrer_avis
from style import (BEIGE, CREME, NOIR, VERT_CLAIR, VERT_PALE, BEIGE_FONCE,
                   SOUS_TITRE, TEXTE, GRAS, PETIT, POLICE,
                   Bouton, carte, champ_texte, NoteEtoiles)

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def nom_valide(texte):
    """Un nom ne contient que des lettres, des espaces, des tirets ou des apostrophes."""
    return texte != "" and all(c.isalpha() or c in " -'" for c in texte)


class FenetreSaisie(tk.Frame):
    """Formulaire d'avis. Les données validées sont enregistrées dans 4 fichiers CSV."""

    def __init__(self, app):
        super().__init__(app, bg=BEIGE)
        self.app = app

        # --- En-tête ---------------------------------------------------------
        entete = tk.Frame(self, bg=VERT_PALE)
        entete.pack(fill="x")
        tk.Frame(entete, bg=VERT_CLAIR, height=8).pack(fill="x")
        tk.Label(entete, text="Votre avis nous intéresse", font=SOUS_TITRE,
                 bg=VERT_PALE, fg=NOIR).pack(pady=(12, 0))
        tk.Label(entete, text="Quelques questions rapides pour nous aider à améliorer "
                              "le zoo. Les champs marqués * sont obligatoires.",
                 font=TEXTE, bg=VERT_PALE, fg=NOIR).pack(pady=(2, 12))

        corps = tk.Frame(self, bg=BEIGE)
        corps.pack(expand=True, pady=10)

        # --- Colonne de gauche : le visiteur --------------------------------
        gauche = carte(corps, padx=24, pady=16)
        gauche.grid(row=0, column=0, sticky="n", padx=12)
        self.titre_section(gauche, "Vous et votre groupe")

        self.nom = champ_texte(gauche)
        self.prenom = champ_texte(gauche)
        self.genre = ttk.Combobox(gauche, values=GENRES, state="readonly", width=24)
        self.age = ttk.Combobox(gauche, values=TRANCHES_AGE, state="readonly", width=24)
        self.pays = ttk.Combobox(gauche, values=PAYS, state="readonly", width=24)
        self.region = ttk.Combobox(gauche, width=24)
        self.nb_visiteurs = ttk.Spinbox(gauche, from_=1, to=50, width=6, font=TEXTE)
        self.nb_visiteurs.set(1)

        self.pays.bind("<<ComboboxSelected>>", self.maj_regions)
        self.pays.set("France")
        self.maj_regions()

        lignes = [("Nom *", self.nom), ("Prénom *", self.prenom),
                  ("Genre *", self.genre), ("Tranche d'âge *", self.age),
                  ("Pays *", self.pays), ("Région", self.region),
                  ("Nombre de personnes\ndans le groupe *", self.nb_visiteurs)]
        for i, (texte, widget) in enumerate(lignes, start=1):
            self.ligne(gauche, i, texte, widget)

        # --- Colonne de droite : la visite ----------------------------------
        droite = carte(corps, padx=24, pady=16)
        droite.grid(row=0, column=1, sticky="n", padx=12)
        self.titre_section(droite, "Votre visite")

        # Date de la visite : jour / mois / année (aujourd'hui par défaut)
        aujourdhui = date.today()
        cadre_date = tk.Frame(droite, bg=CREME)
        self.jour = ttk.Spinbox(cadre_date, from_=1, to=31, width=4, font=TEXTE)
        self.jour.set(aujourdhui.day)
        self.mois = ttk.Combobox(cadre_date, values=MOIS, state="readonly", width=10)
        self.mois.current(aujourdhui.month - 1)
        self.annee = ttk.Spinbox(cadre_date, from_=2020, to=aujourdhui.year, width=6,
                                 font=TEXTE)
        self.annee.set(aujourdhui.year)
        for w in (self.jour, self.mois, self.annee):
            w.pack(side="left", padx=(0, 6))
        self.ligne(droite, 1, "Date de la visite *", cadre_date)

        # Les trois notes de 1 à 5
        self.note_proprete = NoteEtoiles(droite)
        self.note_infra = NoteEtoiles(droite)
        self.note_globale = NoteEtoiles(droite)
        self.ligne(droite, 2, "Propreté du zoo *", self.note_proprete)
        self.ligne(droite, 3, "Qualité des\ninfrastructures *", self.note_infra)
        self.ligne(droite, 4, "Note globale *", self.note_globale)

        tk.Label(droite, bg=CREME, fg=NOIR, font=PETIT, justify="left",
                 text="Vos réponses sont anonymes : votre nom n'est pas conservé\n"
                      "dans nos statistiques de fréquentation et de satisfaction."
                 ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(18, 0))

        # --- Boutons ---------------------------------------------------------
        bas = tk.Frame(self, bg=BEIGE)
        bas.pack(side="bottom", fill="x", padx=30, pady=20)
        Bouton(bas, "←  Retour", app.afficher_accueil, couleur=BEIGE_FONCE).pack(side="left")
        Bouton(bas, "Valider  ✔", self.valider, police=(POLICE, 14, "bold")).pack(side="right")

        self.nom.focus_set()

    # ------------------------------------------------------------------------
    def titre_section(self, parent, texte):
        tk.Label(parent, text=texte, font=GRAS, bg=CREME, fg=NOIR).grid(
            row=0, column=0, columnspan=2, sticky="w")
        tk.Frame(parent, bg=VERT_CLAIR, height=2).grid(
            row=0, column=0, columnspan=2, sticky="sew", pady=(0, 0))

    def ligne(self, parent, rang, texte, widget):
        """Place une étiquette et son widget sur une ligne de la grille."""
        tk.Label(parent, text=texte, font=TEXTE, bg=CREME, fg=NOIR, justify="left",
                 anchor="w").grid(row=rang, column=0, sticky="w", pady=7, padx=(0, 16))
        widget.grid(row=rang, column=1, sticky="w", pady=7)

    def maj_regions(self, event=None):
        """Met à jour la liste des régions quand le pays change."""
        regions = REGIONS.get(self.pays.get(), [])
        self.region.config(values=regions)
        self.region.set("")
        # Pays sans liste : le visiteur tape lui-même sa région
        self.region.config(state="readonly" if regions else "normal")

    def lire_date(self):
        """Renvoie la date saisie (objet date) ou None si elle est invalide."""
        try:
            d = date(int(self.annee.get()), self.mois.current() + 1, int(self.jour.get()))
        except ValueError:
            return None
        return d

    # ------------------------------------------------------------------------
    def valider(self):
        """Vérifie le formulaire, enregistre l'avis puis ouvre la liste des animaux."""
        erreurs = []
        nom = self.nom.get().strip()
        prenom = self.prenom.get().strip()
        if not nom_valide(nom):
            erreurs.append("Le nom est obligatoire (lettres uniquement).")
        if not nom_valide(prenom):
            erreurs.append("Le prénom est obligatoire (lettres uniquement).")
        if not self.genre.get():
            erreurs.append("Veuillez choisir un genre.")
        if not self.age.get():
            erreurs.append("Veuillez choisir une tranche d'âge.")
        if not self.pays.get():
            erreurs.append("Veuillez choisir un pays.")

        nb = self.nb_visiteurs.get().strip()
        if not nb.isdigit() or not 1 <= int(nb) <= 50:
            erreurs.append("Le nombre de personnes doit être un entier entre 1 et 50.")

        d = self.lire_date()
        if d is None:
            erreurs.append("La date de la visite n'existe pas.")
        elif d > date.today():
            erreurs.append("La date de la visite ne peut pas être dans le futur.")

        for nom_note, note in [("propreté", self.note_proprete),
                               ("infrastructures", self.note_infra),
                               ("note globale", self.note_globale)]:
            if note.note == 0:
                erreurs.append(f"Veuillez donner une note pour : {nom_note}.")

        if erreurs:
            messagebox.showwarning("Formulaire incomplet", "\n".join(erreurs), parent=self)
            return

        enregistrer_avis({
            "genre": self.genre.get(),
            "tranche_age": self.age.get(),
            "pays": self.pays.get(),
            "region": self.region.get().strip() or "Non précisée",
            "nombre_visiteurs": int(nb),
            "note_proprete": self.note_proprete.note,
            "note_infrastructures": self.note_infra.note,
            "note_globale": self.note_globale.note,
            "date_visite": d.isoformat(),          # format AAAA-MM-JJ
        })
        messagebox.showinfo("Merci !", f"Merci {prenom} pour votre avis !\n\n"
                            "Découvrez maintenant nos animaux : vous pouvez "
                            "parrainer celui de votre choix.", parent=self)
        self.app.afficher_animaux()
