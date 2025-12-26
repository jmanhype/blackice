# BLACKICE

> Two paths to software generation. Choose your weapon.

```
 ██████╗ ██╗      █████╗  ██████╗██╗  ██╗██╗ ██████╗███████╗
 ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██║██╔════╝██╔════╝
 ██████╔╝██║     ███████║██║     █████╔╝ ██║██║     █████╗
 ██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██║██║     ██╔══╝
 ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗██║╚██████╗███████╗
 ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝ ╚═════╝╚══════╝
```

```
                              BLACKICE
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
        ┌───────────────────┐     ┌───────────────────┐
        │   SEAN'S PATH     │     │    YOUR PATH      │
        │   (Deterministic) │     │   (LLM-Augmented) │
        └───────────────────┘     └───────────────────┘
```

---

## Two Paths

### [Sean's Path](./seans-path/) - Deterministic Ontology-to-Code

**Status: Repos not publicly available**

| Component | Purpose |
|-----------|---------|
| ggen | Ontology → Code (Rust) |
| unrdf | RDF Knowledge Graph |
| gitvan | Git workflow automation |
| KNHK | Knowledge graph hooks |
| swarmsh-v2 | Swarm orchestration |

- No LLM hallucination
- FMEA/Poka-Yoke built-in
- Deterministic output

---

### [Your Path](./your-path/) - LLM-Augmented Brownfield

**Status: Active**

| Repo | Purpose |
|------|---------|
| speckit | Spec-driven development |
| evogit | Evolutionary code improvement |
| agentic_coding_flywheel_setup | Generate → Test → Fix loop |
| Agent-Skills-for-Context-Engineering | Context patterns |
| get-shit-done | Task ops |
| oh-my-opencode | OpenCode tooling |

- Pattern-matches existing codebases
- Local GPU inference (3090)
- Flywheel validation loop

---

## When to Use Which

| Scenario | Path |
|----------|------|
| Brand new project from spec | **Sean's** |
| Adding to existing codebase | **Yours** |
| Generating data models | **Sean's** |
| Refactoring legacy code | **Yours** |
| Mission-critical systems | **Sean's** |
| Rapid prototyping | **Yours** |

---

## Structure

```
blackice/
├── README.md
├── seans-path/
│   └── README.md           # (repos pending access)
└── your-path/
    ├── README.md
    ├── speckit/
    ├── evogit/
    ├── agentic_coding_flywheel_setup/
    ├── Agent-Skills-for-Context-Engineering/
    ├── get-shit-done/
    └── oh-my-opencode/
```

---

## Quick Start

```bash
# Clone
git clone https://github.com/jmanhype/blackice.git
cd blackice

# Your Path - explore the repos
cd your-path/
ls -la

# Set up vLLM on your 3090
pip install vllm torch
python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/deepseek-coder-6.7b-instruct \
  --gpu-memory-utilization 0.9
```

---

## License

MIT
