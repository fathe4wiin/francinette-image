#!/bin/bash
# Remove the pip/virtualenv install. Does not use sudo.
WHITE='\033[0;37m'
BLUE='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BWhite='\033[1;37m'
NC='\033[0m'
set -euo pipefail

if [ -z "${INSTALL_DIR:-}" ]; then
	INSTALL_DIR="$HOME"
	read -r -p "Install directory (default: $INSTALL_DIR): " user_input
	INSTALL_DIR="${user_input:-$INSTALL_DIR}"
fi

strip_aliases() {
	local rc="$1"
	[ -f "$rc" ] || return 0
	sed -i '/^alias paco=/d; /^alias francinette=/d' "$rc"
	sed -i '/^if ! systemctl status docker | grep "running"/,/^fi$/d' "$rc"
	sed -i '/^if ! docker image ls | grep "francinette-image"/,/^fi$/d' "$rc"
	sed -i '/^if ! docker ps | grep "francinette-image"/,/^fi$/d' "$rc"
}

strip_aliases "$HOME/.zshrc"
strip_aliases "$HOME/.bashrc"

if command -v docker >/dev/null 2>&1; then
	docker stop run-paco >/dev/null 2>&1 || true
	docker rm run-paco >/dev/null 2>&1 || true
	docker rmi -f francinette-image >/dev/null 2>&1 || true
fi

rm -rf "$INSTALL_DIR/francinette" "$INSTALL_DIR/francinette-image"
echo -e "${BLUE}[Francinette] ${GREEN}Uninstalled.${NC}"
echo -e "${WHITE}Open a new terminal so the ${BWhite}paco${WHITE} alias is gone.${NC}"
