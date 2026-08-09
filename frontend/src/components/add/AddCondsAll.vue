<template>
  <div v-for="props in addBinCondPropsArray" :key="props.relOp">
    <AddBinCond v-bind="props" />
  </div>
  <hr />
  <div v-for="props in addUnaryCondPropsArray" :key="props.condType">
    <AddUnaryCond v-bind="props" />
  </div>
</template>

<script setup lang="ts">
import AddBinCond, { type AddBinCondProps } from 'components/add/AddBinCond.vue';
import AddUnaryCond, { type AddUnaryCondProps } from 'components/add/AddUnaryCond.vue';
import {
  areBothNotEmpty,
  areBothValidLineNames,
  areBothValidPlaneNames,
  isValidLineAndPlaneNames,
  // TODO(你补全): 按需引入你需要的校验函数
  // areBothValidTriangleNames, isValidTriangleName,
  // isValidTetrahedronName, isValidPointAndPlaneNames,
} from 'components/add/validityCheck';

const problem = window.pywebview.api.problem;

/**
 * 3D 版条件按钮(与 problem.py 的条件方法一一对应)
 * 注意: 三角形全等/相似已移除 —— 立体几何少用,平面判断交给 2D 版
 */
const addBinCondPropsArray: Array<AddBinCondProps> = [
  {
    relOp: '=',
    condType: '表达式相等',
    validityCheckFunc: areBothNotEmpty,
    submitFunc: problem.add_expr_eq,
  },
  {
    relOp: '\\parallel',
    condType: '两直线平行',
    validityCheckFunc: areBothValidLineNames,
    submitFunc: problem.add_line_parallel_line,
  },
  {
    relOp: '\\perp',
    condType: '两直线垂直',
    validityCheckFunc: areBothValidLineNames,
    submitFunc: problem.add_line_perp_line,
  },
  {
    relOp: '\\parallel',
    condType: '线面平行',
    validityCheckFunc: isValidLineAndPlaneNames,
    submitFunc: problem.add_line_parallel_plane,
  },
  {
    relOp: '\\perp',
    condType: '线面垂直',
    validityCheckFunc: isValidLineAndPlaneNames,
    submitFunc: problem.add_line_perp_plane,
  },
  {
    relOp: '\\parallel',
    condType: '面面平行',
    validityCheckFunc: areBothValidPlaneNames,
    submitFunc: problem.add_plane_parallel_plane,
  },
  {
    relOp: '\\perp',
    condType: '面面垂直',
    validityCheckFunc: areBothValidPlaneNames,
    submitFunc: problem.add_plane_perp_plane,
  },
  // TODO(你补全): 如果你后端还有其它二元条件,在这里加
];

const addUnaryCondPropsArray: Array<AddUnaryCondProps> = [
  // TODO(你补全): 3D 一元条件
  // 你后端目前没有 AddUnaryCond 装饰的条件方法(2D 的平行四边形/正方形等是平面概念),
  // 如果以后加"共面""等边四面体"等,在这里配。
  // 示例:
  // {
  //   condType: '共面',
  //   validityCheckFunc: isValidTetrahedronName,
  //   submitFunc: problem.add_coplanar,
  // },
];
</script>
