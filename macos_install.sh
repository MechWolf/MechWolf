#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
VENV_NAME=".venv-macos"

log()  { printf "\n==> %s\n" "$*"; }
ok()   { printf "✓ %s\n" "$*"; }
warn() { printf "⚠ %s\n" "$*" >&2; }
fail() { printf "✗ %s\n" "$*" >&2; exit 1; }

trap 'printf "\n✗ Installation failed near line %s.\n" "$LINENO" >&2' ERR

echo "============================================================"
echo " MechWolf - macOS Development Bootstrap"
echo "============================================================"
echo
echo "Repository directory:"
echo "  $PROJECT_DIR"
echo

cd "$PROJECT_DIR"

[[ "$(uname -s)" == "Darwin" ]] || fail "This installer supports macOS only."

log "Checking Xcode Command Line Tools"
if xcode-select -p >/dev/null 2>&1; then
  ok "Xcode Command Line Tools are available"
else
  echo "Xcode Command Line Tools are required."
  echo "macOS will open the installer now."
  xcode-select --install || true
  echo
  echo "Complete the Apple installer, then rerun ./macos_install.sh."
  exit 0
fi

log "Checking Homebrew"
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is not installed."
  read -r -p "Install Homebrew using the official installer? [Y/n]: " INSTALL_BREW

  if [[ "$INSTALL_BREW" =~ ^[Nn]$ ]]; then
    fail "Homebrew is required by this bootstrap."
  fi

  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
fi

command -v brew >/dev/null 2>&1 || fail "Homebrew is not available on PATH."
ok "Homebrew: $(brew --version | head -n 1)"

log "Checking Git"
if command -v git >/dev/null 2>&1; then
  ok "Git: $(git --version)"
else
  brew install git
  ok "Git installed: $(git --version)"
fi

log "Checking Graphviz"
if command -v dot >/dev/null 2>&1; then
  ok "Graphviz: $(dot -V 2>&1)"
else
  brew install graphviz
  ok "Graphviz installed: $(dot -V 2>&1)"
fi

log "Checking Python"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  brew install python
  PYTHON_BIN="$(brew --prefix python)/bin/python3"
fi

PYTHON_VERSION="$("$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
PYTHON_MAJOR="$("$PYTHON_BIN" -c 'import sys; print(sys.version_info.major)')"
PYTHON_MINOR="$("$PYTHON_BIN" -c 'import sys; print(sys.version_info.minor)')"

[[ "$PYTHON_MAJOR" -eq 3 ]] || fail "Python 3 is required."

if [[ "$PYTHON_MINOR" -lt 7 ]]; then
  fail "MechWolf requires Python 3.7 or newer."
fi

ok "Python: $PYTHON_VERSION"

VENV_DIR="$PROJECT_DIR/$VENV_NAME"

log "Checking virtual environment"

if [[ -d "$VENV_DIR" && ! -x "$VENV_DIR/bin/python" ]]; then
  warn "Existing '$VENV_NAME' appears incomplete."
  read -r -p "Delete and recreate it? [Y/n]: " RECREATE

  if [[ "$RECREATE" =~ ^[Nn]$ ]]; then
    fail "Cannot continue with an invalid virtual environment."
  fi

  rm -rf "$VENV_DIR"
fi

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
  ok "Created $VENV_NAME"
else
  ok "$VENV_NAME already exists"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

log "Upgrading packaging tools"
python -m pip install --upgrade pip wheel
python -m pip install "setuptools<81"

log "Installing MechWolf in editable mode"
python -m pip install -e .

log "Installing developer dependencies"
python -m pip install -r requirements-dev.txt

log "Registering Jupyter kernel"
python -m ipykernel install --user \
  --name "mechwolf-macos" \
  --display-name "MechWolf (macOS)" >/dev/null

ok "Jupyter kernel registered: MechWolf (macOS)"

log "Verifying installation"

python - <<'PY'
import sys
import mechwolf as mw
import graphviz

print(f"✓ Python {sys.version.split()[0]}")
print(f"✓ MechWolf {getattr(mw, '__version__', 'unknown')}")
print(f"✓ MechWolf location: {mw.__file__}")
print("✓ graphviz Python package import")
PY

command -v dot >/dev/null 2>&1 || fail "Native Graphviz 'dot' executable is unavailable."

ok "Native Graphviz executable: $(command -v dot)"

echo
echo "============================================================"
echo " Installation complete"
echo "============================================================"
echo
echo "Activate the development environment with:"
echo
echo "  source \"$VENV_DIR/bin/activate\""
echo
echo "Run the test suite with:"
echo
echo "  pytest"
echo
echo "Start Jupyter with:"
echo
echo "  jupyter notebook"
echo