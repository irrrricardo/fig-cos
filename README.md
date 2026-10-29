# fig-cos

**An Agent Skill for reconstructing scientific figures as editable SVG and PowerPoint.**

[简体中文](README.zh-CN.md) · [Install the Skill](#quick-start--install-the-skill) · [SKILL.md](skills/fig-cos/SKILL.md) · [Gallery](docs/GALLERY.md) · [Quality standard](docs/QUALITY.md)

![CI](https://github.com/irrrricardo/fig-cos/actions/workflows/ci.yml/badge.svg)
![Agent Skill](https://img.shields.io/badge/Agent_Skill-Codex%20%7C%20Claude%20Code%20%7C%20DeepSeek_Harness-167d8d)
![Code license](https://img.shields.io/badge/code-MIT-green)

**Install fig-cos into your agent, attach a reference image, and ask the agent to use the Skill.** Its workflow defaults to **Previous local tracing**: trace individual components from the reference, preserve their appearance and structure, and rebuild text, frames and arrows separately. A blurry screenshot does not silently trigger a generic icon, a different protein fold or AI redraw.

The deliverable is the **[Skill bundle](skills/fig-cos/)**: `SKILL.md`, instructions, scripts and resources. Python helpers support the Skill; a separate CLI is optional. The Skill has no required paid drawing backend or bundled LLM API client. Your agent supplies visual inspection and orchestration using its existing tools.

## See the results

### Complex biomedical figure → editable objects

![Biomni reconstruction — historical actual PowerPoint rendering](docs/images/biomni-reconstruction.png)

Historical inspected output: **127 live text objects, 3,978 native objects, zero embedded raster pictures**. Scientific pictograms were recovered/traced locally; some generic UI icons and paper thumbnails used schematic replacements. This is an approximate reconstruction, not pixel-identical or semantic-layer recovery. Adapted from Huang et al., *Biomni*, Figure 1, [bioRxiv 2025](https://doi.org/10.1101/2025.05.30.656746), **CC BY 4.0**. [Changes and credits](docs/GALLERY.md).

### Preserve the original shape, not just its category

![Original reference, earlier imperfect library substitutions, source-derived details](docs/images/source-details.png)

The middle column is a historical imperfect substitution, shown as a comparison rather than a recommended default. The source-derived contours retain the visible biological structures more closely. Same Biomni source and attribution; additional icon credits are in the gallery.

### New designs: native editable components

![Original DNA and cell schematics — historical actual PowerPoint rendering](docs/images/editable-components.png)

Original procedural schematics, not empirical molecular/cellular measurements. [Scene](examples/procedural/scene.json) · [SVG](examples/procedural/editable.svg) · [PPTX](examples/procedural/editable.pptx).

## Quick start — install the Skill

### Codex

Ask Codex's Skill Installer:

```text
$skill-installer install https://github.com/irrrricardo/fig-cos/tree/main/skills/fig-cos
```

Or clone the repository and use the copy-only installer:

```bash
git clone https://github.com/irrrricardo/fig-cos.git
cd fig-cos
python tools/install_skill.py --agent codex
```

This installs the complete bundle into `~/.agents/skills/fig-cos/`. Then attach your reference and ask:

```text
$fig-cos Reconstruct this reference as editable SVG and PowerPoint.
Preserve the component shapes, structure and layout; use local tracing.
```

Codex discovers local skills automatically; if it does not appear, restart the session. [Official guidance](https://learn.chatgpt.com/docs/build-skills).

### Claude Code

From a clone of this repository:

```bash
python tools/install_skill.py --agent claude
```

The destination is `~/.claude/skills/fig-cos/`. Attach the image and invoke:

```text
/fig-cos Reconstruct this figure as editable SVG and PowerPoint, preserving its original shapes and layout.
```

[Claude Code Skill locations and invocation](https://code.claude.com/docs/en/skills).

### DeepSeek Harness

From a clone of this repository:

```bash
python tools/install_skill.py --agent deepseek-harness
```

The destination is `~/.dsh/skills/fig-cos/`, respecting `DSH_HOME` when set. With the Harness's filesystem Skill provider enabled, attach your image and ask:

```text
Load and use the fig-cos Skill to reconstruct this image as editable SVG and PowerPoint.
Keep the reference appearance, structure and layout.
```

This targets the official **DeepSeek Harness**, not the DeepSeek chat website or a provider API. [Official filesystem Skill provider](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md).

### Project-only or manual installation

Use `--scope project --project-dir /path/to/project`, or copy the complete `skills/fig-cos/` bundle into the host's project Skill root:

| Host | User installation | Project installation |
| --- | --- | --- |
| Codex | `~/.agents/skills/fig-cos/` | `<project>/.agents/skills/fig-cos/` |
| Claude Code | `~/.claude/skills/fig-cos/` | `<project>/.claude/skills/fig-cos/` |
| DeepSeek Harness | `~/.dsh/skills/fig-cos/` | `<project>/.dsh/skills/fig-cos/` |

You can also download the Skill ZIP from [Releases](https://github.com/irrrricardo/fig-cos/releases), unzip it, and copy the `fig-cos` folder to the selected root. **Copy the whole bundle, not only `SKILL.md`.** The helper uses Python's standard library and refuses to overwrite an existing installation. No pip package installation is required to register the Skill.

## What the agent needs

The host must be able to read files and run Python, and must provide visual inspection or an explicit text/layout manifest. The agent can prepare the bundled `requirements.txt` in its execution environment when it needs the helper scripts. **Ubuntu/glibc Linux should use Python 3.11/3.12** with the pinned VTracer version; Windows CI covers 3.11/3.13. CairoSVG may need a Cairo runtime and suitable fonts. [Runtime compatibility](docs/COMPATIBILITY.md).

Actual PowerPoint previewing additionally needs Windows + desktop PowerPoint + the optional COM dependency. Writing native PPTX does not require Office. Optional PDF recovery uses PyMuPDF (AGPL/commercial terms); it is not required for image tracing/export. Agent discovery instructions above were checked against official documentation; interactive end-to-end execution in every listed host has not been independently certified.

## Workflow and quality

- Default: source-component local tracing, live text, geometric frames/arrows and native groups.
- Explicitly requested new designs may use procedural/library/host-generated assets; those routes do not replace a reference silently.
- Compare shapes, connections, occlusion, text and layout before smoothness. More/fewer paths and a successful export are not acceptance scores.
- The output is editable SVG/PPTX with previews and source/approximation records. Hidden scientific identity, original alpha layers and semantic parts are not automatically recovered.
- Bioicons/Reactome/SciDraw connectors are optional; their individual asset licenses apply. NIH BioArt is an entry/preview resolver, not a universal SVG downloader.
- No bundled OCR, super-resolution model, image-generation backend, hosted rendering service or MCP server.

[Workflow](docs/WORKFLOW.md) · [Quality standard](docs/QUALITY.md) · [Host integration](docs/AGENTS.md).

## Optional helper CLI / development

Developers can install `python -m pip install .` to expose `fig-cos doctor`, `trace`, `compose`, `export` and other script entry points. **This is companion tooling, not the primary way users install or invoke the Skill.** See [CLI](docs/CLI.md) and [CONTRIBUTING](CONTRIBUTING.md).

```bash
python -m pip install -e ".[dev]"
python tools/validate_release.py
python -m unittest discover -s tests -v
```

## License and acknowledgement

Original code is MIT. Upstream code, icon assets and paper-derived gallery images retain their own terms; the MIT badge does not relicense them. [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md).

The native geometry/export pipeline includes public MIT code from [yrui-cmd/Cell](https://github.com/yrui-cmd/Cell), commit `2465e0adb0537c47538299dfea4de44e265a1055`. fig-cos neither reproduces nor connects to a proprietary Cell server. The portable Skill identifier is `fig-cos`; an existing private `$fig_cos` installation can remain as it is.
