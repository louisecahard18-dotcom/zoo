"""
Génère des avis de visiteurs et des parrainages FICTIFS pour tester les
graphiques de l'interface administrateur avant l'ouverture réelle du site.

Lancement :  python generer_donnees_test.py        (250 avis par défaut)
             python generer_donnees_test.py 500    (nombre d'avis choisi)

Attention : les données sont AJOUTÉES aux fichiers existants. Pour repartir
de zéro, supprimer les fichiers gamme_age.csv, origine.csv, satisfaction.csv,
visiteurs_par_jour.csv et parrainages.csv du dossier data/.
"""

import random
import sys
from datetime import date, timedelta

from donnees import (Zoo, enregistrer_avis, ajouter_ligne_csv, FICHIER_PARRAINAGES,
                     COLONNES_PARRAINAGES, GENRES, TRANCHES_AGE, REGIONS)

PRENOMS = ["camille", "lea", "hugo", "lucas", "chloe", "emma", "louis", "jade",
           "nathan", "ines", "paul", "manon", "theo", "sarah", "jules", "alice"]
NOMS = ["martin", "bernard", "dubois", "thomas", "robert", "richard", "petit",
        "durand", "leroy", "moreau", "simon", "laurent", "lefebvre", "michel"]


def note_aleatoire(moyenne):
    """Note entière entre 1 et 5 autour d'une moyenne donnée."""
    return min(5, max(1, round(random.gauss(moyenne, 0.9))))


def generer_avis(nombre):
    aujourdhui = date.today()
    pays_poids = {"France": 70, "Belgique": 8, "Suisse": 5, "Allemagne": 4,
                  "Royaume-Uni": 3, "Espagne": 3, "Italie": 2, "Pays-Bas": 2,
                  "États-Unis": 1, "Canada": 1, "Luxembourg": 1}
    for _ in range(nombre):
        # Plus de visiteurs le week-end : on tire le jour avec un poids
        jours = [aujourdhui - timedelta(days=i) for i in range(60)]
        jour = random.choices(jours, weights=[3 if j.weekday() >= 5 else 1 for j in jours])[0]
        pays = random.choices(list(pays_poids), weights=list(pays_poids.values()))[0]
        regions = REGIONS[pays]
        enregistrer_avis({
            "genre": random.choices(GENRES, weights=[48, 46, 2, 4])[0],
            "tranche_age": random.choices(TRANCHES_AGE, weights=[10, 8, 14, 32, 26, 10])[0],
            "pays": pays,
            "region": random.choice(regions) if regions else "Non précisée",
            "nombre_visiteurs": random.choices(range(1, 7), weights=[10, 30, 15, 30, 10, 5])[0],
            "note_proprete": note_aleatoire(4.1),
            "note_infrastructures": note_aleatoire(3.6),
            "note_globale": note_aleatoire(4.0),
            "date_visite": jour.isoformat(),
        })


def generer_parrainages(nombre):
    zoo = Zoo()
    # Les animaux « vedettes » sont plus souvent parrainés
    poids = [5 if a.nom in ("Kiara", "Babou", "Nanook", "Tenzin", "Pingu", "Nemo") else 1
             for a in zoo.animaux]
    for _ in range(nombre):
        animal = random.choices(zoo.animaux, weights=poids)[0]
        email = f"{random.choice(PRENOMS)}.{random.choice(NOMS)}@exemple.fr"
        jour = date.today() - timedelta(days=random.randint(0, 60))
        ajouter_ligne_csv(FICHIER_PARRAINAGES, COLONNES_PARRAINAGES, {
            "date": jour.isoformat(), "id_animal": animal.id, "animal": animal.nom,
            "montant": random.choice([10, 15, 20, 25, 30, 50, 75, 100]), "email": email})


if __name__ == "__main__":
    nb_avis = int(sys.argv[1]) if len(sys.argv) > 1 else 250
    generer_avis(nb_avis)
    generer_parrainages(nb_avis // 4)
    print(f"{nb_avis} avis et {nb_avis // 4} parrainages fictifs ajoutés dans data/.")
