<script lang="ts">
import type { ComputedRef, InjectionKey } from "vue";

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

/** injection key for tree context */
export const treeKey: InjectionKey<{
  modelValue: ComputedRef<ID>;
  updateModelValue: (child: _Tree) => void;
  search: ComputedRef<boolean>;
}> = Symbol("AppTree");
</script>

<script setup lang="ts">
import type { VNode } from "vue";
import { computed, provide, ref, useId, useTemplateRef, watch } from "vue";
import AppButton from "@/components/AppButton.vue";
import AppInput from "@/components/AppInput.vue";
import AppScrollable from "@/components/AppScrollable.vue";
import AppTreeItem from "@/components/AppTreeItem.vue";
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
  /** tree structure */
  tree: Tree[];
};

const { tree } = defineProps<Props>();

const modelValue = defineModel<ID>({ default: "" });

type Slots = {
  /** label */
  default: () => unknown;
  /** selected item label */
  selected(props: { value: ID }): VNode;
  /** item action */
  action(props: { child: _Tree }): VNode;
};

defineSlots<Slots>();

/** root element */
const rootElement = useTemplateRef("root");

/** search string */
const search = ref("");

/** internal tree, with extra state */
const _tree = ref<_Tree[]>([]);

/** sync internal tree with input tree */
watch(
  () => tree,
  () => {
    const get = (children = tree): _Tree[] =>
      children.map((child) => ({
        ...child,
        open: false,
        match: true,
        children: child.children ? get(child.children) : [],
      }));

    _tree.value = get();
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
    const recurse = (children = _tree.value): boolean => {
      let match = false;
      for (const child of children) {
        child.match = recurse(child.children) || matches(child, search.value);
        match ||= child.match;
      }
      return match;
    };
    recurse();
  },
  { immediate: true, deep: true },
);

/** close all tree levels */
const closeAll = () => {
  const recurse = (children: _Tree[] = _tree.value) => {
    for (const child of children) {
      child.open = false;
      recurse(child.children);
    }
  };
  recurse();
};

/** open all tree levels */
const openAll = () => {
  const recurse = (children: _Tree[] = _tree.value) => {
    for (const child of children) {
      child.open = true;
      recurse(child.children);
    }
  };
  recurse();
};

/** are all tree levels closed */
const allClosed = () => {
  const recurse = (children: _Tree[] = _tree.value) => {
    for (const child of children)
      if (child.open || !recurse(child.children)) return false;
    return true;
  };
  return recurse();
};

/** expand tree to show selected item */
const openSelected = () => {
  closeAll();
  const recurse = (children: _Tree[] = _tree.value) => {
    for (const child of children)
      if (child.id === modelValue.value || recurse(child.children))
        return (child.open = true);
    return false;
  };
  recurse();

  sleep().then(() =>
    rootElement.value
      ?.querySelector("[aria-selected='true']")
      ?.scrollIntoView({ block: "center" }),
  );
};

/** is selected item visible */
const isSelectedOpen = () => {
  const recurse = (children: _Tree[] = _tree.value) => {
    for (const child of children) {
      if (child.id === modelValue.value) return true;
      if (child.open && recurse(child.children)) return true;
    }
    return false;
  };
  return recurse();
};

/** function to update model value */
const updateModelValue = (child: _Tree) => (modelValue.value = child.id);

/** unique id for tree */
const id = useId();

/** provide tree context */
provide(treeKey, {
  modelValue: computed(() => modelValue.value),
  updateModelValue,
  search: computed(() => !!search.value),
});
</script>

<template>
  <div ref="root" class="flex flex-col gap-1">
    <label :id="id" class="flex items-center gap-2">{{ label }}<slot /></label>

    <div class="mb-1 flex items-center gap-2 text-sm text-gray">
      <slot name="selected" v-bind="{ value: modelValue }" />
    </div>

    <!-- top controls -->
    <div class="flex gap-2">
      <AppInput v-model="search" :icon="Search" placeholder="Search" />
      <AppButton
        v-if="allClosed()"
        v-tooltip="'Expand all tree levels'"
        :square="true"
        @click="openAll()"
      >
        <ListChevronsUpDown />
      </AppButton>
      <AppButton
        v-else
        v-tooltip="'Collapse all tree levels'"
        :square="true"
        @click="closeAll()"
      >
        <ListChevronsDownUp />
      </AppButton>
      <AppButton
        v-tooltip="'Expand tree to show selected'"
        :square="true"
        @click="isSelectedOpen() ? closeAll() : openSelected()"
      >
        <ListCheck />
      </AppButton>
    </div>

    <!-- tree structure -->
    <AppScrollable role="tree" :aria-labelledby="id">
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
    </AppScrollable>
  </div>
</template>
