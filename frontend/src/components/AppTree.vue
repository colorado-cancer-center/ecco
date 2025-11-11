<template>
  <div :role="level === 1 ? 'tree' : 'group'" style="display: contents">
    <div
      v-for="(item, index) in children"
      :key="index"
      class="tree"
      role="treeitem"
      :aria-selected="open[index]"
      :aria-level="level"
      :aria-setsize="children.length"
      :aria-posinset="index + 1"
    >
      <button
        v-show="match(item)"
        class="button"
        :data-level="level"
        @click="onClick(index)"
        @keydown="onKey($event, index)"
      >
        <font-awesome-icon
          v-if="item.children?.length"
          :icon="open[index] || search ? faChevronDown : faChevronRight"
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

        <span v-if="item.children?.length && !search" class="count">
          {{ item.children?.length.toLocaleString() }}
        </span>

        <span class="spacer" />

        <button
          v-for="(action, index) in item.actions"
          :key="index"
          v-tooltip="action.label"
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
        v-if="item.children && (open[index] || search)"
        :children="item.children"
        :parents="getParents(item)"
        :search="search"
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
import { findClosest } from "@/util/dom";

/** one item in tree */
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

/** salient info about item */
type Value = { id: string; label: string };

type Props = {
  /** selected item */
  modelValue?: Value[];
  /** path of parent items leading to this item */
  parents?: Value[];
  /** search string */
  search?: string;
  /** list of children items */
  children?: Item[];
};

const {
  modelValue = [],
  children = [],
  parents = [],
  search = "",
} = defineProps<Props>();

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

const emit = defineEmits<Emits>();

/** list of open states for each child item */
const open = ref<boolean[]>([]);

/** tree depth */
const level = computed(() => parents.length + 1);

/** when children change */
watch(
  () => children,
  () => {
    /** reset open states */
    open.value = Array(children.length).fill(false);
  },
  { immediate: true, deep: true },
);

/** handle button click */
const onClick = (index: number) => {
  const item = children[index];
  if (!item) return;
  /** toggle open/closed */
  if (item.children?.length) open.value[index] = !open.value[index];
  /** select item */ else emit("update:modelValue", getParents(item));
};

/** handle button key press */
const onKey = (event: KeyboardEvent, index: number) => {
  const item = children[index];
  const target = event.target as HTMLElement;
  const isOpen = open.value[index];

  const handle = () => {
    if (event.key === "ArrowRight") {
      if (item?.children?.length) {
        /** expand */
        if (!isOpen) return (open.value[index] = true);
        else
          /** go to child */
          return findClosest(
            target,
            `button[data-level="${level.value + 1}"]`,
            "next",
          )?.focus();
      }
    }

    if (event.key === "ArrowLeft") {
      /** collapse */
      if (isOpen) return (open.value[index] = false);
      else
        /** go to parent */
        return findClosest(
          target,
          `button[data-level="${level.value - 1}"]`,
          "previous",
        )?.focus();
    }

    /** go to next down list */
    if (event.key === "ArrowDown")
      return findClosest(target, `button[data-level]`, "next")?.focus();

    /** go to previous up list */
    if (event.key === "ArrowUp")
      return findClosest(target, `button[data-level]`, "previous")?.focus();
  };

  /** if conditions met and actions performed, prevent browser default action */
  if (handle() !== undefined) event.preventDefault();
};

/** does item match search */
const match = (item: Item) =>
  [...getParents(item), ...getChildren(item)]
    .map(({ id, label }) => [id, label])
    .flat()
    .join(" ")
    .match(new RegExp(search, "i"));

/** traverse up tree and get list of parent items */
const getParents = (item: Item): Value[] =>
  [...parents, item].map(({ id, label }) => ({ id, label }));

/** traverse down tree and get list of nested child items */
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

.tree:not([aria-level="1"]) {
  position: relative;
  padding-left: 20px;
}

.tree:not([aria-level="1"])::before {
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
