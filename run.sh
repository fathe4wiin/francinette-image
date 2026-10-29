#!/bin/bash
# Run the virtualenv install. Does not use Docker.
set -euo pipefail

ROOT="${FRANCINETTE_DIR:-$HOME/francinette}"
exec "$ROOT/tester.sh" "$@"
