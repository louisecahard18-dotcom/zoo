"""
Télécharge les photos des animaux depuis Wikipédia / Wikimedia Commons
(photos sous licence libre) :
    images/<id>.png              petite photo (liste des animaux)
    images/grandes/<id>.png      grande photo (fiche de l'animal)
    images/exclusives/<id>_1.jpg, _2.jpg, _3.jpg   photos envoyées aux parrains
    images/credits.csv           auteur et licence de chaque photo

À lancer une seule fois, avec internet :   pip install pillow
                                           python telecharger_photos.py
"""

import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image, ImageStat

from donnees import Zoo, DOSSIER_IMAGES, ajouter_ligne_csv

PETITE = (176, 124)
GRANDE = (380, 268)
LARGEUR_EXCLUSIVE = 800
FICHIER_CREDITS = os.path.join(DOSSIER_IMAGES, "credits.csv")
COLONNES_CREDITS = ["fichier", "auteur", "licence", "source"]

# Wikimedia demande que les programmes s'identifient
ENTETES = {"User-Agent": "ProjetZooTkinter/1.0 (https://github.com/louisecahard18-dotcom/zoo)"}

# Images à éviter : cartes, dessins, squelettes...
MOTS_INTERDITS = ["map", "carte", "range", "distribution", "repartition", "status", "iucn",
                  "skull", "crane", "squelette", "skeleton", "logo", "illustration",
                  "drawing", "dessin", "planche", "plate", "brehm", "egg", "oeuf", "stamp",
                  "timbre", "coin", "fossil", "diagram", "anatomy", "museum", "taxiderm",
                  "mhnt", "mnhn", "buffon", "histoire naturelle", "voyage", "gravure",
                  "engraving", "painting", "peinture", "brockhaus", "prey", "proie", "dead",
                  "mort", "carcass", "perspective", "sign", "panneau", "poster", "cave",
                  "grotte", "stuffed", "empaille", "naturalise", "specimen", "skin", "peau",
                  "fur", "fourrure", "claw", "griffe", "pattern", "texture"]


# Photos vérifiées à la main qui ne montrent pas l'animal
FICHIERS_EXCLUS = ["File:Funchal_(Madeira,_Portugal),_Rua_de_Santa_Maria_58_--_2025_--_0838.jpg",
                   "File:Arctic_ocean_drift_ice,_the_realm_of_the_polar_bear.jpg",
                   "File:654_Rives_Laïta_Guidel.jpg",
                   "File:653_Rives_Laïta_Guidel.jpg",
                   "File:020240211_Python_regius.jpg"]


def telecharger(url):
    # Si le serveur répond « trop de requêtes » (erreur 429), on attend puis on réessaie
    for essai in range(6):
        try:
            requete = urllib.request.Request(url, headers=ENTETES)
            with urllib.request.urlopen(requete, timeout=30) as reponse:
                time.sleep(1)               # on ne surcharge pas les serveurs
                return reponse.read()
        except urllib.error.HTTPError as erreur:
            if erreur.code != 429 or essai == 5:
                raise
        except (TimeoutError, urllib.error.URLError):     # serveur trop lent : on réessaie
            if essai >= 2:
                raise
        time.sleep(5 * (essai + 1))


def lire_json(url):
    return json.loads(telecharger(url))


def lire_image(url):
    return Image.open(io.BytesIO(telecharger(url))).convert("RGB")


def nettoyer(texte):
    """Garde seulement le nom de l'auteur : sans balises HTML, première ligne, 60 caractères max."""
    texte = re.sub(r"<[^>]+>", "\n", texte)
    lignes = [l.strip() for l in texte.splitlines() if l.strip()]
    auteur = lignes[0] if lignes else "inconnu"
    return auteur if len(auteur) <= 60 else auteur[:57] + "..."


