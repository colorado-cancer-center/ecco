<script lang="ts">
export type Option = {
  id: string;
  label: string;
  secondary?: string;
  [key: string]: unknown;
};

export type Group = {
  group: string;
};

export type Entry = Option | Group;
</script>

<script setup lang="ts" generic="O extends Option">
import type { VNode } from "vue";
import { computed, ref } from "vue";
import AppButton from "@/components/AppButton.vue";
import AppTooltip from "@/components/AppTooltip.vue";
import { frame } from "@/util/misc";
import { Check, ChevronDown, ChevronUp, X } from "@lucide/vue";
import {
  ListboxContent,
  ListboxItem,
  ListboxRoot,
  PopoverContent,
  PopoverPortal,
  PopoverRoot,
  PopoverTrigger,
} from "reka-ui";

type Props = {
  label?: string;
  options: (O | Group)[];
  multi?: boolean;
  truncate?: boolean;
};

type Value = O["id"] | O["id"][];

const {
  label,
  options,
  multi = false,
  truncate = false,
} = defineProps<Props>();

const modelValue = defineModel<Value>({ required: true });

type Slots = {
  /** label */
  default: () => unknown;
  /** extra preview for each option in dropdown and selected label */
  preview: (props: { option?: O }) => unknown;
};

defineSlots<Slots>();

/** normalize single/multi to array */
const toArray = <T,>(value: T | T[]): T[] =>
  Array.isArray(value) ? value : [value];

/** type helper func to check if option is real option or group */
const isOption = (option: unknown): option is O =>
  typeof option === "object" && option !== null && "id" in option;

/** options excluding groups */
const optionsOnly = computed(() => options.filter(isOption));

/** lookup option by id */
const optionLookup = computed(() =>
  Object.fromEntries(optionsOnly.value.map((option) => [option.id, option])),
);

/** model value to pass from listbox */
const value = computed(() => {
  const list = toArray(modelValue.value);
  return multi
    ? list.map((id) => optionLookup.value[id]).filter((option) => !!option)
    : optionLookup.value[list[0] ?? ""];
});

/** model value to emit from listbox to parent */
const onChange = (newValue: unknown) => {
  const list = toArray(newValue).filter(isOption);
  const id = multi ? list.map((option) => option.id) : list[0]?.id || "";
  modelValue.value = id;
  if (!multi) isOpen.value = false;
};

/** open state */
const isOpen = ref(false);

/** full selected option (only relevant in single mode) */
const selectedOption = computed(() => {
  const list = toArray(modelValue.value);
  if (!multi) return optionsOnly.value.find((option) => option.id === list[0]);
  else return undefined;
});

/** label to show as selected value in box */
const selectedLabel = computed<string>(() => {
  const list = toArray(modelValue.value);

  if (!multi) {
    const find = optionLookup.value[list[0] ?? ""];
    return find?.label || "None selected";
  }

  const value = optionsOnly.value.filter((option) => list.includes(option.id));
  if (value.length === 0) return "None selected";
  if (value.length === 1) return value[0]?.label || "1 Selected";
  if (value.length === options.length) return "All selected";
  return value.length + " selected";
});

/** when dropdown opened */
const onDropdownOpen = async (node: VNode) => {
  await frame();
  (node.el as Element).scrollIntoView({ block: "nearest" });
};

/** add "quick" arrow key select */
const onKeypress = async ({ key }: KeyboardEvent) => {
  if (!multi && (key === "ArrowLeft" || key === "ArrowRight")) {
    let index = options.findIndex((option) =>
      isOption(option) ? option.id === modelValue.value : false,
    );
    if (index === -1) return;

    if (key === "ArrowLeft")
      while (index > 0) {
        index--;
        if (isOption(options[index])) break;
      }

    if (key === "ArrowRight")
      while (index < options.length - 1) {
        index++;
        if (isOption(options[index])) break;
      }

    modelValue.value = (options[index] as O).id;
  }
};
</script>

<template>
  <label
    v-bind="$attrs"
    :class="multi ? 'grid grid-cols-[1fr_min-content]' : 'grid'"
    class="gap-2"
  >
    <div :class="['flex items-center gap-2', multi ? 'col-span-2' : '']">
      {{ label }}
      <slot />
    </div>

    <PopoverRoot v-model:open="isOpen">
      <!-- button -->
      <PopoverTrigger as-child>
        <AppButton class="overflow-auto" @keydown="onKeypress">
          <span class="grow text-left" :class="truncate && 'truncate'">
            {{ selectedLabel }}
          </span>
          <span v-if="selectedOption?.secondary" class="text-gray">
            {{ selectedOption.secondary }}
          </span>
          <slot v-if="selectedOption" name="preview" :option="selectedOption" />
          <ChevronUp v-if="isOpen" class="text-dark-gray" />
          <ChevronDown v-else class="text-dark-gray" />
        </AppButton>
      </PopoverTrigger>

      <!-- dropdown -->
      <PopoverPortal>
        <PopoverContent
          align="start"
          :collision-padding="10"
          class="z-100 max-h-(--reka-popover-content-available-height) w-(--reka-popover-trigger-width) overflow-y-auto overscroll-none rounded-md border border-gray bg-white"
        >
          <ListboxRoot
            :model-value="value"
            :multiple="multi"
            :selection-behavior="multi ? 'toggle' : 'replace'"
            @update:model-value="onChange"
          >
            <ListboxContent class="list-none">
              <template v-for="(option, index) in options" :key="index">
                <!-- regular option -->
                <ListboxItem
                  v-if="isOption(option)"
                  v-slot="{ selected }"
                  as-child
                  :value="option"
                >
                  <li
                    class="flex cursor-pointer items-center gap-2 p-2 transition hover:bg-pale data-highlighted:bg-pale data-[state='checked']:bg-pale"
                    @vue:mounted="
                      (node: VNode) => selected && onDropdownOpen(node)
                    "
                  >
                    <Check
                      class="text-success"
                      :class="selected ? 'opacity-100' : 'opacity-0'"
                    />
                    <span class="grow" :class="truncate && 'truncate'">
                      {{ option.label }}
                    </span>
                    <span v-if="option.secondary" class="text-gray">
                      {{ option.secondary }}
                    </span>
                    <slot name="preview" :option="option" />
                  </li>
                </ListboxItem>
                <!-- group option -->
                <li v-else class="flex items-center gap-2 p-2 pl-4 font-bold">
                  {{ option.group }}
                </li>
              </template>
            </ListboxContent>
          </ListboxRoot>
        </PopoverContent>
      </PopoverPortal>
    </PopoverRoot>

    <AppTooltip v-if="multi" content="Deselect all">
      <AppButton @click="modelValue = []">
        <X />
      </AppButton>
    </AppTooltip>
  </label>
</template>
