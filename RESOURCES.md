# BLACKICE Resources & Integration

> All the tools and stacks that make this viable.

## Sean Chatman's Stack (Greenfield Core)

The proven ontology-to-code generation pipeline:

| Repo | Purpose | Integration Point |
|------|---------|-------------------|
| [ggen](https://github.com/seanchatman/ggen) | Ontology → Code generation (Rust, v5.0.2) | Greenfield generator - replaces LLM for structured output |
| [gitvan](https://github.com/seanchatman/gitvan) | Git-native workflow automation (JS, v3.1.0) | Workflow orchestration, git ops |
| [unrdf](https://github.com/seanchatman/unrdf) | RDF Knowledge Graph Platform (17 packages) | Ontology storage, semantic layer |
| [KNHK](https://github.com/seanchatman/KNHK) | Knowledge graph hooks | Event-driven ontology updates |
| [swarmsh-v2](https://github.com/seanchatman/swarmsh-v2) | Swarm orchestration | Multi-agent coordination |

**Why Sean's stack matters**:
- FMEA analysis built-in (Failure Mode and Effects Analysis)
- Poka-Yoke patterns (error-proofing)
- Proper versioning (not research-grade)
- Multiplicative leverage: 1 ontology → N code outputs

## MCP (Model Context Protocol)

| Resource | URL |
|----------|-----|
| MCP Spec | https://modelcontextprotocol.io/ |
| MCP SDK (TS) | https://github.com/modelcontextprotocol/typescript-sdk |
| MCP SDK (Python) | https://github.com/modelcontextprotocol/python-sdk |
| MCP Servers | https://github.com/modelcontextprotocol/servers |

**Integration**: Our `packages/mcp-servers/` exposes BLACKICE as MCP tools.

## Agent Frameworks

| Resource | Purpose | URL |
|----------|---------|-----|
| Claude Agent SDK | Building custom agents | https://github.com/anthropics/anthropic-sdk-python |
| Beads | Git-backed task tracking | https://github.com/anthropics/beads |
| Agent Skills | Context engineering patterns | Built into Claude Code |

## Inference

| Resource | Purpose | URL |
|----------|---------|-----|
| vLLM | Local GPU inference | https://github.com/vllm-project/vllm |
| DeepSeek Coder | Code generation model | https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct |
| Ollama | Easy local models | https://ollama.ai/ |

**3090 Setup**:
```bash
# vLLM with DeepSeek Coder
pip install vllm
python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/deepseek-coder-6.7b-instruct \
  --gpu-memory-utilization 0.9
```

## Code Analysis (Brownfield)

| Resource | Purpose | URL |
|----------|---------|-----|
| Tree-sitter | AST parsing | https://tree-sitter.github.io/tree-sitter/ |
| tree-sitter-python | Python grammar | https://github.com/tree-sitter/tree-sitter-python |
| tree-sitter-javascript | JS grammar | https://github.com/tree-sitter/tree-sitter-javascript |
| tree-sitter-typescript | TS grammar | https://github.com/tree-sitter/tree-sitter-typescript |

## Solvers & Validation

| Resource | Purpose | URL |
|----------|---------|-----|
| OR-Tools | CP-SAT constraint solver | https://developers.google.com/optimization |
| Z3 | SMT solver | https://github.com/Z3Prover/z3 |
| mypy | Type checking | https://mypy-lang.org/ |
| pytest | Testing | https://pytest.org/ |

## Patterns & Methodologies

| Resource | Description |
|----------|-------------|
| Agentic Coding Flywheel | Generate → Test → Fix → Repeat |
| EvoGit | Evolutionary code improvement |
| SpecKit | Spec-driven development |
| FMEA | Failure Mode and Effects Analysis |
| Poka-Yoke | Error-proofing patterns |

## Architecture Decision

### Greenfield Path (Sean's Stack)
```
Ontology (unrdf) → ggen → Code
                      ↓
              gitvan (commit)
```
**Use when**: Starting fresh, structured requirements, need deterministic output

### Brownfield Path (BLACKICE)
```
Existing Code → tree-sitter → Spec
                                ↓
                         LLM + Patterns → Compatible Code
```
**Use when**: Adding to existing codebase, need pattern matching

### Hybrid Path
```
Existing Code → Extract Ontology → unrdf
                                     ↓
                                   ggen → New Code (compatible)
```
**Use when**: Best of both - leverage ontology power with brownfield compatibility

---

## Quick Start with Full Stack

```bash
# 1. Clone BLACKICE
git clone https://github.com/jmanhype/blackice
cd blackice

# 2. Clone Sean's stack
git clone https://github.com/seanchatman/ggen ../ggen
git clone https://github.com/seanchatman/gitvan ../gitvan
git clone https://github.com/seanchatman/unrdf ../unrdf

# 3. Start vLLM (for brownfield LLM needs)
python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/deepseek-coder-6.7b-instruct

# 4. Install BLACKICE
pip install -e ".[all]"

# 5. Run
blackice init
blackice generate spec.yaml --mode hybrid
```
