#!/usr/bin/env bash
# shellcheck disable=SC1091
# ============================================================
# AUTO-GENERATED FROM acfs.manifest.yaml - DO NOT EDIT
# Regenerate: bun run generate (from packages/manifest)
# ============================================================

set -euo pipefail

# Ensure logging functions available
ACFS_GENERATED_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$ACFS_GENERATED_SCRIPT_DIR/../lib/logging.sh" ]]; then
    source "$ACFS_GENERATED_SCRIPT_DIR/../lib/logging.sh"
else
    # Fallback logging functions if logging.sh not found
    # Progress/status output should go to stderr so stdout stays clean for piping.
    log_step() { echo "[*] $*" >&2; }
    log_section() { echo "" >&2; echo "=== $* ===" >&2; }
    log_success() { echo "[OK] $*" >&2; }
    log_error() { echo "[ERROR] $*" >&2; }
    log_warn() { echo "[WARN] $*" >&2; }
    log_info() { echo "    $*" >&2; }
fi

# Source install helpers (run_as_*_shell, selection helpers)
if [[ -f "$ACFS_GENERATED_SCRIPT_DIR/../lib/install_helpers.sh" ]]; then
    source "$ACFS_GENERATED_SCRIPT_DIR/../lib/install_helpers.sh"
fi

# Source contract validation
if [[ -f "$ACFS_GENERATED_SCRIPT_DIR/../lib/contract.sh" ]]; then
    source "$ACFS_GENERATED_SCRIPT_DIR/../lib/contract.sh"
fi

# Optional security verification for upstream installer scripts.
# Scripts that need it should call: acfs_security_init
ACFS_SECURITY_READY=false
acfs_security_init() {
    if [[ "${ACFS_SECURITY_READY}" == "true" ]]; then
        return 0
    fi

    local security_lib="$ACFS_GENERATED_SCRIPT_DIR/../lib/security.sh"
    if [[ ! -f "$security_lib" ]]; then
        log_error "Security library not found: $security_lib"
        return 1
    fi

    # Use ACFS_CHECKSUMS_YAML if set by install.sh bootstrap (overrides security.sh default)
    if [[ -n "${ACFS_CHECKSUMS_YAML:-}" ]]; then
        export CHECKSUMS_FILE="${ACFS_CHECKSUMS_YAML}"
    fi

    # shellcheck source=../lib/security.sh
    # shellcheck disable=SC1091  # runtime relative source
    source "$security_lib"
    load_checksums || { log_error "Failed to load checksums.yaml"; return 1; }
    ACFS_SECURITY_READY=true
    return 0
}

# Master installer - sources all category scripts

source "$ACFS_GENERATED_SCRIPT_DIR/install_base.sh"
source "$ACFS_GENERATED_SCRIPT_DIR/install_users.sh"
source "$ACFS_GENERATED_SCRIPT_DIR/install_filesystem.sh"
source "$ACFS_GENERATED_SCRIPT_DIR/install_shell.sh"
source "$ACFS_GENERATED_SCRIPT_DIR/install_cli.sh"
source "$ACFS_GENERATED_SCRIPT_DIR/install_network.sh"
source "$ACFS_GENERATED_SCRIPT_DIR/install_lang.sh"
source "$ACFS_GENERATED_SCRIPT_DIR/install_tools.sh"
source "$ACFS_GENERATED_SCRIPT_DIR/install_agents.sh"
source "$ACFS_GENERATED_SCRIPT_DIR/install_db.sh"
source "$ACFS_GENERATED_SCRIPT_DIR/install_cloud.sh"
source "$ACFS_GENERATED_SCRIPT_DIR/install_stack.sh"
source "$ACFS_GENERATED_SCRIPT_DIR/install_acfs.sh"

# Install all modules in order
install_all() {
    log_section "ACFS Full Installation"

    install_base
    install_users
    install_filesystem
    install_shell
    install_cli
    install_network
    install_lang
    install_tools
    install_agents
    install_db
    install_cloud
    install_stack
    install_acfs

    log_success "All modules installed!"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    install_all
fi
