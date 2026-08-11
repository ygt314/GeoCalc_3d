# 3D Geometry Calculator (GeoCalc_3d)

> A learning project: brute-force solid geometry with SymPy — the 3D port of [GeometryCalculator](https://github.com/zhdbk3/GeometryCalculator)

## Description

This is a **learning project**, based on [着火的冰块nya](https://b23.tv/IstwV1E)'s [GeometryCalculator](https://github.com/zhdbk3/GeometryCalculator) (GPL-3.0).

It turns high-school solid geometry (points, lines, planes, vectors, distances, angles, volumes, extrema) into an **interactive, solvable** tool:
- Add points (3D coordinates or constraints), add symbols (unknowns), add conditions (parallel / perpendicular / equidistant)
- Solve any expression: `AB` (distance), `angABC` (angle), `vABCD` (tetrahedron volume), etc.
- **Extrema exploration**: solve partial derivatives = 0 for stationary points (with function values)
- **Function value exploration**: given variable values, shows exact + float dual display
- Nested radical simplification (`sqrtdenest`, see [original issue #5](https://github.com/zhdbk3/GeometryCalculator/issues/5))

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 + SymPy (symbolic math) + pywebview |
| GUI | PyQt5 / QtWebEngine (Chromium 87) |
| Frontend | Quasar (Vue 3) + KaTeX (formula rendering) |
| Testing | pytest (81 unit tests, all green) |

## Quick Start

### Prerequisites

- Python 3.12 (virtual env managed by [uv](https://github.com/astral-sh/uv))
- Node.js + npm

### Backend

```bash
cd backend
uv sync                # create .venv and install deps (sympy/pywebview/PyQt5)
uv run pytest          # run all unit tests
```

### Frontend (dev mode, hot reload)

```bash
# Terminal 1: frontend dev server
cd frontend && npm install && npm run dev   # http://localhost:9000

# Terminal 2: backend window (loads dev server)
cd backend && DISPLAY=:0 QT_QPA_PLATFORM=xcb .venv/bin/python src/main_dev.py
```

### Release (built bundle)

```bash
# 1. Build frontend (outputs to backend/src/ui)
cd frontend && npm run build

# 2. Fix asset paths (Quasar absolute paths → file:// relative paths)
cd backend && .venv/bin/python fix_ui_paths.py

# 3. Launch release version
cd backend/src && DISPLAY=:0 QT_QPA_PLATFORM=xcb ../.venv/bin/python main.py
```

> Note: GUI requires a display (under WSLg use `DISPLAY=:0 QT_QPA_PLATFORM=xcb`).

## Usage

1. **Add symbols**: e.g. `a` (side length), `t` (parameter), with optional domain
2. **Add points**: fill 3 coordinates (may contain expressions like `a`), or set unknowns + line/plane constraints
   > Tip: in 3D a point usually needs 3 constraints (3 coordinates, or coordinates + lines). The UI only hints, never enforces
3. **Add conditions**: expression equality, line/plane parallel & perpendicular
4. **Solve**: enter an expression (e.g. `AB`, `angABC`, `vABCD`, `dAtpBCD`) → 🚀 Solve
5. **Extrema**: pick an expression (solve result or custom) → fill variables → 🔍 find stationary points
6. **Function value**: pick an expression → dialog to fill variable values → 📊 compute (exact + float)

### DSL Notation Examples

| Notation | Meaning |
|---|---|
| `AB` | distance between points A and B |
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

## Testing

```bash
cd backend
uv run pytest                  # all tests
uv run pytest tests/           # src top-level only (problem/sympy)
uv run pytest src/data/tests/  # data package only
uv run python tests/run_all.py # centralized runner
```

See [backend/TEST_LAYOUT.md](backend/TEST_LAYOUT.md).

## Sample Problem

`backend/2025GC1.gc.pkl` is a sample problem (find coordinates of point O equidistant from several points). Load it via "Load from file" in the app; details in [backend/2025GC1.example.md](backend/2025GC1.example.md).

## License

[GPL-3.0](LICENSE), original author credited (this is a 3D port for learning purposes).
