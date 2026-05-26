<template>
  <div role="tree" class="flex flex-col gap-2">
    <!-- top controls -->
    <div class="flex gap-2">
      <AppInput v-model="search" :icon="Search" placeholder="Search" />
      <AppButton v-tooltip="'Collapse all tree levels'" @click="closeAll()">
        <ListChevronsDownUp />
      </AppButton>
      <AppButton v-tooltip="'Expand all tree levels'" @click="openAll()">
        <ListChevronsUpDown />
      </AppButton>
      <AppButton
        v-tooltip="'Expand tree to show selected'"
        @click="onSeeSelected()"
      >
        <Crosshair />
      </AppButton>
    </div>

    <!-- tree structure -->
    <AppTreeItem
      :model-value="modelValue"
      :update-model-value="updateModelValue"
      :children="tree"
      :level="1"
      :search="!!search"
    >
      <template #default="slotProps">
        <slot v-bind="slotProps" />
      </template>
    </AppTreeItem>
  </div>
</template>

<script lang="ts">
export type ID = string;

/** nested tree structure */
export type _Tree = {
  id: ID;
  label: string;
  children?: _Tree[];
};

/** nested tree structure, with extra state */
export type Tree = {
  id: ID;
  label: string;
  open: boolean;
  match: boolean;
  children: Tree[];
};
</script>

<script setup lang="ts">
import type { VNode } from "vue";
import { ref, watch } from "vue";
import AppButton from "@/components/AppButton.vue";
import AppInput from "@/components/AppInput.vue";
import AppTreeItem from "@/components/AppTreeItem.vue";
import {
  Crosshair,
  ListChevronsDownUp,
  ListChevronsUpDown,
  Search,
} from "@lucide/vue";

type Props = {
  /** path to selected item */
  modelValue?: ID;
  /** tree structure */
  tree: _Tree[];
};

const { tree: _tree, modelValue = "" } = defineProps<Props>();

type Emits = {
  "update:modelValue": [ID];
};

const emit = defineEmits<Emits>();

type Slots = {
  default(props: { child: Tree }): VNode;
};

defineSlots<Slots>();

/** search string */
const search = ref("");

/** internal tree, with extra state */
const tree = ref<Tree[]>([]);

/** sync internal tree with input tree */
watch(
  () => _tree,
  () => {
    const getTree = (children: _Tree[] = _tree): Tree[] =>
      children.map((child) => ({
        ...child,
        open: false,
        match: true,
        children: child.children ? getTree(child.children) : [],
      }));

    tree.value = getTree();
  },
  { immediate: true, deep: true },
);

const matches = (child: Tree, search: string) =>
  !search.trim() ||
  !![child.id, child.label].join(" ").match(new RegExp(search, "i"));

/** filter sub-trees by search string */
watch(
  [tree, search],
  () => {
    const filterTree = (children: Tree[] = tree.value): boolean => {
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
const closeAll = (children: Tree[] = tree.value) => {
  for (const child of children) {
    child.open = false;
    closeAll(child.children);
  }
};

/** open all tree levels */
const openAll = (children: Tree[] = tree.value) => {
  for (const child of children) {
    child.open = true;
    openAll(child.children);
  }
};

/** expand tree to show selected item */
const onSeeSelected = (children: Tree[] = tree.value) => {
  closeAll();
  for (const child of children)
    if (
      child.id === modelValue ||
      (child.children && onSeeSelected(child.children))
    )
      return (child.open = true);
  return false;
};

/** function to update model value */
const updateModelValue = (child: Tree) => emit("update:modelValue", child.id);
</script>
