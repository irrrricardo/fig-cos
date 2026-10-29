---
name: fig-cos
description: Reconstruct scientific reference images as editable SVG and native PowerPoint. Default to local source-component tracing that preserves appearance, structure and layout; rebuild live text, frames and arrows separately. Also supports explicitly requested schematic design and host-generated asset assembly. Use for scientific diagrams, graphical abstracts, workflows and image-to-vector/PPT tasks, not statistical data plots or photo editing.
license: MIT; third-party assets retain their own licenses. See the repository THIRD_PARTY_NOTICES.md.
---

# fig-cos

The default reference-reconstruction route is **Previous local tracing**: crop and trace individual components from the actual reference, retain their appearance and structure, and reconstruct text/frames/arrows independently. Blurry input or a request for a cleaner image does not authorize a generic icon, new molecular fold, AI redraw or speculative repair. Use alternative redraw/design routes only when explicitly requested. Retain the more faithful baseline when a candidate changes visible structure.

The scripts run locally without a paid rendering backend, model SDK or API key. The calling agent provides image inspection, layout planning and any optional image-editing tools. Files alone do not provide vision, OCR, code execution or a hosted model.

## Select a route

| Request | Read and execute |
| --- | --- |
| Reconstruct a screenshot/PDF, including a blurry one | Local component tracing; [baseline](references/local-tracing.md), [reconstruction](references/reconstruct.md) |
| Design a new schematic from text/sketch | Text, geometry and suitable assets; [design](references/design.md) |
| Explicit library matching | Compare scientific type, representation, silhouette and composition before licensing/style; [libraries](references/icon-libraries.md) |
| Explicit AI redraw / AI asset conversion | Use an actually available host editor, inspect it, then trace/assemble; [AI bridge](references/ai-assets.md) |
| Explicit experimental structural refinement | Keep reference constraints and baseline; [refinement](references/precision-redraw.md), [fidelity research](references/reference-fidelity.md) |

Some detailed reference documents are Chinese; they describe the same local scripts. Do not load every reference at once.

## Default reconstruction

1. Keep the input and record its native pixel dimensions, component boxes, text and relationships. Crop complex illustrations rather than tracing the whole page.
2. Inspect each crop for lettering. Rebuild labels as live text, and frames/arrows as geometry. Use a host image editor only when needed/available to separate overlapping text; never pretend it ran.
3. Trace the original local artwork with the `detail` preset. Optional 2× Lanczos resampling is sampling assistance, not recovered detail; record `--original-size`. Background cleanup must preserve thin lines, holes, contacts and occlusion. Do not swap in a same-category generic object.
4. Assemble components at their reference positions/aspect ratios, with stable component IDs and individual groups. Preserve already accepted text and layout.
5. Export SVG/native PPTX; inspect the full figure and enlarged details against the input. Inspect actual PowerPoint rendering separately when available. Keep approximations, per-asset sources and licenses traceable.

Reusable component contract: [components](references/components.md). Text manifest: [text](references/text-manifest.md). Do not guess a PDB identity from a ribbon icon. Editable paths are approximate color contours, not restored semantic layers, original alpha/gradient layers or hidden biological evidence.

## Execute

`SKILL` means this directory's absolute path. Use explicit paths and new output directories. If the portable Python package is installed, equivalent `fig-cos` CLI commands are available.

```bash
python SKILL/scripts/trace_asset.py --input-image crop-2x.png --original-size 132 175 --text-free --preset detail --output-dir new-component
python SKILL/scripts/compose.py --scene scene.json --output-dir new-figure --export-pptx
python SKILL/scripts/rebuild.py --input-svg approved.svg --output-dir new-export
python SKILL/scripts/check_preserved.py --before before.svg --after after.svg --editable-component selected-icon --report preserved.json
python SKILL/scripts/preview_ppt.py --pptx new-export/editable.pptx --output-dir new-preview --width 2400
```

Python dependencies are in `requirements.txt`. Optional PDF recovery additionally needs `requirements-pdf.txt` (PyMuPDF AGPL/commercial terms). Actual PowerPoint rendering requires Windows, desktop PowerPoint and `requirements-powerpoint.txt`; it is not required merely to write PPTX. CairoSVG previews require a working Cairo runtime and suitable fonts.

Use Python 3.11/3.12 on Ubuntu/glibc Linux: the pinned VTracer 0.6.12 release has no compatible Ubuntu CPython 3.13 wheel. Windows 3.11/3.13 are covered by the repository CI matrix. Do not silently switch tracing engines to bypass this constraint.

Downloads use the external `FIG_COS_CACHE` / XDG / home cache. Network library tools are optional. Unsupported SVG forms fail explicitly; do not silently embed an image and call it a native vector reconstruction. Only supported horizontal/vertical linear gradients and orthogonal transformations are preserved by the gradient adapter.

## Acceptance and delivery

Check appearance, visible structure/connections, occlusion, negative space, text, layout and editability before stylistic smoothness. Path count, PNG size, zero media and successful export are not visual/scientific acceptance scores. A generic clean redraw that changes the reference is a failed candidate.

Deliver the requested SVG/PPTX, inspected preview, scene/code and source/approximation records. If no real PowerPoint render was inspected, say so. `visually_reviewed=false` must remain false until a person/agent actually views the image. Exact `.ai` files need separate Illustrator save/verification. Supply only the assets the user has requested and respect per-asset redistribution terms.
