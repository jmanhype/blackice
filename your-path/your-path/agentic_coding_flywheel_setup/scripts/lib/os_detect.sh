#!/usr/bin/env bash
# ============================================================
# ACFS Installer - OS Detection Library
# Detects and validates the operating system
#
# Requires: logging.sh to be sourced first for log_* functions
# ============================================================

# Fallback logging if logging.sh not sourced
if ! declare -f log_fatal &>/dev/null; then
    log_fatal() { echo "FATAL: $1" >&2; exit 1; }
    log_detail() { echo "  $1" >&2; }
    log_warn() { echo "WARN: $1" >&2; }
    log_success() { echo "OK: $1" >&2; }
fi

# Detect OS and version
# Sets: OS_ID, OS_VERSION, OS_VERSION_MAJOR, OS_CODENAME
detect_os() {
    if [[ ! -f /etc/os-release ]]; then
        log_fatal "Cannot detect OS. /etc/os-release not found."
    fi

    # shellcheck disable=SC1091
    source /etc/os-release

    export OS_ID="$ID"
    export OS_VERSION="$VERSION_ID"
    export OS_VERSION_MAJOR="${VERSION_ID%%.*}"
    export OS_CODENAME="${VERSION_CODENAME:-unknown}"

    log_detail "Detected: $PRETTY_NAME"
}

# Validate that we're running on a supported OS
# Returns 0 if supported, 1 if not (but continues with warning)
validate_os() {
    detect_os

    if [[ "$OS_ID" != "ubuntu" ]]; then
        log_warn "ACFS is designed for Ubuntu but detected: $OS_ID"
        log_warn "Proceeding anyway, but some features may not work correctly."
        return 1
    fi

    if [[ "$OS_VERSION_MAJOR" -lt 24 ]]; then
        log_warn "Ubuntu $OS_VERSION detected. Recommended: Ubuntu 24.04+ or 25.x"
        log_warn "Some packages may not be available in older versions."
        return 1
    fi

    log_success "OS validated: Ubuntu $OS_VERSION"
    return 0
}

# Check if running on a fresh VPS (heuristic)
# Returns 0 if likely fresh, 1 otherwise
is_fresh_vps() {
    local indicators=0

    # Check for minimal packages
    if ! command -v git &>/dev/null; then
        ((indicators += 1))
    fi

    # Check for default ubuntu user without customization
    if [[ -f /home/ubuntu/.bashrc ]] && ! grep -q "ACFS" /home/ubuntu/.bashrc 2>/dev/null; then
        ((indicators += 1))
    fi

    # Check for minimal installed packages
    local pkg_count
    pkg_count=$(dpkg -l 2>/dev/null | wc -l)
    if [[ $pkg_count -lt 500 ]]; then
        ((indicators += 1))
    fi

    if [[ $indicators -ge 2 ]]; then
        log_detail "Detected fresh VPS environment"
        return 0
    fi

    log_detail "Detected existing system with customizations"
    return 1
}

# Get architecture
get_arch() {
    local arch
    arch=$(uname -m)

    case "$arch" in
        x86_64)
            echo "amd64"
            ;;
        aarch64|arm64)
            echo "arm64"
            ;;
        *)
            echo "$arch"
            ;;
    esac
}

# Check if running in WSL
is_wsl() {
    if grep -qi microsoft /proc/version 2>/dev/null; then
        return 0
    fi
    return 1
}

# Check if running in Docker
is_docker() {
    if [[ -f /.dockerenv ]]; then
        return 0
    fi
    if grep -q docker /proc/1/cgroup 2>/dev/null; then
        return 0
    fi
    return 1
}
