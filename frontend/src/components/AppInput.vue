<template>
  <div class="container" :class="$attrs.class">
    <input
      v-bind="omit($attrs, 'class')"
      class="input"
      :style="{ paddingRight: sideSize.width.value + 'px' }"
      :value="modelValue"
      @input="
        (event) =>
          $emit(
            'update:modelValue',
            (event.currentTarget as HTMLInputElement).value,
          )
      "
    />

    <div ref="side" class="side">
      <button v-if="modelValue" @click="$emit('update:modelValue', '')">
        <font-awesome-icon :icon="faXmark" />
      </button>
      <button v-else disabled>
        <font-awesome-icon :icon="icon" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTemplateRef } from "vue";
import { omit } from "lodash";
import { faXmark } from "@fortawesome/free-solid-svg-icons";
import type { IconDefinition } from "@fortawesome/free-solid-svg-icons";
import { useElementSize } from "@vueuse/core";

defineOptions({ inheritAttrs: false });

type Props = {
  modelValue: string;
  icon?: IconDefinition;
};

defineProps<Props>();

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

defineEmits<Emits>();

const sideElement = useTemplateRef("side");
const sideSize = useElementSize(sideElement, undefined, { box: "border-box" });
</script>

<style scoped>
.container {
  display: flex;
  position: relative;
  align-items: center;
  width: 100%;
}

.input {
  flex-grow: 1;
  background: var(--light-gray);
}

.side {
  display: flex;
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  align-items: center;
}
</style>
