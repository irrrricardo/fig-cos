# Runtime compatibility

Python 3.11+; Python dependencies are declared in `pyproject.toml`. Core tracing/export runs locally and has no model API client. CairoSVG may need the Cairo shared library from the OS. Font availability affects text layout; Arial is the historic default, not a font bundled by this project. Choose an installed font when reproducing a scene on another OS.

## Supported CI matrix

Ubuntu/glibc Linux: Python **3.11 and 3.12**. Windows: Python **3.11 and 3.13**. The pinned `vtracer==0.6.12` has no compatible manylinux CPython 3.13 wheel; use Python 3.11/3.12 on Ubuntu instead of silently substituting a different tracing engine. The package's Python minimum is not a promise that every OS/Python/CPU combination has dependency wheels. Other environments require separate verification.

| Feature | Requirement / verification boundary |
| --- | --- |
| SVG tracing, assembly, native PPTX writing | Python core dependencies; local Windows verification, Windows/Linux CI |
| PNG SVG previews | CairoSVG + a working Cairo runtime |
| PDF region recovery | `pip install ".[pdf]"`; PyMuPDF AGPL/commercial terms apply |
| Actual PowerPoint preview | Windows + installed desktop Microsoft PowerPoint + `pip install ".[powerpoint]"` |
| macOS | Intended portable core; no claim of actual macOS/PowerPoint rendering verification |
| Library searches/downloads | Network; public endpoints can change; retain each asset's license |
| AI image editing | Host-provided optional tool; no automatic external-API fallback |

Windows Cairo runtime setup varies by Python installation. Follow [CairoSVG's official instructions](https://cairosvg.org/documentation/). On Ubuntu, CI uses `apt-get install libcairo2 fonts-liberation`. No Microsoft Office installation is attempted by this package.

Downloads go to `FIG_COS_CACHE`, or `XDG_CACHE_HOME/fig-cos`, or `~/.cache/fig-cos`. The bundled Bioicons index can be read offline; update/download operations use the external writable cache rather than the installed package directory.

`doctor` tests dependency imports, not application rendering or scientific validity. The portable public skill name is `fig-cos`, matching [Agent Skills naming](https://agentskills.io/specification). Python uses `fig_cos`. Host-specific metadata is optional.
