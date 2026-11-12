// Code commun à la page caméra (iPad) et à la page parrain (iPhone).
// La vidéo passe directement de l'iPad à l'iPhone (WebRTC). Supabase Realtime ne sert
// qu'à échanger les messages de mise en relation, sur un canal dont le nom est dérivé
// de la clé secrète : sans le QR code, impossible de deviner le canal.
'use strict';

const CFG = window.CAMERA_CONFIG || {};

const App = {
  // ---------- Réglages ----------
  isConfigured() {
    const url = String(CFG.SUPABASE_URL || ''), key = String(CFG.SUPABASE_KEY || '');
    return /^https:\/\/.+/.test(url) && !/VOTRE/.test(url) && key.length > 20 && !/VOTRE/.test(key);
  },

  applyLabels() {
    for (const el of document.querySelectorAll('[data-label]')) el.textContent = CFG[el.dataset.label] || '';
    document.title = `${CFG.CAMERA_NUMERO || 'CAM'} — ${CFG.CAMERA_NOM || 'Caméra'}`;
  },

  // ---------- Clés ----------
  b64url(bytes) {
    return btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  },
  async sha256(text) {
    return new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text)));
  },
  /** Clé de la caméra : reste sur l'iPad (dans son favori), n'est jamais publiée. */
  newCameraKey() {
    return App.b64url(crypto.getRandomValues(new Uint8Array(24)));
  },
  /** Clé des parrains (dans le QR code), calculée à partir de la clé caméra.
   *  On ne peut pas retrouver la clé caméra à partir d'elle. */
  async viewerKey(cameraKey) {
    return App.b64url(await App.sha256('canopee-parrain:' + cameraKey)).slice(0, 32);
  },
  async channelName(viewerKey) {
    const h = await App.sha256('canopee-canal:' + viewerKey);
    return 'cam-' + [...h.slice(0, 16)].map((b) => b.toString(16).padStart(2, '0')).join('');
  },
  isKey: (k) => typeof k === 'string' && /^[A-Za-z0-9_-]{32}$/.test(k),
  hashParam(name) {
    return new URLSearchParams(location.hash.slice(1)).get(name);
  },

  // ---------- Canal de mise en relation (Supabase Realtime) ----------
  /**
   * Rejoint le canal. handlers: { onMessage(event, payload), onPeers(list), onStatus(ok) }
   * Renvoie { send(event, payload), close() }.
   */
  async joinChannel(viewerKey, me, handlers) {
    const client = (App._client ||= window.supabase.createClient(CFG.SUPABASE_URL, CFG.SUPABASE_KEY, {
      auth: { persistSession: false, autoRefreshToken: false },
    }));
    const channel = client.channel(await App.channelName(viewerKey), {
      config: { broadcast: { self: false, ack: false }, presence: { key: me.id } },
    });

    for (const ev of ['hello', 'offer', 'answer', 'ice', 'bye']) {
      channel.on('broadcast', { event: ev }, ({ payload }) => {
        if (payload && (!payload.to || payload.to === me.id)) handlers.onMessage(ev, payload);
      });
    }
    channel.on('presence', { event: 'sync' }, () => {
      const peers = Object.values(channel.presenceState()).flat();
      handlers.onPeers && handlers.onPeers(peers);
    });

    channel.subscribe(async (status) => {
      if (status === 'SUBSCRIBED') {
        await channel.track({ role: me.role, id: me.id, at: Date.now() });
        handlers.onStatus && handlers.onStatus(true);
      } else if (['CHANNEL_ERROR', 'TIMED_OUT', 'CLOSED'].includes(status)) {
        handlers.onStatus && handlers.onStatus(false, status);
      }
    });

    return {
      send: (event, payload) => channel.send({ type: 'broadcast', event, payload: { ...payload, from: me.id } }),
      async close() { try { await channel.untrack(); } catch {} client.removeChannel(channel); },
    };
  },

  // Les candidats ICE peuvent arriver avant la description distante : on les met en attente.
  async addIce(pc, cand) {
    if (!cand) return;
    if (pc.remoteDescription) { try { await pc.addIceCandidate(cand); } catch {} }
    else (pc._pending ||= []).push(cand);
  },
  async flushIce(pc) {
    for (const c of pc._pending || []) { try { await pc.addIceCandidate(c); } catch {} }
    pc._pending = [];
  },

  // ---------- Habillage « vidéosurveillance » ----------
  /** Date et heure en surimpression : 12/11/2026 14:03:27 */
  clock(el) {
    const pad = (n) => String(n).padStart(2, '0');
    const tick = () => {
      const d = new Date();
      el.textContent = `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ` +
        `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
    };
    tick();
    setInterval(tick, 1000);
  },


  /** Empêche la mise en veille de l'écran (iPadOS 16.4+). */
  async keepAwake() {
    if (!('wakeLock' in navigator)) return;
    const req = async () => { try { await navigator.wakeLock.request('screen'); } catch {} };
    await req();
    document.addEventListener('visibilitychange', () => document.visibilityState === 'visible' && req());
  },

  /** Masque la barre de boutons après quelques secondes sans toucher l'écran. */
  autoHide(el, ms = 4000) {
    let t;
    const show = () => { el.classList.remove('faded'); clearTimeout(t); t = setTimeout(() => el.classList.add('faded'), ms); };
    ['pointerdown', 'pointermove', 'keydown'].forEach((e) => document.addEventListener(e, show));
    show();
  },

  /** QR code en SVG (bibliothèque qrcode-generator). */
  qrSvg(text) {
    const qr = qrcode(0, 'M');
    qr.addData(text);
    qr.make();
    return qr.createSvgTag({ cellSize: 8, margin: 2, scalable: true });
  },
};
