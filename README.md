# Zoo de la Canopée — interface Tkinter

Interface graphique du site du zoo, codée en Python avec Tkinter, d'après le
document « Fenêtres du site du zoo ».

## Lancer l'application

```
python main.py
```

Seul Tkinter est nécessaire. Modules facultatifs :

| Module       | Sert à                                        | Installation            |
|--------------|-----------------------------------------------|-------------------------|
| `matplotlib` | onglet « Statistiques » de l'espace admin      | `pip install matplotlib` |
| `pillow`     | script de téléchargement des photos            | `pip install pillow`     |

## Fenêtres codées

1. **Page de garde** : remerciements, « Donner mon avis », « Voir les animaux », accès administrateur.
2. **Saisie** : nom, prénom, genre, tranche d'âge, pays, région, nombre de personnes, date, 3 notes (étoiles de 1 à 5). Tout est vérifié avant l'enregistrement.
3. **Liste des animaux** : 40 animaux (photo, nom, espèce, état de santé), filtres par classification et par état de santé.
6. **Connexion administrateur** : identifiant et mot de passe (blocage de 30 s après 3 erreurs).
7. **Interface administrateur**, avec 3 onglets :
   * *Fiches animaux* : modification du nom, de l'espèce, de l'âge, de la classification, du nombre et de l'état de santé ; signalement d'une naissance ;
   * *Statistiques* : graphiques tirés des CSV des visiteurs ;
   * *Mails envoyés* : journal des mails automatiques aux parrains.

La fiche animal (4) et le parrainage (5) ne sont pas encore codés : cliquer
sur un animal affiche un aperçu provisoire (`ouvrir_fiche()` dans `main.py`).

## Comptes administrateur

| Utilisateur | Mot de passe |
|-------------|--------------|
| `admin`     | `zoo2026`    |
| `soigneur`  | `girafe`     |

Seule l'empreinte SHA-256 des mots de passe est stockée (`donnees.py`).

## Fichiers de données (`data/`)

Séparateur `;`, encodage UTF-8, dates au format `AAAA-MM-JJ`. Les fichiers
se lisent avec `csv.DictReader(f, delimiter=";")` ou `pandas.read_csv(f, sep=";")`.

| Fichier                  | Colonnes                                                         | Rempli par |
|--------------------------|------------------------------------------------------------------|------------|
| `gamme_age.csv`          | id_visite, date_visite, genre, tranche_age                       | Saisie     |
| `origine.csv`            | id_visite, date_visite, pays, region                             | Saisie     |
| `satisfaction.csv`       | id_visite, date_visite, note_proprete, note_infrastructures, note_globale | Saisie |
| `visiteurs_par_jour.csv` | id_visite, date_visite, nombre_visiteurs                         | Saisie     |
| `parrainages.csv`        | date, id_animal, animal, montant, email                          | Parrainage |
| `animaux.csv`            | id, nom, espece, …, age, nombre, sante, …                        | Admin      |
| `mails_envoyes.txt`      | journal des mails (envoi simulé)                                 | Admin      |

Le même `id_visite` se retrouve dans les quatre fichiers d'avis : on peut
donc les recouper (par exemple, la note globale selon la tranche d'âge).
Le nom et le prénom du visiteur ne sont pas enregistrés, pour que les
statistiques restent anonymes.

Pour tester les graphiques avant d'avoir de vrais avis :
`python generer_donnees_test.py` ajoute 250 avis et des parrainages **fictifs**.

## Photos des animaux

Lancer une fois `python telecharger_photos.py` (connexion internet et Pillow
nécessaires) : une photo par animal est récupérée sur Wikipédia et
enregistrée dans `images/<id>.png`. Sans photo, une vignette de couleur est
dessinée à la place. On peut aussi déposer ses propres images PNG de
176 × 124 pixels dans `images/`.

## Organisation du code

| Fichier                 | Contenu                                                |
|-------------------------|--------------------------------------------------------|
| `main.py`               | fenêtre principale et navigation                       |
| `donnees.py`            | classes `Animal` et `Zoo`, lecture/écriture des CSV, mails |
| `statistiques.py`       | graphiques matplotlib                                  |
| `style.py`              | couleurs, polices, widgets personnalisés               |
| `fenetre_accueil.py`    | fenêtre 1                                              |
| `fenetre_saisie.py`     | fenêtre 2                                              |
| `fenetre_animaux.py`    | fenêtre 3                                              |
| `fenetre_admin.py`      | fenêtres 6 et 7                                        |
