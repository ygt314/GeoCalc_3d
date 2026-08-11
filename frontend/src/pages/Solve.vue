<template>
  <q-page>
    <h1>计算求解</h1>

    <!-- ═══════════ ① 求解区(独立) ═══════════ -->
    <div>请输入要计算的表达式：</div>
    <q-input v-model="expr" dense />
    <div class="container">
      <q-btn :disable="expr.length === 0 || solving" @click="solve" class="primary"
        > 🚀 求解！
      </q-btn>
      <q-linear-progress indeterminate v-if="solving" />
      <div id="duration">用时 {{ duration }}</div>
    </div>
    <div v-if="solutions.length > 0">
      <div>以下是所有可能的解：</div>
      <div
        v-for="s in solutions"
        :key="s"
        class="solution-row"
        :class="{ selected: selectedDisplay === s }"
        @click="pickSolution(s)"
        v-katex
      >$$ {{ s }} $$
      </div>
      <div class="hint">👆 点击某个解,选中为极值探索对象</div>
    </div>

    <hr />

    <!-- ═══════════ ② 极值探索区(独立) ═══════════ -->
    <h2>🔍 极值点探索</h2>

    <!-- 探索对象来源选择 -->
    <div class="container">
      <q-radio v-model="exploreSource" val="solution" label="用求解结果" />
      <q-radio v-model="exploreSource" val="custom" label="自定义表达式" />
    </div>

    <!-- 自定义表达式输入(仅当选择自定义) -->
    <div v-if="exploreSource === 'custom'" class="container">
      <label>表达式</label>
      <q-input v-model="customExpr" dense placeholder="如 t**2 - 2*t + 1" />
    </div>
    <!-- 用求解结果时,直接渲染选中的解(KaTeX),无文本框 -->
    <div v-else-if="exploreSource === 'solution'" class="container">
      <label>选中的解</label>
      <span v-if="selectedKey" class="selected-solution" v-katex>
        $ {{ selectedDisplay }} $
      </span>
      <span v-else class="hint">(先点击上方求解结果,选择要探索的解)</span>
    </div>

    <!-- 探索变量 -->
    <div class="container">
      <label>探索变量</label>
      <q-input v-model="exploreSyms" dense placeholder="空格分隔,如 t u" />
    </div>

    <div class="container">
      <q-btn
        :disable="!canExplore || exploring"
        color="secondary"
        @click="explore"
      > 🔍 极值探索
      </q-btn>
      <!-- 函数值探索: 弹框输入变量值 -->
      <q-btn
        :disable="!canExplore || exploring"
        color="accent"
        @click="openFuncPicker"
      > 📊 函数值探索
      </q-btn>
      <q-linear-progress indeterminate v-if="exploring" />
    </div>

    <!-- 函数值探索弹框: 输入各变量取值 -->
    <q-dialog v-model="funcPickerOpen">
      <q-card style="min-width: 400px">
        <q-card-section>
          <h2>📊 函数值探索</h2>
          <div class="hint">
            对
            <span v-if="exploreSource === 'solution'">{{ selectedDisplay }}</span>
            <span v-else>{{ customExpr }}</span>
            计算函数值
          </div>
          <div v-for="s in exploreSymsList" :key="s" class="container">
            <label>{{ s }} =</label>
            <q-input v-model="funcValues[s]" dense placeholder="输入数值" type="number" step="any" />
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn v-close-popup flat label="取消" />
          <q-btn v-close-popup color="accent" :disable="!funcValuesReady" @click="exploreFunc"
            > 计算 </q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- 探索结果 -->
    <div v-if="exploreDone">
      <div>可能的驻点：</div>
      <div v-for="(e, i) in extrema" :key="i">
        点{{ i + 1 }}: <span v-katex>$ {{ e }} $</span>
      </div>
    </div>
    <div v-else-if="exploreError" class="warn">
      🔍 极值探索:{{ exploreError }}
    </div>

    <!-- 函数值探索结果 -->
    <div v-if="funcResult !== ''" class="func-result">
      <hr />
      <div>
        📊 函数值:
        <span v-if="exploreSource === 'solution'">{{ selectedDisplay }}</span>
        <span v-else>{{ customExpr }}</span>
        在
        <span v-for="(v, s) in funcValues" :key="s">{{ s }}={{ v }} </span>
        处 = <span ref="funcResultEl" v-html="funcResultHtml"></span>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import katex from 'katex';

// ── 求解区 ──
const expr = ref('');
const solving = ref(false);
const solutions = ref<Array<string>>([]);
const selectedDisplay = ref('');       // 选中的完整解(显示用,如 't = 2')
const selectedKey = ref('');           // 选中的纯 latex 键(传给后端,如 '2')

// 选中某个解: 提取等号右边的纯 latex 作为后端缓存键
function pickSolution(s: string) {
  selectedDisplay.value = s;
  const eqIdx = s.indexOf(' = ');
  selectedKey.value = eqIdx >= 0 ? s.slice(eqIdx + 3) : s;
}

function solve() {
  solving.value = true;
  solutions.value = [];
  selectedDisplay.value = '';
  selectedKey.value = '';
  window.pywebview.api.problem
    .solve(expr.value)
    .then((result) => {
      solutions.value = result;
    })
    .catch((e) => {
      alert('求解出错 qwq\n' + e);
    })
    .finally(() => {
      solving.value = false;
    });
}

