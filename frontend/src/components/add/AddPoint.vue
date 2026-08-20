<template>
  <div class="point-btns">
    <q-btn :icon="ionAddOutline" @click="dialogOpen = true">添加点</q-btn>
    <q-btn :icon="ionLocateOutline" @click="originOpen = true">添加原点</q-btn>
    <q-btn :icon="ionMoveOutline" @click="moveOpen = true">平移添加点</q-btn>
    <!-- 向量指点: 基点 + 向量 = 新点 -->
    <q-btn :icon="ionNavigateOutline" @click="openVec">向量指点</q-btn>
  </div>
  <q-dialog v-model="dialogOpen" persistent>
    <q-card>
      <q-form @reset="reset" @submit="submit">
        <q-card-section>
          <h1>添加点坐标</h1>
          <h2>名称</h2>
          <q-input v-model="name" dense />
          <h2>3D 确定点需要 3 个约束:填 3 个坐标,或坐标+直线组合共 3 项</h2>
          <div class="container">
            <label>横坐标</label>
            <q-input v-model="x_str" dense placeholder="表达式 / 输入 x 设未知数" />
          </div>
          <div class="container">
            <label>纵坐标</label>
            <q-input v-model="y_str" dense placeholder="表达式 / 输入 y 设未知数" />
          </div>
          <!-- 竖坐标输入框,3D 新增
               同样支持"输入 z 设未知数" -->
          <div class="container">
            <label>竖坐标</label>
            <q-input v-model="z_str" dense placeholder="表达式 / 输入 z 设未知数" />
          </div>
          <div class="container">
            <label>在直线</label>
            <q-input v-model="line1" dense />
            <label>上</label>
          </div>
          <div class="container">
            <label>在直线</label>
            <q-input v-model="line2" dense />
            <label>上</label>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn v-close-popup type="reset">取消</q-btn>
          <q-btn type="submit" class="primary" :disable="!isValid">确认</q-btn>
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>

  <!-- 添加原点弹框: 只需名称,坐标自动 (0,0,0) -->
  <q-dialog v-model="originOpen" persistent>
    <q-card>
      <q-form @reset="originReset" @submit="submitOrigin">
        <q-card-section>
          <h1>添加原点</h1>
          <h2>名称(通常是 O)</h2>
          <q-input v-model="originName" dense />
          <div class="hint">原点坐标为 (0, 0, 0)</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn v-close-popup type="reset">取消</q-btn>
          <q-btn type="submit" class="primary" :disable="!isValidOriginName">确认</q-btn>
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>

  <!-- 平移添加点弹框: 点名称 + 操作表达式(DSL,直接透传后端) -->
  <q-dialog v-model="moveOpen" persistent>
    <q-card>
      <q-form @reset="moveReset" @submit="submitMove">
        <q-card-section>
          <h1>平移添加点</h1>
          <h2>点名称</h2>
          <q-input v-model="moveName" dense placeholder="如 E" />
          <h2>操作表达式(支持 DSL 语法)</h2>
          <q-input v-model="moveWay" dense placeholder="如 xA+1" />
          <div class="hint">新点 = 沿该轴平移基点,如 xA+1 → (xA+1, yA, zA)</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn v-close-popup type="reset">取消</q-btn>
          <q-btn type="submit" class="primary" :disable="!isValidMove">确认</q-btn>
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>

  <!-- 向量指点弹框: 基点 + 向量表达式 = 新点 -->
  <q-dialog v-model="vecOpen" persistent>
    <q-card>
      <q-form @reset="vecReset" @submit="submitVec">
        <q-card-section>
          <h1>向量指点</h1>
          <h2>点名称</h2>
          <q-input v-model="vecName" dense placeholder="如 C" />
          <h2>基点(留空则用原点)</h2>
          <q-input v-model="vecBase" dense placeholder="如 A(可留空)" />
          <h2>向量表达式(支持 DSL 语法)</h2>
          <q-input v-model="vecWay" dense placeholder="如 vecAB 或 (1, 0, 0)" />
          <div class="hint">新点 = 基点 + 向量,如 A + vecAB</div>
          <!-- 基点留空但未设置原点: 提示并禁用确认 -->
          <div v-if="vecBase.trim().length === 0 && origPoint.length === 0" class="warn">
            ⚠️ 基点留空需要使用原点,请先点击"添加原点"
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn v-close-popup type="reset">取消</q-btn>
          <q-btn type="submit" class="primary" :disable="!isValidVec">确认</q-btn>
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ionAddOutline, ionLocateOutline, ionMoveOutline, ionNavigateOutline } from '@quasar/extras/ionicons-v8';
import { ref, computed } from 'vue';
import { isValidNewPointName } from 'components/add/validityCheck';
import { useDataStore } from 'stores/data';

const dialogOpen = ref(false);

const name = ref('');
const x_str = ref('');
const y_str = ref('');
// z_str —— 3D 新增的竖坐标
const z_str = ref('');
const line1 = ref('');
const line2 = ref('');

// ── 原点添加 ──
const originOpen = ref(false);
const originName = ref('');

