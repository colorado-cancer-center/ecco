<template>
  <div :role="level === 1 ? 'tree' : 'group'" class="tree">
    <div v-if="level === 1" class="controls">
      <AppInput
        v-if="isRef(search)"
        v-model="search.value"
        class="search"
        :icon="faSearch"
        placeholder="Search"
      />
      <AppButton
        v-tooltip="'Open all'"
        :icon="faFolderOpen"
        @click="onOpenAll"
      />
      <AppButton
        v-tooltip="'Close all'"
        :icon="faFolderClosed"
        @click="onCloseAll"
      />
    </div>

    <div
      v-for="(item, key, index) in children"
      :key="key"
      class="tree-item"
      role="treeitem"
      :aria-selected="isOpen[key]"
      :aria-level="level"
      :aria-setsize="size(children)"
      :aria-posinset="index + 1"
    >
      <div v-show="match(item)" class="tree-row">
        <button
          class="tree-button"
          :disabled="!isEmpty(item.children) && !!unref(search)"
          :data-level="level"
          @click="onClick(key)"
          @keydown="onKey($event, key)"
        >
          <font-awesome-icon
            v-if="!isEmpty(item.children)"
            :icon="
              isOpen[key] || unref(search) ? faChevronDown : faChevronRight
            "
            class="icon"
          />

          <font-awesome-icon
            v-else
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

          <span v-if="item.children && !unref(search)" class="count">
            {{ size(item.children).toLocaleString() }}
          </span>
        </button>

        <button
          v-for="(action, actionIndex) in item.actions"
          :key="actionIndex"
          v-tooltip="action.label"
        >
          <font-awesome-icon
            :icon="action.icon"
            class="icon"
            @click.stop="action.onClick(getParents(item))"
          />
        </button>
      </div>

      <AppTree
        v-show="item.children && (isOpen[key] || unref(search))"
        :children="item.children"
        :parents="getParents(item)"
        :parent-search="unref(search)"
        :parent-bus="unref(bus)"
        :model-value="modelValue"
        @update:model-value="(value) => $emit('update:modelValue', value)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, isRef, ref, unref, watch } from "vue";
import { isEmpty, isEqual, size } from "lodash";
import {
  faCheck,
  faChevronDown,
  faChevronRight,
  faFolderClosed,
  faFolderOpen,
  faSearch,
  type IconDefinition,
} from "@fortawesome/free-solid-svg-icons";
import { useEventBus } from "@vueuse/core";
import type { UseEventBusReturn } from "@vueuse/core";
import AppButton from "@/components/AppButton.vue";
import AppInput from "@/components/AppInput.vue";
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

export type Items = Record<string, Item>;

type Props = {
  /** selected item */
  modelValue?: string[];
  /** path of parent items leading to this item */
  parents?: Item[];
  /** list of children items */
  children?: Items;
  /** passed down search from parent */
  parentSearch?: string;
  /** passed down events from parent */
  parentBus?: Bus;
};

const {
  modelValue = [],
  children = {},
  parents = [],
  parentSearch = "",
  parentBus = undefined,
} = defineProps<Props>();

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

const emit = defineEmits<Emits>();

/** search string */
const search = computed(() => parentSearch || ref(""));

/** list of open states for each child item */
const isOpen = ref<Record<string, boolean>>({});

/** tree depth */
const level = computed(() => parents.length + 1);

/** open item */
const open = (key: string) => (isOpen.value[key] = true);

/** close item */
const close = (key: string) => delete isOpen.value[key];

/** open all */
const openAll = () =>
  Object.keys(children).forEach((key) => (isOpen.value[key] = true));

/** close all */
const closeAll = () => (isOpen.value = {});

/** toggle open state */
const toggle = (key: string) => (isOpen.value[key] ? close(key) : open(key));

/** event bus type */
type Bus = UseEventBusReturn<"open" | "close", undefined>;

/** event bus */
const bus = computed<Bus>(() => parentBus || useEventBus(Symbol()));

/** react to bus events */
bus.value.on((event) => {
  if (event === "open") openAll();
  if (event === "close") closeAll();
});

/** emit bus events */
const onOpenAll = () => bus.value.emit("open");
const onCloseAll = () => bus.value.emit("close");

/** does item match search */
const match = (item: Item) =>
  !![...getParents(item), ...getChildren(item)]
    .map(({ id, label }) => [id, label])
    .flat()
    .join(" ")
    .match(new RegExp(unref(search.value), "i"));

/** traverse up tree and get list of parent items */
const getParents = (item: Item): Item[] =>
  [...parents, { ...item, openAll, closeAll }].map(({ id, label }) => ({
    id,
    label,
  }));

/** traverse down tree and get list of nested child items */
const getChildren = (item: Item): Item[] =>
  Object.values(item.children ?? {})
    .map((item) => [{ ...item, openAll, closeAll }, ...getChildren(item)])
    .flat()
    .map(({ id, label }) => ({ id, label }));

/** handle button click */
const onClick = (key: string) => {
  const item = children[key];
  if (!item) return;
  /** toggle isOpen/closed */
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

  const handle = () => {
    if (event.key === "ArrowRight") {
      if (!isEmpty(item?.children)) {
        /** expand */
        if (!isOpen.value[key]) return open(key);
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
      if (isOpen.value[key]) return close(key);
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

/** when children change, reset open states */
watch(() => children, closeAll, { immediate: true, deep: true });
</script>

<style scoped>
.tree,
.tree-item {
  display: flex;
  flex-direction: column;
}

.tree-item:not([aria-level="1"]) {
  position: relative;
  padding-left: 20px;
}

.tree-item:not([aria-level="1"])::before {
  position: absolute;
  top: 0;
  bottom: 0;
  left: calc(20px - 2px);
  width: 2px;
  background: var(--light-gray);
  content: "";
}

.controls {
  display: flex;
  align-items: center;
  width: 100%;
  margin-bottom: 5px;
  gap: 5px;
}

.tree-row {
  display: flex;
  align-items: center;
  gap: 5px;
}

.tree-button {
  flex-grow: 1;
  flex-basis: 0;
  justify-content: flex-start;
  min-width: 0;
  text-align: left;
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
</style>
