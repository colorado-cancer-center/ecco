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
        v-tooltip="'Go to selected'"
        :icon="faCrosshairs"
        @click="onSeeSelected"
      />
      <AppButton
        v-tooltip="'Open all'"
        :icon="faAnglesDown"
        @click="onOpenAll"
      />
      <AppButton
        v-tooltip="'Close all'"
        :icon="faAnglesUp"
        @click="onCloseAll"
      />
    </div>

    <div
      v-for="(item, index) in children"
      :key="index"
      class="tree-item"
      role="treeitem"
      :aria-selected="isEqual(modelValue, getValue(item))"
      :aria-expanded="isOpen[index]"
      :aria-level="level"
      :aria-setsize="size(children)"
      :aria-posinset="index + 1"
    >
      <div v-show="match(item)" class="tree-row">
        <button
          class="tree-opener"
          :disabled="!isEmpty(item.children) && !!unref(search)"
          :data-level="level"
          @click="onClick(index)"
          @keydown="onKey($event, index)"
        >
          <font-awesome-icon
            v-if="!isEmpty(item.children)"
            :icon="
              isOpen[index] || unref(search) ? faChevronDown : faChevronRight
            "
            class="icon"
          />

          <font-awesome-icon
            v-else-if="isEqual(modelValue, getValue(item))"
            :icon="faCheck"
            class="icon check"
            data-tree-selected
          />

          <font-awesome-icon v-else :icon="faCircle" class="icon uncheck" />

          <span class="label">
            {{ item.label }}
          </span>

          <span v-if="item.children && !unref(search)" class="count">
            {{ size(item.children).toLocaleString() }}
          </span>
        </button>
        <div class="tree-action">
          <slot :parents="getParents(item)"></slot>
        </div>
      </div>

      <AppTree
        v-show="item.children && (isOpen[index] || unref(search))"
        :children="item.children"
        :parents="getParents(item)"
        :parent-search="unref(search)"
        :parent-bus="unref(bus)"
        :model-value="modelValue"
        @update:model-value="(value) => $emit('update:modelValue', value)"
      >
        <template #default="slotProps">
          <slot name="default" v-bind="slotProps" />
        </template>
      </AppTree>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, isRef, ref, unref, watch, type VNode } from "vue";
import { isEmpty, isEqual, size } from "lodash";
import { faCircle } from "@fortawesome/free-regular-svg-icons";
import {
  faAnglesDown,
  faAnglesUp,
  faCheck,
  faChevronDown,
  faChevronRight,
  faCrosshairs,
  faSearch,
} from "@fortawesome/free-solid-svg-icons";
import { useEventBus } from "@vueuse/core";
import type { UseEventBusReturn } from "@vueuse/core";
import AppButton from "@/components/AppButton.vue";
import AppInput from "@/components/AppInput.vue";
import { findClosest } from "@/util/dom";
import { sleep } from "@/util/misc";

/** one item in tree */
type Item = {
  id?: ID;
  label: string;
  children?: Item[];
};

type ID = string;

type Props = {
  /** selected item */
  modelValue?: ID[];
  /** path of parent items leading to this item */
  parents?: Item[];
  /** list of children items */
  children?: Item[];
  /** passed down search from parent */
  parentSearch?: string;
  /** passed down events from parent */
  parentBus?: Bus;
};

const {
  modelValue = [],
  children = [],
  parents = [],
  parentSearch = "",
  parentBus = undefined,
} = defineProps<Props>();

type Emits = {
  "update:modelValue": [ID[]];
};

const emit = defineEmits<Emits>();

type Slots = {
  default(props: { parents: ReturnType<typeof getParents> }): VNode;
};

defineSlots<Slots>();

/** search string */
const search = computed(() => parentSearch || ref(""));

/** list of open states for each child item */
const isOpen = ref<Record<number, boolean>>({});

/** tree depth */
const level = computed(() => parents.length + 1);

/** open item */
const open = (index: number) => (isOpen.value[index] = true);

/** close item */
const close = (index: number) => delete isOpen.value[index];

