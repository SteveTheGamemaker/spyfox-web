# Engine investigation

The supplied ISO is an August 1997 Spy Fox in Dry Cereal disc. Its game uses SCUMM v6 with Humongous Entertainment extensions version 90. The Windows launchers and installation libraries are not needed by the browser interpreter.

| File | Role | Bytes |
| --- | --- | ---: |
| spyfox.he0 | Resource directories and engine limits | 49,221 |
| spyfox.he1 | Rooms, scripts, images, animations, effects | 69,543,091 |
| spyfox.he2 | Speech | 139,053,674 |
| spyfox.he4 | Music | 30,445,290 |

HE0 and HE1 are XOR-obfuscated with byte 0x69. Decoded chunks begin with a four-byte tag and a big-endian length including the eight-byte header. HE0 contains MAXS, DIRI, DIRR, DIRS, DIRN, DIRC, DIRF, DIRM, DLFL, RNAM, DOBJ, and AARY blocks. HE1 contains one LECF container holding 50 LFLF room containers. HE2 begins with TLKB; HE4 begins with SONG. Audio HSHD headers scanned in these files use mostly 11,025 Hz, with some 11,000 and 7,000 Hz effects. Original data is passed unchanged to ScummVM.

## Browser runtime and fix

Runtime binaries were retrieved from https://scummvm.kuendig.io/ on September 10, 2026. The project and build scripts are at https://github.com/chkuendig/scummvm-demo . Its source submodule pointed to https://github.com/chkuendig/scummvm/tree/c663ad7ab10ad669c8b6d9941f1f3814ba4c2486 at inspection time; deployed-binary correspondence was not independently established. Upstream project: https://github.com/scummvm/scummvm .

The unmodified runtime stalled in Audio::RateConverter_Impl::upsampleConvert during the opening sequence. Chrome debugger stack inspection located the loop. The source commonConvert routine can compute a zero count when the output remainder is smaller than the integer upsampling factor, leaving the output pointer unchanged indefinitely. Changing output rates did not resolve the observed stall.

The delivered binary redirects 78 direct calls from upsampleConvert specializations to their existing interpolateConvert counterparts. Function signatures and original instruction bytes were checked before patching. Only same-length call operands were changed; section sizes, function indices, and dynamic-linking metadata were retained. The patch manifest records every change and both whole-file SHA-256 hashes. WABT wasm-validate passed, and Chrome then advanced through the intro with audio enabled. The source-equivalent change is to use interpolateConvert in the integer-upsampling branch of audio/rate.cpp.

The `scummvm.wasm` shipped in this repository already includes this fix, so no build-time patching is required; `build.sh` only extracts the game resources.

The JavaScript runtime is otherwise the downloaded runtime. The browser shell uses MEMFS for the complete game data and ScummVM’s existing IDBFS mount for saves/settings. Engine plugins and menu resources are served locally. The game is not dependent on the original EXE, Windows, a remote emulator, or cloud services.