// 原点名称合法: 与普通点相同(单个大写字母,未占用)
const isValidOriginName = computed(
  () => isValidNewPointName(originName.value) && !dataStore.pointNames.includes(originName.value),
);

function originReset() {
  originName.value = '';
}

function submitOrigin() {
  window.pywebview.api.problem
    .add_O_point(originName.value)
    .then(() => {
      dataStore.pointNames.push(originName.value);
      originOpen.value = false;
      originReset();
    })
    .catch((e) => {
      alert('添加原点失败 qwq\n' + e);
    });
}

// ── 平移添加点 ──
const moveOpen = ref(false);
const moveName = ref('');
const moveWay = ref('');   // 操作表达式(DSL),直接透传后端,如 xA+1

// 点名称合法 + 操作表达式格式正确(至少 <轴><点> 如 xA)
const isValidMove = computed(
  () =>
    isValidNewPointName(moveName.value) &&
    !dataStore.pointNames.includes(moveName.value) &&
    moveWay.value.trim().length >= 4,
);

function moveReset() {
  moveName.value = moveWay.value = '';
}

function submitMove() {
  // 操作表达式直接透传后端(支持 DSL: 符号/表达式/数值)
  window.pywebview.api.problem
    .add_point_from_move(moveName.value, moveWay.value.trim())
    .then(() => {
      dataStore.pointNames.push(moveName.value);
      moveOpen.value = false;
      moveReset();
    })
    .catch((e) => {
      alert('平移添加失败 qwq\n' + e);
    });
}

// ── 向量指点: 基点 + 向量 = 新点 ──
const vecOpen = ref(false);
const vecName = ref('');
const vecBase = ref('');
const vecWay = ref('');
// 已设置的原点(空 = 未设置)。基点留空时依赖它,未设置则拒绝
const origPoint = ref('');

// 打开弹框时查询后端原点状态(每次打开都刷新)
function openVec() {
  vecOpen.value = true;
  void window.pywebview.api.problem.get_orig_point().then((r) => {
    origPoint.value = r;
  });
}

// 点名称合法 + 向量表达式非空 + 基点有效
// 基点留空时: 必须已设置原点(origPoint 非空),否则拒绝(按钮变灰)
const isValidVec = computed(
  () =>
    isValidNewPointName(vecName.value) &&
    !dataStore.pointNames.includes(vecName.value) &&
    vecWay.value.trim().length > 0 &&
    (vecBase.value.trim().length > 0 || origPoint.value.length > 0),
);

function vecReset() {
  vecName.value = vecBase.value = vecWay.value = '';
}

function submitVec() {
  window.pywebview.api.problem
    .add_point_from_vec(vecName.value, vecBase.value.trim(), vecWay.value.trim())
    .then(() => {
      dataStore.pointNames.push(vecName.value);
      vecOpen.value = false;
      vecReset();
    })
    .catch((e) => {
      alert('向量指点失败 qwq\n' + e);
    });
}

const notEmpty = (str: string) => str.length > 0;
/**
 * 1. 点名称合法
 * 2. 只提示不强制: 不限制填写项数,把决定权交给用户/后端
 *    (提示语已说明"3D 通常需要 3 个约束",但万一有特殊场景
 *    比如 2 个约束恰好确定点,让用户自己试,后端会兜底报错)
 *    这里只要求: 至少填了 1 项
 */
const isValid = computed(
  () =>
    isValidNewPointName(name.value) &&
    // 至少填一项(不强制 3 项,决定权给用户)
    +notEmpty(x_str.value) +
      +notEmpty(y_str.value) +
      +notEmpty(z_str.value) +
      +notEmpty(line1.value) +
      +notEmpty(line2.value) >=
      1,
);

function reset() {
  // 加入 z_str.value = ''
  name.value = x_str.value = y_str.value = z_str.value = line1.value = line2.value = '';
}

const dataStore = useDataStore();

function submit() {
  window.pywebview.api.problem
    // 传入 z_str.value(位置在 y 之后,line1 之前)
    .add_point(name.value, x_str.value, y_str.value, z_str.value, line1.value, line2.value)
    .then(() => {
      dataStore.pointNames.push(name.value);
      // 可能有未知数的添加
      // 条件里加 z_str.value === 'z'
      if (x_str.value === 'x' || y_str.value === 'y' || z_str.value === 'z') {
        void window.pywebview.api.problem.get_symbol_names().then((result) => {
          Object.assign(dataStore.symbolNames, result);
        });
      }
      // 一定要最后再重置
      dialogOpen.value = false;
      reset();
    })
    .catch((e) => {
      alert('解析失败 qwq\n' + e);
    });
}
</script>

<style scoped>
.point-btns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5em;
  max-width: 400px;
}

.container {
  display: flex;
  align-items: center;
  gap: 0.5em;
  margin: 0.5em;
}

.container .q-input {
  flex-grow: 1;
}

.hint {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
}

.warn {
  font-size: 12px;
  color: #c62828;
  margin-top: 6px;
  padding: 4px 8px;
  background: #ffebee;
  border-radius: 4px;
}
</style>
