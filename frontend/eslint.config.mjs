import path from "node:path";
import { fileURLToPath } from "node:url";
import prettier from "eslint-plugin-prettier";
import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";

const compat = new FlatCompat({
  baseDirectory: path.dirname(fileURLToPath(import.meta.url)),
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

export default [
  ...compat.extends(
    "plugin:vue/vue3-recommended",
    "plugin:vuejs-accessibility/recommended",
    "eslint:recommended",
    "@vue/eslint-config-typescript",
    "@vue/eslint-config-prettier/skip-formatting",
  ),
  {
    plugins: {
      prettier,
    },
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
    },
    rules: {
      "prettier/prettier": "warn",
      "prefer-const": ["error", { destructuring: "all" }],
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { ignoreRestSiblings: true },
      ],
      "@typescript-eslint/consistent-type-definitions": ["error", "type"],
      "@typescript-eslint/consistent-type-imports": "error",
      "vue/no-v-html": "off",
      "vuejs-accessibility/label-has-for": [
        "error",
        {
          controlComponents: ["SliderRoot", "AppNumber"],
          required: { some: ["nesting", "id"] },
          allowChildren: true,
        },
      ],
    },
    files: ["**/*.ts", "**/*.vue"],
  },
  {
    ignores: ["dist"],
  },
];
