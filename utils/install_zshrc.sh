#!/bin/bash
# Shell aliases for the virtualenv install. Does not start Docker and does not use sudo.

RC_FILE="$HOME/.zshrc"
if [ -z "${INSTALL_DIR:-}" ]; then
    INSTALL_DIR="$HOME"
fi
DEST="$INSTALL_DIR/francinette"

touch "$RC_FILE"
sed -i '/^alias paco=/d; /^alias francinette=/d' "$RC_FILE"
printf "alias paco='%s/tester.sh'\n" "$DEST" >> "$RC_FILE"
printf "alias francinette='%s/tester.sh'\n" "$DEST" >> "$RC_FILE"
