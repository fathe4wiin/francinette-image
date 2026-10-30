#!/bin/bash
# Install francinette with a normal virtualenv and pip. Does not use sudo or Docker.
WHITE='\033[0;37m'
BLUE='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BWhite='\033[1;37m'
NC='\033[0m'
set -euo pipefail

REPO="https://github.com/fathe4wiin/francinette-image.git"
UPSTREAM="https://github.com/xicodomingues/francinette.git"

if [ "$(id -u)" -eq 0 ]; then
	echo -e "${RED}Do not run this installer as root. It only needs a normal user and pip.${NC}"
	exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
	echo -e "${RED}python3 is not installed. This installer will not use sudo to install it.${NC}"
	exit 1
fi
if ! command -v git >/dev/null 2>&1; then
	echo -e "${RED}git is not installed. This installer will not use sudo to install it.${NC}"
	exit 1
fi

if [ -z "${INSTALL_DIR:-}" ]; then
	INSTALL_DIR="$HOME"
	read -r -p "Install directory (default: $INSTALL_DIR): " user_input
	INSTALL_DIR="${user_input:-$INSTALL_DIR}"
fi
mkdir -p "$INSTALL_DIR"
INSTALL_DIR="$(cd "$INSTALL_DIR" && pwd)"
export INSTALL_DIR

DEST="$INSTALL_DIR/francinette"
IMAGE_DIR=""

if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
	SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	if [ -d "$SCRIPT_DIR/francinette" ] && [ -f "$SCRIPT_DIR/scripts/drop_libft_bonus_rule.py" ]; then
		IMAGE_DIR="$SCRIPT_DIR"
	fi
fi

if [ -z "$IMAGE_DIR" ]; then
	IMAGE_DIR="$INSTALL_DIR/francinette-image"
	rm -rf "$IMAGE_DIR"
	echo -e "${GREEN}Cloning ${BWhite}fathe4wiin/francinette-image${NC}"
	git clone --depth 1 "$REPO" "$IMAGE_DIR"
fi

echo -e "${GREEN}Cloning the francinette runner${NC}"
rm -rf "$DEST"
git clone --depth 1 "$UPSTREAM" "$DEST"
rm -rf "$DEST/.git"

echo -e "${GREEN}Copying the test suites from this repository${NC}"
cp -a "$IMAGE_DIR/francinette/." "$DEST/"
python3 "$IMAGE_DIR/scripts/drop_libft_bonus_rule.py" \
	"$DEST/tests/libft/war-machine/srcs/compil_lib.sh"
find "$DEST" -name '*.py' -print0 \
	| xargs -0 sed -i 's/from pipes import quote/from shlex import quote/g'
chmod 755 "$DEST/tester.sh"

make_venv() {
	local dest="$1"
	rm -rf "$dest"
	if python3 -m venv "$dest" 2>/dev/null; then
		return 0
	fi
	echo -e "${BLUE}python3-venv is missing. Creating the virtualenv with pip's virtualenv. No sudo.${NC}"
	local pyz
	pyz="$(mktemp)"
	curl -fsSL https://bootstrap.pypa.io/virtualenv.pyz -o "$pyz"
	python3 "$pyz" "$dest"
	rm -f "$pyz"
}

echo -e "${GREEN}Creating a virtualenv and installing with pip${NC}"
make_venv "$DEST/venv"
"$DEST/venv/bin/python" -m pip install --upgrade pip
"$DEST/venv/bin/python" -m pip install -r "$DEST/requirements.txt"
"$DEST/venv/bin/python" -m pip install norminette

write_aliases() {
	local rc="$1"
	touch "$rc"
	sed -i '/^alias paco=/d; /^alias francinette=/d' "$rc"
	printf "alias paco='%s/tester.sh'\n" "$DEST" >> "$rc"
	printf "alias francinette='%s/tester.sh'\n" "$DEST" >> "$rc"
}

write_aliases "$HOME/.zshrc"
write_aliases "$HOME/.bashrc"

echo -e "${BLUE}[Francinette] ${GREEN}Installation completed.${NC}"
echo -e "${WHITE}Virtualenv: ${BWhite}$DEST/venv${NC}"
echo -e "${WHITE}Open a new terminal, then run ${BWhite}paco${WHITE} or ${BWhite}francinette${WHITE} in your project folder.${NC}"
