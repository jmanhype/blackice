# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Automatic Ubuntu Upgrade**: The installer now automatically upgrades Ubuntu to 25.10 before running the main ACFS installation
  - Detects current Ubuntu version and calculates sequential upgrade path
  - Handles reboots automatically via systemd resume service
  - Supports upgrade chains: 22.04 → 24.04 → 24.10 → 25.04 → 25.10
  - Creates MOTD banners to show progress to reconnecting users
  - Includes preflight checks for disk space, network, and apt state
  - Provides graceful degradation if upgrade fails but system is functional
  - Skip with `--skip-ubuntu-upgrade` flag
  - Full documentation at `docs/ubuntu-upgrade.md`

## [0.1.0] - 2024-12-20

### Added

- Initial release of ACFS (Agentic Coding Flywheel Setup)
- One-liner installer for Ubuntu VPS environments
- Web wizard at agent-flywheel.com for beginners
- Full Dicklesworthstone stack integration (8 tools)
- Three AI coding agents: Claude Code, Codex CLI, Gemini CLI
- Manifest-driven tool definitions
- Checkpointed, idempotent installation
- Interactive onboarding TUI
