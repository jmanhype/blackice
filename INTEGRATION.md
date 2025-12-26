# Integration Architecture

> How all the pieces connect for a viable software factory.

## The Full Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              BLACKICE                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                         ORCHESTRATION                            │    │
│  │  Flywheel: Generate → Validate → Fix → Repeat                   │    │
│  │  Pipeline: Multi-stage execution                                 │    │
│  │  Tasks: Git-backed tracking (Beads-style)                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                │                                         │
│         ┌────────────────────┬┴───────────────────┐                     │
│         ▼                    ▼                    ▼                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│  │ GREENFIELD  │     │ BROWNFIELD  │     │  VALIDATION │               │
│  │             │     │             │     │             │               │
│  │ Sean's ggen │     │ tree-sitter │     │ Gates:      │               │
│  │ unrdf onto  │     │ LLM extract │     │ - syntax    │               │
│  │ gitvan ops  │     │ patterns    │     │ - types     │               │
│  └─────────────┘     └─────────────┘     │ - tests     │               │
│         │                   │             │ - patterns  │               │
│         │                   │             │ - solvers   │               │
│         │                   │             └─────────────┘               │
│         │                   │                    │                      │
│         └───────────────────┴────────────────────┘                      │
│                             │                                            │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                         INFERENCE                                │    │
│  │  vLLM (local 3090) ←→ DeepSeek Coder 6.7B/33B                   │    │
│  │  Fallback: Ollama, OpenAI API                                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                             │                                            │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                         MCP LAYER                                │    │
│  │  Expose as tools: solve, extract, generate, validate            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Sean's Stack Integration

### ggen (Ontology → Code)

```python
# packages/greenfield/ggen_adapter.py

import subprocess
from pathlib import Path

class GgenAdapter:
    """Adapter for Sean's ggen ontology-to-code generator."""

    def __init__(self, ggen_path: Path = Path("../ggen")):
        self.ggen_path = ggen_path
        self.verify_installation()

    def verify_installation(self):
        """Verify ggen is available."""
        if not (self.ggen_path / "Cargo.toml").exists():
            raise RuntimeError(
                f"ggen not found at {self.ggen_path}. "
                "Clone from: https://github.com/seanchatman/ggen"
            )

    def generate(self, ontology_path: Path, output_dir: Path) -> dict:
        """Generate code from ontology using ggen."""
        result = subprocess.run(
            ["cargo", "run", "--", str(ontology_path), "-o", str(output_dir)],
            cwd=self.ggen_path,
            capture_output=True,
            text=True,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
```

### unrdf (Knowledge Graph)

```python
# packages/greenfield/unrdf_adapter.py

class UnrdfAdapter:
    """Adapter for Sean's unrdf knowledge graph platform."""

    def __init__(self, unrdf_path: Path = Path("../unrdf")):
        self.unrdf_path = unrdf_path

    def load_ontology(self, path: Path) -> dict:
        """Load an ontology from unrdf."""
        # unrdf uses RDF/OWL format
        pass

    def extract_to_ontology(self, code_path: Path) -> dict:
        """Extract code structure to ontology format."""
        # Bridge brownfield extraction to ontology
        pass
```

### gitvan (Git Workflow)

```python
# packages/orchestration/gitvan_adapter.py

class GitvanAdapter:
    """Adapter for Sean's gitvan git workflow automation."""

    def __init__(self, gitvan_path: Path = Path("../gitvan")):
        self.gitvan_path = gitvan_path

    def commit_artifact(self, artifact, message: str):
        """Commit generated artifact using gitvan conventions."""
        pass

    def create_branch(self, name: str, from_branch: str = "main"):
        """Create a feature branch for generation."""
        pass
```

## Viability Checklist

### What Makes This Viable (vs. toy project)

- [ ] **Sean's ggen**: Deterministic ontology→code (not just LLM hallucination)
- [ ] **FMEA patterns**: Built-in failure mode analysis
- [ ] **Poka-Yoke**: Error-proofing in the generation pipeline
- [ ] **Git-native**: Everything versioned, auditable
- [ ] **Solver verification**: BFS/CP-SAT proves correctness
- [ ] **Pattern matching**: Brownfield compatibility guaranteed
- [ ] **Local GPU**: No API dependency, runs on your 3090

### What's Different from "AI Code Gen"

| Typical AI Code Gen | BLACKICE + Sean's Stack |
|---------------------|-------------------------|
| LLM guesses code | Ontology defines structure |
| Hope it works | Solver proves it works |
| One-shot generation | Flywheel iterates to correctness |
| Ignores existing code | Pattern-matches brownfield |
| API-dependent | Local GPU (3090) |
| No versioning | Git-native artifacts |

## Dependency Graph

```
blackice (this repo)
├── ggen (Sean's) ──────────► Greenfield generation
├── gitvan (Sean's) ────────► Git workflow automation
├── unrdf (Sean's) ─────────► Ontology/knowledge graph
├── vllm ───────────────────► Local LLM inference
├── tree-sitter ────────────► Code parsing (brownfield)
├── ortools ────────────────► Constraint solving
└── mcp ────────────────────► Tool protocol
```

## Installation with Full Dependencies

```bash
# Core
pip install -e ".[all]"

# Sean's stack (clone adjacent)
cd ..
git clone https://github.com/seanchatman/ggen
git clone https://github.com/seanchatman/gitvan
git clone https://github.com/seanchatman/unrdf
cd ggen && cargo build --release
cd ../gitvan && npm install
cd ../unrdf && npm install

# vLLM for 3090
pip install vllm torch

# Start inference
python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/deepseek-coder-6.7b-instruct \
  --gpu-memory-utilization 0.9 \
  --port 8000
```

## Next Steps

1. **Wire ggen adapter** - Call ggen from greenfield skill
2. **Bridge extraction to ontology** - Output brownfield extraction as RDF
3. **gitvan integration** - Use gitvan for all git operations
4. **unrdf for spec storage** - Store specs as knowledge graph
5. **End-to-end test** - Full pipeline from spec to committed code
