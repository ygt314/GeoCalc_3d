# 示例几何题 (Sample Problems)

本目录存放示例题目存档,可在应用内"从文件加载"体验。
These are sample problem archives, loadable via "Load from file" in the app.

> 其他位置的 `*.gc.pkl` 默认被 git 忽略(见 .gitignore),本目录例外保留。
> Other `*.gc.pkl` files are git-ignored (see .gitignore); this directory is the exception.

## 目录结构 / Layout

```
example_pkl/
├── README.md          ← 本文档
├── GC1.gc.md          ← 高考 I 卷真题引导(含文科/理科/通用版)
├── GC2.gc.md          ← 高考 II 卷真题引导
├── GC2/               ← II 卷题目存档目录(.gc.pkl 放这里)
├── gdjy2025.gc.pkl    ← 高考教育卷 2025
└── mytest1.gc.pkl     ← 个人测试题
```

## 真题引导 / Gaokao Guide

高考几何真题的**解题引导**(题目图片 + 输入 DSL + 标准答案):

- [GC1.gc.md](GC1.gc.md) — 高考 I 卷(2020~2026,文科/理科/通用版)
- [GC2.gc.md](GC2.gc.md) — 高考 II 卷(含 II 卷题目存档目录 [GC2/](GC2/))

每道题的"加载文件名"对应 `.gc.pkl`,按文档中的 **输入** 求解、对照 **求解** 答案即可。
Each entry's "加载文件名" maps to a `.gc.pkl`; follow the **输入** (input) to solve and compare with the **求解** (answer).

## 用法 / Usage

应用内: **添加页 → 从文件加载** 选择 `.gc.pkl` 文件。
In the app: **Add page → Load from file**, pick a `.gc.pkl` file.

或用 Python 直接读取 / Or read directly with Python:

```python
import pickle, sys
sys.path.insert(0, 'backend/src')

with open('example_pkl/mytest1.gc.pkl', 'rb') as f:
    p = pickle.load(f)

print(p.solve('AB'))   # 求解示例
```

## 注意 / Notes

- 题目来源为高考真题改编,仅供学习,版权归原作者
- Problems are Gaokao variants for learning only; copyright belongs to the original authors.
- 加载后可直接: 求解 / 极值探索 / 函数值探索
- After loading you can directly: solve / extrema explore / function value explore.
