"""
Graphiques construits à partir des fichiers CSV remplis par les visiteurs.

Chaque fonction reçoit un « axe » matplotlib (ax) et y trace un graphique.
Elle renvoie False s'il n'y a pas encore de données à afficher.
Ces fonctions peuvent aussi être utilisées en dehors de l'interface :
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(); graphe_tranches_age(ax); plt.show()
"""

from donnees import (lire_csv, FICHIER_AGES, FICHIER_ORIGINE, FICHIER_SATISFACTION,
                     FICHIER_VISITEURS, FICHIER_PARRAINAGES, TRANCHES_AGE, GENRES)

VERTS = ["#3E6B48", "#5E8F5F", "#7FAE7F", "#A9CBA4", "#CFE2C6", "#E3D5B8"]


def compter(lignes, colonne):
    """Renvoie un dictionnaire {valeur: nombre d'apparitions} pour une colonne."""
    compteur = {}
    for ligne in lignes:
        valeur = ligne[colonne]
        compteur[valeur] = compteur.get(valeur, 0) + 1
    return compteur


def habiller(ax, titre):
    """Mise en forme commune : titre, fond, suppression des bordures inutiles."""
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
    pays = sorted(compteur, key=compteur.get)        # du moins au plus fréquent
    ax.barh(pays, [compteur[p] for p in pays], color=VERTS[1])
    ax.set_xlabel("Nombre de répondants")
    habiller(ax, "Origine des visiteurs (pays)")
    return True


def graphe_regions(ax):
    lignes = [l for l in lire_csv(FICHIER_ORIGINE) if l["pays"] == "France"]
    if not lignes:
        return False
    compteur = compter(lignes, "region")
    regions = sorted(compteur, key=compteur.get)
    ax.barh(regions, [compteur[r] for r in regions], color=VERTS[2])
    ax.set_xlabel("Nombre de répondants")
    habiller(ax, "Visiteurs français par région")
    return True


def graphe_satisfaction(ax):
    lignes = lire_csv(FICHIER_SATISFACTION)
    if not lignes:
        return False
    criteres = [("note_proprete", "Propreté"),
                ("note_infrastructures", "Infrastructures"),
                ("note_globale", "Note globale")]
    # Pour chaque critère : nombre de notes 1, 2, 3, 4 et 5 (barres groupées)
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


def graphe_frequentation(ax):
    lignes = lire_csv(FICHIER_VISITEURS)
    if not lignes:
        return False
    par_jour = {}
    for l in lignes:
        par_jour[l["date_visite"]] = par_jour.get(l["date_visite"], 0) + int(l["nombre_visiteurs"])
    jours = sorted(par_jour)            # les dates AAAA-MM-JJ se trient correctement
    ax.plot(jours, [par_jour[j] for j in jours], marker="o", color=VERTS[0])
    ax.fill_between(jours, [par_jour[j] for j in jours], color=VERTS[3], alpha=0.5)
    # On n'affiche qu'une date sur n pour que l'axe reste lisible
    pas = max(1, len(jours) // 10)
    ax.set_xticks(jours[::pas])
    ax.set_xticklabels([j[8:10] + "/" + j[5:7] for j in jours[::pas]], rotation=30)
    ax.set_ylabel("Visiteurs")
    habiller(ax, "Nombre de visiteurs par jour")
    return True


def graphe_parrainages(ax):
    lignes = lire_csv(FICHIER_PARRAINAGES)
    if not lignes:
        return False
    dons = {}
    for l in lignes:
        dons[l["animal"]] = dons.get(l["animal"], 0) + float(l["montant"])
    animaux = sorted(dons, key=dons.get)[-12:]       # les 12 animaux les plus parrainés
    ax.barh(animaux, [dons[a] for a in animaux], color=VERTS[1])
    ax.set_xlabel("Total des dons (€)")
    habiller(ax, "Dons de parrainage par animal")
    return True


# Liste utilisée par l'interface admin pour créer les boutons
GRAPHIQUES = [
    ("Tranches d'âge", graphe_tranches_age),
    ("Genres", graphe_genres),
    ("Pays", graphe_pays),
    ("Régions (France)", graphe_regions),
    ("Satisfaction", graphe_satisfaction),
    ("Fréquentation", graphe_frequentation),
    ("Parrainages", graphe_parrainages),
]
