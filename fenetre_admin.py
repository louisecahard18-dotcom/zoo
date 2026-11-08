

import tkinter as tk
from tkinter import ttk
from donnees import (verifier_identifiants)


from style import (BEIGE, CREME, NOIR, VERT_CLAIR, VERT_PALE, BEIGE_FONCE,
                   SOUS_TITRE, TEXTE, GRAS, PETIT, PETIT_GRAS, POLICE,
                   Bouton, carte, champ_texte)






class FenetreConnexion(tk.Frame):
    

    def __init__(self, app):
        super().__init__(app, bg=BEIGE)
        self.app = app

        tk.Frame(self, bg=VERT_CLAIR, height=14).pack(fill="x")

        boite = carte(self, padx=40, pady=30)
        boite.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(boite, text="Espace administrateur", font=SOUS_TITRE, bg=CREME,
                 fg=NOIR).grid(row=0, column=0, columnspan=2, pady=(0, 4))
        tk.Label(boite, text="Réservé aux soigneurs et au personnel du zoo",
                 font=PETIT, bg=CREME, fg=NOIR).grid(row=1, column=0, columnspan=2,
                                                     pady=(0, 20))

        self.utilisateur = champ_texte(boite)
        self.mot_de_passe = champ_texte(boite, show="•")
        for rang, (texte, champ) in enumerate([("Utilisateur", self.utilisateur),
                                               ("Mot de passe", self.mot_de_passe)], start=2):
            tk.Label(boite, text=texte, font=TEXTE, bg=CREME, fg=NOIR).grid(
                row=rang, column=0, sticky="w", pady=6, padx=(0, 14))
            champ.grid(row=rang, column=1, pady=6)

        self.voir = tk.BooleanVar()
        ttk.Checkbutton(boite, text="Afficher le mot de passe", variable=self.voir,
                        command=self.basculer_mdp).grid(row=5, column=1, sticky="w")

        boutons = tk.Frame(boite, bg=CREME)
        boutons.grid(row=6, column=0, columnspan=2, pady=(22, 0), sticky="ew")
        Bouton(boutons, "←  Retour", app.afficher_accueil, couleur=BEIGE_FONCE).pack(side="left")
        self.bouton_connexion = Bouton(boutons, "Se connecter", self.connexion)
        self.bouton_connexion.pack(side="right")

        self.message = tk.Label(boite, text="", font=PETIT_GRAS, bg=CREME, fg=NOIR)
        self.message.grid(row=7, column=0, columnspan=2, pady=(12, 0))

     
        for champ in (self.utilisateur, self.mot_de_passe):
            champ.bind("<Return>", lambda e: self.connexion())
        self.utilisateur.focus_set()

    def basculer_mdp(self):
        self.mot_de_passe.config(show="" if self.voir.get() else "•")

    def connexion(self):
        utilisateur = self.utilisateur.get().strip().lower()
        if verifier_identifiants(utilisateur, self.mot_de_passe.get()):
            self.app.afficher_admin(utilisateur)
        else:
            self.mot_de_passe.delete(0, "end")
            self.message.config(text="Identifiant ou mot de passe incorrect.")
            
class fenetreAdmin(tk.Frame):
    
    def __init__(self,app,utilisateur):
        super().__init__(app,bg=BEIGE)
        self.app=app
        self.zoo=app.zoo
        self.animal=None
        self.animaux_affiche=[]
        
        entete = tk.Frame(self,bg=VERT_PALE)
        entete.pack(fill='x')
        tk.Frame(entete, bg=VERT_CLAIR, height=8).pack(fill="x")
        ligne = tk.Frame(entete, bg=VERT_PALE)
        ligne.pack(fill="x", padx=20, pady=10)
        tk.Label(ligne, text="Interface administrateur", font=SOUS_TITRE,
                 bg=VERT_PALE, fg=NOIR).pack(side="left")
        Bouton(ligne, "Déconnexion", self.deconnexion, couleur=BEIGE_FONCE).pack(side="right")
        tk.Label(ligne, text=f"Connecté : {utilisateur}", font=TEXTE, bg=VERT_PALE,
                 fg=NOIR).pack(side="right", padx=16)
        
        self.onglets=ttk.Notebook(self)
        self.onglet.pack(fill="both",expand=True, pdx=14, pdy=10)
        self.onglet_fiche=tk.Frame(self.onglet(),bg=BEIGE)
        self.onglet_statanimaux=tk.Frame(self.onglet(),bg=BEIGE)
        self.onglet_statvisiteur=tk.Frame(self.onglet(),bg=BEIGE)
        self.onglet_mails=tk.Frame(self.onglet(),bg=BEIGE)
        self.onglet.add(self.onglet_fiche, text="Fiche des animaux")
        self.onglet.add(self.onglet_statanimaux, text="Statistique des animaux")
        self.onglet.add(self.onglet_statvisiteur, text="Statstique sur les visiteurs")
        self.onglet.add(self.onglet_mails, text="Historique des mails envoyès aux parains")
        self.onglets.bind("<<NotebookTabChanged>>", self.changement_onglet)
        
        self.construire_fiches()
        self.construire_stats()
 

        self.rafraichir_liste()
        if self.animaux_affiches:
            self.selectionner(self.animaux_affiches[0])
            
def construire_fiches(self):
     
     gauche = carte(self.onglet_fiches, padx=10, pady=10)
     gauche.pack(side="left", fill="y", padx=(10, 6), pady=10)
     tk.Label(gauche, text="Choix de l'animal", font=GRAS, bg=CREME,
              fg=NOIR).pack(anchor="w")

     cadre_liste = tk.Frame(gauche, bg=CREME)
     cadre_liste.pack(fill="both", expand=True)
     barre = ttk.Scrollbar(cadre_liste, orient="vertical")
     self.liste = tk.Listbox(cadre_liste, width=34, font=TEXTE, bg=CREME, fg=NOIR,
                             selectbackground=VERT_CLAIR, selectforeground=NOIR,
                             activestyle="none", relief="flat", highlightthickness=0,
                             exportselection=False, yscrollcommand=barre.set)
     barre.config(command=self.liste.yview)
     barre.pack(side="right", fill="y")
     self.liste.pack(side="left", fill="both", expand=True)
     self.liste.bind("<<ListboxSelect>>", self.clic_liste)
     tk.Label(gauche, text="Fond orangé : animal qui n'est pas en bonne santé",
              font=PETIT, bg=CREME, fg=NOIR).pack(anchor="w", pady=(6, 0))
        




