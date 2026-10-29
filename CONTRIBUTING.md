# Contributing

Use Python 3.11+ and install `python -m pip install -e ".[dev]"`. Run `python tools/validate_release.py` and `python -m unittest discover -s tests -v` before opening a pull request. For a user-visible rendering change, include same-scale before/after previews and identify the renderer actually used.

Preserve the local-tracing default and accepted text/layout. New renderers, AI adapters or library substitutions must be optional and document their actual integration state. Do not use a generic redraw to mask a fidelity regression.

Use an issue for reproducible bugs or a focused pull request with the problem, resulting behavior, validation and limitations. Add sources/licenses for new assets. Do not contribute figures or data that cannot be redistributed under their recorded terms.

Vendor files retain upstream attribution and hashes. If an upstream file changes, update the provenance, hash manifest and applicable notices together. Do not remove attribution to simplify branding.

## Releases

Use semantic versions. Build a wheel/sdist with `python -m build`, run tests on a clean installation, and package the complete `skills/fig-cos` directory as a portable skill ZIP. Do not publish test outputs or private development archives.
