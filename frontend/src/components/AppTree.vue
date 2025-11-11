<template>
  <div :role="level === 1 ? 'tree' : 'group'" style="display: contents">
    <div
      v-for="(item, index) in children"
      :key="index"
      class="tree"
      :data-level="level"
      role="treeitem"
      :aria-expanded="open[index]"
      :aria-level="level"
      :aria-setsize="children.length"
      :aria-posinset="index + 1"
    >
      <button class="button" @click="onClick(index)" v-show="match(item)">
        <font-awesome-icon
          v-if="item.children?.length"
          :icon="open[index] || filter ? faChevronDown : faChevronRight"
          class="icon"
        />

        <font-awesome-icon
          v-if="!item.children?.length"
          :icon="faCheck"
          class="icon check"
          :style="{
            opacity: isEqual(modelValue, getParents(item)) ? 1 : 0,
          }"
        />

        <span class="truncate">
          {{ item.label }}
        </span>

        <span v-if="item.children?.length && !filter" class="count">
          {{ item.children?.length.toLocaleString() }}
        </span>

        <span class="spacer" />

        <button
          v-for="(action, index) in item.actions"
          v-tooltip="action.label"
          :key="index"
          class="action button"
        >
          <font-awesome-icon
            :icon="action.icon"
            class="icon"
            @click.stop="action.onClick(getParents(item))"
          />
        </button>
      </button>

      <AppTree
        v-if="item.children && (open[index] || filter)"
        :children="item.children"
        :parents="getParents(item)"
        :filter="filter"
        :model-value="modelValue"
        @update:model-value="(value) => $emit('update:modelValue', value)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { isEqual } from "lodash";
import {
  faCheck,
  faChevronDown,
  faChevronRight,
  type IconDefinition,
} from "@fortawesome/free-solid-svg-icons";

type Value = { id: string; label: string };

type Item = {
  id: string;
  label: string;
  children?: Item[];
  actions?: {
    label: string;
    icon: IconDefinition;
    onClick: (parents: Value[]) => void;
  }[];
};

type Props = {
  modelValue?: Value[];
  parents?: Value[];
  filter?: string;
  children?: Item[];
};

const {
  modelValue = [],
  children = [],
  parents = [],
  filter = "",
} = defineProps<Props>();

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

const emit = defineEmits<Emits>();

const open = ref<boolean[]>([]);

const level = computed(() => parents.length + 1);

watch(
  () => children.length,
  (length) => {
    open.value = Array(length).fill(false);
  },
  { immediate: true },
);

const onClick = (index: number) => {
  const item = children[index];
  if (!item) return;
  if (item.children?.length) open.value[index] = !open.value[index];
  else emit("update:modelValue", getParents(item));
};

const match = (item: Item) =>
  [...getParents(item), ...getChildren(item)]
    .map(({ id, label }) => [id, label])
    .flat()
    .join(" ")
    .match(new RegExp(filter, "i"));

const getParents = (item: Item): Value[] =>
  [...parents, item].map(({ id, label }) => ({ id, label }));

const getChildren = (item: Item): Value[] =>
  (item.children ?? [])
    .map((item) => [item, ...getChildren(item)])
    .flat()
    .map(({ id, label }) => ({ id, label }));
</script>

<style scoped>
.tree {
  display: flex;
  flex-direction: column;
}

.tree:not([data-level="1"]) {
  position: relative;
  padding-left: 20px;
}

.tree:not([data-level="1"])::before {
  position: absolute;
  top: 0;
  bottom: 0;
  left: calc(20px - 2px);
  width: 2px;
  background: var(--light-gray);
  content: "";
}

.button {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  gap: 10px;
  border: none;
  border-radius: var(--rounded);
  background: none;
  font: inherit;
  cursor: pointer;
  transition: background var(--fast);
}

.button:hover:not(:has(.button:hover)) {
  background: var(--light-gray);
}

.icon {
  width: 20px;
  color: var(--gray);
}

.check {
  color: var(--theme-dark);
}

.count {
  color: var(--gray);
}

.spacer {
  flex-grow: 1;
}

.action {
  display: inline-flex;
  align-items: center;
  padding: 5px;
  gap: 10px;
  border: none;
  border-radius: var(--rounded);
  background: none;
  font: inherit;
  cursor: pointer;
  transition: background var(--fast);
}
</style>
