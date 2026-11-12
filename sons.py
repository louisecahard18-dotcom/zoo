

import os

# pygame sert à jouer les sons ; s'il n'est pas installé, le site marche sans son
try:
    from pygame import mixer
except ImportError:
    mixer = None

DOSSIER_SONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sons")
FICHIER_MUSIQUE = os.path.join(DOSSIER_SONS, "fanfare.mp3")


def jouer(fichier):
    if mixer is None or not os.path.exists(fichier):
        return
    try:
        mixer.init()
        mixer.music.load(fichier)
        mixer.music.play()
    except RuntimeError:           # pas de haut-parleur, fichier illisible...
        return


def effet_musique():
    # fanfare jouée après un don ou un parrainage
    jouer(FICHIER_MUSIQUE)


def cri_animal(animal):
    # cri de l'animal (sons/<id>.mp3, 3 secondes) ; rien si l'animal n'a pas de son
    jouer(os.path.join(DOSSIER_SONS, f"{animal.id}.mp3"))
