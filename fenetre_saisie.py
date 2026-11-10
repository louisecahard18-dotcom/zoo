

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from donnees import GENRES, TRANCHES_AGE, PAYS, enregistrer_avis
from style import (BEIGE, CREME, NOIR, VERT_CLAIR, VERT_PALE, BEIGE_FONCE,
                   SOUS_TITRE, TEXTE, GRAS, PETIT, POLICE,
                   Bouton, carte, champ_texte, NoteEtoiles, Calendrier)


def nom_valide(texte):
   
    return texte != "" and all(c.isalpha() or c in " -'" for c in texte)


class FenetreSaisie(tk.Frame):
    

    def __init__(self, app):
        super().__init__(app, bg=BEIGE)
        self.app = app

       
        entete = tk.Frame(self, bg=VERT_PALE)
        entete.pack(fill="x")
        tk.Frame(entete, bg=VERT_CLAIR, height=8).pack(fill="x")
        tk.Label(entete, text="Votre avis nous intéresse", font=SOUS_TITRE,
                 bg=VERT_PALE, fg=NOIR).pack(pady=(12, 0))
        tk.Label(entete, text="Les questions marquées * sont obligatoires.",
                 font=TEXTE, bg=VERT_PALE, fg=NOIR).pack(pady=(2, 12))

        corps = tk.Frame(self, bg=BEIGE)
        corps.pack(expand=True, pady=10)

        
        gauche = carte(corps, padx=24, pady=16)
        gauche.grid(row=0, column=0, sticky="n", padx=12)
        self.titre_section(gauche, "Vous et votre groupe")

        self.nom = champ_texte(gauche)
        self.prenom = champ_texte(gauche)
        self.genre = ttk.Combobox(gauche, values=GENRES, state="readonly", width=24)
        self.age = ttk.Combobox(gauche, values=TRANCHES_AGE, state="readonly", width=24)
        self.pays = ttk.Combobox(gauche, values=PAYS, state="readonly", width=24)
        self.nb_visiteurs = ttk.Spinbox(gauche, from_=1, to=50, width=6, font=TEXTE)
        self.nb_visiteurs.set(1)

        self.pays.set("France")

        lignes = [("Nom *", self.nom), ("Prénom *", self.prenom),
                  ("Genre *", self.genre), ("Tranche d'âge *", self.age),
                  ("Pays *", self.pays),
                  ("Nombre de personnes\ndans le groupe *", self.nb_visiteurs)]
        for i, (texte, widget) in enumerate(lignes, start=1):
            self.ligne(gauche, i, texte, widget)


        droite = carte(corps, padx=24, pady=16)
        droite.grid(row=0, column=1, sticky="n", padx=12)
        self.titre_section(droite, "Votre visite")

        
        self.calendrier = Calendrier(droite)
        self.ligne(droite, 1, "Date de la visite *", self.calendrier)

      
        self.note_proprete = NoteEtoiles(droite)
        self.note_infra = NoteEtoiles(droite)
        self.note_globale = NoteEtoiles(droite)
        self.ligne(droite, 2, "Propreté du zoo *", self.note_proprete)
        self.ligne(droite, 3, "Qualité des\ninfrastructures *", self.note_infra)
        self.ligne(droite, 4, "Note globale *", self.note_globale)

        tk.Label(droite, bg=CREME, fg=NOIR, font=PETIT, justify="left",
                 text="Vos réponses sont anonymes"
                 ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(18, 0))

       
        bas = tk.Frame(self, bg=BEIGE)
        bas.pack(side="bottom", fill="x", padx=30, pady=20)
        Bouton(bas, " Retour", app.afficher_accueil, couleur=BEIGE_FONCE).pack(side="left")
        Bouton(bas, "Valider  ", self.valider, police=(POLICE, 14, "bold")).pack(side="right")

        self.nom.focus_set()


    def titre_section(self, parent, texte):
        tk.Label(parent, text=texte, font=GRAS, bg=CREME, fg=NOIR).grid(
            row=0, column=0, columnspan=2, sticky="w")
        tk.Frame(parent, bg=VERT_CLAIR, height=2).grid(
            row=0, column=0, columnspan=2, sticky="sew", pady=(0, 0))

    def ligne(self, parent, rang, texte, widget):
      
        tk.Label(parent, text=texte, font=TEXTE, bg=CREME, fg=NOIR, justify="left",
                 anchor="w").grid(row=rang, column=0, sticky="w", pady=7, padx=(0, 16))
        widget.grid(row=rang, column=1, sticky="w", pady=7)

 
    def valider(self):
      
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
            erreurs.append("Le nombre de personnes doit être entre 1 et 50.")

        d = self.calendrier.date
        if d > date.today():
            erreurs.append("La date de la visite est incorrecte.")

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
            "nombre_visiteurs": int(nb),
            "note_proprete": self.note_proprete.note,
            "note_infrastructures": self.note_infra.note,
            "note_globale": self.note_globale.note,
            "date_visite": d.isoformat(),          
        })
        messagebox.showinfo("Merci !", f"Merci {prenom} pour votre avis !\n\n"
                            "Découvrez maintenant nos animaux : vous pouvez "
                            "parrainer celui de votre choix.", parent=self)
        self.app.afficher_animaux()
