#!/bin/bash
# Rebuild the local checkout into the virtualenv. Does not use sudo or Docker.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${INSTALL_DIR:-$HOME}" bash "$DIR/install.sh"
