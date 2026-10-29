# Agent / LLM integration

## Skill-capable agents

Install the package, then run `fig-cos install-skill --target /your/skills/fig-cos`. Alternatively, install the repository's `src/fig_cos/skills/fig-cos` directory with your client's skill installer. The `name` and directory are both `fig-cos`. Client discovery paths and invocation syntax vary; use that client's documentation.

Read `SKILL.md` first and load only the relevant references. Some detailed references are Chinese; the public entry and integration guide are English. The current default is source-component tracing, not generic reconstruction.

## Tool-calling models

Expose a bounded CLI runner in the host application, pass file paths/scene JSON, and return the CLI result and artifact references. A possible tool schema is:

```json
{"name":"fig_cos_compose","parameters":{"type":"object","properties":{"scene_path":{"type":"string"},"output_dir":{"type":"string"}},"required":["scene_path","output_dir"],"additionalProperties":false}}
```

Its host implementation runs `fig-cos compose --scene <scene_path> --output-dir <output_dir> --export-pptx`. This is an integration example, not a network service shipped here. The host should pass arguments as an array, constrain accessible files, and provide images back to the model for review.

A plain text-only chat cannot execute the skill by reading Markdown alone. For input screenshots, supply a vision-capable agent or a user-provided layout/text manifest. No particular LLM provider is required by the deterministic engine.

## Optional future adapters

No MCP server, hosted rendering service, OCR model, super-resolution model or image-generation backend is included in v0.1.0. Such adapters should reuse the CLI/engine and the same fidelity checks rather than implement a second drawing pipeline.
