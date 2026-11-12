# Caméra d'enclos — Zoo de la Canopée

L'iPad filme l'enclos. Le parrain scanne un QR code avec son iPhone, et Safari affiche la vidéo en direct avec un habillage de caméra de surveillance (● REC, date et heure, nom de la caméra).

- Aucune application à installer, ni sur l'iPad ni sur l'iPhone.
- L'iPad et l'iPhone peuvent être sur des réseaux différents (Wi-Fi du zoo et 4G, par exemple).
- C'est gratuit : le site est hébergé sur **GitHub Pages**, et **Supabase** sert uniquement à mettre les deux appareils en relation.
- La vidéo va directement de l'iPad à l'iPhone. Elle ne passe pas par Supabase et n'est jamais enregistrée (le « REC » est décoratif).

## Comment l'accès est protégé

- Au premier lancement, l'iPad crée une **clé secrète de caméra**. Elle reste sur l'iPad, dans l'adresse de la page et dans la mémoire de Safari, et n'apparaît **nulle part dans le code publié**.
- Le **QR code des parrains** contient une autre clé, calculée à partir de la première. Elle permet de regarder, mais pas de retrouver la clé de la caméra.
- Sans le QR code, impossible de trouver la vidéo : la clé fait 32 caractères aléatoires.
- Si le QR code circule trop, le bouton **« Créer une nouvelle clé »** sur l'iPad rend tous les anciens QR codes inutilisables.

Le code du site peut donc être public sans risque. La clé Supabase « publishable » qu'il contient est faite pour ça.

---

## Fichiers

| Fichier | Rôle | À modifier ? |
|---|---|---|
| `config.js` | Réglages : Supabase et textes affichés | **Oui, une fois** |
| `camera.html` | Page de l'iPad : clé, QR code, diffusion | Non |
| `index.html` | Page du parrain, ouverte par le QR code | Non |
| `app.js`, `style.css` | Code et couleurs communs | Non |
| `vendor/` | Bibliothèques Supabase et QR code, copiées pour ne dépendre d'aucun autre site | Non |

---

## Étape 1 — Créer le projet Supabase (5 min, sur ordinateur)

1. Va sur **supabase.com** et clique sur **Start your project**. Crée un compte ou connecte-toi avec GitHub.
2. Clique sur **New project**.
3. Remplis le formulaire :
   - **Name** : `camera-enclos`
   - **Database Password** : clique sur *Generate a password*. Tu n'en auras pas besoin ensuite.
   - **Region** : une région européenne (*Paris* ou *Frankfurt*, par exemple).
   - Plan **Free**.
4. Clique sur **Create new project** et patiente une à deux minutes.
5. Dans le menu de gauche, ouvre la roue dentée **Project Settings**, puis **API Keys**. Copie dans un bloc-notes :
   - l'adresse **Project URL**, de la forme `https://abcdefghij.supabase.co` (affichée en haut de la page ou dans **Data API**) ;
   - la clé **Publishable key**, qui commence par `sb_publishable_…`.

   ⚠️ Ne copie **jamais** la clé *secret* ni *service_role*.
6. Vérification : dans **Realtime › Settings** (ou **Project Settings › Realtime**), l'option d'accès public aux canaux (*Allow public access*) doit être **activée**. Elle l'est normalement par défaut. Si tu la désactives, la caméra ne pourra plus se connecter.

Tu n'as besoin de créer **aucune table** ni aucune règle : le système utilise seulement les canaux Realtime de Supabase.

---

## Étape 2 — Mettre le site en ligne avec GitHub Pages

### 2a. Mettre le code sur la branche `main`

Le code se trouve sur la branche `claude/blissful-wright-bor8bq`. Il faut le fusionner dans `main` :

1. Ouvre le dépôt `zoo` sur github.com.
2. Clique sur l'onglet **Pull requests**, puis **New pull request**.
3. Choisis **base : `main`** ← **compare : `claude/blissful-wright-bor8bq`**.
4. Clique sur **Create pull request** deux fois, puis sur **Merge pull request** et **Confirm merge**.

### 2b. Rendre le dépôt public

GitHub Pages n'est gratuit que pour les dépôts **publics**, et le dépôt `zoo` est actuellement **privé**.

