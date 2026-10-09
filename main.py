"""
Site du Zoo de la Canopée — interface graphique (Tkinter).

Lancement :  python main.py

Fenêtres codées :
    1. Page de garde
    2. Saisie de l'avis du visiteur
    3. Liste des animaux
    6. Connexion administrateur
    7. Interface administrateur
Les fenêtres 4 (fiche animal) et 5 (parrainage) seront ajoutées plus tard :
la méthode ouvrir_fiche() est déjà prévue pour faire le lien.
"""

import tkinter as tk
from tkinter import messagebox

from donnees import Zoo, NOM_DU_ZOO
from style import BEIGE, configurer_ttk
from fenetre_accueil import FenetreAccueil
from fenetre_saisie import FenetreSaisie
from fenetre_animaux import FenetreAnimaux
from fenetre_admin import FenetreConnexion, FenetreAdmin


class ApplicationZoo(tk.Tk):
    """
    Fenêtre principale. Chaque « fenêtre » du cahier des charges est un Frame
    qui remplace le précédent : on navigue ainsi dans une seule fenêtre,
    comme sur un site web.
    """

    def __init__(self):
        super().__init__()
        self.title(NOM_DU_ZOO)
        self.geometry("1150x760")
        self.minsize(1050, 700)
        self.configure(bg=BEIGE)
        configurer_ttk(self)

        self.zoo = Zoo()          # charge les animaux depuis data/animaux.csv
        self.page = None
        self.afficher_accueil()

    def changer_page(self, classe, *arguments):
        """Détruit la page actuelle et affiche une nouvelle page de la classe donnée."""
        if self.page is not None:
            self.page.destroy()
        self.page = classe(self, *arguments)
        self.page.pack(fill="both", expand=True)

    # --- Navigation entre les fenêtres --------------------------------------
    def afficher_accueil(self):
        self.changer_page(FenetreAccueil)

    def afficher_saisie(self):
        self.changer_page(FenetreSaisie)

    def afficher_animaux(self):
        self.changer_page(FenetreAnimaux)

    def afficher_connexion(self):
        self.changer_page(FenetreConnexion)

    def afficher_admin(self, utilisateur):
        self.changer_page(FenetreAdmin, utilisateur)

    def ouvrir_fiche(self, animal):
        """Fenêtre 4 (fiche animal) : à développer. Aperçu provisoire en attendant."""
        messagebox.showinfo(
            animal.nom,
            f"{animal.nom} — {animal.espece}\n"
            f"Classification : {animal.classification}\n"
            f"Âge : {animal.age} an(s)   ·   Au zoo : {animal.nombre}\n"
            f"État de santé : {animal.sante}\n\n"
            f"{animal.description}\n\n"
            "(La fiche complète et le parrainage arrivent bientôt.)",
            parent=self)


if __name__ == "__main__":
    ApplicationZoo().mainloop()
