#!/bin/bash
#
# LEDsplay - Raspberry Pi Setup Script
# Downloads latest release from GitHub and configures the system.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/PabloCSScobar/ledsplay/main/setup.sh | sudo bash
#   # or
#   sudo ./setup.sh
#

set -euo pipefail

readonly APP_DIR="${APP_DIR:-/opt/ledsplay}"
readonly APP_USER="${APP_USER:-pi}"
readonly APP_GROUP="${APP_GROUP:-ledsplay}"
readonly GITHUB_REPO="${GITHUB_REPO:-PabloCSScobar/ledsplay}"
readonly RELEASES_API="https://api.github.com/repos/${GITHUB_REPO}/releases/latest"
readonly LOG_FILE="${LOG_FILE:-/var/log/ledsplay-setup.log}"

# --- Logging ---

log()    { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
info()   { log "INFO  $*"; }
ok()     { log "  OK  $*"; }
fail()   { log "ERROR $*"; exit 1; }

# --- Checks ---

check_root() {
    [[ $EUID -eq 0 ]] || fail "This script must be run as root (use sudo)"
}

check_os() {
    [[ -f /etc/os-release ]] || fail "Cannot determine OS version"
    . /etc/os-release
    [[ "$ID" == "raspbian" || "$ID" == "debian" ]] || fail "This script is designed for Raspberry Pi OS / Debian"
    info "Detected: $PRETTY_NAME"
}

check_user() {
    id "$APP_USER" &>/dev/null || fail "User '$APP_USER' does not exist. Run this on a Raspberry Pi with default user."
}

# --- System Setup ---

install_packages() {
    info "Updating package lists..."
    apt-get update -qq

    info "Installing required packages..."
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        gcc make build-essential python3-dev \
        git scons swig python3-venv \
        libjack0 libjack-dev \
        curl jq
    ok "Packages installed"
}

setup_permissions() {
    info "Setting up user and permissions..."
    groupadd -f "$APP_GROUP" || true
    usermod -a -G "$APP_GROUP,spi,gpio,kmem" "$APP_USER"
    mkdir -p "$APP_DIR"
    chown -R "$APP_USER:$APP_GROUP" "$APP_DIR"
    chmod -R 775 "$APP_DIR"
    ok "Permissions configured"
}

configure_hardware() {
    info "Configuring hardware (SPI, audio)..."

    local config_file="/boot/firmware/config.txt"
    [[ -f "$config_file" ]] || config_file="/boot/config.txt"
    [[ -f "$config_file" ]] || fail "Cannot find config.txt"

    # Enable SPI
    if ! grep -q "^dtparam=spi=on" "$config_file"; then
        echo "dtparam=spi=on" >> "$config_file"
        info "SPI enabled"
    fi

    # Disable onboard audio (conflicts with PWM for LEDs)
    if ! grep -q "blacklist snd_bcm2835" /etc/modprobe.d/snd-blacklist.conf 2>/dev/null; then
        echo 'blacklist snd_bcm2835' > /etc/modprobe.d/snd-blacklist.conf
        info "Audio blacklisted"
    fi

    if grep -q "^dtparam=audio=on" "$config_file"; then
        sed -i 's/^dtparam=audio=on/#dtparam=audio=on/' "$config_file"
        info "Audio disabled in config.txt"
    fi

    ok "Hardware configured"
}

# --- Application Download ---

download_latest_release() {
    info "Fetching latest release from GitHub..."

    local release_json
    release_json=$(curl -fsSL "$RELEASES_API") || fail "Cannot reach GitHub API. Check internet connection."

    local tag_name
    tag_name=$(echo "$release_json" | jq -r '.tag_name // empty')
    [[ -n "$tag_name" ]] || fail "No releases found in $GITHUB_REPO. Publish a release first."

    local version="${tag_name#v}"
    info "Latest version: $version"

    # Find .tar.gz asset
    local tarball_url
    tarball_url=$(echo "$release_json" | jq -r '.assets[] | select(.name | endswith(".tar.gz")) | .browser_download_url' | head -1)
    [[ -n "$tarball_url" ]] || fail "No .tar.gz asset found in release $tag_name"

    # Find optional sha256sums
    local sha256_url
    sha256_url=$(echo "$release_json" | jq -r '.assets[] | select(.name | endswith("sha256sums.txt")) | .browser_download_url' | head -1)

    # Download tarball
    local tmp_dir="/tmp/ledsplay-setup"
    rm -rf "$tmp_dir"
    mkdir -p "$tmp_dir"

    info "Downloading $tarball_url ..."
    curl -fSL -o "$tmp_dir/release.tar.gz" "$tarball_url" || fail "Download failed"

    # Verify checksum if available
    if [[ -n "$sha256_url" ]]; then
        info "Verifying checksum..."
        curl -fsSL -o "$tmp_dir/sha256sums.txt" "$sha256_url"
        local expected_hash
        expected_hash=$(awk '{print $1}' "$tmp_dir/sha256sums.txt" | head -1)
        local actual_hash
        actual_hash=$(sha256sum "$tmp_dir/release.tar.gz" | awk '{print $1}')
        [[ "$expected_hash" == "$actual_hash" ]] || fail "Checksum mismatch! Expected: $expected_hash Got: $actual_hash"
        ok "Checksum verified"
    fi

    # Extract to APP_DIR
    info "Extracting to $APP_DIR ..."
    # Backup existing installation if present
    if [[ -d "$APP_DIR" && -f "$APP_DIR/start.py" ]]; then
        info "Backing up existing installation..."
        local bak_dir="${APP_DIR}.bak-$(date +%Y%m%d%H%M%S)"
        cp -a "$APP_DIR" "$bak_dir"
        ok "Backup saved to $bak_dir"
    fi

    mkdir -p "$APP_DIR"
    tar -xzf "$tmp_dir/release.tar.gz" -C "$APP_DIR" --strip-components=0
    echo "$version" > "$APP_DIR/VERSION"

    chown -R "$APP_USER:$APP_GROUP" "$APP_DIR"
    chmod -R 775 "$APP_DIR"

    rm -rf "$tmp_dir"
    ok "Application v$version installed to $APP_DIR"
}

# --- Python Environment ---

setup_python() {
    info "Setting up Python virtual environment..."

    local venv_dir="$APP_DIR/venv"

    # Configure piwheels for precompiled ARM packages
    cat > /etc/pip.conf << 'EOF'
[global]
extra-index-url=https://www.piwheels.org/simple
EOF

    if [[ ! -d "$venv_dir" ]]; then
        sudo -u "$APP_USER" python3 -m venv "$venv_dir"
    fi

    info "Upgrading pip..."
    sudo -u "$APP_USER" "$venv_dir/bin/pip" install --upgrade pip -q

    if [[ -f "$APP_DIR/requirements.txt" ]]; then
        info "Installing Python dependencies (this may take 10-20 minutes on RPi Zero)..."
        local total
        total=$(grep -cve '^\s*$\|^\s*#' "$APP_DIR/requirements.txt" 2>/dev/null || echo "?")
        local count=0
        while IFS= read -r line; do
            # Skip empty lines and comments
            [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
            count=$((count + 1))
            local pkg="${line%%[>=<]*}"
            info "  [$count/$total] Installing $pkg..."
            sudo -u "$APP_USER" "$venv_dir/bin/pip" install "$line" -q 2>&1 | tee -a "$LOG_FILE" || true
        done < "$APP_DIR/requirements.txt"
    fi

    ok "Python environment ready"
}

# --- Systemd Service ---

setup_service() {
    info "Setting up systemd service..."

    cat > /etc/systemd/system/ledsplay.service <<EOF
[Unit]
Description=LEDsplay - Piano LED Controller
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=5
User=root
Group=root
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python3 $APP_DIR/start.py
StandardOutput=journal
StandardError=journal
Environment="PYTHONUNBUFFERED=1"
AmbientCapabilities=CAP_SYS_RAWIO
SupplementaryGroups=gpio spi kmem

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable ledsplay.service

    if [[ -f "$APP_DIR/start.py" ]]; then
        systemctl restart ledsplay.service
        ok "Service started"
    else
        info "Service configured but not started (no start.py yet)"
    fi
}

# --- Demo cache ---

generate_demo_cache() {
    local script="$APP_DIR/generate_cache.py"
    if [[ ! -f "$script" ]]; then
        info "generate_cache.py not found, skipping demo cache generation"
        return
    fi

    info "Generating MusicXML cache for bundled songs..."
    "$APP_DIR/venv/bin/python3" "$script" 2>/dev/null && ok "Demo cache generated" || \
        info "Cache generation failed (songs will be parsed on first play)"
}

# --- Summary ---

print_summary() {
    local version="unknown"
    [[ -f "$APP_DIR/VERSION" ]] && version=$(cat "$APP_DIR/VERSION")

    echo
    echo "============================================"
    echo "  LEDsplay v$version installed successfully!"
    echo "============================================"
    echo
    echo "  App directory:  $APP_DIR"
    echo "  Service:        ledsplay.service"
    echo "  Web interface:  http://ledsplay.local"
    echo
    echo "  Useful commands:"
    echo "    sudo systemctl status ledsplay.service"
    echo "    sudo journalctl -u ledsplay.service -f"
    echo
    echo "  A reboot is required to activate SPI and audio changes:"
    echo "    sudo reboot"
    echo
}

# --- Main ---

main() {
    echo
    echo "=== LEDsplay Raspberry Pi Setup ==="
    echo

    check_root
    check_os
    check_user
    install_packages
    setup_permissions
    configure_hardware
    download_latest_release
    setup_python
    generate_demo_cache
    setup_service
    print_summary
}

trap 'fail "Script failed at line $LINENO"' ERR

main "$@"
