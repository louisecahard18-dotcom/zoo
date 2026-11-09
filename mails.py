

import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from donnees import (NOM_DU_ZOO, MONTANT_PARRAINAGE, FICHIER_MAILS, DOSSIER_DATA,
                     parrains, credit_photo)

# L'adresse Gmail du zoo et son mot de passe d'application sont dans config_mail.py
# (fichier à créer à partir de config_mail_exemple.py, à ne pas mettre sur GitHub)
try:
    from config_mail import ADRESSE_ZOO, MOT_DE_PASSE
except ImportError:
    ADRESSE_ZOO = ""
    MOT_DE_PASSE = ""

SERVEUR = "smtp.gmail.com"


def envoyer_par_gmail(message):
    mot_de_passe = MOT_DE_PASSE.replace(" ", "")     # le code Gmail s'affiche avec des espaces
    try:
        # d'abord le port 465 (connexion chiffrée dès le début)
        with smtplib.SMTP_SSL(SERVEUR, 465, timeout=10) as serveur:
            serveur.login(ADRESSE_ZOO, mot_de_passe)
            serveur.send_message(message)
    except smtplib.SMTPAuthenticationError:
        raise                                         # mauvais mot de passe : inutile de réessayer
    except OSError:
        # le port 465 est parfois bloqué (wifi d'école, antivirus) : on essaie le port 587
        with smtplib.SMTP(SERVEUR, 587, timeout=10) as serveur:
            serveur.starttls()
            serveur.login(ADRESSE_ZOO, mot_de_passe)
            serveur.send_message(message)


def envoyer_mail(destinataire, sujet, texte, photos=()):
    message = EmailMessage()
    message["From"] = f"{NOM_DU_ZOO} <{ADRESSE_ZOO}>"
    message["To"] = destinataire
    message["Subject"] = sujet
    message.set_content(texte)
    jointes = [chemin for chemin in photos if os.path.exists(chemin)]
    for chemin in jointes:
        with open(chemin, "rb") as f:
            message.add_attachment(f.read(), maintype="image", subtype="jpeg",
                                   filename=os.path.basename(chemin))

    if ADRESSE_ZOO == "":
        statut = "non envoyé (fichier config_mail.py manquant)"
    else:
        try:
            envoyer_par_gmail(message)
            statut = "envoyé"
        except OSError as erreur:          # pas d'internet, mauvais mot de passe...
            statut = f"non envoyé ({erreur})"

    noter_dans_historique(destinataire, sujet, texte, jointes, statut)
    return statut == "envoyé"


def noter_dans_historique(destinataire, sujet, texte, photos, statut):
    os.makedirs(DOSSIER_DATA, exist_ok=True)
    with open(FICHIER_MAILS, "a", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"Date   : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write(f"À      : {destinataire}\n")
        f.write(f"Sujet  : {sujet}\n")
        f.write(f"Statut : {statut}\n")
        if photos:
            f.write("Photos : " + ", ".join(os.path.basename(p) for p in photos) + "\n")
        f.write("\n" + texte + "\n\n")


def lire_historique():
    if not os.path.exists(FICHIER_MAILS):
        return ""
    with open(FICHIER_MAILS, "r", encoding="utf-8") as f:
        return f.read()


def prevenir_parrains(animal, sujet, texte):
    # envoie le même mail à tous les parrains, renvoie (nombre envoyés, nombre de parrains)
    emails = parrains(animal)
    envoyes = 0
    for email in emails:
        if envoyer_mail(email, sujet, texte):
            envoyes = envoyes + 1
    return envoyes, len(emails)


def mail_parrainage(animal, email):
    photos = animal.photos_exclusives()
    credits = "\n".join(credit_photo(p) for p in photos if credit_photo(p))
    texte = (f"Bonjour,\n\n"
             f"Merci de parrainer {animal.nom} ({animal.espece}) au {NOM_DU_ZOO} !\n\n"
             f"Votre parrainage de {MONTANT_PARRAINAGE} € par mois est renouvelé "
             f"automatiquement chaque mois. Il nous aide à nourrir et soigner {animal.nom}.\n\n"
             f"Vous trouverez en pièces jointes 3 photos exclusives de {animal.nom}.\n"
             f"Nous vous écrirons si son état de santé change ou en cas de naissance.\n\n"
             f"À bientôt au zoo !\nL'équipe du {NOM_DU_ZOO}\n\n{credits}")
    return envoyer_mail(email, f"Merci de parrainer {animal.nom} !", texte, photos)


def mail_sante(animal, ancien_etat):
    texte = (f"Bonjour,\n\n"
             f"Vous parrainez {animal.nom} ({animal.espece}) au {NOM_DU_ZOO}.\n"
             f"Son état de santé vient de changer : {ancien_etat} -> {animal.sante}.\n\n"
             f"Nos soigneurs veillent sur lui chaque jour.\n\n"
             f"L'équipe du {NOM_DU_ZOO}")
    return prevenir_parrains(animal, f"Des nouvelles de {animal.nom}", texte)


def mail_naissance(animal, nb_bebes):
    texte = (f"Bonjour,\n\n"
             f"Nous avons la joie de vous annoncer la naissance de {nb_bebes} bébé(s) "
             f"chez {animal.nom} ({animal.espece}) !\n"
             f"Le groupe compte maintenant {animal.nombre} animaux.\n\n"
             f"Merci pour votre parrainage.\n\nL'équipe du {NOM_DU_ZOO}")
    return prevenir_parrains(animal, f"Heureux événement chez {animal.nom} !", texte)


def mail_don(montant, email):
    texte_montant = f"{montant:.2f}".replace(".", ",")
    texte = (f"Bonjour,\n\n"
             f"Merci beaucoup pour votre don de {texte_montant} € au {NOM_DU_ZOO} !\n\n"
             f"Il servira à soigner et nourrir nos animaux, à améliorer leurs enclos et à "
             f"protéger les espèces menacées.\n\n"
             f"L'équipe du {NOM_DU_ZOO}")
    return envoyer_mail(email, "Merci pour votre don !", texte)
