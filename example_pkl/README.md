# 示例几何题 (Sample Problems)

本目录存放示例题目存档,可在应用内"从文件加载"体验。
These are sample problem archives, loadable via "Load from file" in the app.

> 其他位置的 `*.gc.pkl` 默认被 git 忽略(见 .gitignore),本目录例外保留。
> Other `*.gc.pkl` files are git-ignored (see .gitignore); this directory is the exception.

## 目录 / Index

| 文件 File | 题目 / Problem | 内容 / Content |
|---|---|---|
| `2020GC1.gc.pkl` | 2020 高考 I 卷通用版 / 2020 Gaokao I general | 圆锥 + 面面垂直/体积,求 OP = √2/2 |
| `2020GC1w.gc.pkl` | 2020 高考 I 卷文科 / 2020 Gaokao I liberal arts | 同背景文科版,体积 = √6/8 |
| `2020GC1l.gc.pkl` | 2020 高考 I 卷理科 / 2020 Gaokao I science | 同背景理科版,二面角 = 2√5/5 |
| `2020GCs.gc.pkl` | 2020 新高考(山东)/ 2020 New Gaokao | 点 P,A,B,C,D,Q;求 PA = √2 |
| `2021GC1.gc.pkl` | 2021 新高考 I 卷 / 2021 New Gaokao I | 棱台 + 2AE=ED + 二面角45°;求 OC = 1 |
| `2022GC1.gc.pkl` | 2022 新高考 I 卷 / 2022 New Gaokao I | 三棱柱 + 体积4 + 面积2√2;求 AC = 2√2 |
| `2025GC1.gc.pkl` | 2025 高考全国一卷改编 / 2025 Gaokao variant | 空间点 O 到 B/D/C/P 等距;求 AB = √2,OB 含嵌套根号 |
| `gdjy2025.gc.pkl` | 高考教育卷 2025 / Gaokao Education 2025 | 12 个点 + OJ=2 + 向量等量;求 AB = 4 |
| `mytest1.gc.pkl` | 个人测试题 / Personal test | 同 2025GC1 结构 + 参数 m;可玩极值探索 |

## 真题引导 / Gaokao Guide

高考几何真题的**解题引导**(题目图片 + 输入 DSL + 标准答案)见子文档:

- [GC.gc.md](GC.gc.md) — 2020~2026 高考真题引导(含文科/理科/通用版)

每道题的"加载文件名"对应本目录的 `.gc.pkl`,按文档中的 **输入** 求解、对照 **求解** 答案即可。
The Gaokao problem guide (problem images + DSL input + answers) is in [GC.gc.md](GC.gc.md); each entry's "加载文件名" maps to a `.gc.pkl` here.

## 用法 / Usage

应用内: **添加页 → 从文件加载** 选择 `.gc.pkl` 文件。
In the app: **Add page → Load from file**, pick a `.gc.pkl` file.

或用 Python 直接读取 / Or read directly with Python:

```python
import pickle, sys
sys.path.insert(0, 'backend/src')

with open('example_pkl/2025GC1.gc.pkl', 'rb') as f:
    p = pickle.load(f)

print(p.solve('OB'))   # → ['OB = √(2√3+8)/2']  (嵌套根号已化简)
```

## 注意 / Notes

- 题目来源为高考真题改编,仅供学习,版权归原作者
- Problems are Gaokao variants for learning only; copyright belongs to the original authors.
- 加载后可直接: 求解 / 极值探索 / 函数值探索
- After loading you can directly: solve / extrema explore / function value explore.
