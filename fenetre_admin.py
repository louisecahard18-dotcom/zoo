"""Fenêtres 6 et 7 : connexion administrateur et interface d'administration."""

import tkinter as tk
from tkinter import ttk, messagebox

import commandes
from donnees import (CLASSIFICATIONS, ETATS_SANTE, FICHIER_VISITEURS, FICHIER_SATISFACTION,
                     FICHIER_PARRAINAGES, lire_csv, lire_journal_mails,
                     verifier_identifiants)
from statistiques import GRAPHIQUES
from style import (BEIGE, CREME, NOIR, VERT, VERT_CLAIR, VERT_PALE, BEIGE_FONCE,
                   SOUS_TITRE, TEXTE, GRAS, PETIT, PETIT_GRAS, CONSOLE, POLICE,
                   Bouton, carte, champ_texte, vignette_animal)

# matplotlib sert à tracer les graphiques. S'il n'est pas installé,
# le reste de l'interface fonctionne quand même.
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB = True
except ImportError:
    MATPLOTLIB = False

ESSAIS_MAX = 3              # nombre d'essais avant blocage temporaire
DUREE_BLOCAGE = 30          # en secondes


# ============================================================================
# Fenêtre 6 : connexion
# ============================================================================
class FenetreConnexion(tk.Frame):
    """Demande l'identifiant, le mot de passe et, facultativement, un code commande."""

    def __init__(self, app):
        super().__init__(app, bg=BEIGE)
        self.app = app
        self.essais = 0

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
        self.code = champ_texte(boite)
        for rang, (texte, champ) in enumerate([("Utilisateur", self.utilisateur),
                                               ("Mot de passe", self.mot_de_passe),
                                               ("Code commande", self.code)], start=2):
            tk.Label(boite, text=texte, font=TEXTE, bg=CREME, fg=NOIR).grid(
                row=rang, column=0, sticky="w", pady=6, padx=(0, 14))
            champ.grid(row=rang, column=1, pady=6)

        self.voir = tk.BooleanVar()
        ttk.Checkbutton(boite, text="Afficher le mot de passe", variable=self.voir,
                        command=self.basculer_mdp).grid(row=5, column=1, sticky="w")
        tk.Label(boite, font=PETIT, bg=CREME, fg=NOIR, justify="left",
                 text="Code commande (facultatif) : exécuté dès la connexion,\n"
                      "ex. modifier/sante/Kiara/malade  —  tapez « aide » pour la liste."
                 ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(12, 0))

        boutons = tk.Frame(boite, bg=CREME)
        boutons.grid(row=7, column=0, columnspan=2, pady=(22, 0), sticky="ew")
        Bouton(boutons, "←  Retour", app.afficher_accueil, couleur=BEIGE_FONCE).pack(side="left")
        self.bouton_connexion = Bouton(boutons, "Se connecter", self.connexion)
        self.bouton_connexion.pack(side="right")

        self.message = tk.Label(boite, text="", font=PETIT_GRAS, bg=CREME, fg=NOIR)
        self.message.grid(row=8, column=0, columnspan=2, pady=(12, 0))

        # La touche Entrée valide le formulaire
        for champ in (self.utilisateur, self.mot_de_passe, self.code):
            champ.bind("<Return>", lambda e: self.connexion())
        self.utilisateur.focus_set()

    def basculer_mdp(self):
        self.mot_de_passe.config(show="" if self.voir.get() else "•")

    def connexion(self):
        if self.essais >= ESSAIS_MAX:
            return                                    # connexion bloquée
        utilisateur = self.utilisateur.get().strip().lower()
        if verifier_identifiants(utilisateur, self.mot_de_passe.get()):
            self.app.afficher_admin(utilisateur, self.code.get().strip())
            return

        self.essais += 1
        self.mot_de_passe.delete(0, "end")
        if self.essais < ESSAIS_MAX:
            self.message.config(text=f"Identifiants incorrects "
                                     f"({ESSAIS_MAX - self.essais} essai(s) restant(s)).")
        else:
            self.message.config(text=f"Trop d'essais : réessayez dans {DUREE_BLOCAGE} s.")
            self.after(DUREE_BLOCAGE * 1000, self.debloquer)

    def debloquer(self):
        self.essais = 0
        self.message.config(text="Vous pouvez réessayer.")


