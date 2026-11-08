

import tkinter as tk
from tkinter import messagebox

import mails
from donnees import NOM_DU_ZOO, email_valide, enregistrer_don
from style import (BEIGE, CREME, NOIR, VERT_CLAIR, VERT_PALE, BEIGE_FONCE,
                   SOUS_TITRE, TEXTE, GRAS, POLICE,
                   Bouton, carte, champ_texte)


class FenetreDon(tk.Frame):

    def __init__(self, app):
        super().__init__(app, bg=BEIGE)
        self.app = app

        entete = tk.Frame(self, bg=VERT_PALE)
        entete.pack(fill="x")
        tk.Frame(entete, bg=VERT_CLAIR, height=8).pack(fill="x")
        ligne = tk.Frame(entete, bg=VERT_PALE)
        ligne.pack(fill="x", padx=20, pady=10)
        Bouton(ligne, "Retour", app.afficher_accueil, couleur=BEIGE_FONCE).pack(side="left")
        tk.Label(ligne, text="Faire un don", font=SOUS_TITRE, bg=VERT_PALE,
                 fg=NOIR).pack(side="left", padx=20)

        boite = carte(self, padx=40, pady=30)
        boite.place(relx=0.5, rely=0.55, anchor="center")

        tk.Label(boite, text="Soutenez le zoo avec un don libre", font=SOUS_TITRE, bg=CREME,
                 fg=NOIR).pack(anchor="w")
        tk.Label(boite, font=TEXTE, bg=CREME, fg=NOIR, justify="left",
                 text=f"Le {NOM_DU_ZOO} vit grâce à ses visiteurs. Votre don, du montant de "
                      f"votre choix, sert à :").pack(anchor="w", pady=(12, 6))
        tk.Label(boite, font=TEXTE, bg=CREME, fg=NOIR, justify="left",
                 text="•  nourrir et soigner nos animaux (vétérinaires, médicaments)\n"
                      "•  agrandir et améliorer les enclos pour leur bien-être\n"
                      "•  protéger les espèces menacées, comme le tigre de Sumatra ou l'axolotl\n"
                      "•  accueillir les écoles pour faire découvrir la nature aux enfants"
                 ).pack(anchor="w")
        tk.Label(boite, text="Chaque euro compte. Merci !", font=GRAS, bg=CREME,
                 fg=NOIR).pack(anchor="w", pady=(10, 0))

        formulaire = tk.Frame(boite, bg=CREME)
        formulaire.pack(anchor="w", pady=(22, 0))
        self.montant = champ_texte(formulaire, largeur=10)
        self.email = champ_texte(formulaire, largeur=32)
        tk.Label(formulaire, text="Montant du don (€) *", font=TEXTE, bg=CREME, fg=NOIR).grid(
            row=0, column=0, sticky="w", pady=6, padx=(0, 14))
        self.montant.grid(row=0, column=1, sticky="w", pady=6)
        tk.Label(formulaire, text="Votre adresse e-mail *", font=TEXTE, bg=CREME, fg=NOIR).grid(
            row=1, column=0, sticky="w", pady=6, padx=(0, 14))
        self.email.grid(row=1, column=1, sticky="w", pady=6)

        Bouton(boite, "Faire mon don", self.valider,
               police=(POLICE, 14, "bold")).pack(anchor="e", pady=(20, 0))
        self.montant.focus_set()

    def valider(self):
        texte = self.montant.get().strip().replace(",", ".")
        try:
            montant = float(texte)
        except ValueError:
            montant = 0
        if not 0 < montant <= 100000:
            messagebox.showwarning("Don", "Le montant doit être un nombre entre 0 et 100 000 €.",
                                   parent=self)
            return
        email = self.email.get().strip().lower()
        if not email_valide(email):
            messagebox.showwarning("Don", "L'adresse e-mail n'est pas valide.", parent=self)
            return

        enregistrer_don(round(montant, 2), email)
        if mails.mail_don(montant, email):
            fin = f"Un mail de remerciement a été envoyé à {email}."
        else:
            fin = "Le mail de remerciement n'a pas pu être envoyé pour le moment."
        texte_montant = f"{montant:.2f}".replace(".", ",")
        messagebox.showinfo("Merci !", f"Merci pour votre don de {texte_montant} € !\n\n{fin}",
                            parent=self)
        self.app.afficher_accueil()
