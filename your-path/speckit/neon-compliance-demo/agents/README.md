# Agents (Rust/Tokio)

**Tech Stack**: Rust 1.75+, Tokio 1.35+, async-nats, aws-sdk-rust

## Tasks to Implement
- Initialize Rust project: `cargo init --name neon_compliance_agents`
- NATS subscriber (subscribe to `scan.aws` subject)
- AWS scanners: S3, IAM, CloudTrail
- Evidence collection and Phoenix API callbacks
- Async job processing with Tokio
- Tests: cargo test with integration tests

## Reference
- AsyncAPI spec: `../contracts/asyncapi.yaml` (NATS message formats)
- Tasks: `../specs/001-phase-0-foundations/tasks.md` (T128-T143)
- Plan: `../specs/001-phase-0-foundations/plan.md`
