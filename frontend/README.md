# 3D几何计算器 前端 (geocalc-3d-frontend)

3D几何计算器（GeoCalc_3d）的前端，由 pywebview 运行并与 Python 后端通信。

## 安装依赖

```bash
npm install
```

## 开发模式（热更新）

```bash
npm run dev
# 浏览器打开 http://localhost:9000
# 配合后端: cd backend && python src/main_dev.py
```

## 构建正式版

```bash
npm run build
# 输出到 ../backend/src/ui
# 之后运行: cd ../backend && python fix_ui_paths.py && cd src && python main.py
```

## 技术

- Quasar (Vue 3) + Vite + TypeScript
- KaTeX 公式渲染（`v-katex` 指令，见 `src/boot/katex.ts`）
- 与后端通过 `window.pywebview.api` 桥接（类型声明在 `src/types/pywebview.d.ts`）

## 注意

- Chromium 87 不支持 ES2022 API，`index.html` 已加 polyfill（`Object.hasOwn` / `Array.prototype.at`）
- 正式版需 `fix_ui_paths.py` 修正资源路径（Quasar 绝对路径 → file:// 相对路径）
