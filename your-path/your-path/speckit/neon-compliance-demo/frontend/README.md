# Frontend (Next.js/React/TypeScript)

**Tech Stack**: Next.js 14, React 18, TypeScript 5.3+, Tailwind CSS

## Design System
- **Theme**: Tokyo Night Storm (`#1A1B26` base)
- **Grid**: 8px spacing system
- **Typography**: Inter font family
- **Accessibility**: WCAG 2.1 AA (4.5:1 contrast, keyboard nav, screen readers)

## Tasks to Implement
- Initialize Next.js: `npx create-next-app@14 . --typescript --tailwind --app --no-src-dir`
- Generate TypeScript types from OpenAPI: `specmatic generate typescript`
- Components:
  - OnboardingWizard
  - FrameworkSelectionCard, FrameworkSelectionPage
  - ReadinessGauge, ControlBreakdown, DashboardPage
  - AWSIntegrationForm, IntegrationsPage
  - ScanProgressBar, ScanResultsTable, ScanDetailPage
- Hooks: useWebSocket, useAuth
- API client (REST + WebSocket)
- Tests: Vitest + React Testing Library, Playwright E2E

## Reference
- OpenAPI spec: `../contracts/openapi.yaml` (generate types from this)
- AsyncAPI spec: `../contracts/asyncapi.yaml` (WebSocket events)
- Tasks: `../specs/001-phase-0-foundations/tasks.md` (T048, T070-T071, T090-T093, T113-T114, T144-T147)
- Plan: `../specs/001-phase-0-foundations/plan.md`

## Gemini Integration
All components should be delegated to Gemini CLI for implementation:
```bash
gemini -p "TASK: Implement <ComponentName> component..."
```