def fichiers_de_l_article(titre):
    """Noms des fichiers d'images d'un article Wikipédia, dans l'ordre de l'article."""
    url = "https://fr.wikipedia.org/api/rest_v1/page/media-list/" + urllib.parse.quote(
        titre.replace(" ", "_"))
    noms = []
    for element in lire_json(url).get("items", []):
        if element.get("type") == "image":
            noms.append("File:" + element["title"].split(":", 1)[1])
    return noms


def fichiers_de_qualite(nom_scientifique):
    """Photos de l'espèce labellisées « Quality images » sur Commons (vérifiées par des bénévoles)."""
    return fichiers_commons(f'"{nom_scientifique}" incategory:Quality_images')


def fichiers_commons(recherche):
    """Fichiers de Commons qui correspondent à une recherche (nom scientifique)."""
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search"
           "&srnamespace=6&srlimit=20&srsearch=" + urllib.parse.quote(recherche))
    return [r["title"] for r in lire_json(url)["query"]["search"]]


def infos_images(noms):
    """Pour chaque fichier : adresse de la miniature, taille, auteur, licence."""
    infos = []
    for debut in range(0, len(noms), 40):
        url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
               "&prop=imageinfo&iiprop=url|size|mime|extmetadata&iiurlwidth=960"
               "&iiextmetadatafilter=Artist|LicenseShortName&titles="
               + urllib.parse.quote("|".join(noms[debut:debut + 40])))
        pages = lire_json(url)["query"].get("pages", {})
        par_titre = {p["title"]: p for p in pages.values()}
        for nom in noms[debut:debut + 40]:
            page = par_titre.get(nom.replace("_", " "))
            if page is None or "imageinfo" not in page:
                continue
            ii = page["imageinfo"][0]
            meta = ii.get("extmetadata", {})
            infos.append({
                "nom": nom, "url": ii.get("thumburl", ii["url"]), "mime": ii["mime"],
                "largeur": ii["width"], "hauteur": ii["height"],
                "auteur": nettoyer(meta.get("Artist", {}).get("value", "inconnu")),
                "licence": meta.get("LicenseShortName", {}).get("value", "?"),
                "source": ii["descriptionurl"]})
    return infos


def image_acceptable(info):
    nom = urllib.parse.unquote(info["nom"]).lower().replace("_", " ")
    for a, b in [("é", "e"), ("è", "e"), ("â", "a"), ("ô", "o"), ("œ", "oe")]:
        nom = nom.replace(a, b)
    proportions = info["largeur"] / info["hauteur"]
    return (info["mime"] == "image/jpeg" and info["largeur"] >= 600
            and urllib.parse.unquote(info["nom"]).replace(" ", "_") not in FICHIERS_EXCLUS
            and 0.5 <= proportions <= 2.2                   # pas de montage très étiré
            and re.search(r"1[78]\d\d", nom) is None       # pas d'œuvre des années 1700-1800
            and not any(mot in nom for mot in MOTS_INTERDITS))


def est_en_couleur(image):
    # les gravures et les photos en noir et blanc ont une saturation presque nulle
    return ImageStat.Stat(image.convert("HSV")).mean[1] > 40


