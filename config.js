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

  // 2) Textes affichés en surimpression sur la vidéo
  NOM_ZOO: "Zoo de la Canopée",
  CAMERA_NUMERO: "CAM 01",
  CAMERA_NOM: "Enclos",

  // 3) Réseau (optionnel) : serveurs utilisés pour relier l'iPad et l'iPhone.
  //    Les serveurs STUN suffisent la plupart du temps. Si l'image ne passe pas
  //    sur certains réseaux (4G, Wi-Fi d'entreprise…), ajoute ici un serveur TURN.
  ICE_SERVERS: [
    { urls: "stun:stun.l.google.com:19302" },
    { urls: "stun:stun.cloudflare.com:3478" }
  ]
};
