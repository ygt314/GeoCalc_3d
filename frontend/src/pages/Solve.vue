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
        :class="{ selected: selectedSolution === s }"
        @click="selectedSolution = s"
        v-katex
      >$$ {{ s }} $$
      </div>
      <div class="hint">👆 点击某个解,可把它作为极值探索对象</div>
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
    <!-- 用求解结果时,显示当前选中的解 -->
    <div v-else-if="exploreSource === 'solution'" class="container">
      <label>选中的解</label>
      <q-input :model-value="selectedSolution || '(点击上方求解结果选择)'" dense readonly />
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
      <q-linear-progress indeterminate v-if="exploring" />
    </div>

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
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

// ── 求解区 ──
const expr = ref('');
const solving = ref(false);
const solutions = ref<Array<string>>([]);
const selectedSolution = ref('');   // 用户点击选中的解(探索对象)

function solve() {
  solving.value = true;
  solutions.value = [];
  selectedSolution.value = '';
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

// 是否可以探索
const canExplore = computed(() => {
  if (exploreSyms.value.trim().length === 0) return false;
  if (exploreSource.value === 'solution') {
    return selectedSolution.value.length > 0;   // 需选中一个解
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
    // 用求解结果: choice = 选中解的 LaTeX, custom=True(从缓存字典取)
    window.pywebview.api.problem
      .expore_extrema(selectedSolution.value, syms, true)
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
    // 自定义表达式: choice = 表达式字符串, custom=False(DSL 解析)
    window.pywebview.api.problem
      .expore_extrema(customExpr.value, syms, false)
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
</style>
