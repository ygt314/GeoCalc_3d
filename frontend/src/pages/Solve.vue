<template>
  <q-page>
    <h1>计算求解</h1>
    <div>请输入要计算的表达式：</div>
    <q-input v-model="expr" dense />
    <!-- 极值探索变量:用户自行决定,留空则跳过探索 -->
    <div class="container">
      <label>极值探索变量(可选)</label>
      <q-input
        v-model="exploreSymsInput"
        dense
        placeholder="空格分隔,如 t u。留空则不探索"
      />
    </div>
    <div class="container">
      <q-btn :disable="expr.length === 0 || solving" @click="solve" class="primary"
        > 🚀 启动！
      </q-btn>
      <q-linear-progress indeterminate v-if="solving" />
      <div id="duration">用时 {{ duration }}</div>
    </div>
    <div v-if="solutions.length > 0">
      <div>以下是所有可能的解：</div>
      <div v-for="s in solutions" :key="s" v-katex>$$ {{ s }} $$</div>
    </div>

    <!-- ═══════════════════ 极值点探索(求解后自动进行) ═══════════════════ -->
    <div v-if="exploreDone">
      <hr />
      <div>
        <b>🔍 极值点探索</b>(对表达式 {{ expr }} 求偏导 = 0,变量:{{ exploreSyms }})
      </div>
      <div v-if="extrema.length > 0">
        <div>可能的驻点：</div>
        <div v-for="(e, i) in extrema" :key="i">
          点{{ i + 1 }}: <span v-katex>$ {{ e.latex }} $</span>
        </div>
      </div>
      <div v-else>无驻点或无解(表达式可能是常量,或函数无驻点)</div>
    </div>
    <div v-else-if="exploreError" class="warn">
      🔍 极值探索:{{ exploreError }}
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const expr = ref('');

const solving = ref(false);
const t1 = ref(0);
const t2 = ref(0);

const solutions = ref<Array<string>>([]);

// ── 极值点探索(求解后自动,变量由用户输入决定) ──
const exploreSymsInput = ref('');
const exploreDone = ref(false);
const exploreSyms = ref('');
const extrema = ref<Array<{ latex: string; values: Array<number> }>>([]);
const exploreError = ref('');

function solve() {
  t1.value = t2.value = Date.now();
  solving.value = true;
  solutions.value = [];
  exploreDone.value = false;
  exploreError.value = '';
  window.pywebview.api.problem
    .solve(expr.value)
    .then(async (result) => {
      if (result.length === 0) {
        result.push('无解');
      }
      solutions.value = result;
      // ── 求解后自动进行极值点探索(仅当用户填了变量) ──
      const syms = exploreSymsInput.value.trim();
      if (syms.length === 0) {
        return; // 用户未指定变量,跳过探索
      }
      try {
        exploreSyms.value = syms;
        const ext = await window.pywebview.api.problem.get_expore(expr.value, syms);
        extrema.value = ext;
        exploreDone.value = true;
      } catch (e) {
        exploreError.value = String(e);
      }
    })
    .catch((e) => {
      alert('求解出错 qwq\n' + e);
    })
    .finally(() => {
      solving.value = false;
    });
}

// 实现计时器
const duration = ref('00:00:00');

setInterval(() => {
  if (solving.value) {
    t2.value = Date.now();
    const t = (t2.value - t1.value) / 1000;
    let h: number | string = Math.floor(t / 3600);
    let m: number | string = Math.floor((t % 3600) / 60);
    let s: number | string = Math.floor(t % 60);
    // 在前面补 0
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
</style>
