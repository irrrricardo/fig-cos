# Workflow / 默认工作流

## Reference reconstruction

1. Keep the original input; record canvas size, labels, frames/arrows and component boxes. Visual reading/OCR is supplied by the calling agent, not an embedded model.
2. Crop each complex illustration. Preserve its aspect ratio, orientation, visible parts, connections and occlusion. Source-derived tracing is the default; do not substitute a generic library asset merely because its category matches.
3. Inspect lettering before declaring a crop text-free. Rebuild text as live SVG/PPT text using a manifest. If lettering overlaps artwork, use an available host editor or reconstruct the affected region explicitly; no image-generation backend is bundled.
4. Optional 2× Lanczos resampling can help contour fitting. Pass native `--original-size` to `trace`; enlargement adds no evidence. Start with `detail`, not `clean` merely to minimize objects.
5. Protect thin lines and holes while matching uniform backgrounds. Background masks and quantization can delete real connections; compare before/after crops.
6. Place components with stable IDs at reference coordinates. Use native geometry for frames/arrows and live text for labels. Scene schema and examples: [component contract](../src/fig_cos/skills/fig-cos/references/components.md), [text manifest](../src/fig_cos/skills/fig-cos/references/text-manifest.md).
7. Export SVG/PPTX, compare full page and close-ups, and render the actual PPT in PowerPoint where available. Record approximations and sources. Use `check-preserved` to verify that a local edit leaves the rest unchanged.

## Design from scratch

Use the procedural demo or a scene JSON as a starting point. Library/AI/procedural assets are allowed when requested for a new design. Molecular cartoons without confirmed structural data remain schematics. Existing generic bin/protein examples are design utilities, not restoration models.

## Deliverables

Editable SVG, native PPTX, inspected preview, runnable scene/code, text manifest where relevant, per-component provenance and license credits. If actual PPT rendering is unavailable, explicitly state that it remains unverified.
