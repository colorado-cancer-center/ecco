<template>
  <div :role="level === 1 ? 'tree' : 'group'" class="flex flex-col">
    <!-- top controls -->
    <div v-if="level === 1" class="mb-2 flex gap-2">
      <AppInput
        v-if="isRef(search)"
        v-model="search.value"
        :icon="Search"
        placeholder="Search"
      />
      <AppButton v-tooltip="'Collapse all tree levels'" @click="onCloseAll">
        <ListChevronsDownUp />
      </AppButton>
      <AppButton v-tooltip="'Expand all tree levels'" @click="onOpenAll">
        <ListChevronsUpDown />
      </AppButton>
      <AppButton
        v-tooltip="'Expand tree to show selected'"
        @click="onSeeSelected"
      >
        <Crosshair />
      </AppButton>
    </div>

    <!-- list -->
    <div
      v-for="(item, index) in children"
      :key="index"
      class="relative flex flex-col"
      :class="
        level !== 1 &&
        'relative pl-4 before:absolute before:inset-y-0 before:left-3.5 before:w-0.5 before:bg-stone-50'
      "
      role="treeitem"
      :aria-selected="isEqual(modelValue, getValue(item))"
      :aria-expanded="isOpen[index]"
      :aria-level="level"
      :aria-setsize="size(children)"
      :aria-posinset="index + 1"
    >
      <!-- row -->
      <div v-show="match(item)" class="flex items-center gap-2">
        <!-- expand/collapse/select -->
        <button
          class="min-h-8 grow basis-0 justify-start gap-2 rounded-md p-1 text-left hover:bg-stone-100"
          :class="isEqual(modelValue, getValue(item)) && 'bg-stone-100'"
          :disabled="!isEmpty(item.children) && !!unref(search)"
          :data-level="level"
          @click="onClick(index)"
          @keydown="onKey($event, index)"
        >
          <!-- expand/collapse icon -->
          <template v-if="!isEmpty(item.children)">
            <ChevronDown
              v-if="isOpen[index] || unref(search)"
              class="text-stone-300"
            />
            <ChevronRight v-else class="text-stone-300" />
          </template>
          <!-- selection icon -->
          <template v-else>
            <Check
              v-if="isEqual(modelValue, getValue(item))"
              class="text-emerald-500"
              data-tree-selected
            />
            <Check v-else class="opacity-0" />
          </template>

          <!-- text label -->
          <span>
            {{ item.label }}
          </span>

          <!-- count -->
          <span v-if="item.children && !unref(search)" class="text-stone-300">
            {{ size(item.children).toLocaleString() }}
          </span>
        </button>

        <!-- action -->
        <slot :parents="getParents(item)" />
      </div>

      <!-- children items -->
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
import type { VNode } from "vue";
import type { UseEventBusReturn } from "@vueuse/core";
import { computed, isRef, ref, unref, watch } from "vue";
import AppButton from "@/components/AppButton.vue";
import AppInput from "@/components/AppInput.vue";
import { findClosest } from "@/util/dom";
import { sleep } from "@/util/misc";
import {
  Check,
  ChevronDown,
  ChevronRight,
  Crosshair,
  ListChevronsDownUp,
  ListChevronsUpDown,
  Search,
} from "@lucide/vue";
import { useEventBus } from "@vueuse/core";
import { isEmpty, isEqual, size } from "lodash";

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
