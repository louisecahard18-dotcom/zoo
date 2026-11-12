// Outils partagés entre la page caméra (iPad) et la page parrain.
'use strict';

const Zoo = {
  async config() {
    const res = await fetch('/api/config', { cache: 'no-store' });
    return res.json();
  },

  store: {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch {} },
    del(k) { try { localStorage.removeItem(k); } catch {} },
  },

  /**
   * WebSocket de signalisation avec reconnexion automatique.
   * handlers: { onMessage(msg, send), onOpen(send), onClose(), onFatal(message) }
   */
  signal(join, handlers) {
    let ws, retry = 1000, stopped = false;
    const send = (m) => ws && ws.readyState === 1 && ws.send(JSON.stringify(m));
    const open = () => {
      const proto = location.protocol === 'https:' ? 'wss' : 'ws';
      ws = new WebSocket(`${proto}://${location.host}/ws`);
      ws.onopen = () => { retry = 1000; send({ type: 'join', ...join }); handlers.onOpen && handlers.onOpen(send); };
      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === 'error') {
          stopped = true; // code faux, enclos inconnu ou caméra remplacée : inutile de réessayer
          handlers.onFatal && handlers.onFatal(msg.message);
          return;
        }
        handlers.onMessage(msg, send);
      };
      ws.onclose = () => {
        if (stopped) return; // arrêt volontaire ou erreur définitive : pas de reconnexion
        handlers.onClose && handlers.onClose();
        setTimeout(open, retry);
        retry = Math.min(retry * 2, 10000);
      };
    };
    open();
    return { send, stop() { stopped = true; ws && ws.close(); } };
  },

  /** File d'attente des candidats ICE arrivés avant la description distante. */
  async addIce(pc, cand) {
    if (!cand) return;
    if (pc.remoteDescription) { try { await pc.addIceCandidate(cand); } catch {} }
    else (pc._pending ||= []).push(cand);
  },
  async flushIce(pc) {
    for (const c of pc._pending || []) { try { await pc.addIceCandidate(c); } catch {} }
    pc._pending = [];
  },

  /** Horloge style vidéosurveillance : 12/11/2026 14:03:27 */
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

  /** Grain vidéo animé (aussi utilisé comme « neige » quand le signal est perdu). */
  noise(canvas) {
    const w = (canvas.width = 160), h = (canvas.height = 90);
    const ctx = canvas.getContext('2d');
    const img = ctx.createImageData(w, h);
    let last = 0;
    const frame = (t) => {
      if (t - last > 60) {
        last = t;
        const d = img.data;
        for (let i = 0; i < d.length; i += 4) {
          const v = (Math.random() * 255) | 0;
          d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255;
        }
        ctx.putImageData(img, 0, 0);
      }
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  },

  /** Empêche l'écran de l'iPad de se mettre en veille (Safari 16.4+). */
  async keepAwake() {
    if (!('wakeLock' in navigator)) return false;
    const request = async () => { try { await navigator.wakeLock.request('screen'); } catch {} };
    await request();
    document.addEventListener('visibilitychange', () => document.visibilityState === 'visible' && request());
    return true;
  },

  /** Masque la barre d'outils après quelques secondes d'inactivité. */
  autoHide(el, ms = 4000) {
    let t;
    const show = () => { el.classList.remove('faded'); clearTimeout(t); t = setTimeout(() => el.classList.add('faded'), ms); };
    ['pointerdown', 'pointermove', 'keydown'].forEach((e) => document.addEventListener(e, show));
    show();
  },
};
