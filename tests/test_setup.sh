#!/bin/bash
# Tests for setup.sh functions with fake pip/python (no root, no network, no Pi).
# Usage: bash tests/test_setup.sh
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAILED=0

# Runs a snippet in a fresh bash with setup.sh sourced into a temporary APP_DIR.
# Fake venv: pip/python record their arguments and working directory, exit with FAKE_*_RC.
run_case() {
    local dir; dir=$(mktemp -d)
    mkdir -p "$dir/app/venv/bin"
    cat > "$dir/app/venv/bin/pip" <<'EOF'
#!/bin/bash
echo "$*" >> "$(dirname "$0")/../../../pip.args"
[[ "$*" == *" -r "* ]] || exit 0
echo "Collecting Flask==3.1.0"
echo "  Building wheel for zstandard (pyproject.toml): started"
echo "Successfully installed Flask-3.1.0"
exit "${FAKE_PIP_RC:-0}"
EOF
    cat > "$dir/app/venv/bin/python3" <<'EOF'
#!/bin/bash
echo "$PWD|$*" >> "$(dirname "$0")/../../../python.args"
exit "${FAKE_PY_RC:-0}"
EOF
    cp "$dir/app/venv/bin/python3" "$dir/app/venv/bin/python"
    chmod +x "$dir/app/venv/bin/"*
    echo "Flask==3.1.0" > "$dir/app/requirements.txt"
    (
        cd "$dir"
        APP_DIR="$dir/app" LOG_FILE="$dir/setup.log" PIP_CONF="$dir/pip.conf" \
        LEDSPLAY_SETUP_NO_MAIN=1 bash -c "
            source '$ROOT/setup.sh'
            sudo() { shift 2; \"\$@\"; }
            $1
        " > "$dir/stdout" 2>&1
        echo $? > "$dir/rc"
    )
    echo "$dir"
}

check() {
    local name="$1"; shift
    if "$@"; then PASS=$((PASS + 1)); echo "  ok   $name"
    else FAILED=$((FAILED + 1)); echo "  FAIL $name"; fi
}

echo "setup_python"

d=$(run_case 'touch "$APP_DIR/constraints.txt"; setup_python')
check "installs all requirements in one pip call with constraints" \
    grep -qx -- "install --only-binary :all: --progress-bar off -r $d/app/requirements.txt -c $d/app/constraints.txt" "$d/pip.args"
check "succeeds when pip succeeds" grep -qx 0 "$d/rc"
check "writes full pip output to the log" grep -q "Building wheel for zstandard" "$d/setup.log"
check "shows package progress in the terminal" grep -q "Collecting Flask==3.1.0" "$d/stdout"
check "keeps build noise out of the terminal" bash -c "! grep -q 'Building wheel' '$d/stdout'"
check "verifies imports after install" grep -q "import flask" "$d/python.args"
check "configures piwheels" grep -q "piwheels.org/simple" "$d/pip.conf"

d=$(run_case 'setup_python')
check "works without constraints.txt (older releases)" \
    grep -qx -- "install --only-binary :all: --progress-bar off -r $d/app/requirements.txt" "$d/pip.args"

d=$(run_case 'export FAKE_PIP_RC=1; setup_python')
check "fails when pip fails" bash -c "! grep -qx 0 '$d/rc'"
check "logs an error when pip fails" grep -q "ERROR.*Python packages" "$d/setup.log"
check "does not report success when pip fails" bash -c "! grep -q 'Python environment ready' '$d/setup.log'"

d=$(run_case 'export FAKE_PY_RC=1; setup_python')
check "fails when imports fail" bash -c "! grep -qx 0 '$d/rc'"
check "logs an error when imports fail" grep -q "ERROR.*import" "$d/setup.log"

echo "generate_demo_cache"

d=$(run_case 'touch "$APP_DIR/generate_cache.cpython-313-arm-linux-gnueabihf.so"; generate_demo_cache')
check "runs the compiled cache generator in APP_DIR" \
    grep -qx -- "$d/app|-c import generate_cache; generate_cache.main()" "$d/python.args"
check "reports success" grep -q "Demo cache generated" "$d/setup.log"

d=$(run_case 'touch "$APP_DIR/generate_cache.py"; generate_demo_cache')
check "runs the source cache generator in APP_DIR" \
    grep -qx -- "$d/app|-c import generate_cache; generate_cache.main()" "$d/python.args"

d=$(run_case 'generate_demo_cache')
check "skips when there is no cache generator" grep -q "skipping demo cache generation" "$d/setup.log"
check "does not run python without a cache generator" test ! -e "$d/python.args"

echo
echo "$PASS passed, $FAILED failed"
[[ $FAILED -eq 0 ]]
