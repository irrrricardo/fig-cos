# Quality and acceptance standard

| Check | What acceptance means |
| --- | --- |
| Appearance | Reference silhouette, proportions, direction and visible parts retained |
| Structure | Connections, branches, contacts, occlusion and negative space retained |
| Text | Correct wording, editable text, readable layout |
| Layout | Accepted text/frames and unedited regions preserved |
| Editability | Native paths/text/groups; embedded pictures explicitly disclosed |
| Provenance | Original source, native resolution, transformation and license recorded |
| Actual rendering | SVG and PowerPoint preview inspected separately |

Reference fidelity takes priority over smoothness. A clean generic object with a different shape is not a reconstruction upgrade. More paths, fewer paths, a larger PNG, no raster media, or a successful export do not establish visual/scientific correctness.

Default route: **Previous local tracing**. Experimental redraw or AI replacement requires an explicit request and stays a separate candidate until inspected. Preserve a more faithful baseline if a candidate changes the structure.

Do not infer a PDB identity from a small ribbon cartoon. Do not claim that super-resolution or tracing recovers hidden molecular detail. Library candidates must match representation and composition, not just subject matter.

Issue reports should include the minimal input/scene, command, `fig-cos doctor` output (review local paths before sharing), expected/actual behavior, and whether a real PowerPoint render was inspected.
