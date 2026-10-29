# A figure you can keep editing

![Labels, colors and layout in action](../../docs/images/editable-in-action.gif)

Open [before.svg](before.svg), [after.svg](after.svg) or the [editable PowerPoint](after.pptx).

1. Change the cell-panel heading to **Study group A**.
2. Switch the DNA strands to teal/coral and the highlighted cell to gold.
3. Move the grouped cell artwork by **22, -10** source-coordinate units.

The four `step-*.svg` files are the actual animation states. The GIF is rendered from these SVG states with CairoSVG; the PPTX contains native text, paths and groups. The starting artwork is fig-cos's original procedural DNA/cell example. Artwork/code: MIT.

Reproduce the edits:

```bash
python examples/editing/edit.py --output outputs/edited.svg
```
