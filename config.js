// =====================================================================
//  RÉGLAGES DE LA CAMÉRA — c'est le seul fichier à modifier.
//  Garde bien les guillemets "..." et les virgules en fin de ligne.
// =====================================================================
window.CAMERA_CONFIG = {

  // 1) Supabase : Project Settings › API Keys (voir le guide README.md)
  //    - SUPABASE_URL : l'adresse « Project URL », par ex. "https://abcdefgh.supabase.co"
  //    - SUPABASE_KEY : la clé « Publishable key » (commence par sb_publishable_…)
  //      ⚠️ JAMAIS la clé « secret » ni « service_role ».
  SUPABASE_URL: "https://rhecwnozxgrzbxkcizzm.supabase.co",
  SUPABASE_KEY: "sb_publishable_EGYqIULikZzFOZa3GnVU6g_KsPe9fp3",

  // 2) Clé du QR code des parrains : c'est elle qui rend le QR code UNIQUE ET PERMANENT.
  //    ⚠️ Ne la modifie pas : tous les QR codes déjà imprimés cesseraient de fonctionner.
  //    (À changer seulement si le QR code a circulé auprès de personnes indésirables :
  //    32 caractères parmi A-Z a-z 0-9 - _ , puis réimprimer le QR code.)
  CLE_QR: "6qehiuaMRjnZ0uLiekfFFmwjJ2FiDKm9",

  // 3) Textes affichés en surimpression sur la vidéo
  NOM_ZOO: "Zoo de la Canopée",
  CAMERA_NUMERO: "CAM 01",
  CAMERA_NOM: "Enclos",

  // 4) Réseau (optionnel) : serveurs utilisés pour relier l'iPad et l'iPhone.
  //    Les serveurs STUN suffisent la plupart du temps. Si l'image ne passe pas
  //    sur certains réseaux (4G, Wi-Fi d'entreprise…), ajoute ici un serveur TURN.
  ICE_SERVERS: [
    { urls: "stun:stun.l.google.com:19302" },
    { urls: "stun:stun.cloudflare.com:3478" }
  ]
};
