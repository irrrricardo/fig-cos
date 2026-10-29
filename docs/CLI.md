# CLI reference

`fig-cos --help` lists commands. Most commands forward arguments to the corresponding bundled script; append `--help` to inspect the exact schema. JSON output and process exit codes are suitable for a host tool runner. Some export scripts log intermediate JSON in addition to their final report; use generated report files as the stable artifact record.

| Command | Function |
| --- | --- |
| `doctor` | Import/runtime checks; no application-rendering certification |
| `demo --output-dir NEW` | Self-contained procedural SVG/PPTX example |
| `install-skill --target NEW/fig-cos` | Copy portable skill without overwriting an existing directory |
| `trace` | Text-free local raster → approximate SVG component |
| `compose` | Scene JSON → SVG, optional native PPTX |
| `export` | Approved SVG/image + optional text manifest → native PPTX; default detail preset |
| `preview-ppt` | Real Windows PowerPoint render (optional extra/application) |
| `validate-svg` | Vector structure validation; not visual acceptance |
| `check-preserved` | Compare unedited DOM regions |
| `quality` | Original resolution versus placement report |
| `search-icons` | Bioicons metadata / Lucide fetch operations |
| `catalog` / `candidates` | Optional scientific library candidates |
| `normalize-svg` | Supported SVG normalization |
| `pdf-region` | Optional PDF-region source recovery |

```bash
fig-cos compose --scene examples/procedural/scene.json --output-dir outputs/my-demo --export-pptx
fig-cos search-icons search antibody --limit 3
fig-cos preview-ppt --pptx outputs/my-demo/export/editable.pptx --output-dir outputs/ppt-preview --width 2400
```

Use new output directories. Scripts do not upload the reference or call an LLM API. Library commands explicitly use network access. Only declare `--text-free` after checking the component; otherwise letters remain path outlines.
