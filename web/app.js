/* Minimal bootstrap: load the extracted game data into the in-memory FS, then start ScummVM.
 * The complete SCUMM/HE interpreter comes from the vendored ScummVM runtime (web/vendor/). */
'use strict';
const $ = id => document.getElementById(id);
const canvas = $('canvas');
const status = $('status');
const log = text => { if (text) status.textContent = text; console.log(text); };

function fail(message) {
  status.textContent = '';
  const err = $('error');
  err.hidden = false;
  err.textContent = `The game could not start: ${message}`;
  console.error(message);
}

window.Module = {
  canvas,
  preRun: [() => {
    addRunDependency('game-data');
    FS.mkdirTree('/game');
    const files = ['spyfox.he0', 'spyfox.he1', 'spyfox.he2', 'spyfox.he4'];
    (async () => {
      for (const name of files) {
        const res = await fetch(`data/games/spyfox/${name}`);
        if (!res.ok) throw new Error(`${name}: HTTP ${res.status}`);
        const total = Number(res.headers.get('Content-Length'));
        const bytes = new Uint8Array(total);
        const reader = res.body.getReader();
        let offset = 0;
        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          bytes.set(value, offset);
          offset += value.length;
          if (total) status.textContent = `Loading ${name}… ${Math.round(offset / total * 100)}%`;
        }
        if (offset !== total) throw new Error(`${name}: incomplete download`);
        FS.writeFile(`/game/${name}`, bytes, { canOwn: true });
      }
      status.textContent = 'Starting engine…';
      removeRunDependency('game-data');
    })().catch(fail);
  }],
  // Runtime binaries live in vendor/ (the ScummVM WASM build).
  locateFile: path => (path.startsWith('/') ? path : `vendor/${path}`),
  print: log,
  printErr: log,
  setStatus: log,
  onAbort: fail,
  onRuntimeInitialized() { canvas.focus(); },
};

// The engine reads its launch arguments from the URL fragment.
$('start').onclick = () => {
  $('start').style.display = 'none';
  history.replaceState(null, '', '#--output-rate=44100 spyfox');
  const script = document.createElement('script');
  script.src = 'vendor/scummvm.js';
  script.onerror = () => fail('the game engine could not be loaded');
  document.body.append(script);
};

canvas.addEventListener('contextmenu', event => event.preventDefault());
