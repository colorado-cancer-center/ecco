<template>
  <label :class="multi ? 'multi' : 'single'">
    <div class="label" :style="{ gridColumn: multi ? 'span 2' : '' }">
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
            :icon="open ? faCaretUp : faCaretDown"
            :flip="true"
            class="box"
            @keydown="onKeypress"
          >
            <span class="box-label">
              {{ selectedLabel }}
            </span>
            <slot
              v-if="selectedOption"
              name="preview"
              :option="selectedOption"
            />
          </AppButton>
        </ListboxButton>

        <!-- dropdown -->
        <ListboxOptions class="list">
          <template v-for="(option, key) in options" :key="key">
            <!-- regular option -->
            <ListboxOption
              v-if="isOption(option)"
              v-slot="{ active, selected }"
              as="template"
              :value="option"
            >
              <li
                :class="['item', { active, selected }]"
                @vue:mounted="(node: VNode) => selected && onDropdownOpen(node)"
              >
                <font-awesome-icon
                  :style="{ opacity: selected ? 1 : 0 }"
                  :icon="faCheck"
                />
                <span class="item-label">{{ option.label }}</span>
                <slot name="preview" :option="option" />
              </li>
            </ListboxOption>
            <!-- group option -->
            <li v-else class="group item">{{ option.group }}</li>
          </template>
        </ListboxOptions>
      </Float>
    </Listbox>

    <AppButton
      v-if="multi"
      v-tooltip="'Deselect all'"
      :icon="faXmark"
      @click="$emit('update:modelValue', [])"
    />
  </label>
</template>

<script setup lang="ts" generic="O extends Option">
import type { VNode } from "vue";
import { computed } from "vue";
import { size } from "@floating-ui/dom";
import {
  faCaretDown,
  faCaretUp,
  faCheck,
  faXmark,
} from "@fortawesome/free-solid-svg-icons";
import { Float } from "@headlessui-float/vue";
import {
  Listbox,
  ListboxButton,
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

const {
  label,
  options,
  multi = false,
  modelValue,
  tooltip = "",
} = defineProps<Props>();

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

<style scoped>
.multi,
.single {
  display: grid;
  gap: 10px;
  cursor: pointer;
}

.multi {
  grid-template-columns: 1fr min-content;
}

.single {
  grid-template-columns: 1fr;
}

.box {
  overflow: auto;
}

.box :deep(.icon) {
  color: var(--gray);
}

.box-label {
  flex-grow: 1;
  overflow: hidden;
  text-align: left;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list {
  margin: 0;
  padding: 0;
  overflow-y: auto;
  overscroll-behavior: none;
  border-radius: var(--rounded);
  background: var(--white);
  box-shadow: var(--shadow);
}

.item {
  display: flex;
  align-items: center;
  padding: 5px 10px;
  gap: 10px;
  line-height: var(--compact);
  list-style: none;
  cursor: pointer;
}

.item-label {
  flex-grow: 1;
}

.active {
  background: var(--light-gray);
}

.selected {
  background: var(--theme-light);
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
