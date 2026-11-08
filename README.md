# Zoo de la Canopée — interface Tkinter

Interface graphique du site du zoo, codée en Python avec Tkinter, d'après le
document « Fenêtres du site du zoo ».

## Lancer l'application

```
python main.py
```

Il faut Tkinter et `matplotlib` (déjà installés avec Anaconda / Spyder).
`pillow` ne sert qu'au script de téléchargement des photos.

## Fenêtres

1. **Page de garde** : « Donner mon avis », « Voir les animaux », « Faire un don », accès administrateur.
2. **Saisie** : nom, prénom, genre, tranche d'âge, pays, nombre de personnes, date, 3 notes (étoiles de 1 à 5).
3. **Liste des animaux** : 39 animaux avec leur photo, filtres par classification et par état de santé.
4. **Fiche animal** : grande photo, informations, description, bouton « Parrainer cet animal ».
5. **Parrainage** : 5 € par mois renouvelés automatiquement ; la personne donne son e-mail et reçoit
   un mail de remerciement avec 3 photos exclusives, puis un mail si l'état de santé de l'animal change
   ou en cas de naissance.
- **Don libre** : montant au choix + e-mail, avec un texte qui explique à quoi sert l'argent ;
  un mail de remerciement est envoyé.
6. **Connexion administrateur** : identifiant et mot de passe.
7. **Interface administrateur**, avec 4 onglets :
   * *Fiches des animaux* : modification des animaux, signalement d'une naissance (mails aux parrains) ;
   * *Statistiques des animaux* : proportion d'animaux malades et gestants, état de santé,
     classement des animaux les plus parrainés avec l'argent versé ;
   * *Statistiques des visiteurs* : chiffres clés, graphiques (âge, genre, pays, satisfaction,
     fréquentation), dons libres ;
   * *Historique des mails* : tous les mails envoyés (ou non envoyés) par le site.

## Comptes administrateur

| Utilisateur | Mot de passe |
|-------------|--------------|
| `admin`     | `zoo2026`    |
| `soigneur`  | `girafe`     |

Les comptes se modifient dans le dictionnaire `COMPTES_ADMIN` de `donnees.py`.

## Envoi des vrais mails (Gmail)

Les mails partent depuis une adresse Gmail du zoo :

1. Créer une adresse Gmail pour le zoo (par exemple `zoo.canopee@gmail.com`).
2. Dans le compte Google : **Sécurité** → activer la **validation en deux étapes**, puis créer un
   **mot de passe d'application** (16 lettres).
3. Copier `config_mail_exemple.py` sous le nom `config_mail.py` et y écrire l'adresse et ce mot de
   passe d'application.

`config_mail.py` contient un mot de passe : il est ignoré par git, il ne faut pas le mettre sur GitHub.
Sans ce fichier (ou sans internet), le site fonctionne quand même : les mails sont marqués
« non envoyé » dans l'historique de l'espace administrateur.

## Photos

Les photos viennent de Wikipédia / Wikimedia Commons (licences libres). Le script
`telecharger_photos.py` les télécharge :

* `images/<id>.png` : petite photo (liste des animaux) ;
* `images/grandes/<id>.png` : grande photo (fiche de l'animal) ;
* `images/exclusives/<id>_1.jpg` à `_3.jpg` : les 3 photos envoyées aux nouveaux parrains ;
* `images/credits.csv` : auteur et licence de chaque photo (affichés sur la fiche et dans les mails).

## Fichiers de données (`data/`)

Séparateur `;`, encodage UTF-8, dates au format `AAAA-MM-JJ`. Les fichiers
se lisent avec `csv.DictReader(f, delimiter=";")` ou `pandas.read_csv(f, sep=";")`.

| Fichier                  | Colonnes                                                         | Rempli par |
|--------------------------|------------------------------------------------------------------|------------|
| `gamme_age.csv`          | id_visite, date_visite, genre, tranche_age                       | Saisie     |
| `origine.csv`            | id_visite, date_visite, pays                                     | Saisie     |
| `satisfaction.csv`       | id_visite, date_visite, note_proprete, note_infrastructures, note_globale | Saisie |
| `visiteurs_par_jour.csv` | id_visite, date_visite, nombre_visiteurs                         | Saisie     |
| `parrainages.csv`        | date, id_animal, animal, montant, email                          | Parrainage |
| `dons.csv`               | date, montant, email                                             | Don libre  |
| `animaux.csv`            | id, nom, espece, …, age, nombre, sante, …                        | Admin      |
| `mails_envoyes.txt`      | historique des mails                                             | Site       |

Le même `id_visite` se retrouve dans les quatre fichiers d'avis : on peut
donc les recouper (par exemple, la note globale selon la tranche d'âge).
Le nom et le prénom du visiteur ne sont pas enregistrés, pour que les
statistiques restent anonymes.

Le total versé par un parrain = 5 € × nombre de mois depuis le début de son parrainage
(fonction `nombre_de_mois` de `donnees.py`).

Pour tester les graphiques avant d'avoir de vrais visiteurs :
`python generer_donnees_test.py` ajoute des avis, des parrainages et des dons **fictifs**.

## Organisation du code

| Fichier                 | Contenu                                                |
|-------------------------|--------------------------------------------------------|
| `main.py`               | fenêtre principale et navigation entre les pages       |
| `donnees.py`            | classes `Animal` et `Zoo`, fichiers CSV, parrainages, dons |
| `mails.py`              | envoi des mails (Gmail) et historique                  |
| `statistiques.py`       | graphiques matplotlib et classement des parrainages    |
| `style.py`              | couleurs, polices, boutons, cartes, photos             |
| `fenetre_accueil.py`    | page de garde                                          |
| `fenetre_saisie.py`     | avis du visiteur                                       |
| `fenetre_animaux.py`    | liste des animaux                                      |
| `fenetre_fiche.py`      | fiche d'un animal                                      |
| `fenetre_parrainage.py` | parrainage                                             |
| `fenetre_don.py`        | don libre                                              |
| `fenetre_admin.py`      | connexion et interface administrateur                  |
