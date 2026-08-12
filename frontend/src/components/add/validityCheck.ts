import { useDataStore } from 'stores/data';

const dataStore = useDataStore();

// prettier-ignore
const validSymbolNames = [
  // 小写英文字母（除 x, y 外）
  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
  'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
  'q', 'r', 's', 't', 'u', 'v', 'w', 'z',
  // 希腊字母的英文拼写（除 pi 外）
  'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
  'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron',
  'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega'
];

/**
 * 检查用户输入的新符号名称是否合法
 * 1. 不能和已有的符号重合
 * 2. 必须是一个小写英文字母（除 x, y 外）或希腊字母的英文拼写（除 pi 外），即在 `validSymbolNames` 中
 */
export function isValidNewSymbolName(name: string) {
  if (dataStore.symbolNames.includes(name)) {
    return false;
  }
  return validSymbolNames.includes(name);
}

/**
 * 检查用户输入的新点名称是否合法
 * 是一个不与已有的点重复的大写英文字母即可
 */
export function isValidNewPointName(name: string) {
  if (dataStore.pointNames.includes(name)) {
    return false;
  }
  const charCode = name.charCodeAt(0);
  return name.length === 1 && 65 <= charCode && charCode <= 90;
}

/**
 * 检查是否为合法的直线名
 * 是两个不相同的大写字母，且均在已有的点里即可
 */
export function isValidLineName(name: string) {
  if (name.length !== 2) {
    return false;
  }
  const [p1, p2] = name.split('') as [string, string];
  return p1 !== p2 && dataStore.pointNames.includes(p1) && dataStore.pointNames.includes(p2);
}

/**
 * 添加条件时，最简单的合法性检查函数，只要两边都有东西就行
 */
export function areBothNotEmpty(input1: string, input2: string) {
  return input1.length > 0 && input2.length > 0;
}

/**
 * 两者都是合法的直线名
 */
export function areBothValidLineNames(input1: string, input2: string) {
  return isValidLineName(input1) && isValidLineName(input2);
}

/**
 * 判断是否是合法的多边形名
 * 1. 长度正确
 * 2. 没有重复字母
 * 3. 每个字母都是合法的点名
 * @param name 需判断的多边形名
 * @param n 多边形边数
 */
function isValidPolygonName(name: string, n: number) {
  // 判断字符串长度正确且不重复
  if (name.length !== n || new Set(name).size !== n) {
    return false;
  }
  // 判断每一位均为合法点名
  for (const char of name) {
    if (!dataStore.pointNames.includes(char)) {
      return false;
    }
  }
  return true;
}

/**
 * 是合法的三角形名
 */
export function isValidTriangleName(name: string) {
  return isValidPolygonName(name, 3);
}

/**
 * 是合法的四边形名
 */
export function isValidQuadrilateralName(name: string) {
  return isValidPolygonName(name, 4);
}

/**
 * 两者都是合法的三角形名
 */
export function areBothValidTriangleNames(input1: string, input2: string) {
  return isValidTriangleName(input1) && isValidTriangleName(input2);
}

// ═══════════════════════════════════════════════
// 3D 新增校验函数
// ═══════════════════════════════════════════════

/**
 * 是合法的平面名（3D 版支持两种写法,与三角形 'ABC' 区分）:
 *   - 'pABC' : p + 三个不同大写字母（如 pABC → 平面ABC）
 *   - 'ABCD' : 四个不同大写字母（如 ABCD → 平面ABCD,四点确定/表示平面）
 * 注意: 三字母裸写 'ABC' 表示三角形,不是平面!
 */
export function isValidPlaneName(name: string) {
  if (name.startsWith('p') && name.length === 4) {
    return isValidPolygonName(name.slice(1), 3);  // pABC → ABC 三点
  }
  return isValidPolygonName(name, 4);             // ABCD → 四点
}

/**
 * 平面名统一转换为后端法向量方法需要的 'pABC' 格式:
 *   - 'pABC' → 'pABC'（不变）
 *   - 'ABCD' → 'pABC'（取前三点加 p）
 */
export function normalizePlaneName(name: string): string {
  if (name.startsWith('p')) {
    return name;
  }
  return 'p' + name.slice(0, 3);
}

/**
 * 两者都是合法的平面名（面面平行/垂直）
 */
export function areBothValidPlaneNames(input1: string, input2: string) {
  return isValidPlaneName(input1) && isValidPlaneName(input2);
}

/**
 * 一个是合法直线名(2 点)，另一个是合法平面名(3 点)（线面平行/垂直）
 * 顺序: input1 = 直线, input2 = 平面
 */
export function isValidLineAndPlaneNames(input1: string, input2: string) {
  return isValidLineName(input1) && isValidPlaneName(input2);
}

/**
 * 是合法的四面体名
 * 是四个不同的大写字母，且均在已有的点里即可（如 ABCD）
 */
export function isValidTetrahedronName(name: string) {
  return isValidPolygonName(name, 4);
}

/**
 * 两者都是合法的四面体名
 */
export function areBothValidTetrahedronNames(input1: string, input2: string) {
  return isValidTetrahedronName(input1) && isValidTetrahedronName(input2);
}

/**
 * 是一个合法点 + 一个合法平面（点面距离 dAtpBCD）
 * TODO(你确认): 后端 dAtpBCD 的格式是 dAtpBCD,即 "d" + 点 + "tp" + 平面,
 * 前端这里校验的是拆开的两个输入,格式按你的 DSL 设计
 */
export function isValidPointAndPlaneNames(input1: string, input2: string) {
  return isValidNewPointName(input1) && isValidPlaneName(input2);
}
