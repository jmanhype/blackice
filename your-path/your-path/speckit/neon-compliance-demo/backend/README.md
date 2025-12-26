# Backend (Phoenix/Elixir)

**Tech Stack**: Phoenix 1.7+, Elixir 1.16+, PostgreSQL 15+, NATS 2.10+

## Tasks to Implement
- Initialize Phoenix project: `mix phx.new . --app neon_compliance --database postgres --no-html`
- Database migrations (RLS policies, multi-tenant tables)
- Authentication (JWT with Guardian)
- NATS publisher for agent communication
- REST API controllers per OpenAPI spec
- Phoenix Channels for WebSocket real-time updates
- Contexts: Accounts, Frameworks, Programs, Integrations, Evidence
- Tests: ExUnit with 90%+ coverage

## Reference
- OpenAPI spec: `../contracts/openapi.yaml`
- AsyncAPI spec: `../contracts/asyncapi.yaml`
- Tasks: `../specs/001-phase-0-foundations/tasks.md` (T016-T036, backend tasks from US1-US5)
- Plan: `../specs/001-phase-0-foundations/plan.md`