// ── 极值探索区 ──
const exploreSource = ref<'solution' | 'custom'>('solution'); // 探索对象来源
const customExpr = ref('');        // 自定义表达式
const exploreSyms = ref('');       // 探索变量
const exploring = ref(false);
const exploreDone = ref(false);
const extrema = ref<Array<string>>([]);
const exploreError = ref('');

// ── 函数值探索区 ──
const funcPickerOpen = ref(false);   // 弹框开关
const funcValues = ref<Record<string, string>>({});  // 变量 → 输入值
const funcResult = ref('');          // 函数值结果
// 用 katex.renderToString 显式渲染(避免 v-katex 指令在 v-if 挂载时序问题)
const funcResultHtml = ref('');

// 探索变量列表(空格分隔 → 数组)
const exploreSymsList = computed(() =>
  exploreSyms.value.trim().split(/\s+/).filter(Boolean),
);

// 打开弹框: 初始化变量输入框
function openFuncPicker() {
  funcValues.value = {};
  for (const s of exploreSymsList.value) {
    funcValues.value[s] = '';
  }
  funcResult.value = '';
  funcResultHtml.value = '';
  funcPickerOpen.value = true;
}

// 所有变量都已填值
const funcValuesReady = computed(
  () => exploreSymsList.value.length > 0
    && exploreSymsList.value.every((s) => funcValues.value[s] !== '' && funcValues.value[s] !== undefined),
);

// 计算函数值: 把变量值 dict 传给后端
function exploreFunc() {
  const syms = exploreSyms.value.trim();
  const values: Record<string, number> = {};
  for (const s of exploreSymsList.value) {
    values[s] = Number(funcValues.value[s]);
  }
  funcResult.value = '';
  funcResultHtml.value = '';
  const done = (r: string) => {
    funcResult.value = r;
    // 后端返回的数字字符串(如 '1')也能被 katex 渲染
    funcResultHtml.value = katex.renderToString(r, { throwOnError: false });
  };
  if (exploreSource.value === 'solution') {
    window.pywebview.api.problem
      .expore_func(selectedKey.value, syms, values, false)
      .then(done)
      .catch((e) => { alert('函数值探索出错 qwq\n' + e); });
  } else {
    window.pywebview.api.problem
      .expore_func(customExpr.value, syms, values, true)
      .then(done)
      .catch((e) => { alert('函数值探索出错 qwq\n' + e); });
  }
}

// 是否可以探索
const canExplore = computed(() => {
  if (exploreSyms.value.trim().length === 0) return false;
  if (exploreSource.value === 'solution') {
    return selectedKey.value.length > 0;   // 需选中一个解(有纯 latex 键)
  }
  return customExpr.value.trim().length > 0;    // 需填自定义表达式
});

function explore() {
  exploring.value = true;
  exploreDone.value = false;
  exploreError.value = '';
  extrema.value = [];
  const syms = exploreSyms.value.trim();
  if (exploreSource.value === 'solution') {
    // 用求解结果: choice = 选中解的纯 latex 键, custom=False(从缓存字典取)
    window.pywebview.api.problem
      .expore_extrema(selectedKey.value, syms, false)
      .then((result) => {
        extrema.value = result;
        exploreDone.value = true;
      })
      .catch((e) => {
        exploreError.value = String(e);
      })
      .finally(() => {
        exploring.value = false;
      });
  } else {
    // 自定义表达式: choice = 表达式字符串, custom=True(DSL 解析)
    window.pywebview.api.problem
      .expore_extrema(customExpr.value, syms, true)
      .then((result) => {
        extrema.value = result;
        exploreDone.value = true;
      })
      .catch((e) => {
        exploreError.value = String(e);
      })
      .finally(() => {
        exploring.value = false;
      });
  }
}

// 计时器
const duration = ref('00:00:00');
const t1 = ref(0);
const t2 = ref(0);
setInterval(() => {
  if (solving.value) {
    t2.value = Date.now();
    const t = (t2.value - t1.value) / 1000;
    let h: number | string = Math.floor(t / 3600);
    let m: number | string = Math.floor((t % 3600) / 60);
    let s: number | string = Math.floor(t % 60);
    h = h.toString().padStart(2, '0');
    m = m.toString().padStart(2, '0');
    s = s.toString().padStart(2, '0');
    duration.value = `${h}:${m}:${s}`;
  }
}, 100);
</script>

<style scoped>
.container {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 0.5em;
}

.q-btn {
  flex-shrink: 0;
}

.q-linear-progress {
  flex-grow: 1;
}

#duration {
  flex-shrink: 0;
  margin-left: auto;
}

.warn {
  color: #f60;
}

.solution-row {
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
}

.solution-row:hover {
  background: rgba(0, 0, 0, 0.05);
}

.solution-row.selected {
  background: rgba(0, 128, 255, 0.15);
  outline: 1px solid rgba(0, 128, 255, 0.4);
}

.hint {
  font-size: 12px;
  color: #888;
}

.selected-solution {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  background: rgba(0, 128, 255, 0.1);
  border: 1px solid rgba(0, 128, 255, 0.3);
}

.func-result {
  color: #333;
}
</style>
