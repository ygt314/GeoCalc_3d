'''
数据操作
'''

from collections import deque
import pickle

from data import MathObj, GCSymbol, GCPoint, Cond
from type_hints import LatexItem

from webview import windows, FileDialog

class DataOperate:
    def __init__(self):
        self.math_objs: dict[str, MathObj] = {}
        self.symbol_names: list[str] = []
        self.point_names: list[str] = []
        self.cond_ids: list[str] = []
        # 记录原点
        self.orig_point = ''
    # ═══════════════════════════════════════════════════════
    # 第六部分：查询 / 删除 / 存取（抄 2D 原版，几乎不改）
    # ═══════════════════════════════════════════════════════
    def get_symbol_names(self) -> list[str]:
        return self.symbol_names
    
    def get_point_names(self) -> list[str]:
        return self.point_names
    
    def get_orig_point(self) -> str:
        """返回已设置的原点(空字符串 = 未设置,add_O_point 后才有值)"""
        return self.orig_point
    
    def get_cond_ids(self) -> list[str]:
        return self.cond_ids
    
    def get_symbols_latex(self) -> list[LatexItem]:
        """
        获取需要在前端页面上展示的符号的 LaTeX，包含取值范围（含始末 $ $）
        相同取值范围的符号会被并到一起
        :return: 一个列表，每项为一个字典（对象）
                 id: 取值范围的 LaTeX，用于前端 ``v-for`` 的 ``key``
                 latex: 该取值范围的完整的 LaTeX
        """
        # 将每个符号名挂到其取值范围上
        domain_names_dict: dict[str, list[str]] = {}
        for name in self.symbol_names:
            gc_symbol: GCSymbol = self.math_objs[name]  # type: ignore
            name_latex = gc_symbol.get_name_latex()
            domain_latex = gc_symbol.get_domain_latex()
            if domain_latex not in domain_names_dict:
                domain_names_dict[domain_latex] = []
            domain_names_dict[domain_latex].append(name_latex)
    
        # 生成结果
        result = []
        for domain, names in domain_names_dict.items():
            result.append({
                'id': domain,
                'latex': fr"$ \displaystyle {', '.join(names)} \in {domain} $"
            })
    
        return result
    
    def get_points_latex(self):
        """获取所有点的 LaTeX（3D 版点的 LaTeX 是三元组，但本方法逻辑不变）"""
        result = []
        for name in self.point_names:
            result.append({
                'id': name,
                'latex': fr'$ \displaystyle {self.math_objs[name].get_latex()} $'  # type: ignore
            })
        return result
    
    def get_conds_latex(self):
        """获取所有条件的 LaTeX（原始 + 方程，本方法逻辑不变）"""
        result = []
        for cond_id in self.cond_ids:
            cond: Cond = self.math_objs[cond_id]  # type: ignore
            result.append({
                'id': fr'$$ {cond.get_raw_latex()} $$',
                'latex': cond.get_eqs_latex()
            })
        return result
    
    def get_deeply_required_by(self, identifier: str) -> list[str]:
        """查询一个对象被哪些对象依赖（含后代，BFS）—— 抄 2D 原版，一字不改"""
        # BFS
        result = set()
        visited = {identifier}
        queue = deque([identifier])
    
        while len(queue) > 0:
            current_id = queue.popleft()
            for i in self.math_objs[current_id].required_by:
                if i not in visited:
                    result.add(i)
                    visited.add(i)
                    queue.append(i)
    
        return list(result)
    
    def del_objs(self, ids: list[str]) -> None:
        """删除对象及其依赖关系 —— 抄 2D 原版，一字不改"""
        for i in ids:
            # 删除对象
            del self.math_objs[i]
            # 列表除名
            for l in [self.symbol_names, self.point_names, self.cond_ids]:
                if i in l:
                    l.remove(i)
        # 删除依赖关系
        for obj in self.math_objs.values():
            obj.required_by -= set(ids)
    # 读写3D pickle文件
    def save_to_file(self) -> None:
        path = windows[0].create_file_dialog(FileDialog.SAVE, file_types=('几何计算器 pickle 文件 (*.gc.pkl)',))
        if path is not None:
            path = path[0]
            with open(path, 'wb') as f:
                pickle.dump(self, f)
    
    def load_from_file(self) -> None:
        path = windows[0].create_file_dialog(FileDialog.OPEN, file_types=('几何计算器 pickle 文件 (*.gc.pkl)',))
        if path is not None:
            path = path[0]
            with open(path, 'rb') as f:
                self.__dict__ = pickle.load(f).__dict__
