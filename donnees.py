

import csv
import os



DOSSIER = os.path.dirname(os.path.abspath(__file__))
DOSSIER_DATA = os.path.join(DOSSIER, "data")
DOSSIER_IMAGES = os.path.join(DOSSIER, "images")

FICHIER_ANIMAUX = os.path.join(DOSSIER_DATA, "animaux.csv")
FICHIER_AGES = os.path.join(DOSSIER_DATA, "gamme_age.csv")
FICHIER_ORIGINE = os.path.join(DOSSIER_DATA, "origine.csv")
FICHIER_SATISFACTION = os.path.join(DOSSIER_DATA, "satisfaction.csv")
FICHIER_VISITEURS = os.path.join(DOSSIER_DATA, "visiteurs_par_jour.csv")
FICHIER_PARRAINAGES = os.path.join(DOSSIER_DATA, "parrainages.csv")
FICHIER_MAILS = os.path.join(DOSSIER_DATA, "mails_envoyes.txt")


COLONNES_ANIMAUX = ["id", "nom", "espece", "nom_scientifique", "classification",
                    "age", "nombre", "sante", "regime", "origine", "poids",
                    "statut_uicn", "description", "wikipedia"]
COLONNES_AGES = ["id_visite", "date_visite", "genre", "tranche_age"]
COLONNES_ORIGINE = ["id_visite", "date_visite", "pays", "region"]
COLONNES_SATISFACTION = ["id_visite", "date_visite", "note_proprete",
                         "note_infrastructures", "note_globale"]
COLONNES_VISITEURS = ["id_visite", "date_visite", "nombre_visiteurs"]
COLONNES_PARRAINAGES = ["date", "id_animal", "animal", "montant", "email"]

SEPARATEUR = ";"


NOM_DU_ZOO = "Zoo de la Canopée"

CLASSIFICATIONS = ["Mammifère", "Oiseau", "Reptile", "Amphibien", "Poisson"]

ETATS_SANTE = ["Bonne santé", "Sous surveillance", "Malade", "Blessé",
               "En convalescence", "Gestante"]

GENRES = ["Femme", "Homme", "Autre", "Ne souhaite pas répondre"]

TRANCHES_AGE = ["Moins de 12 ans", "12-17 ans", "18-25 ans", "26-40 ans",
                "41-60 ans", "Plus de 60 ans"]


REGIONS = {
    "France": ["Auvergne-Rhône-Alpes", "Bourgogne-Franche-Comté", "Bretagne",
               "Centre-Val de Loire", "Corse", "Grand Est", "Hauts-de-France",
               "Île-de-France", "Normandie", "Nouvelle-Aquitaine", "Occitanie",
               "Pays de la Loire", "Provence-Alpes-Côte d'Azur", "Outre-mer"],
    "Belgique": ["Bruxelles-Capitale", "Flandre", "Wallonie"],
    "Suisse": ["Suisse romande", "Suisse alémanique", "Suisse italienne"],
    "Luxembourg": ["Luxembourg"],
    "Allemagne": [], "Espagne": [], "Italie": [], "Royaume-Uni": [],
    "Pays-Bas": [], "Portugal": [], "États-Unis": [], "Canada": [],
    "Autre": [],
}
PAYS = list(REGIONS.keys())


COMPTES_ADMIN = {
    "admin": "zoo2026",
    "soigneur": "girafe",
}


def verifier_identifiants(utilisateur, mot_de_passe):
    
    return utilisateur in COMPTES_ADMIN and COMPTES_ADMIN[utilisateur] == mot_de_passe



def lire_csv(fichier):
    
    if not os.path.exists(fichier):
        return []
    with open(fichier, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter=SEPARATEUR))


def ecrire_csv(fichier, colonnes, lignes):
   
    os.makedirs(os.path.dirname(fichier), exist_ok=True)
    with open(fichier, "w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes, delimiter=SEPARATEUR)
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


def ajouter_ligne_csv(fichier, colonnes, ligne):
   
    os.makedirs(os.path.dirname(fichier), exist_ok=True)
    nouveau = not os.path.exists(fichier) or os.path.getsize(fichier) == 0
    with open(fichier, "a", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes, delimiter=SEPARATEUR)
        if nouveau:
            ecrivain.writeheader()
        ecrivain.writerow(ligne)



def prochain_id_visite():
   
    ids = [int(l["id_visite"]) for l in lire_csv(FICHIER_VISITEURS)
           if l["id_visite"].isdigit()]
    return max(ids, default=0) + 1


def enregistrer_avis(avis):
    
    id_visite = prochain_id_visite()
    date = avis["date_visite"]

    ajouter_ligne_csv(FICHIER_AGES, COLONNES_AGES, {
        "id_visite": id_visite, "date_visite": date,
        "genre": avis["genre"], "tranche_age": avis["tranche_age"]})
    ajouter_ligne_csv(FICHIER_ORIGINE, COLONNES_ORIGINE, {
        "id_visite": id_visite, "date_visite": date,
        "pays": avis["pays"], "region": avis["region"]})
    ajouter_ligne_csv(FICHIER_SATISFACTION, COLONNES_SATISFACTION, {
        "id_visite": id_visite, "date_visite": date,
        "note_proprete": avis["note_proprete"],
        "note_infrastructures": avis["note_infrastructures"],
        "note_globale": avis["note_globale"]})
    ajouter_ligne_csv(FICHIER_VISITEURS, COLONNES_VISITEURS, {
        "id_visite": id_visite, "date_visite": date,
        "nombre_visiteurs": avis["nombre_visiteurs"]})
    return id_visite






class Animal:
   

    def __init__(self, ligne):
        
        self.id = int(ligne["id"])
        self.nom = ligne["nom"]
        self.espece = ligne["espece"]
        self.nom_scientifique = ligne["nom_scientifique"]
        self.classification = ligne["classification"]
        self.age = int(ligne["age"])
        self.nombre = int(ligne["nombre"])
        self.sante = ligne["sante"]
        self.regime = ligne["regime"]
        self.origine = ligne["origine"]
        self.poids = ligne["poids"]
        self.statut_uicn = ligne["statut_uicn"]
        self.description = ligne["description"]
        self.wikipedia = ligne["wikipedia"]

    def en_dictionnaire(self):
        
        return {col: getattr(self, col) for col in COLONNES_ANIMAUX}

    def chemin_photo(self):
        
        return os.path.join(DOSSIER_IMAGES, f"{self.id}.png")

    def __repr__(self):
        return f"Animal({self.nom}, {self.espece})"


class Zoo:
    

    def __init__(self):
        self.animaux = []
        self.charger()

    
    def charger(self):
        self.animaux = [Animal(l) for l in lire_csv(FICHIER_ANIMAUX)]

    def sauvegarder(self):
        ecrire_csv(FICHIER_ANIMAUX, COLONNES_ANIMAUX,
                   [a.en_dictionnaire() for a in self.animaux])

    
    def nom_existe(self, nom, sauf=None):
        
        for a in self.animaux:
            if a.nom.lower() == nom.lower() and a is not sauf:
                return True
        return False

    def filtrer(self, classification=None, sante=None):
       
        resultat = []
        for a in self.animaux:
            if classification and a.classification != classification:
                continue
            if sante and a.sante != sante:
                continue
            resultat.append(a)
        return resultat

   
 

   
    
