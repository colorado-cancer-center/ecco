<template>
  <label
    :class="
      multi
        ? 'grid grid-cols-[1fr_min-content] gap-x-2 gap-y-1'
        : 'grid grid-cols-1 gap-y-1'
    "
  >
    <div :class="multi ? 'col-span-2' : ''">
      {{ label }}
    </div>

    <Listbox
      v-slot="{ open }"
      :model-value="value"
      :multiple="multi"
      @update:model-value="onChange"
    >
      <Float
        :middleware="middleware"
        floating-as="template"
        portal
        adaptive-width
        strategy="fixed"
      >
        <!-- button -->
        <ListboxButton as="template">
          <AppButton
            v-tooltip="tooltip"
            class="overflow-auto [&_.icon]:text-gray"
            @keydown="onKeypress"
          >
            <span :class="['grow text-left', truncate && 'truncate']">
              {{ selectedLabel }}
            </span>
            <slot
              v-if="selectedOption"
              name="preview"
              :option="selectedOption"
            />
            <ChevronUp v-if="open" class="text-dark-gray" />
            <ChevronDown v-else class="text-dark-gray" />
          </AppButton>
        </ListboxButton>

        <!-- dropdown -->
        <ListboxOptions
          class="list-none overflow-y-auto overscroll-none rounded-md bg-white shadow-md"
        >
          <template v-for="(option, index) in options" :key="index">
            <!-- regular option -->
            <ListboxOption
              v-if="isOption(option)"
              v-slot="{ active, selected }"
              as="template"
              :value="option"
            >
              <li
                :class="[
                  'flex cursor-pointer items-center p-2 transition',
                  { 'bg-light-gray': active, 'bg-theme-light': selected },
                ]"
                @vue:mounted="(node: VNode) => selected && onDropdownOpen(node)"
              >
                <Check :style="{ opacity: selected ? 1 : 0 }" />
                <span :class="['grow', truncate && 'truncate']">
                  {{ option.label }}
                </span>
                <slot name="preview" :option="option" />
              </li>
            </ListboxOption>
            <!-- group option -->
            <li v-else class="flex items-center gap-2 p-2 font-bold">
              {{ option.group }}
            </li>
          </template>
        </ListboxOptions>
      </Float>
    </Listbox>

    <AppButton
      v-if="multi"
      v-tooltip="'Deselect all'"
      @click="$emit('update:modelValue', [])"
    >
      <X />
    </AppButton>
  </label>
</template>

<script setup lang="ts" generic="O extends Option">
import type { VNode } from "vue";
import { computed } from "vue";
import AppButton from "@/components/AppButton.vue";
import { frame } from "@/util/misc";
import { size } from "@floating-ui/dom";
import { Float } from "@headlessui-float/vue";
import {
  Listbox,
  ListboxButton,
  ListboxOption,
  ListboxOptions,
} from "@headlessui/vue";
import { Check, ChevronDown, ChevronUp, X } from "@lucide/vue";

export type Option = {
  id: string;
  label: string;
  [key: string]: unknown;
};

export type Group = {
  group: string;
};

export type Entry = Option | Group;

type Props = {
  label: string;
  options: (O | Group)[];
  multi?: boolean;
  modelValue: O["id"] | O["id"][];
  tooltip?: string;
  truncate?: boolean;
};

const {
  label,
  options,
  multi = false,
  modelValue,
  tooltip = "",
  truncate = false,
} = defineProps<Props>();

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

const emit = defineEmits<Emits>();

type Slots = {
  /** extra preview for each option in dropdown and selected label */
  preview: (props: { option?: O }) => unknown;
};

defineSlots<Slots>();

/** floating-ui middleware */
const middleware = [
  size({
    apply({ availableHeight, elements }) {
      Object.assign(elements.floating.style, {
        /** limit popover height to available height */
        maxHeight: `${availableHeight - 20}px`,
      });
    },
  }),
];

/** normalize single/multi to array */
const toArray = <T,>(value: T | T[]): T[] =>
  Array.isArray(value) ? value : [value];

/** type helper func to check if option is real option or group */
const isOption = (option: O | Group | undefined): option is O =>
  !!option && "id" in option;

/** options excluding groups */
const optionsOnly = computed(() => options.filter(isOption));

/** lookup option by id */
const optionLookup = computed(() =>
  Object.fromEntries(optionsOnly.value.map((option) => [option.id, option])),
);

/** model value to pass from parent to headlessui */
const value = computed(() => {
  const list = toArray(modelValue);
  return multi
    ? list.map((id) => optionLookup.value[id]).filter((option) => !!option)
    : optionLookup.value[list[0] ?? ""];
});

/** model value to emit from headlessui to parent */
const onChange = async (value: O | O[]) => {
  const list = toArray(value);
  const id = multi ? list.map((option) => option.id) : list[0]?.id || "";
  emit("update:modelValue", id);
};

/** full selected option (only relevant in single mode) */
const selectedOption = computed(() => {
  const list = toArray(modelValue);
  if (!multi) return optionsOnly.value.find((option) => option.id === list[0]);
  else return undefined;
});

/** label to show as selected value in box */
const selectedLabel = computed<string>(() => {
  const list = toArray(modelValue);

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
      isOption(option) ? option.id === modelValue : false,
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

    emit("update:modelValue", (options[index] as O).id);
  }
};
</script>
