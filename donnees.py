"""
Gestion des données du zoo : animaux, avis des visiteurs, parrainages et mails.

Toutes les données sont stockées dans des fichiers CSV (séparateur « ; »,
encodage UTF-8) dans le dossier data/. Ce format se relit facilement avec
le module csv, avec pandas (pd.read_csv(fichier, sep=";")) ou avec Excel,
ce qui permet ensuite de tracer des graphiques.
"""

import csv
import os
import hashlib
from datetime import datetime

# ----------------------------------------------------------------------------
# Chemins des fichiers
# ----------------------------------------------------------------------------
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

# En-têtes des fichiers CSV (l'ordre des colonnes est fixé ici)
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

# ----------------------------------------------------------------------------
# Listes de valeurs possibles
# ----------------------------------------------------------------------------
NOM_DU_ZOO = "Zoo de la Canopée"

CLASSIFICATIONS = ["Mammifère", "Oiseau", "Reptile", "Amphibien", "Poisson"]

ETATS_SANTE = ["Bonne santé", "Sous surveillance", "Malade", "Blessé",
               "En convalescence", "Gestante"]

GENRES = ["Femme", "Homme", "Autre", "Ne souhaite pas répondre"]

TRANCHES_AGE = ["Moins de 12 ans", "12-17 ans", "18-25 ans", "26-40 ans",
                "41-60 ans", "Plus de 60 ans"]

# Pour chaque pays, la liste des régions proposées.
# Une liste vide signifie que le visiteur tape lui-même sa région.
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

# Comptes administrateurs : identifiant -> empreinte SHA-256 du mot de passe.
# (On ne stocke jamais un mot de passe en clair.)
#   admin    / zoo2026
#   soigneur / girafe
COMPTES_ADMIN = {
    "admin": "97c98f42e45c974165a9b9677df8bb947edc520e58cd32ecd604f694b7f2e566",
    "soigneur": "88edae009b37cdab6ac7129ad25457e0a76dcd5a697d73b8bc55584063ab2ad5",
}


def empreinte(mot_de_passe):
    """Renvoie l'empreinte SHA-256 (en hexadécimal) d'un mot de passe."""
    return hashlib.sha256(mot_de_passe.encode("utf-8")).hexdigest()


def verifier_identifiants(utilisateur, mot_de_passe):
    """Renvoie True si le couple identifiant / mot de passe est correct."""
    attendu = COMPTES_ADMIN.get(utilisateur.strip().lower())
    return attendu is not None and attendu == empreinte(mot_de_passe)


# ----------------------------------------------------------------------------
# Fonctions utilitaires
# ----------------------------------------------------------------------------
def lire_csv(fichier):
    """Lit un fichier CSV et renvoie la liste de ses lignes (dictionnaires)."""
    if not os.path.exists(fichier):
        return []
    with open(fichier, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter=SEPARATEUR))


