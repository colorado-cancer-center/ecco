<template>
  <div class="container">
    <Listbox
      :model-value="value"
      :multiple="multi"
      @update:model-value="onChange"
    >
      <ListboxLabel>{{ label || "-" }}</ListboxLabel>
      <Float
        :shift="10"
        :middleware="middleware"
        floating-as="template"
        portal
        adaptive-width
        strategy="fixed"
      >
        <ListboxButton v-slot="{ open }" as="template">
          <AppButton
            v-tooltip="tooltip"
            :icon="open ? faCaretUp : faCaretDown"
            :flip="true"
            class="box"
            :style="{ gridColumn: multi ? '' : 'span 2' }"
            @keydown="onKeypress"
          >
            {{ selectedLabel }}
            <template #preview>
              <slot
                v-if="selectedOption"
                name="preview"
                :option="selectedOption"
              />
            </template>
          </AppButton>
        </ListboxButton>
        <ListboxOptions>
          <ListboxOption
            v-for="(option, index) in options"
            v-slot="{ active, selected }"
            :key="index"
            as="template"
            :value="option"
          >
            <li
              :class="{ active, selected }"
              @vue:mounted="(node: VNode) => selected && onOpen(node)"
            >
              <font-awesome-icon
                :style="{ opacity: selected ? 1 : 0 }"
                :icon="faCheck"
              />
              <span>{{ option.label }}</span>
              <slot name="preview" :option="option" />
            </li>
          </ListboxOption>
        </ListboxOptions>
      </Float>
    </Listbox>
    <AppButton
      v-if="multi"
      v-tooltip="allSelected ? 'Deselect all' : 'Select all'"
      :icon="allSelected ? faXmark : faCheckDouble"
      @click="toggleAll"
    />
  </div>
</template>

<script setup lang="ts" generic="O extends Option">
import { computed, type VNode } from "vue";
import { clamp } from "lodash";
import { size } from "@floating-ui/dom";
import {
  faCaretDown,
  faCaretUp,
  faCheck,
  faCheckDouble,
  faXmark,
} from "@fortawesome/free-solid-svg-icons";
import { Float } from "@headlessui-float/vue";
import {
  Listbox,
  ListboxButton,
  ListboxLabel,
  ListboxOption,
  ListboxOptions,
} from "@headlessui/vue";
import AppButton from "@/components/AppButton.vue";
import { frame } from "@/util/misc";

export type Option = {
  id: string;
  label: string;
  [key: string]: unknown;
};

type Props = {
  label: string;
  options: O[];
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
  // extra preview element to show for each option in dropdown and selected option in label
  preview: (props: { option?: O }) => unknown;
};

defineSlots<Slots>();

// floating-ui middleware
const middleware = [
  size({
    apply({ availableHeight, elements }) {
      Object.assign(elements.floating.style, {
        // limit popover height to available height
        maxHeight: `${availableHeight - 20}px`,
      });
    },
  }),
];

// normalize single/multi to array
function normalize<T>(value: T | T[]): T[] {
  return Array.isArray(value) ? value : [value];
}

// model value to pass from parent to headlessui
const value = computed(() => {
  let list = normalize(props.modelValue);
  return props.multi
    ? props.options.filter((option) => list.includes(option.id))
    : props.options.find((option) => list.includes(option.id)) || "";
});

// model value to emit from headlessui to parent
async function onChange(value: O | O[]) {
  let list = normalize(value);
  const id = props.multi ? list.map((v) => v.id) : list[0]?.id || "";
  emit("update:modelValue", id);
}

// full selected option
const selectedOption = computed(() => {
  // normalize to array
  let list = normalize(props.modelValue);
  if (!props.multi)
    return props.options.find((option) => option.id === list[0]);
  else return undefined;
});

// label to show as selected value in box
const selectedLabel = computed<string>(() => {
  // normalize to array
  let list = normalize(props.modelValue);
  if (!props.multi)
    return (
      props.options.find((option) => option.id === list[0])?.label ||
      "None selected"
    );
  const value = props.options.filter((option) => list.includes(option.id));
  if (value.length === 0) return "None selected";
  if (value.length === 1) return value[0]?.label || "1 Selected";
  if (value.length === props.options.length) return "All selected";
  return value.length + " selected";
});

// whether all options are selected
const allSelected = computed(
  () => props.multi && props.options.length === props.modelValue.length,
);

// select/deselect all
function toggleAll() {
  emit(
    "update:modelValue",
    allSelected.value ? [] : props.options.map((option) => option.id),
  );
}

// add "quick" arrow key select
function onKeypress({ key }: KeyboardEvent) {
  if (!props.multi && (key === "ArrowLeft" || key === "ArrowRight")) {
    let index = props.options.findIndex(
      (option) => option.id === props.modelValue,
    );
    if (key === "ArrowLeft") index--;
    if (key === "ArrowRight") index++;
    index = clamp(index, 0, props.options.length - 1);
    const id = props.options[index]?.id;
    if (id) emit("update:modelValue", id);
  }
}

// when listbox opened
async function onOpen(node: VNode) {
  await frame();
  (node.el as Element).scrollIntoView();
}
</script>

<style scoped>
.container {
  display: grid;
  grid-template-columns: 1fr min-content;
  gap: 10px;
}

.container > label {
  grid-column: span 2;
}

.box :deep(span) {
  flex-grow: 1;
  text-align: left;
}

.box :deep(svg) {
  color: var(--gray);
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
  background: var(--off-white);
}
</style>
