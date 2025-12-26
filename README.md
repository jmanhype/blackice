# BLACKICE

> The integration layer for deterministic + LLM-augmented software generation.

```
 ██████╗ ██╗      █████╗  ██████╗██╗  ██╗██╗ ██████╗███████╗
 ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██║██╔════╝██╔════╝
 ██████╔╝██║     ███████║██║     █████╔╝ ██║██║     █████╗
 ██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██║██║     ██╔══╝
 ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗██║╚██████╗███████╗
 ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝ ╚═════╝╚══════╝
```

---

## Three-Repo Architecture

BLACKICE connects three repositories into a unified software generation system:

```
┌─────────────────────────────────────────────────────────────────┐
│                         BLACKICE                                 │
│                    (Integration Layer)                           │
├─────────────────────────────────────────────────────────────────┤
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │ ai-factory  │     │   speckit   │     │  external   │       │
│  │ (control)   │     │  (workflow) │     │   tools     │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│         │                    │                    │             │
│    Solvers              Spec-Driven          evogit             │
│    Gates                  Phases             flywheel           │
│    Traces               Templates            vLLM               │
│    Manifests              Beads              etc.               │
└─────────────────────────────────────────────────────────────────┘
```

| Repo | Purpose | Philosophy |
|------|---------|------------|
| [ai-factory](https://github.com/jmanhype/ai-factory) | Control plane, solvers, gates, traces | Deterministic, provable |
| [speckit](https://github.com/jmanhype/speckit) | Spec-driven workflow, Beads integration | Structured phases |
| blackice (this) | Integration, dispatch, orchestration | Connects everything |

---

## Core Repositories

### ai-factory - The Control Plane

Git-native artifact manufacturing with deterministic quality gates.

```
ai-factory/
├── specs/           # WHAT to build
├── tasks/           # Work orders
├── ops/
│   ├── procedures/  # HOW to build
│   ├── solvers/     # BFS, CP-SAT (neuro-symbolic)
│   ├── gates/       # Quality enforcement
│   └── traces/      # Run manifests (provenance)
└── repos/           # Manufactured artifacts
```

**Key Invariants:**
- Everything provable (tests + benchmarks + traces)
- Git = control plane
- No promotion without gates
- Every run yields trace

### speckit - The Workflow Engine

Specification-driven development with persistent memory.

```
constitution → specify → clarify → plan → checklist → tasks → analyze → implement
```

**Key Features:**
- Technology-agnostic specifications
- Quality gates at each phase
- Beads integration for long-term memory
- Pivotal Labs methodology (TDD, user stories, IPM)

### blackice - The Integration Layer

This repository provides:
- **Dispatch logic**: Route tasks to ai-factory solvers or LLM tools
- **Integration examples**: How to combine the repos
- **Adapters**: Wrappers for external tools (vLLM, evogit, etc.)
- **Orchestration**: Multi-repo workflows

---

## When to Use What

| Task Type | Primary Repo | Why |
|-----------|--------------|-----|
| Deterministic planning (puzzles, optimization) | ai-factory | BFS/CP-SAT solvers, provable |
| New feature from spec | speckit | Structured phases, quality gates |
| Artifact manufacturing with gates | ai-factory | Promotion rules, traces |
| Brownfield code changes | speckit + LLM tools | Pattern matching, flywheel |
| Complex multi-step workflow | blackice | Orchestrates both |

---

## Quick Start

### 1. Clone All Three

```bash
# The trio
git clone https://github.com/jmanhype/ai-factory.git
git clone https://github.com/jmanhype/speckit.git
git clone https://github.com/jmanhype/blackice.git
```

### 2. Set Up ai-factory

```bash
cd ai-factory
export FACTORY_ROOT=$(pwd)
export FACTORY_DATA_ROOT=/data/factory
mkdir -p $FACTORY_DATA_ROOT/{runs,datasets,models,cache}
```

### 3. Set Up speckit

```bash
cd ../speckit
# Copy to your project
cp -r .specify /path/to/your-project/
cp -r .claude/commands/speckit*.md /path/to/your-project/.claude/commands/
```

### 4. Use blackice for Integration

```bash
cd ../blackice
# See examples/ for integration patterns
```

---

## Integration Patterns

### Pattern 1: Spec → Factory

Use speckit for requirements, ai-factory for deterministic generation.

```
User Story → /speckit.specify → spec.md
                    ↓
            /speckit.plan → plan.md
                    ↓
            ai-factory task → deterministic output
                    ↓
            Gate validation → promotion
```

### Pattern 2: Factory → LLM Refinement

Use ai-factory for structure, LLM for polish.

```
ai-factory solver → structured solution
                    ↓
            vLLM refinement → natural language
                    ↓
            Flywheel validation → quality check
```

### Pattern 3: Full Pipeline

```
speckit.specify → speckit.plan → ai-factory.task → LLM.refine → gate.validate → promote
```

---

## External Tools (Dependencies)

These are referenced, not embedded:

| Tool | Purpose | Integration |
|------|---------|-------------|
| [evogit](https://github.com/johnnyheineken/evogit) | Evolutionary code improvement | Git-based iteration |
| [agentic_coding_flywheel_setup](https://github.com/davidvc/agentic_coding_flywheel_setup) | Generate → Test → Fix loop | Quality validation |
| [vLLM](https://github.com/vllm-project/vllm) | Local LLM inference | GPU acceleration |
| [Beads](https://github.com/jmanhype/beads) | Persistent task memory | Long-term context |

---

## Directory Structure

```
blackice/
├── README.md              # This file
├── integrations/          # Adapters connecting repos
│   ├── factory_speckit.py # ai-factory ↔ speckit bridge
│   └── llm_adapter.py     # LLM tool wrappers
├── examples/              # Usage examples
│   ├── spec_to_factory/   # Spec-driven factory task
│   └── full_pipeline/     # End-to-end workflow
└── docs/                  # Architecture docs
    ├── ARCHITECTURE.md    # How pieces connect
    └── DECISIONS.md       # Why this structure
```

---

## Philosophy

### Why Three Repos?

1. **Separation of Concerns**: Each repo has one job
2. **Independent Evolution**: Update one without breaking others
3. **Clear Ownership**: ai-factory = control, speckit = workflow, blackice = glue
4. **Composability**: Use what you need, ignore the rest

### The Deterministic + LLM Balance

```
┌─────────────────────────────────────────────────┐
│              DETERMINISTIC                       │
│  (ai-factory solvers, gates, proofs)            │
│                                                  │
│  Use when: correctness matters, math problems,  │
│            optimization, provable outputs       │
├─────────────────────────────────────────────────┤
│              LLM-AUGMENTED                       │
│  (vLLM, flywheel, pattern matching)             │
│                                                  │
│  Use when: creativity needed, brownfield code,  │
│            natural language, fuzzy requirements │
└─────────────────────────────────────────────────┘

BLACKICE dispatches to the right tool for the job.
```

---

## License

MIT
