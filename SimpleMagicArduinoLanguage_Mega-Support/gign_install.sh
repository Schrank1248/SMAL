echo "Willkommen lieber Nutzer! [ENTER]"
read
echo "In den naechsten Schritten wird der SMAL-Installer SMAL und die SMAL-IDE installieren. [ENTER]"
read

#OS="$(uname -s)"
OS="Linux"

if [ "$OS" = "Linux" ]; then
  DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}"
  TARGET="$DATA_DIR/org.kde.syntax-highlighting/syntax"

  INSTALLER=""
  if command -v apt >/dev/null 2>&1; then
    INSTALLER="apt"
  elif command -v dnf >/dev/null 2>&1; then
    INSTALLER="dnf"
  elif command -v pacman >/dev/null 2>&1; then
    INSTALLER="pacman"
  else
    echo "Kein Installationsprogramm gefunden."
    exit
  fi
  echo "Installiere Kate auf '$OS' mit '$INSTALLER'..."
  echo

  if [ "$INSTALLER" = "apt" ]; then
    sudo apt install kate
  elif [ "$INSTALLER" = "dnf" ]; then
    sudo dnf install kate
  elif [ "$INSTALLER" = "pacman" ]; then
    sudo pacman -S kate
  fi

  echo

  echo "Kate installiert!"
  printf "Kopiere syntax-highlighting nach '$TARGET'... "

  cp SMAL.xml "$TARGET"
  cp smal.js "$TARGET"

  echo "[FERTIG]"

elif [ "$OS" = "Darwin" ]; then
  echo "Installiere Kate auf macOS..."

  brew install kate

  echo "Kate installiert!"

  DATA_DIR="${XDG_DATA_HOME:-$HOME/Library/Application Support}"

  TARGET="$DATA_DIR/org.kde.syntax-highlighting/syntax"
  mkdir -p "$TARGET"

  printf "Kopiere syntax-highlighting nach '$TARGET'... "

  cp SMAL.xml "$TARGET"
  cp smal.js "$TARGET"

  echo "[FERTIG]"
fi
