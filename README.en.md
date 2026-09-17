# 3D Geometry Calculator (GeoCalc_3d)

> A learning project: brute-force solid geometry with SymPy — the 3D port of [GeometryCalculator](https://github.com/zhdbk3/GeometryCalculator)

## Description

A **learning project**, ported from [GeometryCalculator](https://github.com/zhdbk3/GeometryCalculator) by [着火de冰块nya](https://b23.tv/IstwV1E) (GPL-3.0).

It turns high-school solid geometry (points, lines, planes, vectors, distances, angles, volumes, extrema) into an **interactive, solvable** tool:
- Add points (3D coordinates or constraints), unknowns, conditions (parallel/perpendicular/equidistant)
- Solve any expression: `AB` (distance), `angABC` (angle), `vABCD` (tetrahedron volume), etc.
- **Extrema exploration**: partial derivatives to find stationary points (with function values)
- **Function value exploration**: given variable values, exact + float dual display
- Nested radical simplification (`sqrtdenest`, see [upstream issue #5](https://github.com/zhdbk3/GeometryCalculator/issues/5))

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.12+ (Windows: latest OK; Linux: 3.12) + SymPy + pywebview |
| GUI | PyQt5 / QtWebEngine (Chromium 87) |
| Frontend | Quasar (Vue 3) + KaTeX (formula rendering) |
| Tests | pytest (115 unit tests green) |

---

# Usage (end users)

> Don't want to touch code? Download the packaged program from [Releases](https://gitee.com/ygt314159/GeoCalc_3d/releases) — supports **Windows**, **WSL2 / Linux**, and **Android (QPython)**.

## Windows Users

Download the installer made with **Inno Setup** from Release:

```
geocalc3d.exe
```

**Double-click to install**, then launch from Start Menu / desktop shortcut.

> - Requires Windows 10/11 (64-bit); uses the built-in WebView2 runtime
> - No Python or any dependencies needed

## WSL2 / Linux Users

Download the split archives from Release (Gitee limits single attachments to 100MB, so the bundle is split into two):

```
GeoCalc3D-wsl2.tar.gz.aa
GeoCalc3D-wsl2.tar.gz.ab
```

**Put both in the same directory, then merge & extract:**

```bash
# Merge the two parts and extract
cat GeoCalc3D-wsl2.tar.gz.aa GeoCalc3D-wsl2.tar.gz.ab | tar xzf -
cd GeoCalc3D

# Run (requires WSLg graphics)
export DISPLAY=:0 WAYLAND_DISPLAY=wayland-0
./GeoCalc3D
```

> - If WSLg isn't enabled: ensure Windows ≥ Win11 / Win10 21H2, `wsl --update` and restart
> - Double-click also works if your file manager has WSLg association

## Android / QPython Users

> All you need is an Android phone: no root, no PC. The [QPython](https://www.qpython.com/) build runs the backend on-device and renders the UI in QPython's built-in WebView.

Download **`geocalc.zip`** from the [v1.3.1.qpython](https://gitee.com/ygt314159/GeoCalc_3d/releases/tag/v1.3.1.qpython) release. It bundles **two apps**: **plane geometry (`geocalc_2d`)** and **solid geometry (`geocalc_3d`)**.

1. **Dependencies**: install `sympy` inside QPython (the `bottle` web server is usually shipped with QPython; install it too if QPython reports it missing).
2. **Copy into the project dir**: open `geocalc.zip` with MT Manager and **enter the archive**, then copy both the `geocalc_2d` and `geocalc_3d` folders into QPython's project directory:
   ```
   /sdcard/Android/data/org.qpython.qpy/files/projects3/
   ```
3. **Run**: open QPython → tap the logo at the top to open the project list → pick `geocalc_2d` (plane) or `geocalc_3d` (solid). The app starts a local server and opens the WebView; **press Back to stop**.

> - Local ports: **8080 (2D) / 8081 (3D)**; the UI is the exact same frontend build as the desktop versions.
> - QPython's bundled Python and Termux's Python are separate environments — install dependencies in each.
> - Solving relies on SymPy; phones are slower than desktops on heavy problems.
> - Ran into a problem? Open an [issue](https://gitee.com/ygt314159/GeoCalc_3d/issues) (include your phone model + QPython version to help us reproduce).

## Usage

1. **Add unknowns**: e.g. `a` (side length), `t` (parameter), optional domain
2. **Add points**: fill 3 coordinates (may contain expressions like `a`), or unknowns + line/plane constraints
   > Tip: in 3D a point usually needs 3 constraints (3 coordinates, or coordinates + lines); the UI only hints, never forces
3. **Add conditions**: expression equality, line/plane parallel/perpendicular
4. **Solve**: enter an expression (`AB`, `angABC`, `vABCD`, `dAtpBCD`) → 🚀 Solve
5. **Extrema explore**: pick an expression (solution or custom) → fill variables → 🔍 stationary points
6. **Function value**: pick an expression → dialog for variable values → 📊 compute (exact + float)

### DSL Notation Examples

| Notation | Meaning |
|---|---|
| `AB` | distance between A and B |
| `vecAB` | vector AB |
| `angABC` | angle ∠ABC |
| `angvABCD` | angle between vectors AB and CD |
| `angrABCD` | angle between AB and plane CDE |
| `angcAB_CDE` | angle between line AB and plane CDE |
| `dAtpBCD` | distance from A to plane BCD |
| `vABCD` | volume of tetrahedron A-BCD |
| `StABC` | area of triangle ABC |
| `xP` / `yP` / `zP` | coordinates of point P |
| `nABC` | normal vector of plane ABC |

### Sample Problems

Sample problems are not bundled in the package; get them from the repo when needed:

```bash
# Clone the repo (or download just the example_pkl/ directory)
git clone https://gitee.com/ygt314159/GeoCalc_3d.git
# In the app, "Load from file" and pick a .gc.pkl under example_pkl/
```

[example_pkl/](example_pkl/) holds sample problems (Gaokao variants, personal tests, etc.); see [example_pkl/README.md](example_pkl/README.md).

---

# Development (build from source)

> Want to modify code / learn the implementation? Read on.

## Prerequisites

- Python ([uv](https://github.com/astral-sh/uv) manages the venv)
  - **Windows (10/11)**: supports the **latest Python** (tested with 3.14) for running & packaging
    — uses the built-in WebView2, zero Qt dependency, not limited by PyQt5
  - **WSL2/Linux**: needs **Python 3.12** — depends on PyQt5 (5.15.11 has no 3.13+ wheels)
- Node.js + npm

## Quick Start

### Backend

```bash
cd backend
uv sync                # create .venv, install deps (sympy/pywebview/PyQt5)
uv run pytest          # run all unit tests
```

### Frontend (dev mode, hot reload)

```bash
# Terminal 1: frontend dev server
cd frontend && npm install && npm run dev   # http://localhost:9000

# Terminal 2: backend window (loads dev server)
cd backend && DISPLAY=:0 QT_QPA_PLATFORM=xcb .venv/bin/python src/main_dev.py
```

### Release (run from source)

```bash
# 1. Build frontend (output to backend/src/ui)
cd frontend && npm run build

# 2. Fix asset paths (Quasar absolute → file:// relative)
cd backend && .venv/bin/python fix_ui_paths.py

# 3. Run release build
cd backend/src && DISPLAY=:0 QT_QPA_PLATFORM=xcb ../.venv/bin/python main.py
```

> Note: GUI needs a display (WSLg: `DISPLAY=:0 QT_QPA_PLATFORM=xcb`).

## Developing on Android: Termux vs QPython (HTTP-ified backend)

> pywebview can't run on Android Termux (QPython): Termux can't build a usable WebEngine/Qt backend, and pywebview has no headless mode. So the Android path **drops the pywebview window and falls back to a plain HTTP API service**; the frontend build is **unchanged** (inject `ui_shim.js` to map `window.pywebview.api.*` onto HTTP `/api/*`).

**Termux and QPython are two different things — don't mix them up:**

- **Termux (terminal)**: the project supports **frontend development & build** in Termux (Node + npm). The backend can't run pywebview, so it runs as an HTTP service opened via an external browser / `termux-open http://127.0.0.1:PORT` — the terminal environment **can't reach the system WebView**.
- **QPython (app)**: ships its own Python and **can drive the system WebView**. The frontend build can be dropped straight into a QPython project; the entry `main.py` starts Bottle via the `#qpy:webapp:` directive and, once the server is ready, QPython **immediately opens its built-in browser (system WebView)** at the local port — close to a native window.

| | Termux | QPython |
|---|---|---|
| Python | separate env (can't install a pywebview backend) | bundled; install `sympy`/`bottle` via QPyPI |
| System WebView | ✗ (unreachable from terminal) | ✓ (auto-opened after Bottle starts) |
| Backend | plain HTTP API service | plain HTTP API service (same `main.py`) |
| Can do | frontend dev/build | run the full app |

> The HTTP-ified backend entry is the in-package `main.py` (Bottle: serves `ui/` + `/api/<ns>/<method>` + `/api/file/save|load` + injects the shim); both environments share the same file — they only **display** differently: Termux opens a browser manually, QPython opens the WebView automatically. QPython ports: 2D = `8080`, 3D = `8081`.

## Packaging (build release artifacts)

Supports **Windows** and **WSL2/Linux**. Full guide: [backend/PACKAGING.md](backend/PACKAGING.md).

### Windows (.exe + installer)

```bash
# 1. Build the frontend
cd frontend && npm install && npm run build
# 2. PyInstaller package (run on Windows, output backend/dist/GeoCalc3D/)
cd backend
uv sync && uv pip install pyinstaller
pyinstaller GeoCalc3D.spec
# 3. (optional) Build installer geocalc3d.exe with Inno Setup (see PACKAGING.md)
```

> Windows build uses the built-in WebView2 — no Qt bundled, small size

### WSL2 / Linux (split archives)

```bash
# 1-2. Same as above: build frontend + PyInstaller package (run on WSL2)
# 3. Split into parts (Gitee limits single attachments to 100MB)
cd backend/dist
tar czf - GeoCalc3D/ | split -b 90m - GeoCalc3D-wsl2.tar.gz.
# Output: GeoCalc3D-wsl2.tar.gz.aa + .ab — users merge & extract to use
```

> `GeoCalc3D.spec` is the only packaging entry point; dist/build outputs are not committed — each developer packages in their own environment.

## Testing

```bash
cd backend
uv run pytest                  # all tests
uv run pytest tests/           # src top-level only (problem/sympy)
uv run pytest src/data/tests/  # data package only
uv run python tests/run_all.py # centralized runner
```

See [backend/TEST_LAYOUT.md](backend/TEST_LAYOUT.md).

## Major Version History

| Version | Description |
|---|---|
| v1.0.0 | Full 3D implementation, complete frontend & backend |
| v1.1.0 | DSL support for spatial solids (plane / tetrahedron / frustum, etc.) |
| v1.2.0 | Function value & extrema exploration |
| v1.3.0 | Vector solving support |
| v1.3.1 | Packaging & release: Windows installer (Inno), WSL2 split archives |
| v1.3.1.qpython | Android QPython build (plane + solid, no root) |

## License

[GPL-3.0](LICENSE), original author credited (this is a 3D port for learning purposes).
