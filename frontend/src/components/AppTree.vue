<template>
  <div :role="level === 1 ? 'tree' : 'group'" class="col">
    <div
      v-for="(item, key, index) in children"
      :key="key"
      class="col tree"
      role="treeitem"
      :aria-selected="open[key]"
      :aria-level="level"
      :aria-setsize="size(children)"
      :aria-posinset="index + 1"
    >
      <button
        v-show="match(item)"
        class="button"
        :data-level="level"
        @click="onClick(key)"
        @keydown="onKey($event, key)"
      >
        <font-awesome-icon
          v-if="!isEmpty(item.children)"
          :icon="open[key] || search ? faChevronDown : faChevronRight"
          class="icon"
        />

        <font-awesome-icon
          v-if="isEmpty(item.children)"
          :icon="faCheck"
          class="icon check"
          :style="{
            opacity: isEqual(
              modelValue,
              getParents(item).map(({ id }) => id),
            )
              ? 1
              : 0,
          }"
        />

        <span class="label">
          {{ item.label }}
        </span>

        <span v-if="item.children && !search" class="count">
          {{ size(item.children).toLocaleString() }}
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
        v-if="item.children && (open[key] || search)"
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
import { computed, ref, watch, watchEffect } from "vue";
import { isEmpty, isEqual, size } from "lodash";
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
  children?: Items;
  actions?: {
    label: string;
    icon: IconDefinition;
    onClick: (parents: Item[]) => void;
  }[];
};

type Items = Record<string, Item>;

type Props = {
  /** selected item */
  modelValue?: string[];
  /** path of parent items leading to this item */
  parents?: Item[];
  /** search string */
  search?: string;
  /** list of children items */
  children?: Items;
};

const {
  modelValue = [],
  children = {},
  parents = [],
  search = "",
} = defineProps<Props>();

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

const emit = defineEmits<Emits>();

/** list of open states for each child item */
const open = ref<Record<string, boolean>>({});

/** tree depth */
const level = computed(() => parents.length + 1);

/** when children change */
watch(
  () => children,
  () => {
    /** reset open states */
    open.value = {};
  },
  { immediate: true, deep: true },
);

/** expand */
const expand = (key: string) => (open.value[key] = true);

/** collapse */
const collapse = (key: string) => delete open.value[key];

/** toggle open */
const toggle = (key: string) => (open.value[key] ? collapse(key) : expand(key));

/** handle button click */
const onClick = (key: string) => {
  const item = children[key];
  if (!item) return;
  /** toggle open/closed */
  if (!isEmpty(item.children)) toggle(key);
  else
    /** select item */
    emit(
      "update:modelValue",
      getParents(item).map(({ id }) => id),
    );
};

/** handle button key press */
const onKey = (event: KeyboardEvent, key: string) => {
  const item = children[key];
  const target = event.target as HTMLElement;
  const isOpen = open.value[key];

  const handle = () => {
    if (event.key === "ArrowRight") {
      if (item?.children?.length) {
        /** expand */
        if (!isOpen) return expand(key);
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
      if (isOpen) return collapse(key);
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
const getParents = (item: Item): Item[] =>
  [...parents, item].map(({ id, label }) => ({ id, label }));

/** traverse down tree and get list of nested child items */
const getChildren = (item: Item): Item[] =>
  Object.values(item.children ?? {})
    .map((item) => [item, ...getChildren(item)])
    .flat()
    .map(({ id, label }) => ({ id, label }));

watchEffect(() => console.log(children));
</script>

<style scoped>
.col {
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
  text-align: left;
  cursor: pointer;
  transition: background var(--fast);
}

.button:hover:not(:has(.button:hover)) {
  background: var(--light-gray);
}

.icon {
  flex-shrink: 0;
  width: 20px;
  color: var(--gray);
}

.check {
  color: var(--success);
}

.label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