1. Dans le dépôt, ouvre **Settings**, onglet **General**.
2. Tout en bas, dans **Danger Zone**, clique sur **Change visibility**, puis **Change to public** et confirme.

Aucun secret ne se trouve dans le code (voir « Comment l'accès est protégé »). Si tu préfères garder `zoo` privé, crée un nouveau dépôt public, par exemple `camera-enclos`, et copies-y tous les fichiers avec **Add file › Upload files**.

### 2c. Renseigner `config.js`

1. Sur github.com, ouvre le fichier **`config.js`** dans la branche `main`.
2. Clique sur l'icône ✏️ **Edit this file**.
3. Remplace les valeurs **entre guillemets** :
   ```js
   SUPABASE_URL: "https://abcdefghij.supabase.co",
   SUPABASE_KEY: "sb_publishable_xxxxxxxxxxxxxxxx",

   NOM_ZOO: "Zoo de la Canopée",
   CAMERA_NUMERO: "CAM 01",
   CAMERA_NOM: "Enclos des lémuriens",
   ```
   Garde les guillemets `"` et les virgules en fin de ligne.
4. Clique sur **Commit changes…**, puis encore sur **Commit changes**.

Tu pourras modifier `NOM_ZOO`, `CAMERA_NUMERO` et `CAMERA_NOM` quand tu veux, de la même façon. Le QR code ne change pas.

### 2d. Activer GitHub Pages

1. **Settings › Pages** (menu de gauche).
2. **Build and deployment › Source** : **Deploy from a branch**.
3. **Branch** : `main`, dossier **`/ (root)`**, puis **Save**.
4. Attends deux à trois minutes et recharge la page. Une bannière affiche l'adresse du site :
   ```
   https://louisecahard18-dotcom.github.io/zoo/
   ```

À chaque modification de `config.js`, le site se met à jour tout seul en une à deux minutes.

---

## Étape 3 — Installer l'iPad (une seule fois)

1. Sur l'iPad, ouvre **Safari** et va à l'adresse :
   ```
   https://louisecahard18-dotcom.github.io/zoo/camera.html
   ```
2. Touche **Créer la clé de la caméra**. L'adresse de la page se termine alors par `#cle=…` : c'est la clé de ta caméra.
3. **Tout de suite :** touche le bouton **Partager** (carré avec une flèche), puis **Sur l'écran d'accueil**, puis **Ajouter**. À partir de maintenant, ouvre toujours la caméra depuis **cette icône** : elle garde la clé. Ajoute aussi la page à tes favoris, par sécurité.
4. Touche **Démarrer la caméra** et **autorise** l'accès à la caméra.
5. L'image apparaît avec l'habillage de surveillance. Touche l'écran pour afficher les boutons :
   - **Changer de caméra** : bascule entre la caméra arrière (par défaut) et la caméra avant.
   - **Écran noir** : éteint l'affichage sans couper la diffusion. Touche l'écran pour le rallumer.
   - **Arrêter** : coupe la diffusion.

### Pour que l'iPad tienne toute la journée

- Garde-le **branché sur secteur**.
- **Réglages › Luminosité et affichage › Verrouillage automatique › Jamais.** La page empêche déjà la mise en veille, mais c'est plus sûr.
- **Accès guidé**, pour qu'on ne puisse pas quitter la page : **Réglages › Accessibilité › Accès guidé** › activer. Ensuite, sur la page caméra, **triple-clic** sur le bouton du haut (ou le bouton principal rond sur les anciens iPad), puis **Démarrer**. Refais un triple-clic et saisis le code pour sortir.
- Safari doit rester **au premier plan**. Si l'iPad se verrouille, la vidéo s'arrête. Rouvre la page et touche **Démarrer la caméra**.

---

## Étape 4 — Le QR code permanent

Sur la page de l'iPad, dans la carte **« 2. QR code des parrains »** :

- **Télécharger le QR code** : une image prête à imprimer, avec le nom du zoo et de l'enclos.
- **Copier le lien** : pour l'envoyer par e-mail ou SMS à un parrain.

Tu peux aussi ouvrir la page caméra sur ton ordinateur (en recopiant l'adresse complète avec `#cle=…`) pour télécharger l'image plus facilement.

Le QR code reste valable **tant que tu ne crées pas de nouvelle clé**. Les modifications de textes, de couleurs ou de code ne l'invalident pas.

---

## Étape 5 — Tester avec l'iPhone

1. La caméra de l'iPad est démarrée.
2. Sur l'iPhone, **désactive le Wi-Fi** pour tester en 4G, donc sur un réseau différent.
3. Ouvre l'**Appareil photo** et vise le QR code, puis touche le lien jaune qui apparaît.
4. Safari s'ouvre : d'abord « Connexion à la caméra… », puis la vidéo en quelques secondes.
5. Sur l'iPad, le coin en haut à gauche indique **« REC · 1 parrain »**.

Tourne l'iPhone à l'horizontale pour une image plus grande.

---

## En cas de problème

| Ce que tu vois | Cause probable | Solution |
|---|---|---|
| iPad : « Étape manquante : Supabase » | `config.js` pas rempli ou mal recopié | Vérifie l'adresse et la clé, avec les guillemets |
| iPad : « Accès à la caméra refusé » | Autorisation refusée | **Réglages › Safari › Caméra › Autoriser**, puis recharge |
| iPhone : « Signal perdu — caméra hors ligne » | La caméra de l'iPad n'est pas démarrée, ou l'iPad est en veille | Sur l'iPad, ouvre l'icône et touche **Démarrer la caméra** |
| iPhone : « caméra hors ligne » alors que l'iPad filme | Le **code canal** de l'iPhone (sous « caméra hors ligne ») est différent de celui de l'iPad (en bas à droite pendant la diffusion) : le QR code et l'iPad n'ont pas la même clé | Sur l'iPad, touche **Créer une nouvelle clé**, ou, sur une page sans clé, colle le lien du QR code distribué dans « Tu as déjà distribué un QR code ? » |
| iPhone : reste bloqué sur « Connexion à la caméra… » ou « nouvel essai… » | Le réseau bloque la connexion directe (rare, surtout sur les Wi-Fi d'entreprise) | Essaie un autre réseau. Si c'est fréquent, ajoute un serveur TURN (ci-dessous) |
| L'iPhone ne trouve jamais la caméra, alors qu'elle tourne | Supabase en pause, ou accès public Realtime désactivé | Tableau de bord Supabase : clique sur **Restore project** s'il est en pause, et vérifie l'étape 1.6 |
| Page introuvable (404) | GitHub Pages pas encore publié ou mauvaise adresse | Attends quelques minutes et vérifie **Settings › Pages** |
| L'icône de l'iPad redemande de « créer une clé » | Icône créée avant l'étape 2, ou clé effacée | **Ne crée pas de nouvelle clé** si des QR codes sont distribués : colle le lien du QR code (il contient `#v=`) dans la carte « Tu as déjà distribué un QR code ? » |

## Bon à savoir

- **Pause Supabase.** Les projets gratuits sont mis en pause après une période d'inactivité (une semaine environ). Si la caméra tourne régulièrement, ça ne devrait pas arriver. Sinon, va sur le tableau de bord Supabase et clique sur **Restore project** : rien n'est perdu et le QR code reste le même.
- **Nombre de parrains simultanés.** L'iPad envoie un flux vidéo à chaque parrain connecté. Compte **une dizaine de spectateurs simultanés au maximum**, selon la connexion du zoo.
- **Serveur TURN (optionnel).** Sur certains réseaux très fermés, la connexion directe est impossible. Un service TURN gratuit ou peu cher (Metered, Cloudflare Calls…) fournit un identifiant à ajouter dans `ICE_SERVERS` de `config.js` :
  ```js
  { urls: "turn:adresse-du-service:3478", username: "…", credential: "…" }
  ```
  Ces identifiants seront visibles dans le code public. Choisis donc un service avec un quota limité.
- **Vie privée.** Filme uniquement l'enclos, en évitant les allées où passent les visiteurs.

## Tester sur un ordinateur

Les pages sont de simples fichiers. Depuis le dossier du projet, lance un petit serveur :

```bash
python3 -m http.server 8000
```

Ouvre ensuite `http://localhost:8000/camera.html`. La caméra fonctionne sur `localhost` sans HTTPS.