# ============================================================================
# Fenêtre 7 : interface d'administration
# ============================================================================
class FenetreAdmin(tk.Frame):
    """Modification des fiches animaux, codes commandes, statistiques et mails."""

    def __init__(self, app, utilisateur, code_initial=""):
        super().__init__(app, bg=BEIGE)
        self.app = app
        self.zoo = app.zoo
        self.animal = None                 # animal actuellement sélectionné
        self.animaux_affiches = []         # animaux visibles dans la liste (même ordre)
        self.historique = []               # codes commandes déjà tapés
        self.position_historique = 0

        # --- En-tête ---------------------------------------------------------
        entete = tk.Frame(self, bg=VERT_PALE)
        entete.pack(fill="x")
        tk.Frame(entete, bg=VERT_CLAIR, height=8).pack(fill="x")
        ligne = tk.Frame(entete, bg=VERT_PALE)
        ligne.pack(fill="x", padx=20, pady=10)
        tk.Label(ligne, text="Interface administrateur", font=SOUS_TITRE,
                 bg=VERT_PALE, fg=NOIR).pack(side="left")
        Bouton(ligne, "Déconnexion", self.deconnexion, couleur=BEIGE_FONCE).pack(side="right")
        tk.Label(ligne, text=f"Connecté : {utilisateur}", font=TEXTE, bg=VERT_PALE,
                 fg=NOIR).pack(side="right", padx=16)

        # --- Barre d'état (en bas) -------------------------------------------
        self.etat = tk.Label(self, text="Prêt.", font=PETIT, bg=BEIGE_FONCE, fg=NOIR,
                             anchor="w", padx=10)
        self.etat.pack(side="bottom", fill="x")

        # --- Onglets ---------------------------------------------------------
        self.onglets = ttk.Notebook(self)
        self.onglets.pack(fill="both", expand=True, padx=14, pady=10)
        self.onglet_fiches = tk.Frame(self.onglets, bg=BEIGE)
        self.onglet_console = tk.Frame(self.onglets, bg=BEIGE)
        self.onglet_stats = tk.Frame(self.onglets, bg=BEIGE)
        self.onglet_mails = tk.Frame(self.onglets, bg=BEIGE)
        self.onglets.add(self.onglet_fiches, text="Fiches animaux")
        self.onglets.add(self.onglet_console, text="Codes commandes")
        self.onglets.add(self.onglet_stats, text="Statistiques")
        self.onglets.add(self.onglet_mails, text="Mails envoyés")
        self.onglets.bind("<<NotebookTabChanged>>", self.changement_onglet)

        self.construire_fiches()
        self.construire_console()
        self.construire_stats()
        self.construire_mails()

        self.rafraichir_liste()
        if self.animaux_affiches:
            self.selectionner(self.animaux_affiches[0])

        # Code commande saisi sur la page de connexion
        if code_initial:
            self.onglets.select(self.onglet_console)
            self.executer_commande(code_initial)

    # ========================================================================
    # Onglet 1 : fiches animaux
    # ========================================================================
    def construire_fiches(self):
        # --- Liste des animaux (à gauche) ------------------------------------
        gauche = carte(self.onglet_fiches, padx=10, pady=10)
        gauche.pack(side="left", fill="y", padx=(10, 6), pady=10)
        tk.Label(gauche, text="Choix de l'animal", font=GRAS, bg=CREME,
                 fg=NOIR).pack(anchor="w")
        self.recherche = tk.StringVar()
        self.recherche.trace_add("write", lambda *a: self.rafraichir_liste())
        champ_texte(gauche, largeur=28, textvariable=self.recherche).pack(fill="x", pady=6)

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

        # --- Formulaire (à droite) -------------------------------------------
        self.droite = carte(self.onglet_fiches, padx=20, pady=14)
        self.droite.pack(side="left", fill="both", expand=True, padx=(6, 10), pady=10)

        haut = tk.Frame(self.droite, bg=CREME)
        haut.pack(fill="x")
        self.cadre_vignette = tk.Frame(haut, bg=CREME)
        self.cadre_vignette.pack(side="left")
        infos = tk.Frame(haut, bg=CREME)
        infos.pack(side="left", fill="both", expand=True, padx=18)
        self.titre_fiche = tk.Label(infos, font=SOUS_TITRE, bg=CREME, fg=NOIR, anchor="w")
        self.titre_fiche.pack(fill="x")
        self.infos_fiche = tk.Label(infos, font=PETIT, bg=CREME, fg=NOIR, anchor="w",
                                    justify="left", wraplength=420)
        self.infos_fiche.pack(fill="x", pady=(4, 0))

        tk.Frame(self.droite, bg=VERT_CLAIR, height=2).pack(fill="x", pady=12)

        form = tk.Frame(self.droite, bg=CREME)
        form.pack(fill="x")
        self.champ_nom = champ_texte(form, largeur=22)
        self.champ_espece = champ_texte(form, largeur=22)
        self.champ_age = ttk.Spinbox(form, from_=0, to=200, width=6, font=TEXTE)
        self.champ_classe = ttk.Combobox(form, values=CLASSIFICATIONS, state="readonly",
                                         width=14)
        self.champ_nombre = ttk.Spinbox(form, from_=0, to=999, width=6, font=TEXTE)
        self.champ_sante = ttk.Combobox(form, values=ETATS_SANTE, state="readonly", width=18)

        champs = [("Nom", self.champ_nom, 0, 0), ("Espèce", self.champ_espece, 0, 2),
                  ("Âge (ans)", self.champ_age, 1, 0),
                  ("Classification", self.champ_classe, 1, 2),
                  ("Nombre de bêtes", self.champ_nombre, 2, 0),
                  ("État de santé", self.champ_sante, 2, 2)]
        for texte, widget, rang, col in champs:
            tk.Label(form, text=texte, font=TEXTE, bg=CREME, fg=NOIR).grid(
                row=rang, column=col, sticky="w", pady=7, padx=(0 if col == 0 else 30, 10))
            widget.grid(row=rang, column=col + 1, sticky="w", pady=7)

        # Naissance d'un bébé
        cadre_naissance = tk.Frame(self.droite, bg=VERT_PALE, padx=12, pady=8)
        cadre_naissance.pack(fill="x", pady=(14, 0))
        self.naissance = tk.BooleanVar()
        tk.Checkbutton(cadre_naissance, text="Signaler une naissance", variable=self.naissance,
                       font=GRAS, bg=VERT_PALE, fg=NOIR, activebackground=VERT_PALE,
                       selectcolor=CREME).pack(side="left")
        tk.Label(cadre_naissance, text="Nombre de bébés :", font=TEXTE, bg=VERT_PALE,
                 fg=NOIR).pack(side="left", padx=(20, 6))
        self.nb_bebes = ttk.Spinbox(cadre_naissance, from_=1, to=30, width=4, font=TEXTE)
        self.nb_bebes.set(1)
        self.nb_bebes.pack(side="left")

        self.info_parrains = tk.Label(self.droite, font=PETIT, bg=CREME, fg=NOIR,
                                      anchor="w", justify="left", wraplength=620)
        self.info_parrains.pack(fill="x", pady=(10, 0))

        boutons = tk.Frame(self.droite, bg=CREME)
        boutons.pack(side="bottom", fill="x", pady=(10, 0))
        Bouton(boutons, "Enregistrer", self.enregistrer).pack(side="right")
        Bouton(boutons, "Annuler les changements", lambda: self.selectionner(self.animal),
               couleur=BEIGE_FONCE).pack(side="right", padx=10)

    def rafraichir_liste(self):
        """Remplit la liste de gauche selon la recherche (en gardant la sélection)."""
        self.animaux_affiches = self.zoo.filtrer(recherche=self.recherche.get())
        self.liste.delete(0, "end")
        for i, a in enumerate(self.animaux_affiches):
            self.liste.insert("end", f" {a.nom}  —  {a.espece}")
            if a.sante != "Bonne santé":
                self.liste.itemconfig(i, bg="#F4DDBF")
        if self.animal in self.animaux_affiches:
            i = self.animaux_affiches.index(self.animal)
            self.liste.selection_set(i)
            self.liste.see(i)

    def clic_liste(self, event=None):
        selection = self.liste.curselection()
        if selection:
            self.selectionner(self.animaux_affiches[selection[0]])

    def selectionner(self, animal):
        """Affiche la fiche d'un animal dans le formulaire."""
        if animal not in self.zoo.animaux:
            animal = self.zoo.animaux[0] if self.zoo.animaux else None
        self.animal = animal
        if animal is None:
            return

        for w in self.cadre_vignette.winfo_children():
            w.destroy()
        vignette_animal(self.cadre_vignette, animal).pack()

        self.titre_fiche.config(text=f"{animal.nom}  (fiche n°{animal.id})")
        self.infos_fiche.config(
            text=f"{animal.nom_scientifique} · {animal.regime} · {animal.origine}\n"
                 f"Poids moyen : {animal.poids} · Statut UICN : {animal.statut_uicn}\n"
                 f"{animal.description}")

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

        nb = len(self.zoo.parrains(animal))
        self.info_parrains.config(
            text=f"{animal.nom} a {nb} parrain(s). Un mail leur est envoyé automatiquement "
                 f"si l'état de santé change ou en cas de naissance.")
        self.rafraichir_liste()

    def enregistrer(self):
        """Enregistre le formulaire et prévient les parrains si nécessaire."""
        animal = self.animal
        if animal is None:
            return
        valeurs = {"nom": self.champ_nom.get(), "espece": self.champ_espece.get(),
                   "age": self.champ_age.get(), "classification": self.champ_classe.get(),
                   "nombre": self.champ_nombre.get(), "sante": self.champ_sante.get()}

        nb_parrains = len(self.zoo.parrains(animal))
        if (valeurs["sante"] != animal.sante or self.naissance.get()) and nb_parrains > 0:
            if not messagebox.askyesno("Confirmation", f"Un mail va être envoyé aux "
                                       f"{nb_parrains} parrain(s) de {animal.nom}.\n"
                                       "Continuer ?", parent=self):
                return
        try:
            messages = self.zoo.modifier(animal, valeurs)
            if self.naissance.get():
                nb = self.nb_bebes.get()
                if not nb.isdigit():
                    raise ValueError("Le nombre de bébés doit être un entier.")
                messages += self.zoo.naissance(animal, int(nb))
        except ValueError as erreur:
            messagebox.showerror("Valeur incorrecte", str(erreur), parent=self)
            return

        self.etat.config(text=" | ".join(messages))
        messagebox.showinfo("Fiche enregistrée", "\n".join(messages), parent=self)
        self.selectionner(animal)

    # ========================================================================
    # Onglet 2 : codes commandes
    # ========================================================================
    def construire_console(self):
        cadre = carte(self.onglet_console, padx=12, pady=12)
        cadre.pack(fill="both", expand=True, padx=10, pady=10)

        self.sortie = tk.Text(cadre, font=CONSOLE, bg=CREME, fg=NOIR, relief="flat",
                              wrap="word", state="disabled", padx=8, pady=6)
        barre = ttk.Scrollbar(cadre, orient="vertical", command=self.sortie.yview)
        self.sortie.config(yscrollcommand=barre.set)

        bas = tk.Frame(cadre, bg=CREME)
        bas.pack(side="bottom", fill="x", pady=(10, 0))
        barre.pack(side="right", fill="y")
        self.sortie.pack(fill="both", expand=True)

        tk.Label(bas, text="Code >", font=CONSOLE, bg=CREME, fg=NOIR).pack(side="left")
        self.entree = champ_texte(bas, largeur=60)
        self.entree.config(font=CONSOLE)
        self.entree.pack(side="left", fill="x", expand=True, padx=8)
        self.entree.bind("<Return>", lambda e: self.executer_commande(self.entree.get()))
        self.entree.bind("<Up>", lambda e: self.parcourir_historique(-1))
        self.entree.bind("<Down>", lambda e: self.parcourir_historique(1))
        Bouton(bas, "Exécuter", lambda: self.executer_commande(self.entree.get())).pack(side="left")
        Bouton(bas, "Aide", lambda: self.executer_commande("aide"),
               couleur=BEIGE_FONCE).pack(side="left", padx=(8, 0))

        self.ecrire_console("Console des codes commandes du zoo.\n"
                            "Exemple : modifier/sante/Kiara/malade — tapez « aide » pour "
                            "voir toutes les commandes. Flèches ↑ ↓ : historique.\n")

    def ecrire_console(self, texte):
        self.sortie.config(state="normal")
        self.sortie.insert("end", texte + "\n")
        self.sortie.config(state="disabled")
        self.sortie.see("end")

    def executer_commande(self, texte):
        texte = texte.strip()
        if not texte:
            return
        self.historique.append(texte)
        self.position_historique = len(self.historique)
        self.entree.delete(0, "end")

        reponse = commandes.executer(texte, self.zoo)
        self.ecrire_console(f"> {texte}\n{reponse}\n")
        self.etat.config(text=reponse.splitlines()[0] if reponse else "")
        # Les commandes peuvent avoir modifié les animaux : on met à jour l'onglet 1
        self.selectionner(self.animal)

    def parcourir_historique(self, sens):
        if not self.historique:
            return
        self.position_historique = min(max(self.position_historique + sens, 0),
                                       len(self.historique))
        self.entree.delete(0, "end")
        if self.position_historique < len(self.historique):
            self.entree.insert(0, self.historique[self.position_historique])

    # ========================================================================
    # Onglet 3 : statistiques (lecture des CSV)
    # ========================================================================
    def construire_stats(self):
        self.indicateurs = tk.Frame(self.onglet_stats, bg=BEIGE)
        self.indicateurs.pack(fill="x", padx=10, pady=(10, 0))

        corps = tk.Frame(self.onglet_stats, bg=BEIGE)
        corps.pack(fill="both", expand=True, padx=10, pady=10)
        menu = carte(corps, padx=10, pady=10)
        menu.pack(side="left", fill="y")
        tk.Label(menu, text="Graphiques", font=GRAS, bg=CREME, fg=NOIR).pack(anchor="w",
                                                                             pady=(0, 8))
        self.zone_graphe = carte(corps)
        self.zone_graphe.pack(side="left", fill="both", expand=True, padx=(10, 0))

        if not MATPLOTLIB:
            tk.Label(self.zone_graphe, font=TEXTE, bg=CREME, fg=NOIR, justify="center",
                     text="Le module matplotlib n'est pas installé.\n\n"
                          "Installez-le avec :  pip install matplotlib\n"
                          "puis relancez l'application.").pack(expand=True)
            return

        self.boutons_graphes = []
        for titre, fonction in GRAPHIQUES:
            b = Bouton(menu, titre, lambda f=fonction: self.tracer(f), couleur=CREME,
                       survol=VERT_CLAIR, police=PETIT, width=16)
            b.pack(fill="x", pady=3)
            self.boutons_graphes.append((b, fonction))
        Bouton(menu, "Actualiser", lambda: self.tracer(self.graphe_actuel),
               couleur=BEIGE_FONCE, police=PETIT).pack(fill="x", pady=(16, 0))

        self.figure = Figure(figsize=(7, 4.4), dpi=100, facecolor=CREME)
        self.canvas_graphe = FigureCanvasTkAgg(self.figure, master=self.zone_graphe)
        self.canvas_graphe.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)
        self.graphe_actuel = GRAPHIQUES[0][1]

    def maj_indicateurs(self):
        """Petites cases de chiffres clés en haut de l'onglet statistiques."""
        for w in self.indicateurs.winfo_children():
            w.destroy()
        visites = lire_csv(FICHIER_VISITEURS)
        notes = lire_csv(FICHIER_SATISFACTION)
        parrainages = lire_csv(FICHIER_PARRAINAGES)
        moyenne = (sum(int(n["note_globale"]) for n in notes) / len(notes)) if notes else 0
        chiffres = [("Avis reçus", str(len(visites))),
                    ("Visiteurs", str(sum(int(v["nombre_visiteurs"]) for v in visites))),
                    ("Note globale moyenne", f"{moyenne:.2f} / 5" if notes else "—"),
                    ("Parrainages", str(len(parrainages))),
                    ("Dons récoltés", f"{sum(float(p['montant']) for p in parrainages):.0f} €"),
                    ("Animaux à surveiller",
                     str(sum(1 for a in self.zoo.animaux if a.sante != "Bonne santé")))]
        for titre, valeur in chiffres:
            case = carte(self.indicateurs, padx=12, pady=6)
            case.pack(side="left", padx=(0, 8), fill="x", expand=True)
            tk.Label(case, text=valeur, font=(POLICE, 16, "bold"), bg=CREME, fg=NOIR).pack()
            tk.Label(case, text=titre, font=PETIT, bg=CREME, fg=NOIR).pack()

    def tracer(self, fonction):
        """Trace le graphique demandé dans la zone de droite."""
        self.graphe_actuel = fonction
        for bouton, f in self.boutons_graphes:
            bouton.changer_couleur(VERT if f is fonction else CREME)
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if not fonction(ax):
            ax.axis("off")
            ax.text(0.5, 0.5, "Pas encore de données pour ce graphique.\n"
                              "Elles apparaîtront après les premiers avis de visiteurs.",
                    ha="center", va="center", fontsize=12)
        self.figure.tight_layout()
        self.canvas_graphe.draw()

    # ========================================================================
    # Onglet 4 : journal des mails
    # ========================================================================
    def construire_mails(self):
        cadre = carte(self.onglet_mails, padx=12, pady=12)
        cadre.pack(fill="both", expand=True, padx=10, pady=10)
        haut = tk.Frame(cadre, bg=CREME)
        haut.pack(fill="x", pady=(0, 8))
        tk.Label(haut, font=PETIT, bg=CREME, fg=NOIR, justify="left",
                 text="Mails envoyés automatiquement aux parrains (envoi simulé : "
                      "ils sont enregistrés dans data/mails_envoyes.txt).").pack(side="left")
        Bouton(haut, "Actualiser", self.maj_mails, couleur=BEIGE_FONCE,
               police=PETIT).pack(side="right")
        self.texte_mails = tk.Text(cadre, font=CONSOLE, bg=CREME, fg=NOIR, relief="flat",
                                   wrap="word", padx=8, pady=6)
        barre = ttk.Scrollbar(cadre, orient="vertical", command=self.texte_mails.yview)
        self.texte_mails.config(yscrollcommand=barre.set)
        barre.pack(side="right", fill="y")
        self.texte_mails.pack(fill="both", expand=True)

    def maj_mails(self):
        self.texte_mails.config(state="normal")
        self.texte_mails.delete("1.0", "end")
        self.texte_mails.insert("1.0", lire_journal_mails() or "Aucun mail envoyé pour l'instant.")
        self.texte_mails.config(state="disabled")
        self.texte_mails.see("end")

    # ========================================================================
    def changement_onglet(self, event=None):
        """Met à jour l'onglet qui vient d'être ouvert (les données ont pu changer)."""
        onglet = self.onglets.nametowidget(self.onglets.select())
        if onglet is self.onglet_stats:
            self.maj_indicateurs()
            if MATPLOTLIB:
                self.tracer(self.graphe_actuel)
        elif onglet is self.onglet_mails:
            self.maj_mails()
        elif onglet is self.onglet_console:
            self.entree.focus_set()

    def deconnexion(self):
        if messagebox.askyesno("Déconnexion", "Voulez-vous vous déconnecter ?", parent=self):
            self.app.afficher_accueil()
