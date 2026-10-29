# fig-cos development conventions

- Preserve the default Previous local tracing route for reference reconstruction. Do not silently replace the reference with generic icons or newly imagined structures.
- Runtime resources live under `src/fig_cos/skills/fig-cos/`; `src/fig_cos/cli.py` is the portable dispatcher. Keep CLI examples, skill instructions and dependencies consistent.
- Preserve third-party licenses and per-asset attribution. Vendor files are hash-checked; do not relabel upstream code as original work.
- Use small, redistributable fixtures. Check source shape, text, groups, raster count and unedited regions for relevant changes. Real PowerPoint visual verification remains separate from headless tests.
- Do not commit private reference screenshots, local caches, generated work directories, credentials or machine-specific paths.
