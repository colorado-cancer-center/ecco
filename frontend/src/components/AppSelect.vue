<template>
  <label class="container" @click.prevent>
    <div>{{ label }}</div>

    <Combobox
      :model-value="value"
      :multiple="multi"
      @update:model-value="onChange"
    >
      <Float
        :shift="10"
        :middleware="middleware"
        floating-as="template"
        portal
        adaptive-width
        strategy="fixed"
      >
        <!-- button -->
        <div class="row">
          <div v-if="!query" class="label">
            <span>
              {{ selectedLabel }}
            </span>
            <slot
              v-if="selectedOption"
              name="preview"
              :option="selectedOption"
            />
          </div>
          <ComboboxInput
            class="input"
            @blur="query = ''"
            @change="(event) => (query = event.target.value.toLowerCase())"
          />
          <ComboboxButton v-slot="{ open }" as="template">
            <AppButton :icon="open ? faCaretUp : faCaretDown" class="button" />
          </ComboboxButton>
          <AppButton
            v-if="multi"
            v-tooltip="'Deselect all'"
            :icon="faXmark"
            @click="$emit('update:modelValue', [])"
          />
        </div>

        <!-- dropdown -->
        <ComboboxOptions>
          <template v-for="(option, index) in filtered" :key="index">
            <!-- regular option -->
            <ComboboxOption
              v-if="isOption(option)"
              v-slot="{ active, selected }"
              as="template"
              :value="option"
            >
              <li
                :class="{ active, selected }"
                @vue:mounted="(node: VNode) => selected && onDropdownOpen(node)"
              >
                <font-awesome-icon
                  :style="{ opacity: selected ? 1 : 0 }"
                  :icon="faCheck"
                />
                <span>{{ option.label }}</span>
                <slot name="preview" :option="option" />
              </li>
            </ComboboxOption>
            <!-- group option -->
            <li v-else class="group">{{ option.group }}</li>
          </template>
        </ComboboxOptions>
      </Float>
    </Combobox>
  </label>
</template>

<script setup lang="ts" generic="O extends Option">
import { computed, ref, type VNode } from "vue";
import { size } from "@floating-ui/dom";
import {
  faCaretDown,
  faCaretUp,
  faCheck,
  faXmark,
} from "@fortawesome/free-solid-svg-icons";
import { Float } from "@headlessui-float/vue";
import {
  Combobox,
  ComboboxButton,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
} from "@headlessui/vue";
import AppButton from "@/components/AppButton.vue";
import { frame } from "@/util/misc";

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
};

const props = withDefaults(defineProps<Props>(), {
  multi: false,
  tooltip: "",
});

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

const emit = defineEmits<Emits>();

type Slots = {
  /**
   * extra preview element to show for each option in dropdown and selected
   * option in label
   */
  preview: (props: { option?: O }) => unknown;
};

defineSlots<Slots>();

/** combobox "typeahead" search */
const query = ref("");

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
function toArray<T>(value: T | T[]): T[] {
  return Array.isArray(value) ? value : [value];
}

/** type helper func to check if option is real option or group */
function isOption(option: O | Group | undefined): option is O {
  return !!option && "id" in option;
}

/** model value to pass from parent to headlessui */
const value = computed(() => {
  let list = toArray(props.modelValue);
  return props.multi
    ? props.options
        .filter(isOption)
        .filter((option) => list.includes(option.id))
    : props.options
        .filter(isOption)
        .find((option) => list.includes(option.id)) || "";
});

/** model value to emit from headlessui to parent */
async function onChange(value: O | O[]) {
  let list = toArray(value);
  const id = props.multi ? list.map((v) => v.id) : list[0]?.id || "";
  emit("update:modelValue", id);
}

/** results filtered by query string typed into input */
const filtered = computed(() =>
  props.options.filter(
    (option) =>
      !isOption(option) ||
      option.id.toLowerCase().includes(query.value) ||
      option.label.toLowerCase().includes(query.value),
  ),
);

/** full selected option (only relevant in single mode) */
const selectedOption = computed(() => {
  let list = toArray(props.modelValue);
  if (!props.multi)
    return props.options
      .filter(isOption)
      .find((option) => option.id === list[0]);
  else return undefined;
});

/** label to show as selected value in box */
const selectedLabel = computed<string>(() => {
  let list = toArray(props.modelValue);

  if (!props.multi) {
    const find = props.options
      .filter(isOption)
      .find((option) => option.id === list[0]);
    return (isOption(find) && find?.label) || "None selected";
  }

  const value = props.options
    .filter(isOption)
    .filter((option) => list.includes(option.id));
  if (value.length === 0) return "None selected";
  if (value.length === 1) return value[0]?.label || "1 Selected";
  if (value.length === props.options.length) return "All selected";
  return value.length + " selected";
});

/** when dropdown opened */
async function onDropdownOpen(node: VNode) {
  await frame();
  (node.el as Element).scrollIntoView();
}
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.row {
  display: grid;
  grid-template-columns: 1fr min-content min-content;
  align-items: center;
  border-radius: var(--rounded);
  background: var(--light-gray);
}

.label,
.input {
  grid-row: 1;
  grid-column: 1 / 2;
  padding-left: 10px;
}

.label {
  display: flex;
  z-index: 1;
  align-items: center;
  gap: 10px;
  pointer-events: none;
}

.label > :first-child {
  flex-grow: 1;
}

.input {
  align-self: stretch;
  border: none;
  background: none;
  font: inherit;
}

ul {
  max-width: calc(100vw - 60px);
  margin: 0;
  padding: 0;
  overflow-y: auto;
  overscroll-behavior: none;
  border-radius: var(--rounded);
  background: var(--white);
  box-shadow: var(--shadow);
}

li {
  display: flex;
  align-items: center;
  padding: 5px 10px;
  gap: 10px;
  list-style: none;
  cursor: pointer;
}

li span {
  flex-grow: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.active {
  background: var(--light-gray);
}

.group {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: var(--bold);
  cursor: unset;
}

.group::after {
  flex-grow: 1;
  height: 1px;
  background: var(--gray);
  content: "";
}
</style>