/** see selected */
const seeSelected = async () =>
  children.forEach(async (item, index) => {
    if (getChildren(item).some((item) => isEqual(getValue(item), modelValue)))
      open(index);
    else close(index);
  });

/** open all */
const openAll = () =>
  children.forEach((_, index) => (isOpen.value[index] = true));

/** close all */
const closeAll = () => (isOpen.value = {});

/** toggle open state */
const toggle = (index: number) =>
  isOpen.value[index] ? close(index) : open(index);

/** event bus type */
type Bus = UseEventBusReturn<"see-selected" | "open" | "close", undefined>;

/** event bus */
const bus = computed<Bus>(() => parentBus || useEventBus(Symbol()));

/** react to bus events */
bus.value.on(async (event) => {
  if (event === "see-selected") {
    seeSelected();
    await sleep();
    document
      .querySelector("[aria-selected='true']")
      ?.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  if (event === "open") openAll();
  if (event === "close") closeAll();
});

/** emit bus events */
const onSeeSelected = () => bus.value.emit("see-selected");
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
  [...parents, item].map(({ id, label }) => ({ id, label }));

/** traverse up tree and get list of ids forming path to current element */
const getValue = (item: Item): ID[] =>
  getParents(item)
    .map(({ id }) => id)
    .filter((id) => id !== undefined);

/** traverse down tree and get list of nested child items */
const getChildren = (item: Item): Item[] =>
  item.children
    ?.map((item) => [item, ...getChildren(item)])
    .flat()
    .map(({ id, label }) => ({ id, label })) ?? [];

/** handle button click */
const onClick = (index: number) => {
  const item = children[index];
  if (!item) return;
  /** toggle isOpen/closed */
  if (!isEmpty(item.children)) toggle(index);
  else
    /** select item */
    emit("update:modelValue", getValue(item));
};

/** handle button key press */
const onKey = (event: KeyboardEvent, index: number) => {
  const item = children[index];
  const target = event.target as HTMLElement;

  const prevent = () => event.preventDefault();

  if (event.key === "ArrowRight") {
    prevent();
    if (!isEmpty(item?.children)) {
      /** expand */
      if (!isOpen.value[index]) return open(index);
      else
        /** go to child */
        return findClosest(
          target,
          (el) => el.matches(`button[data-level="${level.value + 1}"]`),
          "next",
        )?.focus();
    }
  }

  if (event.key === "ArrowLeft") {
    prevent();
    /** collapse */
    if (isOpen.value[index]) return close(index);
    else
      /** go to parent */
      return findClosest(
        target,
        (el) => el.matches(`button[data-level="${level.value - 1}"]`),
        "previous",
      )?.focus();
  }

  /** go to next down list */
  if (event.key === "ArrowDown") {
    prevent();
    return findClosest(
      target,
      (el) => el.matches(`button[data-level]`) && el.checkVisibility(),
      "next",
    )?.focus();
  }

  /** go to previous up list */
  if (event.key === "ArrowUp") {
    prevent();
    return findClosest(
      target,
      (el) => el.matches(`button[data-level]`) && el.checkVisibility(),
      "previous",
    )?.focus();
  }
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
  background: var(--off-white);
  content: "";
}

.tree-item[aria-selected="true"] .tree-opener {
  background: var(--off-white);
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

.tree-opener {
  flex-grow: 1;
  flex-basis: 0;
  justify-content: flex-start;
  text-align: left;
}

.tree-action {
  display: flex;
  align-items: center;
  padding: 0;
  gap: 5px;
  opacity: 0;
  transition:
    opacity var(--fast),
    background var(--fast);
}

.tree-row:hover .tree-action {
  opacity: 1;
}

.tree-action:hover,
.tree-opener:hover {
  background: var(--off-white);
}

.icon {
  flex-shrink: 0;
  width: 20px;
  color: var(--gray);
}

.check {
  color: var(--success);
}

.uncheck {
  opacity: 0;
}

.count {
  color: var(--gray);
}
</style>
