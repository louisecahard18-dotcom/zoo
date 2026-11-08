


import tkinter as tk
from tkinter import messagebox

from donnees import Zoo, NOM_DU_ZOO
from style import BEIGE, configurer_ttk
from fenetre_accueil import FenetreAccueil
from fenetre_saisie import FenetreSaisie
from fenetre_animaux import FenetreAnimaux
from fenetre_admin import FenetreConnexion,fenetreAdmin


class ApplicationZoo(tk.Tk):
   

    def __init__(self):
        super().__init__()
        self.title(NOM_DU_ZOO)
        self.geometry("1150x760")
        self.resizable(False, False)      
        self.configure(bg=BEIGE)
        configurer_ttk(self)

        self.zoo = Zoo()          
        self.page = None
        self.afficher_accueil()

    def changer_page(self, classe, *arguments):
        
        if self.page is not None:
            self.page.destroy()
        self.page = classe(self, *arguments)
        self.page.pack(fill="both", expand=True)

    def afficher_accueil(self):
        self.changer_page(FenetreAccueil)

    def afficher_saisie(self):
        self.changer_page(FenetreSaisie)

    def afficher_animaux(self):
        self.changer_page(FenetreAnimaux)

    def afficher_connexion(self):
        self.changer_page(FenetreConnexion)
        
    def afficher_admin(self):
        self.changer_page(fenetreAdmin)
        


    def ouvrir_fiche(self, animal):
        
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