def recadrer(image, taille):
    """Recadre l'image au centre (mêmes proportions que taille) puis la redimensionne."""
    l, h = image.size
    ratio = taille[0] / taille[1]
    if l / h > ratio:
        nouvelle_l = int(h * ratio)
        image = image.crop(((l - nouvelle_l) // 2, 0, (l + nouvelle_l) // 2, h))
    else:
        nouvelle_h = int(l / ratio)
        haut = (h - nouvelle_h) // 3        # on garde plutôt le haut (la tête)
        image = image.crop((0, haut, l, haut + nouvelle_h))
    return image.resize(taille, Image.LANCZOS)


def noter_credit(fichier, info):
    ajouter_ligne_csv(FICHIER_CREDITS, COLONNES_CREDITS, {
        "fichier": fichier, "auteur": info["auteur"], "licence": info["licence"],
        "source": info["source"]})


def sans_doublons(candidats):
    """Enlève les photos en double (même taille et même auteur)."""
    resultat, vus = [], set()
    for info in candidats:
        cle = (info["largeur"], info["hauteur"], info["auteur"])
        if cle not in vus:
            vus.add(cle)
            resultat.append(info)
    return resultat


def choisir(candidats, combien):
    """Télécharge les candidats dans l'ordre et garde les premières images en couleur."""
    choisies = []
    for info in candidats:
        if len(choisies) == combien:
            break
        try:
            image = lire_image(info["url"])
        except OSError:             # image trop lente à venir : on passe à la suivante
            continue
        if est_en_couleur(image):
            choisies.append((info, image))
    return choisies


def complet(animal):
    chemins = [animal.chemin_photo(), animal.chemin_grande_photo()] + animal.photos_exclusives()
    return all(os.path.exists(c) for c in chemins)


def traiter(animal):
    if complet(animal):
        print(f"[déjà là] {animal.nom}")
        return
    # d'abord les photos « Quality images », puis celles de l'article Wikipédia
    noms = []
    for nom in fichiers_de_qualite(animal.nom_scientifique) + fichiers_de_l_article(animal.wikipedia):
        if nom.replace("_", " ") not in [n.replace("_", " ") for n in noms]:
            noms.append(nom)
    candidats = sans_doublons([i for i in infos_images(noms) if image_acceptable(i)])
    if len(candidats) < 4:
        noms_vus = {i["nom"] for i in candidats}
        en_plus = [n for n in fichiers_commons(animal.nom_scientifique) if n not in noms_vus]
        candidats = sans_doublons(candidats + [i for i in infos_images(en_plus)
                                               if image_acceptable(i)])
    if len(candidats) < 4:
        print(f"[pas assez de photos] {animal.nom} : {len(candidats)}")
        return

    # les photos en format paysage d'abord (la première sert de photo principale)
    candidats.sort(key=lambda i: i["largeur"] < i["hauteur"])

    # on télécharge les images une par une jusqu'à en avoir 4 en couleur,
    # et on n'enregistre rien avant, pour ne jamais garder un animal à moitié fait
    choisies = choisir(candidats, 4)
    if len(choisies) < 4:
        # pas assez de photos dans l'article : on en cherche d'autres sur Commons
        noms_vus = {i["nom"] for i in candidats}
        en_plus = [n for n in fichiers_commons(animal.nom_scientifique) if n not in noms_vus]
        deja = {(i["largeur"], i["hauteur"], i["auteur"]) for i in candidats}
        choisies += choisir([i for i in infos_images(en_plus) if image_acceptable(i)
                             and (i["largeur"], i["hauteur"], i["auteur"]) not in deja],
                            4 - len(choisies))
    if len(choisies) < 4:
        print(f"[pas assez de photos en couleur] {animal.nom}")
        return
    principale = choisies[0][0]
    exclusives = [info for info, image in choisies[1:]]
    images = [image for info, image in choisies]

    recadrer(images[0], PETITE).save(animal.chemin_photo())
    recadrer(images[0], GRANDE).save(animal.chemin_grande_photo())
    noter_credit(os.path.basename(animal.chemin_photo()), principale)
    for chemin, image, info in zip(animal.photos_exclusives(), images[1:], exclusives):
        image.thumbnail((LARGEUR_EXCLUSIVE, LARGEUR_EXCLUSIVE))
        image.save(chemin, quality=85)
        noter_credit(os.path.basename(chemin), info)
    print(f"[ok] {animal.nom}", flush=True)


def main():
    os.makedirs(os.path.join(DOSSIER_IMAGES, "grandes"), exist_ok=True)
    os.makedirs(os.path.join(DOSSIER_IMAGES, "exclusives"), exist_ok=True)
    for animal in Zoo().animaux:
        try:
            traiter(animal)
        except (OSError, ValueError, KeyError) as erreur:   # pas de réseau, page introuvable...
            print(f"[erreur] {animal.nom} : {erreur}")


if __name__ == "__main__":
    main()