def ecrire_csv(fichier, colonnes, lignes):
    """Réécrit entièrement un fichier CSV avec les lignes données."""
    os.makedirs(os.path.dirname(fichier), exist_ok=True)
    with open(fichier, "w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes, delimiter=SEPARATEUR)
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


def ajouter_ligne_csv(fichier, colonnes, ligne):
    """Ajoute une ligne à la fin d'un CSV (crée le fichier et l'en-tête si besoin)."""
    os.makedirs(os.path.dirname(fichier), exist_ok=True)
    nouveau = not os.path.exists(fichier) or os.path.getsize(fichier) == 0
    with open(fichier, "a", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes, delimiter=SEPARATEUR)
        if nouveau:
            ecrivain.writeheader()
        ecrivain.writerow(ligne)


# ----------------------------------------------------------------------------
# Avis des visiteurs (fenêtre 2 - Saisie)
# ----------------------------------------------------------------------------
def prochain_id_visite():
    """Renvoie un numéro de visite unique (le plus grand déjà utilisé + 1)."""
    ids = [int(l["id_visite"]) for l in lire_csv(FICHIER_VISITEURS)
           if l["id_visite"].isdigit()]
    return max(ids, default=0) + 1


def enregistrer_avis(avis):
    """
    Enregistre l'avis d'un visiteur dans les 4 fichiers CSV prévus.

    avis est un dictionnaire contenant les clés : genre, tranche_age, pays,
    region, nombre_visiteurs, note_proprete, note_infrastructures,
    note_globale et date_visite (au format AAAA-MM-JJ).

    Le nom et le prénom ne sont volontairement PAS enregistrés dans les
    fichiers statistiques : les données restent anonymes (RGPD).
    Chaque fichier contient le même id_visite, ce qui permet de recouper
    les fichiers entre eux (par exemple : note globale selon la tranche d'âge).
    """
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


# ----------------------------------------------------------------------------
# Mails automatiques
# ----------------------------------------------------------------------------
def envoyer_mail(destinataire, sujet, corps):
    """
    Envoie un mail. Pour le projet, l'envoi est SIMULÉ : le mail est ajouté au
    journal data/mails_envoyes.txt (visible dans l'interface administrateur).
    Pour un vrai envoi, il suffirait de remplacer ce contenu par un appel au
    module smtplib avec les paramètres du serveur mail du zoo.
    """
    os.makedirs(DOSSIER_DATA, exist_ok=True)
    horodatage = datetime.now().strftime("%d/%m/%Y %H:%M")
    with open(FICHIER_MAILS, "a", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"Date    : {horodatage}\n")
        f.write(f"À       : {destinataire}\n")
        f.write(f"Sujet   : {sujet}\n\n")
        f.write(corps + "\n")


def lire_journal_mails():
    """Renvoie le contenu du journal des mails envoyés (texte)."""
    if not os.path.exists(FICHIER_MAILS):
        return ""
    with open(FICHIER_MAILS, "r", encoding="utf-8") as f:
        return f.read()


# ----------------------------------------------------------------------------
# Animaux
# ----------------------------------------------------------------------------
class Animal:
    """Un animal (ou un groupe d'animaux d'une même espèce) du zoo."""

    def __init__(self, ligne):
        # ligne est un dictionnaire issu du fichier animaux.csv
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
        """Renvoie l'animal sous forme de dictionnaire (pour l'écrire en CSV)."""
        return {col: getattr(self, col) for col in COLONNES_ANIMAUX}

    def chemin_photo(self):
        """Chemin de la photo de l'animal (images/<id>.png)."""
        return os.path.join(DOSSIER_IMAGES, f"{self.id}.png")

    def __repr__(self):
        return f"Animal({self.nom}, {self.espece})"


class Zoo:
    """Regroupe tous les animaux et les opérations de l'administrateur."""

    def __init__(self):
        self.animaux = []
        self.charger()

    # --- lecture / écriture -------------------------------------------------
    def charger(self):
        self.animaux = [Animal(l) for l in lire_csv(FICHIER_ANIMAUX)]

    def sauvegarder(self):
        ecrire_csv(FICHIER_ANIMAUX, COLONNES_ANIMAUX,
                   [a.en_dictionnaire() for a in self.animaux])

    # --- recherche ----------------------------------------------------------
    def nom_existe(self, nom, sauf=None):
        """Renvoie True si un autre animal (différent de sauf) porte déjà ce nom."""
        for a in self.animaux:
            if a.nom.lower() == nom.lower() and a is not sauf:
                return True
        return False

    def filtrer(self, classification=None, sante=None):
        """Renvoie la liste des animaux correspondant aux filtres donnés."""
        resultat = []
        for a in self.animaux:
            if classification and a.classification != classification:
                continue
            if sante and a.sante != sante:
                continue
            resultat.append(a)
        return resultat

    # --- parrains -----------------------------------------------------------
    def parrains(self, animal):
        """Renvoie la liste (sans doublon) des e-mails des parrains d'un animal."""
        emails = []
        for p in lire_csv(FICHIER_PARRAINAGES):
            if p["id_animal"] == str(animal.id) and p["email"] not in emails:
                emails.append(p["email"])
        return emails

    def prevenir_parrains(self, animal, sujet, corps):
        """Envoie le même mail à tous les parrains d'un animal. Renvoie leur nombre."""
        emails = self.parrains(animal)
        for email in emails:
            envoyer_mail(email, sujet, corps)
        return len(emails)

    # --- modifications (interface admin) ------------------------------------
    def modifier(self, animal, nouvelles_valeurs):
        """
        Modifie un animal. nouvelles_valeurs est un dictionnaire
        {champ: valeur} (champs possibles : nom, espece, age, classification,
        nombre, sante). Les valeurs sont vérifiées : une ValueError est levée
        en cas de problème. Si l'état de santé change, les parrains sont
        prévenus par mail. Renvoie la liste des messages à afficher.
        """
        valeurs = self.verifier_valeurs(animal, nouvelles_valeurs)
        messages = []
        ancienne_sante = animal.sante

        for champ, valeur in valeurs.items():
            if getattr(animal, champ) != valeur:
                setattr(animal, champ, valeur)
                messages.append(f"{animal.nom} : {champ} -> {valeur}")

        if animal.sante != ancienne_sante:
            n = self.prevenir_parrains(
                animal,
                f"Des nouvelles de {animal.nom}",
                f"Bonjour,\n\nVous parrainez {animal.nom} ({animal.espece}) "
                f"au {NOM_DU_ZOO}.\nSon état de santé vient d'évoluer : "
                f"{ancienne_sante} -> {animal.sante}.\n\nNos soigneurs veillent "
                f"sur lui au quotidien.\n\nL'équipe du {NOM_DU_ZOO}")
            messages.append(f"Mail envoyé à {n} parrain(s) (changement de santé).")

        if not messages:
            messages.append(f"{animal.nom} : aucune modification.")
        self.sauvegarder()
        return messages

    def verifier_valeurs(self, animal, valeurs):
        """Vérifie et convertit les valeurs saisies. Lève ValueError si erreur."""
        propres = {}
        for champ, valeur in valeurs.items():
            valeur = str(valeur).strip()
            if champ in ("nom", "espece"):
                if not valeur:
                    raise ValueError(f"Le champ « {champ} » ne peut pas être vide.")
                if champ == "nom" and self.nom_existe(valeur, sauf=animal):
                    raise ValueError(f"Le nom « {valeur} » est déjà utilisé.")
                propres[champ] = valeur
            elif champ in ("age", "nombre"):
                if not valeur.isdigit():
                    raise ValueError(f"« {champ} » doit être un entier positif.")
                propres[champ] = int(valeur)
                if champ == "age" and propres[champ] > 200:
                    raise ValueError("Un âge supérieur à 200 ans n'est pas réaliste.")
            elif champ == "classification":
                if valeur not in CLASSIFICATIONS:
                    raise ValueError(f"Classification inconnue : « {valeur} ».")
                propres[champ] = valeur
            elif champ == "sante":
                if valeur not in ETATS_SANTE:
                    raise ValueError(f"État de santé inconnu : « {valeur} ».")
                propres[champ] = valeur
            else:
                raise ValueError(f"Champ inconnu : « {champ} ».")
        return propres

    def naissance(self, animal, nb_bebes=1):
        """Signale la naissance de nb_bebes petits : met à jour le nombre et prévient les parrains."""
        if nb_bebes < 1:
            raise ValueError("Le nombre de bébés doit être au moins 1.")
        animal.nombre += nb_bebes
        if animal.sante == "Gestante":
            animal.sante = "Bonne santé"
        self.sauvegarder()
        texte_bebe = "un bébé" if nb_bebes == 1 else f"{nb_bebes} bébés"
        n = self.prevenir_parrains(
            animal,
            f"Heureux événement chez {animal.nom} !",
            f"Bonjour,\n\nNous avons la joie de vous annoncer la naissance de "
            f"{texte_bebe} chez {animal.nom} ({animal.espece}) !\nLe groupe "
            f"compte désormais {animal.nombre} individus.\n\nMerci pour votre "
            f"parrainage.\n\nL'équipe du {NOM_DU_ZOO}")
        return [f"Naissance : {texte_bebe} chez {animal.nom} "
                f"(effectif : {animal.nombre}).",
                f"Mail envoyé à {n} parrain(s) (naissance)."]
