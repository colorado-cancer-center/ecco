<template>
  <div class="container">
    <Listbox
      v-slot="{ open }"
      :model-value="value"
      :multiple="multi"
      @update:model-value="onChange"
    >
      <ListboxLabel>{{ capitalize(label) || "-" }}:</ListboxLabel>
      <Float
        :shift="10"
        :middleware="middleware"
        floating-as="template"
        portal
        adaptive-width
        strategy="fixed"
      >
        >
        <ListboxButton as="template">
          <AppButton
            :icon="open ? faAngleUp : faAngleDown"
            :flip="true"
            class="button"
          >
            {{ capitalize(selectedLabel) }}
          </AppButton>
        </ListboxButton>
        <ListboxOptions>
          <ListboxOption
            v-for="option in options"
            v-slot="{ active, selected }"
            :key="option.id"
            as="template"
            :value="option"
          >
            <li :class="{ active, selected }">
              <font-awesome-icon
                :style="{ opacity: selected ? 1 : 0 }"
                :icon="faCheck"
              />
              <span>{{ capitalize(option.name) }}</span>
              <svg
                v-if="option.colors?.length"
                :viewBox="`0 0 ${option.colors.length} 1`"
                preserveAspectRatio="none"
              >
                <rect
                  v-for="(color, index) in option.colors"
                  :key="index"
                  :fill="color"
                  :x="index"
                  y="0"
                  width="1"
                  height="1"
                />
              </svg>
            </li>
          </ListboxOption>
        </ListboxOptions>
      </Float>
    </Listbox>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { capitalize } from "lodash";
import { size } from "@floating-ui/dom";
import {
  faAngleDown,
  faAngleUp,
  faCheck,
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
import { sleep } from "@/util/misc";

export type Option = { id: string; name: string; colors?: string[] };

type Props = {
  label: string;
  options: Option[];
  multi?: boolean;
  modelValue: Option["id"] | Option["id"][];
};

const props = withDefaults(defineProps<Props>(), { multi: false });

type Emits = {
  "update:modelValue": [Props["modelValue"]];
};

const emit = defineEmits<Emits>();

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

// model value to pass from parent to headlessui
const value = computed(() =>
  props.multi
    ? props.options.filter((option) => props.modelValue.includes(option.id))
    : props.options.find((option) => option.id === props.modelValue) || "",
);

// model value to emit from headlessui to parent
async function onChange(value: Option | Option[]) {
  const id = Array.isArray(value) ? value.map((v) => v.id) : value.id;
  // https://github.com/ycs77/headlessui-float/issues/80
  await sleep(10);
  emit("update:modelValue", id);
}

// label to show as selected value in box
const selectedLabel = computed<string>(() => {
  const value = props.multi
    ? props.options
        .filter((option) => props.modelValue.includes(option.id))
        .map((option) => option.name)
    : props.options.find((option) => option.id === props.modelValue)?.name ||
      "";
  if (!Array.isArray(value)) return value;
  if (value.length === 0) return "None selected";
  if (value.length === 1) return value[0] || "";
  if (value.length === props.options.length) return "All selected";
  return value.length + " selected";
});
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 10px;
}

.button :deep(span) {
  flex-grow: 1;
  text-align: left;
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

li svg {
  max-width: 100px;
  height: 1em;
}

.active {
  background: var(--off-white);
}
</style>
