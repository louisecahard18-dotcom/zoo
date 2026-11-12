

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import mails
from donnees import (verifier_identifiants, lire_csv, parrains, CLASSIFICATIONS, ETATS_SANTE,
                     FICHIER_SATISFACTION, FICHIER_DONS)
from statistiques import GRAPHIQUES, graphe_sante, classement_parrainages
from style import (BEIGE, CREME, NOIR, VERT_CLAIR, VERT_PALE, BEIGE_FONCE,
                   SOUS_TITRE, TEXTE, GRAS, PETIT, PETIT_GRAS, POLICE,
                   Bouton, carte, champ_texte, vignette_animal)






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


def vider(cadre):
    for widget in cadre.winfo_children():
        widget.destroy()


class FenetreAdmin(tk.Frame):

    def __init__(self, app, utilisateur):
        super().__init__(app, bg=BEIGE)
        self.app = app
        self.zoo = app.zoo
        self.animal = None
        self.graphe_choisi = GRAPHIQUES[0][1]

        entete = tk.Frame(self, bg=VERT_PALE)
        entete.pack(fill="x")
        tk.Frame(entete, bg=VERT_CLAIR, height=8).pack(fill="x")
        ligne = tk.Frame(entete, bg=VERT_PALE)
        ligne.pack(fill="x", padx=20, pady=10)
        tk.Label(ligne, text="Interface administrateur", font=SOUS_TITRE,
                 bg=VERT_PALE, fg=NOIR).pack(side="left")
        Bouton(ligne, "Déconnexion", app.afficher_accueil, couleur=BEIGE_FONCE).pack(side="right")
        tk.Label(ligne, text=f"Connecté : {utilisateur}", font=TEXTE, bg=VERT_PALE,
                 fg=NOIR).pack(side="right", padx=16)

        self.onglets = ttk.Notebook(self)
        self.onglets.pack(fill="both", expand=True, padx=14, pady=10)
        self.onglet_fiches = tk.Frame(self.onglets, bg=BEIGE)
        self.onglet_stat_animaux = tk.Frame(self.onglets, bg=BEIGE)
        self.onglet_stat_visiteurs = tk.Frame(self.onglets, bg=BEIGE)
        self.onglet_mails = tk.Frame(self.onglets, bg=BEIGE)
        self.onglets.add(self.onglet_fiches, text="Fiches des animaux")
        self.onglets.add(self.onglet_stat_animaux, text="Statistiques des animaux")
        self.onglets.add(self.onglet_stat_visiteurs, text="Statistiques des visiteurs")
        self.onglets.add(self.onglet_mails, text="Historique des mails")
        self.onglets.bind("<<NotebookTabChanged>>", self.changement_onglet)

        self.construire_fiches()
        self.selectionner(self.zoo.animaux[0])

    def changement_onglet(self, event):
        # on reconstruit l'onglet ouvert, car les données ont pu changer
        onglet = self.onglets.nametowidget(self.onglets.select())
        if onglet is self.onglet_stat_animaux:
            self.construire_stats_animaux()
        elif onglet is self.onglet_stat_visiteurs:
            self.construire_stats_visiteurs()
        elif onglet is self.onglet_mails:
            self.construire_mails()

    # ---------------- Onglet 1 : fiches des animaux ----------------

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

        droite = carte(self.onglet_fiches, padx=20, pady=14)
        droite.pack(side="left", fill="both", expand=True, padx=(6, 10), pady=10)

        haut = tk.Frame(droite, bg=CREME)
        haut.pack(fill="x")
        self.cadre_photo = tk.Frame(haut, bg=CREME)
        self.cadre_photo.pack(side="left")
        self.titre_fiche = tk.Label(haut, font=SOUS_TITRE, bg=CREME, fg=NOIR)
        self.titre_fiche.pack(side="left", padx=18, anchor="n")

        tk.Frame(droite, bg=VERT_CLAIR, height=2).pack(fill="x", pady=12)

        formulaire = tk.Frame(droite, bg=CREME)
        formulaire.pack(fill="x")
        self.champ_nom = champ_texte(formulaire, largeur=22)
        self.champ_espece = champ_texte(formulaire, largeur=22)
        self.champ_age = ttk.Spinbox(formulaire, from_=0, to=200, width=6, font=TEXTE)
        self.champ_classe = ttk.Combobox(formulaire, values=CLASSIFICATIONS, state="readonly",
                                         width=14)
        self.champ_nombre = ttk.Spinbox(formulaire, from_=1, to=999, width=6, font=TEXTE)
        self.champ_sante = ttk.Combobox(formulaire, values=ETATS_SANTE, state="readonly",
                                        width=18)
        champs = [("Nom", self.champ_nom, 0, 0), ("Espèce", self.champ_espece, 0, 2),
                  ("Âge (ans)", self.champ_age, 1, 0),
                  ("Classification", self.champ_classe, 1, 2),
                  ("Nombre de bêtes", self.champ_nombre, 2, 0),
                  ("État de santé", self.champ_sante, 2, 2)]
        for texte, widget, rang, col in champs:
            tk.Label(formulaire, text=texte, font=TEXTE, bg=CREME, fg=NOIR).grid(
                row=rang, column=col, sticky="w", pady=7, padx=(0 if col == 0 else 30, 10))
            widget.grid(row=rang, column=col + 1, sticky="w", pady=7)

        cadre_naissance = tk.Frame(droite, bg=VERT_PALE, padx=12, pady=8)
        cadre_naissance.pack(fill="x", pady=(14, 0))
        self.naissance = tk.BooleanVar()
        tk.Checkbutton(cadre_naissance, text="Signaler une naissance", variable=self.naissance,
                       font=GRAS, bg=VERT_PALE, fg=NOIR, activebackground=VERT_PALE,
                       selectcolor=CREME).pack(side="left")
        tk.Label(cadre_naissance, text="Nombre de bébés :", font=TEXTE, bg=VERT_PALE,
                 fg=NOIR).pack(side="left", padx=(20, 6))
        self.nb_bebes = ttk.Spinbox(cadre_naissance, from_=1, to=30, width=4, font=TEXTE)
        self.nb_bebes.pack(side="left")

        # la liste des e-mails des parrains de l'animal
        self.info_parrains = tk.Label(droite, font=PETIT_GRAS, bg=CREME, fg=NOIR)
        self.info_parrains.pack(anchor="w", pady=(10, 2))
        cadre_parrains = tk.Frame(droite, bg=CREME)
        cadre_parrains.pack(anchor="w")
        barre_parrains = ttk.Scrollbar(cadre_parrains, orient="vertical")
        self.liste_parrains = tk.Listbox(cadre_parrains, width=44, height=5, font=PETIT,
                                         bg=CREME, fg=NOIR, relief="flat",
                                         highlightthickness=1, highlightbackground=BEIGE_FONCE,
                                         activestyle="none", yscrollcommand=barre_parrains.set)
        barre_parrains.config(command=self.liste_parrains.yview)
        self.liste_parrains.pack(side="left")
        barre_parrains.pack(side="left", fill="y")

        boutons = tk.Frame(droite, bg=CREME)
        boutons.pack(side="bottom", fill="x")
        Bouton(boutons, "Enregistrer", self.enregistrer).pack(side="right")
        Bouton(boutons, "Annuler les changements", lambda: self.selectionner(self.animal),
               couleur=BEIGE_FONCE).pack(side="right", padx=10)

    def rafraichir_liste(self):
        self.liste.delete(0, "end")
        for i, a in enumerate(self.zoo.animaux):
            self.liste.insert("end", f" {a.nom}  —  {a.espece}")
            if a.sante != "Bonne santé":
                self.liste.itemconfig(i, bg="#F4DDBF")
        i = self.zoo.animaux.index(self.animal)
        self.liste.selection_set(i)
        self.liste.see(i)

    def clic_liste(self, event):
        selection = self.liste.curselection()
        if selection:
            self.selectionner(self.zoo.animaux[selection[0]])

    def selectionner(self, animal):
        self.animal = animal
        vider(self.cadre_photo)
        vignette_animal(self.cadre_photo, animal).pack()
        self.titre_fiche.config(text=f"{animal.nom}  (fiche n°{animal.id})")

        self.champ_nom.delete(0, "end")
        self.champ_nom.insert(0, animal.nom)
        self.champ_espece.delete(0, "end")
        self.champ_espece.insert(0, animal.espece)
        self.champ_age.set(animal.age)
        self.champ_classe.set(animal.classification)
        self.champ_nombre.set(animal.nombre)
        self.champ_sante.set(animal.sante)
        self.naissance.set(False)
        self.nb_bebes.set(1)

        emails = parrains(animal)
        self.info_parrains.config(text=f"Parrains de {animal.nom} ({len(emails)}) :")
        self.liste_parrains.delete(0, "end")
        for email in emails:
            self.liste_parrains.insert("end", email)
        self.rafraichir_liste()

    def enregistrer(self):
        animal = self.animal
        nom = self.champ_nom.get().strip()
        espece = self.champ_espece.get().strip()
        age = self.champ_age.get().strip()
        nombre = self.champ_nombre.get().strip()
        bebes = self.nb_bebes.get().strip()

        if nom == "" or espece == "":
            messagebox.showerror("Erreur", "Le nom et l'espèce sont obligatoires.", parent=self)
            return
        if self.zoo.nom_existe(nom, sauf=animal):
            messagebox.showerror("Erreur", f"Un autre animal s'appelle déjà {nom}.", parent=self)
            return
        if not age.isdigit() or not nombre.isdigit() or not bebes.isdigit():
            messagebox.showerror("Erreur", "L'âge, le nombre de bêtes et le nombre de bébés "
                                 "doivent être des nombres entiers.", parent=self)
            return

        ancien_etat = animal.sante
        animal.nom = nom
        animal.espece = espece
        animal.age = int(age)
        animal.classification = self.champ_classe.get()
        animal.nombre = int(nombre)
        animal.sante = self.champ_sante.get()
        if self.naissance.get():
            animal.nombre = animal.nombre + int(bebes)
        self.zoo.sauvegarder()

        messages = ["La fiche a été enregistrée."]
        if animal.sante != ancien_etat:
            envoyes, total = mails.mail_sante(animal, ancien_etat)
            messages.append(f"Changement de santé : mail envoyé à {envoyes} parrain(s) sur {total}.")
        if self.naissance.get():
            envoyes, total = mails.mail_naissance(animal, int(bebes))
            messages.append(f"Naissance : mail envoyé à {envoyes} parrain(s) sur {total}.")
        messagebox.showinfo("Fiche enregistrée", "\n".join(messages), parent=self)
        self.selectionner(animal)

    # ---------------- Outils pour les statistiques ----------------

    def case_chiffre(self, parent, valeur, titre):
        case = carte(parent, padx=12, pady=6)
        case.pack(side="left", padx=(0, 8), fill="x", expand=True)
        tk.Label(case, text=valeur, font=(POLICE, 16, "bold"), bg=CREME, fg=NOIR).pack()
        tk.Label(case, text=titre, font=PETIT, bg=CREME, fg=NOIR).pack()

    def dessiner(self, parent, fonction, *arguments):
        figure = Figure(figsize=(6, 4), dpi=100, facecolor=CREME)
        ax = figure.add_subplot(111)
        if fonction(ax, *arguments) is False:
            ax.axis("off")
            ax.text(0.5, 0.5, "Pas encore de données pour ce graphique.", ha="center",
                    va="center", fontsize=12)
        figure.tight_layout()
        dessin = FigureCanvasTkAgg(figure, master=parent)
        dessin.draw()
        dessin.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)

    # ---------------- Onglet 2 : statistiques des animaux ----------------

    def construire_stats_animaux(self):
        onglet = self.onglet_stat_animaux
        vider(onglet)
        animaux = self.zoo.animaux
        total = len(animaux)
        malades = sum(1 for a in animaux if a.sante == "Malade")
        gestantes = sum(1 for a in animaux if a.sante == "Gestante")
        classement = classement_parrainages(animaux)
        nb_parrainages = sum(nb for nom, nb, somme in classement)
        argent = sum(somme for nom, nb, somme in classement)

        chiffres = tk.Frame(onglet, bg=BEIGE)
        chiffres.pack(fill="x", padx=10, pady=(10, 0))
        self.case_chiffre(chiffres, f"{malades} / {total}  ({100 * malades / total:.0f} %)",
                          "Animaux malades")
        self.case_chiffre(chiffres, f"{gestantes} / {total}  ({100 * gestantes / total:.0f} %)",
                          "Femelles gestantes")
        self.case_chiffre(chiffres, str(nb_parrainages), "Parrainages en cours")
        self.case_chiffre(chiffres, f"{argent:.0f} €", "Total versé par les parrains")

        # on place d'abord le classement à droite, puis le graphique prend le reste
        corps = tk.Frame(onglet, bg=BEIGE)
        corps.pack(fill="both", expand=True, padx=10, pady=10)
        droite = carte(corps, padx=14, pady=10)
        droite.pack(side="right", fill="y", padx=(10, 0))
        gauche = carte(corps)
        gauche.pack(side="left", fill="both", expand=True)
        self.dessiner(gauche, graphe_sante, animaux)

        tk.Label(droite, text="Animaux les plus parrainés", font=GRAS, bg=CREME,
                 fg=NOIR).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))
        for col, titre in enumerate(["N°", "Animal", "Parrains", "Total versé"]):
            tk.Label(droite, text=titre, font=PETIT_GRAS, bg=CREME, fg=NOIR).grid(
                row=1, column=col, sticky="w", padx=6)
        for i, (nom, nb, somme) in enumerate(classement[:12]):
            for col, valeur in enumerate([i + 1, nom, nb, f"{somme:.0f} €"]):
                tk.Label(droite, text=valeur, font=TEXTE, bg=CREME, fg=NOIR).grid(
                    row=i + 2, column=col, sticky="w", padx=6, pady=2)
        if not classement:
            tk.Label(droite, text="Aucun parrainage pour l'instant.", font=TEXTE, bg=CREME,
                     fg=NOIR).grid(row=2, column=0, columnspan=4, sticky="w")

    # ---------------- Onglet 3 : statistiques des visiteurs ----------------

    def construire_stats_visiteurs(self):
        onglet = self.onglet_stat_visiteurs
        vider(onglet)
        notes = lire_csv(FICHIER_SATISFACTION)
        dons = lire_csv(FICHIER_DONS)
        if notes:
            moyenne = f"{sum(int(n['note_globale']) for n in notes) / len(notes):.2f} / 5"
        else:
            moyenne = "-"
        total_dons = sum(float(d["montant"]) for d in dons)

        chiffres = tk.Frame(onglet, bg=BEIGE)
        chiffres.pack(fill="x", padx=10, pady=(10, 0))
        self.case_chiffre(chiffres, str(len(notes)), "Avis reçus")
        self.case_chiffre(chiffres, moyenne, "Note globale moyenne")
        self.case_chiffre(chiffres, str(len(dons)), "Dons libres")
        self.case_chiffre(chiffres, f"{total_dons:.0f} €", "Montant des dons")

        corps = tk.Frame(onglet, bg=BEIGE)
        corps.pack(fill="both", expand=True, padx=10, pady=10)
        menu = carte(corps, padx=10, pady=10)
        menu.pack(side="left", fill="y")
        tk.Label(menu, text="Graphiques", font=GRAS, bg=CREME, fg=NOIR).pack(anchor="w",
                                                                             pady=(0, 8))
        for titre, fonction in GRAPHIQUES:
            Bouton(menu, titre, lambda f=fonction: self.choisir_graphe(f), couleur=CREME,
                   police=PETIT, width=16).pack(fill="x", pady=3)

        zone = carte(corps)
        zone.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.dessiner(zone, self.graphe_choisi)

    def choisir_graphe(self, fonction):
        self.graphe_choisi = fonction
        self.construire_stats_visiteurs()

    # ---------------- Onglet 4 : historique des mails ----------------

    def construire_mails(self):
        vider(self.onglet_mails)
        cadre = carte(self.onglet_mails, padx=12, pady=12)
        cadre.pack(fill="both", expand=True, padx=10, pady=10)
        if mails.ADRESSE_ZOO:
            info = f"Les mails sont envoyés depuis l'adresse {mails.ADRESSE_ZOO}."
        else:
            info = ("Les mails ne peuvent pas partir : il manque le fichier config_mail.py "
                    "(voir le fichier README).")
        tk.Label(cadre, text=info, font=PETIT_GRAS, bg=CREME, fg=NOIR).pack(anchor="w",
                                                                           pady=(0, 8))
        texte = tk.Text(cadre, font=("Courier", 10), bg=CREME, fg=NOIR, relief="flat",
                        wrap="word", padx=8, pady=6)
        barre = ttk.Scrollbar(cadre, orient="vertical", command=texte.yview)
        texte.config(yscrollcommand=barre.set)
        barre.pack(side="right", fill="y")
        texte.pack(fill="both", expand=True)
        texte.insert("1.0", mails.lire_historique() or "Aucun mail envoyé pour l'instant.")
        texte.config(state="disabled")
        texte.see("end")
