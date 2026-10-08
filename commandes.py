"""
Interpréteur des codes commandes de l'administrateur.

Une commande est une suite de mots séparés par des « / », par exemple :
    modifier/sante/Kiara/malade
    naissance/Zuri/2
Les noms d'animaux et les valeurs ne tiennent compte ni des majuscules ni
des accents (« methusalem » trouve « Méthusalem »).
"""

from donnees import CLASSIFICATIONS, ETATS_SANTE, FICHIER_PARRAINAGES, \
    FICHIER_VISITEURS, FICHIER_SATISFACTION, lire_csv, trouver_dans_liste

AIDE = """Codes commandes disponibles (séparateur « / ») :

  aide                                     affiche cette aide
  liste                                    liste tous les animaux
  liste/<classification>                   ex. liste/oiseaux
  afficher/<animal>                        fiche complète, ex. afficher/Kiara
  modifier/sante/<animal>/<état>           ex. modifier/sante/Kiara/malade
  modifier/age/<animal>/<âge>              ex. modifier/age/Timon/5
  modifier/nombre/<animal>/<nombre>        ex. modifier/nombre/Nemo/32
  modifier/classification/<animal>/<cl.>   ex. modifier/classification/Axel/amphibien
  modifier/nom/<animal>/<nouveau nom>      ex. modifier/nom/Rio/Blu
  naissance/<animal>                       signale la naissance d'un bébé
  naissance/<animal>/<nb>                  ex. naissance/Zuri/2
  malades                                  liste les animaux qui ne sont pas en bonne santé
  ajouter/<nom>/<espèce>/<classif.>/<âge>/<nombre>
                                           ex. ajouter/Pumba/Phacochère/mammifère/4/2
  supprimer/<animal>/confirmer             retire un animal du zoo
  parrains/<animal>                        liste les e-mails des parrains
  stats                                    résumé des avis des visiteurs

États de santé : """ + ", ".join(ETATS_SANTE) + """
  (raccourcis acceptés : malade, bonne, blesse, surveillance, convalescence, gestante)
Classifications : """ + ", ".join(CLASSIFICATIONS)

# Nom du champ tapé dans la commande -> attribut de la classe Animal
CHAMPS = {"sante": "sante", "age": "age", "nombre": "nombre", "nb": "nombre",
          "classification": "classification", "classe": "classification",
          "nom": "nom", "espece": "espece"}


def executer(texte, zoo):
    """
    Exécute un code commande sur le zoo et renvoie le texte de la réponse.
    Les erreurs (commande inconnue, animal introuvable, valeur invalide...)
    sont renvoyées sous forme de message plutôt que de faire planter le programme.
    """
    morceaux = [m.strip() for m in texte.strip().strip("/").split("/")]
    if morceaux == [""]:
        return ""
    commande = morceaux[0].lower()
    args = morceaux[1:]

    try:
        if commande in ("aide", "help", "?"):
            return AIDE
        if commande == "liste":
            return cmd_liste(zoo, args)
        if commande == "afficher":
            verifier_nb_args(args, 1, "afficher/<animal>")
            return fiche_texte(trouver_animal(zoo, args[0]))
        if commande == "modifier":
            verifier_nb_args(args, 3, "modifier/<champ>/<animal>/<valeur>")
            champ = CHAMPS.get(args[0].lower())
            if champ is None:
                raise ValueError(f"Champ inconnu : « {args[0]} ». Champs possibles : "
                                 + ", ".join(sorted(set(CHAMPS.values()))))
            animal = trouver_animal(zoo, args[1])
            return "\n".join(zoo.modifier(animal, {champ: args[2]}))
        if commande == "naissance":
            if len(args) not in (1, 2):
                raise ValueError("Syntaxe : naissance/<animal> ou naissance/<animal>/<nb>")
            nb = args[1] if len(args) == 2 else "1"
            if not nb.isdigit():
                raise ValueError("Le nombre de bébés doit être un entier.")
            return "\n".join(zoo.naissance(trouver_animal(zoo, args[0]), int(nb)))
        if commande == "malades":
            liste = [a for a in zoo.animaux if a.sante != "Bonne santé"]
            if not liste:
                return "Tous les animaux sont en bonne santé."
            return "\n".join(f"  {a.nom:<12} {a.espece:<32} {a.sante}" for a in liste)
        if commande == "ajouter":
            verifier_nb_args(args, 5, "ajouter/<nom>/<espèce>/<classification>/<âge>/<nombre>")
            a = zoo.ajouter(*args)
            return f"{a.nom} ({a.espece}) a été ajouté au zoo avec le numéro {a.id}."
        if commande == "supprimer":
            if len(args) != 2 or args[1].lower() != "confirmer":
                raise ValueError("Par sécurité, tapez : supprimer/<animal>/confirmer")
            animal = trouver_animal(zoo, args[0])
            zoo.supprimer(animal)
            return f"{animal.nom} a été retiré de la liste des animaux."
        if commande == "parrains":
            verifier_nb_args(args, 1, "parrains/<animal>")
            animal = trouver_animal(zoo, args[0])
            emails = zoo.parrains(animal)
            if not emails:
                return f"{animal.nom} n'a pas encore de parrain."
            return f"Parrains de {animal.nom} ({len(emails)}) :\n  " + "\n  ".join(emails)
        if commande == "stats":
            return cmd_stats()
        raise ValueError(f"Commande inconnue : « {commande} ». Tapez « aide ».")
    except ValueError as erreur:
        return f"Erreur : {erreur}"


