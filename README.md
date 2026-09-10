# Spy Fox in Dry Cereal — in the browser

Play the original 1997 point-and-click adventure in a web browser, running the
real game resources through [ScummVM]'s SCUMM/HE engine compiled to
WebAssembly. No install, no emulator client, no cloud — just a local web page.

**You provide your own game.** This repo does not include the Spy Fox game
content (and should never be asked to). It ships the engine and the small
amount of glue code needed to run it; you supply a disc image of a copy of the
game you're entitled to use, and a one-step script extracts what's needed.

## Requirements

- **Python 3** (standard library only) for the build and the web server.
- **A disc image of *Spy Fox in Dry Cereal*** (`.iso`), one that contains
  `SPYFOX.HE0`, `SPYFOX.HE1`, `SPYFOX.HE2` and `SPYFOX.HE4` at the disc root.

## Build and play

```sh
# 1. Build from your disc image (extracts the game resources)
./build.sh /path/to/spyfox.iso        # or: ./build.sh  (uses ./spyfox.iso)

# 2. Serve it
python3 serve.py                      # listens on 0.0.0.0:8088

# 3. Open it
#    http://localhost:8088            (same machine)
#    http://<this-machine's-ip>:8088  (another device on your network)
```

`build.sh` runs a dependency-free ISO 9660 extractor that copies the four game
resource files into `web/data/games/spyfox/` (git-ignored, regenerated any
time you re-run it) and writes `docs/disc-manifest.json` with the resulting
offsets, sizes and checksums. The first launch streams ~239 MB of the original
resources into browser memory, so give it a moment on the load bar.

### Serving options

```sh
python3 serve.py --port 9000          # different port
python3 serve.py --host 127.0.0.1     # lock it to this machine only
```

`--host` defaults to `0.0.0.0` so a phone/laptop on the same network can load
it. Use `127.0.0.1` to keep it private.

## Controls

Click to interact and use objects. **Escape** skips a scene, **period** skips
a line of dialogue, **F5** opens save/load, **Space** pauses, **Ctrl+F5** opens
the ScummVM menu. Saves persist in the browser's IndexedDB-backed filesystem
(`savepath=/home/web_user` in `web/scummvm.ini`) — keep using the same browser
and address to retain them.

## How it works

The original disc uses SCUMM v6 with Humongous Entertainment's HE90
extensions. `web/app.js` loads the extracted `spyfox.he0/he1/he2/he4` into
emscripten's in-memory filesystem, then boots the vendored ScummVM runtime,
which interprets them directly. HE0/HE1 are XOR-obfuscated and are decoded and
passed through unchanged by the engine. See [docs/ENGINE.md](docs/ENGINE.md)
for the resource format, runtime provenance, and the one audio fix applied to
the shipped runtime.

## Repository layout

| Path | What it is |
| --- | --- |
| `serve.py` | Local HTTP server with HTTP byte-range support (large assets). |
| `build.sh` | One-step build from your disc image. |
| `tools/extract_game.py` | Dependency-free ISO 9660 extractor for the four HE files. |
| `web/index.html`, `web/app.js` | Minimal browser shell + engine bootstrap. |
| `web/scummvm.ini` | Engine/game configuration. |
| `web/vendor/` | ScummVM runtime (WASM + JS) and its GPLv3 license. |
| `web/data/` | Open-source ScummVM runtime data and engine plugin. |
| `web/data/games/spyfox/` | **Your extracted game resources** (git-ignored; from `build.sh`). |
| `docs/ENGINE.md` | Engine investigation and notes. |

## License

Original glue code: MIT. ScummVM engine: GPLv3 (`web/vendor/COPYING`).
Game content is **not** included — see [LICENSE](LICENSE).

[ScummVM]: https://scummvm.org
