# Caméras d'enclos pour les parrains

Un iPad posé devant un enclos sert de « caméra de surveillance ». Les parrains regardent l'image en direct depuis leur navigateur, avec un rendu de vidéosurveillance : horodatage, ● REC, nom de la caméra, grain et lignes de balayage.

```
iPad (Safari)  ──WebRTC (vidéo directe)──►  navigateurs des parrains
      │                                            │
      └──────── WebSocket (signalisation) ── server.js ──┘
```

La vidéo ne transite pas par le serveur, qui sert seulement les pages et met l'iPad en relation avec les parrains.

## Pages

| URL | Pour qui | Rôle |
|---|---|---|
| `/` | Parrains | Code parrain, puis liste des enclos avec l'état EN DIRECT / HORS LIGNE |
| `/watch?e=lions` | Parrains | Écran de surveillance d'un enclos, avec « SIGNAL PERDU » si l'iPad est coupé |
| `/camera` | iPad | Choix de l'enclos, code soigneur, diffusion |

## Lancer

```bash
npm install
```

```bash
SPONSOR_CODE=monCodeParrain CAMERA_CODE=monCodeSoigneur npm start
```

| Variable | Défaut | Rôle |
|---|---|---|
| `PORT` | `3000` | Port HTTP |
| `SPONSOR_CODE` | `parrain` | Code demandé aux parrains. **À changer.** |
| `CAMERA_CODE` | `soigneur` | Code demandé sur l'iPad pour diffuser. **À changer.** |
| `ICE_SERVERS` | STUN Google | JSON des serveurs STUN/TURN (voir plus bas) |
| `TLS_KEY` / `TLS_CERT` | — | Chemins d'un certificat pour servir en HTTPS directement |

Les enclos se modifient dans `config.json` (`id` pour l'URL, `cam` et `name` pour l'affichage), ainsi que le nom du zoo.

## ⚠️ HTTPS obligatoire pour l'iPad

Safari n'autorise la caméra **qu'en HTTPS**. Deux solutions :

1. **Héberger le serveur** chez un hébergeur Node qui fournit le HTTPS et les WebSockets (Render, Railway, Fly.io…). Commande de démarrage : `npm start`. Définir les variables `SPONSOR_CODE` et `CAMERA_CODE` dans son interface.
2. **En local**, avec un tunnel HTTPS vers ton ordinateur :
   ```bash
   cloudflared tunnel --url http://localhost:3000
   ```
   Il affiche une adresse `https://….trycloudflare.com`, à ouvrir sur l'iPad (`/camera`) et à donner aux parrains.

## Installer l'iPad

1. Ouvrir `https://ton-adresse/camera` dans Safari, choisir l'enclos, saisir le code soigneur, puis toucher **Démarrer la caméra** et autoriser l'accès.
2. Garder l'iPad **branché sur secteur** avec **Safari au premier plan**. La page empêche la mise en veille (iPadOS 16.4+). Par sécurité, régler aussi Réglages › Luminosité et affichage › Verrouillage automatique › Jamais.
3. Pour qu'un passant ne puisse pas quitter la page : Réglages › Accessibilité › **Accès guidé**, puis triple-clic sur le bouton latéral.
4. Le bouton **Écran noir** éteint l'affichage sans couper la diffusion (toucher l'écran pour le rallumer). **Changer de caméra** bascule entre la caméra arrière et la caméra avant.

Si le Wi-Fi ou le serveur coupe, l'iPad se reconnecte seul et les parrains retrouvent l'image automatiquement.

## Limites à connaître

- **Nombre de parrains** : l'iPad envoie un flux vidéo à chaque parrain connecté (environ 0,9 Mbit/s chacun). Avec une bonne connexion, prévoir une dizaine de spectateurs simultanés par iPad au maximum. Au-delà, il faut un serveur relais vidéo (SFU, par exemple LiveKit).
- **Réseaux stricts / 4G** : le STUN suffit en général. Si certains parrains restent sur « réseau bloqué », ajouter un serveur TURN :
  ```bash
  ICE_SERVERS='[{"urls":"stun:stun.l.google.com:19302"},{"urls":"turn:turn.exemple.com:3478","username":"u","credential":"p"}]' npm start
  ```
- Il y a un seul code partagé par tous les parrains. Pour un code par parrain ou par enclos, il faudra une petite base de comptes.
- Aucun enregistrement : le « REC » est purement décoratif.
