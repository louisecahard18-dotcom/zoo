

from donnees import (lire_csv, FICHIER_AGES, FICHIER_ORIGINE, FICHIER_SATISFACTION,
                     FICHIER_PARRAINAGES, TRANCHES_AGE, GENRES,
                     ETATS_SANTE, nombre_de_mois)
from style import COULEURS_SANTE

VERTS = ["#3E6B48", "#5E8F5F", "#7FAE7F", "#A9CBA4", "#CFE2C6", "#E3D5B8"]


def compter(lignes, colonne):
 
    compteur = {}
    for ligne in lignes:
        valeur = ligne[colonne]
        compteur[valeur] = compteur.get(valeur, 0) + 1
    return compteur


def habiller(ax, titre):
   
    ax.set_title(titre, fontsize=13, fontweight="bold", color="#1C1C1C")
    ax.set_facecolor("#FCF9F2")
    for cote in ("top", "right"):
        ax.spines[cote].set_visible(False)


def graphe_tranches_age(ax):
    lignes = lire_csv(FICHIER_AGES)
    if not lignes:
        return False
    compteur = compter(lignes, "tranche_age")
    valeurs = [compteur.get(t, 0) for t in TRANCHES_AGE]
    ax.bar(TRANCHES_AGE, valeurs, color=VERTS[1])
    ax.set_ylabel("Nombre de répondants")
    ax.tick_params(axis="x", labelrotation=20)
    habiller(ax, "Répartition des visiteurs par tranche d'âge")
    return True


def graphe_genres(ax):
    lignes = lire_csv(FICHIER_AGES)
    if not lignes:
        return False
    compteur = compter(lignes, "genre")
    etiquettes = [g for g in GENRES if compteur.get(g, 0) > 0]
    ax.pie([compteur[g] for g in etiquettes], labels=etiquettes, autopct="%1.0f %%",
           colors=VERTS[1:], startangle=90, wedgeprops={"edgecolor": "white"})
    ax.axis("equal")
    habiller(ax, "Répartition par genre")
    return True


def graphe_pays(ax):
    lignes = lire_csv(FICHIER_ORIGINE)
    if not lignes:
        return False
    compteur = compter(lignes, "pays")
    pays = sorted(compteur, key=compteur.get)       
    ax.barh(pays, [compteur[p] for p in pays], color=VERTS[1])
    ax.set_xlabel("Nombre de répondants")
    habiller(ax, "Origine des visiteurs (pays)")
    return True


def graphe_satisfaction(ax):
    lignes = lire_csv(FICHIER_SATISFACTION)
    if not lignes:
        return False
    criteres = [("note_proprete", "Propreté"),
                ("note_infrastructures", "Infrastructures"),
                ("note_globale", "Note globale")]
   
    largeur = 0.15
    for note in range(1, 6):
        hauteurs = [sum(1 for l in lignes if int(l[col]) == note) for col, _ in criteres]
        positions = [i + (note - 3) * largeur for i in range(len(criteres))]
        ax.bar(positions, hauteurs, width=largeur, label=f"{note} ★",
               color=VERTS[5 - note])
    ax.set_xticks(range(len(criteres)))
    ax.set_xticklabels([f"{nom}\n(moy. {sum(int(l[col]) for l in lignes) / len(lignes):.2f})"
                        for col, nom in criteres])
    ax.set_ylabel("Nombre de notes")
    ax.legend(title="Note", frameon=False)
    habiller(ax, "Satisfaction des visiteurs")
    return True


GRAPHIQUES = [
    ("Tranches d'âge", graphe_tranches_age),
    ("Genres", graphe_genres),
    ("Pays", graphe_pays),
    ("Satisfaction", graphe_satisfaction),
]


# --- Statistiques des animaux ---

def graphe_sante(ax, animaux):
    nombres = [sum(1 for a in animaux if a.sante == etat) for etat in ETATS_SANTE]
    ax.barh(ETATS_SANTE, nombres, color=[COULEURS_SANTE[etat] for etat in ETATS_SANTE])
    for i, n in enumerate(nombres):
        ax.text(n + 0.3, i, f"{n}  ({100 * n / len(animaux):.0f} %)", va="center")
    ax.invert_yaxis()
    ax.set_xlabel("Nombre d'animaux")
    ax.set_xlim(0, max(nombres) + 6)
    habiller(ax, "État de santé des animaux")


def classement_parrainages(animaux):
    # liste de (nom, nombre de parrains, total versé), du plus parrainé au moins parrainé
    lignes = lire_csv(FICHIER_PARRAINAGES)
    resultat = []
    for animal in animaux:
        siens = [l for l in lignes if l["id_animal"] == str(animal.id)]
        if siens:
            total = sum(float(l["montant"]) * nombre_de_mois(l["date"]) for l in siens)
            resultat.append((animal.nom, len(siens), total))
    resultat.sort(key=lambda r: (r[1], r[2]), reverse=True)
    return resultat
