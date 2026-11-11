#!/bin/sh
# Install the wheel next to this script into a private Linux environment.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BASE="${XDG_DATA_HOME:-$HOME/.local/share}/maliphors-inator"
if ! python3 -m venv "$BASE/venv"; then
    python3 -m venv --without-pip "$BASE/venv"
fi
if "$BASE/venv/bin/python" -m pip --version >/dev/null 2>&1; then
    "$BASE/venv/bin/python" -m pip install --upgrade "$HERE"/maliphors_inator-*.whl
else
    pip --python "$BASE/venv/bin/python" install --upgrade "$HERE"/maliphors_inator-*.whl
fi
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$APPS"
# Desktop Exec quoting follows the same restricted path conventions as the installer.
ESCAPED=$(printf '%s' "$BASE/venv/bin/maliphors-inator" | sed 's/[\\"`$]/\\&/g;s/%/%%/g')
cat > "$APPS/maliphors-inator.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=maliphors-inator
Comment=Mix idioms and proverbs
Exec="$ESCAPED"
Terminal=false
Categories=Utility;
EOF
printf 'Installed. Launch maliphors-inator from your application menu.\nCLI: %s/venv/bin/maliphors-inator-cli\n' "$BASE"
