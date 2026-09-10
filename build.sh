#!/bin/sh
# Build Spy Fox (browser) from your own disc image.
#
#   ./build.sh                    # uses ./spyfox.iso
#   ./build.sh /path/to/image     # uses the given disc image
#
# Requires Python 3 (standard library only). The disc image must contain the
# four original resource files SPYFOX.HE0/HE1/HE2/HE4 at the ISO 9660 root.
# Extraction writes the resources to web/data/games/spyfox/ (git-ignored).
set -eu
cd "$(dirname "$0")"
ISO="${1:-spyfox.iso}"
if [ ! -f "$ISO" ]; then
  echo "Disc image not found: $ISO"
  echo "Pass a path, or place your disc image as ./spyfox.iso and re-run."
  exit 1
fi
echo "Extracting game resources from $ISO ..."
python3 tools/extract_game.py "$ISO"
echo
echo "Ready. Start the server and play:"
echo "  python3 serve.py"
echo "  # then open http://localhost:8088"
