"""
Télécharge une photo de chaque animal depuis Wikipédia (images libres de
droits de Wikimedia Commons) et l'enregistre dans images/<id>.png, au format
utilisé par l'application (176 x 124 pixels).

À lancer une seule fois, avec une connexion internet :
    pip install pillow
    python telecharger_photos.py

Pour remplacer une photo par une autre, il suffit de mettre une image PNG
de 176 x 124 pixels nommée <id>.png dans le dossier images/ (l'id est le
numéro de l'animal dans data/animaux.csv).
"""

import io
import json
import os
import urllib.parse
import urllib.request

from PIL import Image

from donnees import Zoo, DOSSIER_IMAGES

LARGEUR, HAUTEUR = 176, 124
API = "https://fr.wikipedia.org/api/rest_v1/page/summary/"
# Wikipédia demande que les programmes s'identifient
ENTETES = {"User-Agent": "ProjetZooTkinter/1.0 (projet etudiant)"}


def telecharger(url):
    requete = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=20) as reponse:
        return reponse.read()


def url_photo(titre_page):
    """Renvoie l'adresse de l'image principale d'une page Wikipédia (ou None)."""
    infos = json.loads(telecharger(API + urllib.parse.quote(titre_page.replace(" ", "_"))))
    image = infos.get("thumbnail") or infos.get("originalimage")
    return image["source"] if image else None


def recadrer(image):
    """Recadre l'image au centre (proportions 176/124) puis la redimensionne."""
    image = image.convert("RGB")
    l, h = image.size
    ratio = LARGEUR / HAUTEUR
    if l / h > ratio:                       # image trop large : on coupe les côtés
        nouvelle_l = int(h * ratio)
        gauche = (l - nouvelle_l) // 2
        image = image.crop((gauche, 0, gauche + nouvelle_l, h))
    else:                                   # image trop haute : on coupe en haut et en bas
        nouvelle_h = int(l / ratio)
        haut = (h - nouvelle_h) // 3        # on garde plutôt le haut (la tête de l'animal)
        image = image.crop((0, haut, l, haut + nouvelle_h))
    return image.resize((LARGEUR, HAUTEUR), Image.LANCZOS)


def main():
    os.makedirs(DOSSIER_IMAGES, exist_ok=True)
    credits = ["Photos issues de Wikipédia / Wikimedia Commons (licences libres).",
               "Voir la page de chaque image pour l'auteur et la licence exacte.", ""]
    for animal in Zoo().animaux:
        chemin = animal.chemin_photo()
        if os.path.exists(chemin):
            print(f"[déjà là] {animal.nom}")
            continue
        try:
            url = url_photo(animal.wikipedia)
            if url is None:
                print(f"[pas d'image] {animal.nom} ({animal.wikipedia})")
                continue
            recadrer(Image.open(io.BytesIO(telecharger(url)))).save(chemin)
            credits.append(f"{animal.id}.png  {animal.espece} : {url}")
            print(f"[ok] {animal.nom}")
        except Exception as erreur:          # page introuvable, pas de réseau...
            print(f"[erreur] {animal.nom} : {erreur}")

    with open(os.path.join(DOSSIER_IMAGES, "CREDITS.txt"), "a", encoding="utf-8") as f:
        f.write("\n".join(credits) + "\n")


if __name__ == "__main__":
    main()
