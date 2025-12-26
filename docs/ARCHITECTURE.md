# BLACKICE Architecture

## Overview

BLACKICE is the integration layer connecting three repositories into a unified software generation system.

```
┌────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                            │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                      BLACKICE DISPATCHER                        │
│  Classifies task → routes to appropriate backend                │
└────────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   AI-FACTORY     │ │     SPECKIT      │ │    LLM TOOLS     │
│                  │ │                  │ │                  │
│ • BFS/CP-SAT     │ │ • Phases         │ │ • vLLM           │
│ • Gates          │ │ • Templates      │ │ • Flywheel       │
│ • Traces         │ │ • Beads          │ │ • Pattern match  │
│ • Promotion      │ │ • Constitution   │ │ • Generation     │
└──────────────────┘ └──────────────────┘ └──────────────────┘
         │                    │                    │
         └──────────────────┬─┴────────────────────┘
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                         OUTPUT                                  │
│  Code, artifacts, traces, manifests                             │
└────────────────────────────────────────────────────────────────┘
```

## Repository Responsibilities

### ai-factory (Control Plane)

**Purpose**: Deterministic artifact manufacturing with provable quality.

**Key Components**:
- `specs/`: What to build (machine-readable YAML)
- `tasks/`: Work orders referencing specs
- `ops/procedures/`: How to build (Python scripts)
- `ops/solvers/`: BFS, CP-SAT for planning/optimization
- `ops/gates/`: Quality enforcement functions
- `ops/traces/`: Run manifests (provenance pointers)

**When to Use**:
- Planning/optimization problems
- Anything requiring deterministic output
- Quality-gated promotions
- Traceable artifact creation

### speckit (Workflow Engine)

**Purpose**: Structured spec-driven development with persistent memory.

**Key Components**:
- `.specify/templates/`: Document templates (spec, plan, tasks)
- `.specify/memory/constitution.md`: Project principles
- `.claude/commands/`: Slash commands for workflow phases
- Beads integration for long-term memory

**Workflow Phases**:
```
constitution → specify → clarify → plan → checklist → tasks → analyze → implement
```

**When to Use**:
- New feature development
- Requirements gathering
- Structured implementation
- Long-running projects (Beads persistence)

### blackice (Integration Layer)

**Purpose**: Connect and orchestrate the other repositories.

**Key Components**:
- `integrations/dispatcher.py`: Route tasks to backends
- `integrations/adapters/`: Wrappers for external tools
- `examples/`: Usage patterns
- `docs/`: Architecture documentation

**When to Use**:
- Multi-step workflows spanning repos
- Automatic backend selection
- Pipeline orchestration

## Data Flow Examples

### Example 1: Optimization Task

```
User: "Optimize delivery routes for 10 stops"
                    │
                    ▼
            Dispatcher classifies
            (keywords: optimize, route)
                    │
                    ▼
            AI-FACTORY selected
                    │
                    ▼
            ops/solvers/cpsat_wrapper.py
                    │
                    ▼
            Solution + trace manifest
```

### Example 2: New Feature

```
User: "Add user authentication with OAuth"
                    │
                    ▼
            Dispatcher classifies
            (keywords: feature, add)
                    │
                    ▼
            SPECKIT selected
                    │
                    ▼
            /speckit.specify → spec.md
                    │
                    ▼
            /speckit.plan → plan.md
                    │
                    ▼
            /speckit.tasks → tasks.md
                    │
                    ▼
            Implementation with Beads tracking
```

### Example 3: Code Generation

```
User: "Generate unit tests for UserService"
                    │
                    ▼
            Dispatcher classifies
            (keywords: generate)
                    │
                    ▼
            LLM TOOLS selected
                    │
                    ▼
            vLLM inference
                    │
                    ▼
            Flywheel validation
                    │
                    ▼
            Generated code (validated)
```

## Integration Points

### ai-factory ↔ speckit

```python
# speckit generates spec, factory manufactures artifact
spec = speckit.specify("Add caching layer")
plan = speckit.plan(spec)
task = factory.create_task(from_plan=plan)
result = factory.run(task)
```

### ai-factory ↔ LLM

```python
# Factory solver provides structure, LLM refines
solver_result = factory.solve(optimization_problem)
refined = llm.refine(solver_result, style="user-friendly")
validated = factory.gate_check(refined)
```

### speckit ↔ LLM

```python
# Speckit provides structure, LLM generates code
spec = speckit.specify("Add API endpoint")
plan = speckit.plan(spec)
for task in plan.tasks:
    code = llm.generate(task.description, context=plan)
    speckit.beads.update(task, status="done", code=code)
```

## Configuration

### Environment Variables

```bash
# ai-factory
export FACTORY_ROOT=/path/to/ai-factory
export FACTORY_DATA_ROOT=/data/factory

# speckit
export SPECKIT_ROOT=/path/to/speckit

# LLM
export VLLM_HOST=localhost
export VLLM_PORT=8000
export VLLM_MODEL=deepseek-coder-6.7b-instruct
```

### Dispatcher Configuration

```python
from integrations.dispatcher import Dispatcher

dispatcher = Dispatcher(
    factory_root=Path("/path/to/ai-factory"),
    speckit_root=Path("/path/to/speckit"),
)
```

## Extensibility

### Adding New Backends

1. Add backend to `Backend` enum
2. Implement `_dispatch_<backend>` method
3. Add classification keywords
4. Update documentation

### Adding New Integrations

1. Create adapter in `integrations/`
2. Implement standard interface
3. Add example in `examples/`
4. Document in this file