# ----------------------------------------------------------------------------
def verifier_nb_args(args, n, syntaxe):
    if len(args) != n:
        raise ValueError(f"Syntaxe attendue : {syntaxe}")


def trouver_animal(zoo, nom):
    animal = zoo.chercher(nom)
    if animal is None:
        raise ValueError(f"Aucun animal ne s'appelle « {nom} ». Tapez « liste ».")
    return animal


def fiche_texte(a):
    """Renvoie la fiche d'un animal sous forme de texte."""
    return (f"Fiche n°{a.id} : {a.nom}\n"
            f"  Espèce          : {a.espece} ({a.nom_scientifique})\n"
            f"  Classification  : {a.classification}\n"
            f"  Âge             : {a.age} an(s)\n"
            f"  Nombre au zoo   : {a.nombre}\n"
            f"  État de santé   : {a.sante}\n"
            f"  Régime          : {a.regime}\n"
            f"  Origine         : {a.origine}\n"
            f"  Poids           : {a.poids}\n"
            f"  Statut UICN     : {a.statut_uicn}")


def cmd_liste(zoo, args):
    classe = trouver_dans_liste(args[0], CLASSIFICATIONS, "Classification") if args else None
    animaux = zoo.filtrer(classification=classe)
    lignes = [f"  {a.id:>3}  {a.nom:<12} {a.espece:<32} {a.classification:<10} {a.sante}"
              for a in animaux]
    return f"{len(animaux)} animal(aux) :\n" + "\n".join(lignes)


def cmd_stats():
    """Petit résumé chiffré des fichiers CSV remplis par les visiteurs."""
    visites = lire_csv(FICHIER_VISITEURS)
    notes = lire_csv(FICHIER_SATISFACTION)
    parrainages = lire_csv(FICHIER_PARRAINAGES)
    if not visites:
        return "Aucun avis de visiteur n'a encore été enregistré."
    nb_personnes = sum(int(v["nombre_visiteurs"]) for v in visites)
    texte = (f"Avis enregistrés            : {len(visites)}\n"
             f"Visiteurs (groupes)         : {nb_personnes}\n")
    for colonne, nom in [("note_proprete", "propreté"),
                         ("note_infrastructures", "infrastructures"),
                         ("note_globale", "globale")]:
        moyenne = sum(int(n[colonne]) for n in notes) / len(notes)
        texte += f"Note moyenne {nom:<15}: {moyenne:.2f} / 5\n"
    total_dons = sum(float(p["montant"]) for p in parrainages)
    texte += f"Parrainages                 : {len(parrainages)} ({total_dons:.2f} €)"
    return texte
