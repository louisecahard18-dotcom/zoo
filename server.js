// Serveur "caméras d'enclos" : sert les pages et relaie la signalisation WebRTC.
// La vidéo elle-même passe directement de l'iPad aux navigateurs des parrains (peer-to-peer).
'use strict';

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { WebSocketServer } = require('ws');

const PORT = Number(process.env.PORT) || 3000;
// Code saisi par les parrains pour regarder, et code saisi sur l'iPad pour diffuser.
const SPONSOR_CODE = process.env.SPONSOR_CODE || 'parrain';
const CAMERA_CODE = process.env.CAMERA_CODE || 'soigneur';
// HTTPS local optionnel (l'iPad n'autorise la caméra qu'en HTTPS ou sur localhost).
const TLS_KEY = process.env.TLS_KEY;
const TLS_CERT = process.env.TLS_CERT;

const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'config.json'), 'utf8'));
const enclosureById = new Map(config.enclosures.map((e) => [e.id, e]));
const PUBLIC_DIR = path.join(__dirname, 'public');
// Serveurs STUN/TURN (JSON). Un TURN est conseillé si l'iPad est en 4G ou derrière un réseau strict.
const ICE_SERVERS = process.env.ICE_SERVERS
  ? JSON.parse(process.env.ICE_SERVERS)
  : [{ urls: 'stun:stun.l.google.com:19302' }];

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
};

function handleHttp(req, res) {
  const url = new URL(req.url, 'http://localhost');

  if (url.pathname === '/api/config') {
    res.writeHead(200, { 'Content-Type': MIME['.json'], 'Cache-Control': 'no-store' });
    const live = new Set([...rooms.values()].filter((r) => r.camera).map((r) => r.id));
    res.end(JSON.stringify({
      zooName: config.zooName,
      iceServers: ICE_SERVERS,
      enclosures: config.enclosures.map((e) => ({ ...e, live: live.has(e.id) })),
    }));
    return;
  }

  let file = url.pathname === '/' ? '/index.html' : url.pathname;
  if (!path.extname(file)) file += '.html'; // /camera -> camera.html
  const full = path.normalize(path.join(PUBLIC_DIR, file));
  if (!full.startsWith(PUBLIC_DIR + path.sep)) {
    res.writeHead(403).end();
    return;
  }
  fs.readFile(full, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('Page introuvable');
      return;
    }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(full)] || 'application/octet-stream' });
    res.end(data);
  });
}

const server = TLS_KEY && TLS_CERT
  ? https.createServer({ key: fs.readFileSync(TLS_KEY), cert: fs.readFileSync(TLS_CERT) }, handleHttp)
  : http.createServer(handleHttp);

// ---- Signalisation ----------------------------------------------------------
// rooms: enclosureId -> { id, camera: ws|null, viewers: Map<viewerId, ws> }
const rooms = new Map();
function room(id) {
  if (!rooms.has(id)) rooms.set(id, { id, camera: null, viewers: new Map() });
  return rooms.get(id);
}

const send = (ws, msg) => ws && ws.readyState === ws.OPEN && ws.send(JSON.stringify(msg));
const safeEqual = (a, b) => {
  const ba = Buffer.from(String(a)), bb = Buffer.from(String(b));
  return ba.length === bb.length && crypto.timingSafeEqual(ba, bb);
};

const wss = new WebSocketServer({ server, path: '/ws', maxPayload: 256 * 1024 });

wss.on('connection', (ws) => {
  ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });

  ws.on('message', (raw) => {
    let msg;
    try { msg = JSON.parse(raw); } catch { return; }

    // 1er message obligatoire : { type: 'join', role: 'camera'|'viewer', enclosure, code }
    if (!ws.role) {
      if (msg.type !== 'join' || !enclosureById.has(msg.enclosure)) {
        send(ws, { type: 'error', message: 'Enclos inconnu.' });
        return ws.close();
      }
      const expected = msg.role === 'camera' ? CAMERA_CODE : SPONSOR_CODE;
      if (!['camera', 'viewer'].includes(msg.role) || !safeEqual(msg.code || '', expected)) {
        send(ws, { type: 'error', message: 'Code d’accès incorrect.' });
        return ws.close();
      }
      const r = room(msg.enclosure);
      ws.role = msg.role;
      ws.room = r;

      if (ws.role === 'camera') {
        if (r.camera) { send(r.camera, { type: 'error', message: 'Une autre caméra a pris le relais.' }); r.camera.close(); }
        r.camera = ws;
        send(ws, { type: 'joined', viewers: [...r.viewers.keys()] });
      } else {
        ws.id = crypto.randomUUID();
        r.viewers.set(ws.id, ws);
        send(ws, { type: 'joined', id: ws.id, live: !!r.camera });
        send(r.camera, { type: 'viewer-joined', id: ws.id });
      }
      return;
    }

    const r = ws.room;
    // Relais des messages WebRTC (offer / answer / ice)
    if (!['offer', 'answer', 'ice'].includes(msg.type)) return;
    if (ws.role === 'camera') {
      send(r.viewers.get(msg.to), { type: msg.type, data: msg.data });
    } else {
      send(r.camera, { type: msg.type, from: ws.id, data: msg.data });
    }
  });

  ws.on('close', () => {
    const r = ws.room;
    if (!r) return;
    if (ws.role === 'camera' && r.camera === ws) {
      r.camera = null;
      for (const v of r.viewers.values()) send(v, { type: 'camera-offline' });
    } else if (ws.role === 'viewer') {
      r.viewers.delete(ws.id);
      send(r.camera, { type: 'viewer-left', id: ws.id });
    }
  });
});

// Ping régulier : détecte les iPad en veille / connexions mortes.
setInterval(() => {
  for (const ws of wss.clients) {
    if (!ws.isAlive) { ws.terminate(); continue; }
    ws.isAlive = false;
    ws.ping();
  }
}, 15000);

server.listen(PORT, () => {
  const proto = TLS_KEY ? 'https' : 'http';
  console.log(`Caméras d'enclos prêtes sur ${proto}://localhost:${PORT}`);
  console.log(`  Parrains : ${proto}://<adresse>:${PORT}/        (code : ${SPONSOR_CODE === 'parrain' ? 'parrain — à changer !' : '••••'})`);
  console.log(`  iPad     : ${proto}://<adresse>:${PORT}/camera  (code : ${CAMERA_CODE === 'soigneur' ? 'soigneur — à changer !' : '••••'})`);
});
