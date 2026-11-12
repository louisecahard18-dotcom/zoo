

import tkinter as tk
from tkinter import ttk, messagebox

import mails
from sons import effet_musique
from donnees import MONTANT_PARRAINAGE, email_valide, parrains, enregistrer_parrainage
from style import (BEIGE, CREME, NOIR, VERT_CLAIR, VERT_PALE, BEIGE_FONCE,
                   SOUS_TITRE, TEXTE, GRAS, POLICE,
                   Bouton, carte, champ_texte, vignette_animal)


class FenetreParrainage(tk.Frame):

    def __init__(self, app, animal):
        super().__init__(app, bg=BEIGE)
        self.app = app
        self.animal = animal

        entete = tk.Frame(self, bg=VERT_PALE)
        entete.pack(fill="x")
        tk.Frame(entete, bg=VERT_CLAIR, height=8).pack(fill="x")
        ligne = tk.Frame(entete, bg=VERT_PALE)
        ligne.pack(fill="x", padx=20, pady=10)
        Bouton(ligne, "Retour à la fiche", lambda: app.afficher_fiche(animal),
               couleur=BEIGE_FONCE).pack(side="left")
        tk.Label(ligne, text=f"Parrainer {animal.nom}", font=SOUS_TITRE, bg=VERT_PALE,
                 fg=NOIR).pack(side="left", padx=20)

        boite = carte(self, padx=36, pady=28)
        boite.place(relx=0.5, rely=0.55, anchor="center")

        haut = tk.Frame(boite, bg=CREME)
        haut.pack(fill="x")
        vignette_animal(haut, animal).pack(side="left")
        texte = tk.Frame(haut, bg=CREME)
        texte.pack(side="left", padx=(20, 0))
        tk.Label(texte, text=f"{MONTANT_PARRAINAGE} € par mois", font=SOUS_TITRE, bg=CREME,
                 fg=NOIR).pack(anchor="w")
        tk.Label(texte, font=TEXTE, bg=CREME, fg=NOIR, justify="left",
                 text="Renouvelé automatiquement chaque mois.\n"
                      "Vous pouvez arrêter quand vous voulez.").pack(anchor="w", pady=(4, 0))

        tk.Label(boite, text="Ce que vous recevez :", font=GRAS, bg=CREME,
                 fg=NOIR).pack(anchor="w", pady=(20, 4))
        tk.Label(boite, font=TEXTE, bg=CREME, fg=NOIR, justify="left",
                 text=f"•  un mail de remerciement avec 3 photos exclusives de {animal.nom}\n"
                      f"•  des nouvelles par mail si son état de santé change\n"
                      f"•  un mail en cas de naissance dans sa famille").pack(anchor="w")

        formulaire = tk.Frame(boite, bg=CREME)
        formulaire.pack(anchor="w", pady=(20, 0))
        tk.Label(formulaire, text="Votre adresse e-mail *", font=TEXTE, bg=CREME,
                 fg=NOIR).grid(row=0, column=0, sticky="w", padx=(0, 14))
        self.email = champ_texte(formulaire, largeur=32)
        self.email.grid(row=0, column=1)
        self.accepte = tk.BooleanVar()
        ttk.Checkbutton(formulaire, variable=self.accepte,
                        text=f"J'accepte que {MONTANT_PARRAINAGE} € soient prélevés "
                             f"automatiquement chaque mois").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(12, 0))

        Bouton(boite, "Valider le parrainage", self.valider,
               police=(POLICE, 14, "bold")).pack(anchor="e", pady=(22, 0))
        self.email.focus_set()

    def valider(self):
        email = self.email.get().strip().lower()
        if not email_valide(email):
            messagebox.showwarning("Parrainage", "L'adresse e-mail n'est pas valide.",
                                   parent=self)
            return
        if not self.accepte.get():
            messagebox.showwarning("Parrainage", "Merci de cocher la case pour accepter "
                                   "le renouvellement automatique.", parent=self)
            return
        if email in parrains(self.animal):
            messagebox.showinfo("Parrainage", f"Vous parrainez déjà {self.animal.nom} !",
                                parent=self)
            return

        enregistrer_parrainage(self.animal, email)
        effet_musique()
        if mails.mail_parrainage(self.animal, email):
            fin = f"Un mail de remerciement avec 3 photos exclusives a été envoyé à {email}."
        else:
            fin = "Le mail de remerciement n'a pas pu être envoyé pour le moment."
        messagebox.showinfo("Merci !", f"Vous parrainez maintenant {self.animal.nom} !\n\n{fin}",
                            parent=self)
        self.app.afficher_fiche(self.animal)
