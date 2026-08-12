# 示例几何题 (Sample Problems)

本目录存放示例题目存档,可在应用内"从文件加载"体验。
These are sample problem archives, loadable via "Load from file" in the app.

> 其他位置的 `*.gc.pkl` 默认被 git 忽略(见 .gitignore),本目录例外保留。
> Other `*.gc.pkl` files are git-ignored (see .gitignore); this directory is the exception.

## 目录 / Index

| 文件 File | 题目 / Problem | 内容 / Content |
|---|---|---|
| `2020GC1.gc.pkl` | 2020 高考全国一卷改编 / 2020 Gaokao Paper 1 variant | 点 O,P,D,A,E,B,C;求 OP = √2/2 |
| `2025GC1.gc.pkl` | 2025 高考全国一卷改编 / 2025 Gaokao Paper 1 variant | 空间点 O 到 B/D/C/P 等距;求 AB = √2,OB 含嵌套根号 |
| `gdjy2025.gc.pkl` | 高考教育卷 2025 / Gaokao Education Paper 2025 | 12 个点 + OJ=2 + 向量等量;求 AB = 4 |
| `mytest1.gc.pkl` | 个人测试题 / Personal test | 同 2025GC1 结构 + 参数 m;可玩极值探索 |

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
