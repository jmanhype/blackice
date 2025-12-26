# BLACKICE

> Neuro-symbolic software factory for greenfield and brownfield code generation.

```
 ██████╗ ██╗      █████╗  ██████╗██╗  ██╗██╗ ██████╗███████╗
 ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██║██╔════╝██╔════╝
 ██████╔╝██║     ███████║██║     █████╔╝ ██║██║     █████╗
 ██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██║██║     ██╔══╝
 ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗██║╚██████╗███████╗
 ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝ ╚═════╝╚══════╝
```

## What is BLACKICE?

A unified software generation factory that works for both:
- **Greenfield**: Generate code from specifications
- **Brownfield**: Extract patterns from existing code, generate compatible additions

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         BLACKICE                             │
├─────────────────────────────────────────────────────────────┤
│  CLI (blackice / ice)                                        │
├──────────────┬──────────────┬───────────────┬───────────────┤
│   Skills     │  Orchestration│   Validation  │   Extraction  │
│  greenfield  │   flywheel   │    gates      │   tree-sitter │
│  brownfield  │   pipeline   │    solvers    │   patterns    │
│  refactor    │   tasks      │    BFS/CPSAT  │   languages   │
├──────────────┴──────────────┴───────────────┴───────────────┤
│                       Inference                              │
│                    vLLM / OpenAI API                         │
├─────────────────────────────────────────────────────────────┤
│                      MCP Servers                             │
│              solver | filesystem | extraction                │
├─────────────────────────────────────────────────────────────┤
│                        Shared                                │
│                  types | config | logging                    │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone
git clone https://github.com/your-org/blackice.git
cd blackice

# Install with all dependencies
pip install -e ".[all]"

# Or install specific features
pip install -e ".[inference]"   # vLLM support
pip install -e ".[solvers]"     # OR-Tools
pip install -e ".[extraction]"  # Tree-sitter
```

## Quick Start

### Initialize a project

```bash
blackice init
```

### Generate from spec (Greenfield)

```bash
# Create a spec
cat > spec.yaml << EOF
name: user-service
version: 1.0.0
description: User management service
classes:
  - name: User
    attributes: [id, email, name]
    methods: [create, update, delete]
  - name: UserRepository
    methods: [find_by_id, find_by_email, save]
functions:
  - name: validate_email
    parameters: [email]
    return_type: bool
EOF

# Generate
blackice generate spec.yaml --output ./generated
```

### Extract from existing code (Brownfield)

```bash
# Extract patterns from existing codebase
blackice extract ./existing-project --output spec.yaml

# Generate compatible addition
blackice generate spec.yaml --mode brownfield
```

## Packages

| Package | Description |
|---------|-------------|
| `shared` | Core types, config, logging |
| `inference` | vLLM/OpenAI client, prompts |
| `extraction` | Tree-sitter parsing, pattern detection |
| `validation` | Quality gates, BFS/CP-SAT solvers |
| `orchestration` | Flywheel, pipelines, task tracking |
| `skills` | Agent skills for greenfield/brownfield |
| `mcp-servers` | MCP servers for tool integration |

## The Flywheel

BLACKICE uses an agentic flywheel pattern:

```
┌─────────────┐
│  Generate   │ ◄── LLM creates code from spec
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Validate  │ ◄── Gates check syntax, types, tests, patterns
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Fix      │ ◄── LLM fixes issues based on gate feedback
└──────┬──────┘
       │
       ▼
   Repeat until all gates pass
```

## GPU Requirements

Optimized for local GPU inference:
- **3090/4090**: Run DeepSeek Coder 6.7B or 33B
- **Smaller GPUs**: Use smaller models or quantization

## License

MIT
