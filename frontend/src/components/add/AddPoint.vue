<template>
  <q-btn :icon="ionAddOutline" @click="dialogOpen = true">添加点</q-btn>
  <q-dialog v-model="dialogOpen" persistent>
    <q-card>
      <q-form @reset="reset" @submit="submit">
        <q-card-section>
          <h1>添加点坐标</h1>
          <h2>名称</h2>
          <q-input v-model="name" dense />
          <h2>请在下面 5 项中填写 2 项</h2>
          <div class="container">
            <label>横坐标</label>
            <q-input v-model="x_str" dense placeholder="表达式 / 输入 x 设未知数" />
          </div>
          <div class="container">
            <label>纵坐标</label>
            <q-input v-model="y_str" dense placeholder="表达式 / 输入 y 设未知数" />
          </div>
          <!-- TODO(你确认): 竖坐标输入框,3D 新增
               同样支持"输入 z 设未知数" -->
          <div class="container">
            <label>在直线/平面</label>
            <q-input v-model="line1" dense />
            <label>上</label>
          </div>
          <div class="container">
            <label>在直线/平面</label>
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
</template>

<script setup lang="ts">
import { ionAddOutline } from '@quasar/extras/ionicons-v8';
import { ref, computed } from 'vue';
import { isValidNewPointName, isValidLineName } from 'components/add/validityCheck';
import { useDataStore } from 'stores/data';

const dialogOpen = ref(false);

const name = ref('');
const x_str = ref('');
const y_str = ref('');
// TODO(你补全): z_str —— 3D 新增的竖坐标
// const z_str = ref('');
const line1 = ref('');
const line2 = ref('');

const notEmpty = (str: string) => str.length > 0;
/**
 * 1. 点名称合法
 * 2. TODO(你补全): 5 项(x/y/z/line1/line2)中填写了 2 项且合法
 *    - 坐标(x/y/z)任意填 2 个可确定点;或 1 坐标 + 1 线/面
 *    - 注意 z_str 也要纳入计数
 */
const isValid = computed(
  () =>
    isValidNewPointName(name.value) &&
    +notEmpty(x_str.value) +
      +notEmpty(y_str.value) +
      // TODO(你补全): +notEmpty(z_str.value) +
      +notEmpty(line1.value) +
      +notEmpty(line2.value) ===
      2 &&
    +notEmpty(x_str.value) +
      +notEmpty(y_str.value) +
      +isValidLineName(line1.value) +
      +isValidLineName(line2.value) ===
      2,
);

function reset() {
  // TODO(你补全): 加入 z_str.value = ''
  name.value = x_str.value = y_str.value = line1.value = line2.value = '';
}

const dataStore = useDataStore();

function submit() {
  window.pywebview.api.problem
    // TODO(你补全): 传入 z_str.value(位置在 y 之后,line1 之前)
    // .add_point(name.value, x_str.value, y_str.value, z_str.value, line1.value, line2.value)
    .add_point(name.value, x_str.value, y_str.value, line1.value, line2.value)
    .then(() => {
      dataStore.pointNames.push(name.value);
      // 可能有未知数的添加
      // TODO(你补全): 条件里加 z_str.value === 'z'
      if (x_str.value === 'x' || y_str.value === 'y') {
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
.container {
  display: flex;
  align-items: center;
  gap: 0.5em;
  margin: 0.5em;
}

.container .q-input {
  flex-grow: 1;
}
</style>
