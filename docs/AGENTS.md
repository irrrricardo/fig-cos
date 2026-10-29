# Install and use the fig-cos Skill

The primary integration is the complete `skills/fig-cos/` directory. Its public identifier is `fig-cos`. Python helpers are resources used by the Skill; the optional CLI does not define how an agent discovers it.

## Host installation

Clone the repository, then run the standard-library-only copy helper:

```bash
python tools/install_skill.py --agent codex
python tools/install_skill.py --agent claude
python tools/install_skill.py --agent deepseek-harness
```

Choose the one host you want; do not run all three unless you intend to install into all of them. Defaults:

| Host | User root | Project root | Invocation |
| --- | --- | --- | --- |
| Codex | `~/.agents/skills/fig-cos` | `.agents/skills/fig-cos` | `$fig-cos` |
| Claude Code | `~/.claude/skills/fig-cos` | `.claude/skills/fig-cos` | `/fig-cos` |
| DeepSeek Harness | `~/.dsh/skills/fig-cos` | `.dsh/skills/fig-cos` | Ask it to load and use the `fig-cos` Skill |

For project scope: `--scope project --project-dir /your/project`. For a custom root: `--target /custom/skills/fig-cos`. Existing destinations are never overwritten. The DeepSeek user root respects `DSH_HOME`; Harness must have its filesystem Skill provider enabled. Shared `.agents/skills` roots may also be supported, but the installer uses the native `.dsh` location explicitly.

Manual installation: copy the entire `skills/fig-cos/` bundle, or unzip the portable Skill archive into the chosen root. Keep scripts, references, assets and licenses together. The installer copies files only; it does not configure your agent or install Python requirements. Ask your agent to prepare the helper environment when needed.

Official location/invocation references, checked 2026-10-29:

- [Codex Skill discovery and invocation](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [DeepSeek Harness filesystem Skill provider](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)

This is filesystem integration documentation, not a claim that each host/model combination has passed an independent interactive visual benchmark. If your host does not discover the Skill, check its settings/provider and reload its catalog or start a new session.

## Ask the agent to draw

Attach a reference and say: “Use fig-cos to reconstruct this as editable SVG and PowerPoint. Keep the original component appearance, structure and layout; use local source tracing.” The agent reads `SKILL.md`, inspects the image, records text/boxes, and invokes only the required helpers.

For a new design, explicitly say that you want a new schematic. Do not assume an unclear screenshot authorizes a generic redraw. Some detailed reference documents are Chinese; the public entry and this guide are English.

## Optional tool-runner integration

A custom harness can expose a bounded Python/CLI runner, pass file paths/scene JSON, and return output artifact references and previews. A plain text-only model cannot execute a Skill by reading Markdown alone: the host must provide files and execution, plus visual inspection or an explicit layout/text manifest. No particular LLM provider is required by the scripts.

No MCP server, hosted renderer, OCR model, super-resolution model or image-generation backend is included. Future adapters should reuse the Skill workflow and fidelity checks.
