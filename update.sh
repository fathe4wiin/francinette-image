#!/bin/bash
# Reinstall from fathe4wiin/francinette-image. Does not use sudo or Docker.
set -euo pipefail

REPO="https://github.com/fathe4wiin/francinette-image.git"
TMP="$HOME/.tmp_francinette"

rm -rf "$TMP"
mkdir -p "$TMP"
git clone --depth 1 "$REPO" "$TMP/francinette-image"
INSTALL_DIR="${INSTALL_DIR:-$HOME}" bash "$TMP/francinette-image/install.sh"
rm -rf "$TMP"
