# Your Path (LLM-Augmented Brownfield)

> Agentic coding with flywheel validation on existing codebases.

## Repositories

| Repo | Purpose | Status |
|------|---------|--------|
| [speckit](./speckit) | Spec-driven development | Your repo |
| [evogit](./evogit) | Evolutionary code improvement | Cloned |
| [agentic_coding_flywheel_setup](./agentic_coding_flywheel_setup) | Generate → Test → Fix loop | Cloned |
| [Agent-Skills-for-Context-Engineering](./Agent-Skills-for-Context-Engineering) | Context engineering patterns | Cloned |
| [get-shit-done](./get-shit-done) | Task/project ops | Cloned |
| [oh-my-opencode](./oh-my-opencode) | OpenCode tooling | Cloned |

## What This Path Does

```
Existing Code → tree-sitter → Pattern Extract → vLLM (3090) → Flywheel → Output
```

1. **Extract**: tree-sitter parses existing codebase
2. **Pattern**: Detect naming conventions, architecture patterns
3. **Generate**: vLLM on local 3090 generates compatible code
4. **Validate**: Flywheel runs gates (syntax, types, tests, patterns)
5. **Fix**: Failed gates trigger regeneration
6. **Repeat**: Until all gates pass

## When to Use This Path

| Scenario | Why Your Path |
|----------|---------------|
| Adding to existing codebase | Pattern-matches existing style |
| Refactoring legacy code | Understands context via LLM |
| Rapid prototyping | Faster iteration |
| API integrations | LLM handles edge cases |

## Local Inference Setup

```bash
# vLLM for 3090
pip install vllm torch

# Start server
python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/deepseek-coder-6.7b-instruct \
  --gpu-memory-utilization 0.9 \
  --port 8000
```

## Key Patterns from These Repos

### From agentic_coding_flywheel_setup
- Generate → Test → Fix loop
- Automatic retry on failure
- Quality gate validation

### From evogit
- Evolutionary improvement over time
- Git-based versioning of attempts

### From Agent-Skills-for-Context-Engineering
- Context management for agents
- Skill-based task decomposition

### From speckit
- Spec-driven development workflow
- Phase-based execution (specify → plan → implement)
