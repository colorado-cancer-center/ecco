<script lang="ts">
export type ID = string;

/** nested tree structure */
export type Tree = {
  id: ID;
  label: string;
  children: Tree[];
};

/** internal tree, with extra state */
export type _Tree = {
  id: ID;
  label: string;
  open: boolean;
  match: boolean;
  children: _Tree[];
};
</script>

<script setup lang="ts">
import type { VNode } from "vue";
import { ref, useId, useTemplateRef, watch } from "vue";
import AppButton from "@/components/AppButton.vue";
import AppInput from "@/components/AppInput.vue";
import AppTreeItem from "@/components/AppTreeItem.vue";
import { useScrollable } from "@/util/composables";
import { sleep } from "@/util/misc";
import {
  ListCheck,
  ListChevronsDownUp,
  ListChevronsUpDown,
  Search,
} from "@lucide/vue";

type Props = {
  /** label */
  label?: string;
  /** selected item */
  modelValue?: ID;
  /** tree structure */
  tree: Tree[];
};

const { tree, modelValue = "" } = defineProps<Props>();

type Emits = {
  "update:modelValue": [ID];
};

const emit = defineEmits<Emits>();

type Slots = {
  selected(props: { value: ID }): VNode;
  action(props: { child: _Tree }): VNode;
};

defineSlots<Slots>();

const scrollElement = useTemplateRef("scroll");
useScrollable(scrollElement);

/** search string */
const search = ref("");

/** internal tree, with extra state */
const _tree = ref<_Tree[]>([]);

/** sync internal tree with input tree */
watch(
  () => tree,
  () => {
    const getTree = (children = tree): _Tree[] =>
      children.map((child) => ({
        ...child,
        open: false,
        match: true,
        children: child.children ? getTree(child.children) : [],
      }));

    _tree.value = getTree();
  },
  { immediate: true, deep: true },
);

/** check if tree item matches search string */
const matches = (child: _Tree, search: string) =>
  !search.trim() ||
  !![child.id, child.label].join(" ").match(new RegExp(search, "i"));

/** filter sub-trees by search string */
watch(
  [() => _tree.value, search],
  () => {
    const filterTree = (children = _tree.value): boolean => {
      let match = false;
      for (const child of children) {
        child.match =
          filterTree(child.children) || matches(child, search.value);
        match ||= child.match;
      }
      return match;
    };
    filterTree();
  },
  { immediate: true, deep: true },
);

/** close all tree levels */
const closeAll = (children: _Tree[] = _tree.value) => {
  for (const child of children) {
    child.open = false;
    closeAll(child.children);
  }
};

/** open all tree levels */
const openAll = (children: _Tree[] = _tree.value) => {
  for (const child of children) {
    child.open = true;
    openAll(child.children);
  }
};

/** are all tree levels closed */
const allClosed = (children: _Tree[] = _tree.value) => {
  for (const child of children)
    if (child.open || !allClosed(child.children)) return false;
  return true;
};

/** expand tree to show selected item */
const openSelected = (children: _Tree[] = _tree.value) => {
  closeAll();
  for (const child of children)
    if (child.id === modelValue || openSelected(child.children))
      return (child.open = true);
  return false;
};

/** is selected item visible */
const isSelectedOpen = (children: _Tree[] = _tree.value): boolean => {
  for (const child of children) {
    if (child.id === modelValue) return true;
    if (child.open && isSelectedOpen(child.children)) return true;
  }
  return false;
};

/** function to update model value */
const updateModelValue = (child: _Tree) => emit("update:modelValue", child.id);

const id = useId();
</script>

<template>
  <div ref="root" class="flex max-h-max flex-col gap-1">
    <label :id="id">{{ label }}</label>

    <!-- top controls -->
    <div class="flex gap-2">
      <AppInput v-model="search" :icon="Search" placeholder="Search" />
      <AppButton
        v-if="allClosed()"
        v-tooltip="'Expand all tree levels'"
        @click="openAll()"
      >
        <ListChevronsUpDown />
      </AppButton>
      <AppButton
        v-else
        v-tooltip="'Collapse all tree levels'"
        @click="closeAll()"
      >
        <ListChevronsDownUp />
      </AppButton>
      <AppButton
        v-tooltip="'Expand tree to show selected'"
        @click="isSelectedOpen() ? closeAll() : openSelected()"
      >
        <ListCheck />
      </AppButton>
    </div>

    <div class="my-1 flex items-center gap-2 pl-2 text-sm text-stone-500">
      Selected:
      <slot name="selected" v-bind="{ value: modelValue }" />
    </div>

    <!-- tree structure -->
    <div
      ref="scroll"
      role="tree"
      :aria-labelledby="id"
      class="scrollable overflow-y-auto"
    >
      <AppTreeItem
        :model-value="modelValue"
        :update-model-value="updateModelValue"
        :children="_tree"
        :level="1"
        :search="!!search"
      >
        <template #action="slotProps">
          <slot name="action" v-bind="slotProps" />
        </template>
      </AppTreeItem>
    </div>
  </div>
</template>
