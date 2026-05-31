<script setup lang="ts">
import type { VNode } from "vue";
import type { _Tree, ID } from "@/components/AppTree.vue";
import { findClosest } from "@/util/dom";
import { Check, ChevronDown, ChevronRight } from "@lucide/vue";

type Props = {
  /** path to selected item */
  modelValue?: ID;
  /** function to update model value */
  updateModelValue: (value: _Tree) => void;
  /** nested tree structure */
  children: _Tree[];
  /** depth of children item */
  level: number;
  /** has search string */
  search: boolean;
};

const { modelValue, level } = defineProps<Props>();

type Slots = {
  default(props: { child: _Tree }): VNode;
};

defineSlots<Slots>();

/** handle button key press */
const onKey = (event: KeyboardEvent, child: _Tree) => {
  const target = event.target as HTMLElement;

  const prevent = () => event.preventDefault();

  if (event.key === "ArrowRight") {
    prevent();
    if (child.children.length) {
      /** expand */
      if (!child.open) return (child.open = true);
      else
        /** go to child */
        return findClosest(
          target,
          (el) => el.matches(`button[data-level="${level + 1}"]`),
          "next",
        )?.focus();
    }
  }

  if (event.key === "ArrowLeft") {
    prevent();
    /** collapse */
    if (child.open) return (child.open = false);
    else
      /** go to parent */
      return findClosest(
        target,
        (el) => el.matches(`button[data-level="${level - 1}"]`),
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
</script>

<template>
  <div v-if="children.length" role="group" class="flex flex-col">
    <!-- list -->
    <div
      v-for="(child, index) in children"
      :key="index"
      class="relative flex flex-col"
      :class="[
        level > 1 &&
          'relative pl-4 before:absolute before:inset-y-0 before:left-3.5 before:w-0.5 before:bg-stone-50',
      ]"
      role="treeitem"
      :aria-selected="modelValue === child.id"
      :aria-expanded="child.open"
      :aria-level="level"
      :aria-setsize="children.length"
      :aria-posinset="index + 1"
    >
      <!-- row -->
      <div v-show="child.match" class="flex items-center gap-2">
        <!-- expand/collapse/select -->
        <button
          class="min-h-8 grow basis-0 justify-start gap-2 rounded-md p-1 text-left hover:bg-stone-100"
          :class="modelValue === child.id && 'bg-stone-100'"
          :data-level="level"
          :disabled="search && !!child.children.length"
          @click="
            () => {
              if (child.children.length) child.open = !child.open;
              else updateModelValue(child);
            }
          "
          @keydown="(event) => onKey(event, child)"
        >
          <!-- expand/collapse icon -->
          <template v-if="child.children.length">
            <ChevronDown v-if="child.open" class="text-stone-300" />
            <ChevronRight v-else class="text-stone-300" />
          </template>
          <!-- selection icon -->
          <template v-else>
            <Check v-if="modelValue === child.id" class="text-emerald-500" />
            <Check v-else class="opacity-0" />
          </template>

          <!-- text label -->
          <span>
            {{ child.label }}
          </span>

          <!-- count -->
          <span v-if="child.children.length" class="text-stone-300">
            {{ child.children.length.toLocaleString() }}
          </span>
        </button>

        <!-- action -->
        <slot v-if="!child.children.length" :child="child" />
      </div>

      <!-- children items -->
      <AppTreeItem
        v-show="child.open || (search && child.match)"
        :model-value="modelValue"
        :level="level + 1"
        :search="search"
        :children="child.children"
        :update-model-value="updateModelValue"
      >
        <template #default="slotProps">
          <slot name="default" v-bind="slotProps" />
        </template>
      </AppTreeItem>
    </div>
  </div>
</template>
