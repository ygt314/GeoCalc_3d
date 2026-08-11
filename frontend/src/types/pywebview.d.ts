export interface DomainSettings {
  negative: boolean;
  zero: boolean;
  positive: boolean;
}

export interface LatexItem {
  id: string;
  latex: string;
}

export type AddBinCondFunc = (input1: string, input2: string) => Promise<null>;
export type AddUnaryCondFunc = (input1: string) => Promise<null>;

declare global {
  interface Window {
    pywebview: {
      api: {
        problem: {
          // 函数全部声明为箭头函数，避免 @typescript-eslint/unbound-method 报错

          add_symbol: (name: string, domain_settings: DomainSettings) => Promise<null>;

          // 3D: 多了一个 z_str 参数(在 y 之后,line 之前)
          add_point: (
            name: string,
            x_str: string,
            y_str: string,
            z_str: string,
            line1: string,
            line2: string,
          ) => Promise<null>;

          // 3D 条件方法(与 problem.py 一一对应)
          add_expr_eq: AddBinCondFunc;
          add_line_parallel_line: AddBinCondFunc;
          add_line_perp_line: AddBinCondFunc;
          add_line_parallel_plane: AddBinCondFunc;
          add_line_perp_plane: AddBinCondFunc;
          add_plane_parallel_plane: AddBinCondFunc;
          add_plane_perp_plane: AddBinCondFunc;
          // TODO(你补全): 若后端新增其它条件方法,在这里补声明
          // 2D 的 add_parallel/add_cong 等已移除(3D 不做平面几何条件)

          get_symbol_names: () => Promise<Array<string>>;
          get_point_names: () => Promise<Array<string>>;
          get_cond_ids: () => Promise<Array<string>>;

          get_symbols_latex: () => Promise<Array<LatexItem>>;
          get_points_latex: () => Promise<Array<LatexItem>>;
          get_conds_latex: () => Promise<Array<LatexItem>>;

          get_deeply_required_by: (id: string) => Promise<Array<string>>;
          del_objs: (ids: Array<string>) => Promise<null>;

          save_to_file: () => Promise<null>;
          load_from_file: () => Promise<null>;

          solve: (expr: string) => Promise<Array<string>>;

          // 极值点探索: choice 是自定义表达式(custom=true,DSL 解析)
          // 或求解结果的 LaTeX 键(custom=false,从缓存取)
          // sym_str 变量列表(空格分隔)。返回驻点 LaTeX 字符串列表
          expore_extrema: (
            choice: string,
            sym_str: string,
            custom: boolean,
          ) => Promise<Array<string>>;

          // 函数值探索: choice 同 expore_extrema, values 是 {变量名: 数值}
          // 返回函数值的字符串
          expore_func: (
            choice: string,
            sym_str: string,
            values: Record<string, number>,
            custom: boolean,
          ) => Promise<string>;
        };
        logger: {
          warning: (msg) => Promise<void>;
          error: (msg) => Promise<void>;
        };
      };
    };
  }
}
