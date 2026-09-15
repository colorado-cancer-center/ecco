import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from "@vue/eslint-config-typescript";
import skipFormatting from "eslint-config-prettier/flat";
import tailwind from "eslint-plugin-better-tailwindcss";
import prettier from "eslint-plugin-prettier/recommended";
import vue from "eslint-plugin-vue";
import vueA11y from "eslint-plugin-vuejs-accessibility";
import { globalIgnores } from "eslint/config";

export default defineConfigWithVueTs(
  {
    name: "app/files-to-lint",
    files: ["**/*.{vue,ts}"],
  },

  globalIgnores(["**/dist/**", "**/dist-ssr/**", "**/coverage/**"]),

  skipFormatting,

  {
    name: "Vue",
    extends: vue.configs["flat/recommended"],

    rules: {
      "prefer-const": ["error", { destructuring: "all" }],
      "vue/require-default-prop": "off",
      "vue/no-v-html": "off",
      "vue/no-template-shadow": "off",
    },
  },

  {
    extends: [vueTsConfigs.recommended],
    rules: {
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { ignoreRestSiblings: true },
      ],
      "@typescript-eslint/consistent-type-definitions": ["error", "type"],
      "@typescript-eslint/consistent-type-imports": "error",
    },
  },

  {
    name: "Vue A11y",
    extends: vueA11y.configs["flat/recommended"],
    rules: {
      "vuejs-accessibility/label-has-for": "off",
    },
  },

  {
    name: "Prettier",
    extends: [prettier],
    rules: {
      "prettier/prettier": "warn",
    },
  },

  {
    name: "Tailwind",
    extends: [tailwind.configs.recommended],
    rules: {
      "better-tailwindcss/enforce-consistent-line-wrapping": [
        "warn",
        {
          preferSingleLine: true,
          group: "never",
          printWidth: 0,
        },
      ],
      "better-tailwindcss/no-unknown-classes": ["warn", { ignore: ["step"] }],
    },
    settings: {
      "better-tailwindcss": { entryPoint: "src/styles.css" },
    },
  },
);
