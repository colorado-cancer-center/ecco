import eslintPluginPrettierRecommended from "eslint-plugin-prettier/recommended";
import pluginVue from "eslint-plugin-vue";
import pluginVueA11y from "eslint-plugin-vuejs-accessibility";
import { globalIgnores } from "eslint/config";
import skipFormatting from "@vue/eslint-config-prettier/skip-formatting";
import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from "@vue/eslint-config-typescript";

export default defineConfigWithVueTs(
  globalIgnores(["**/dist/**", "**/dist-ssr/**", "**/coverage/**"]),

  pluginVue.configs["flat/recommended"],
  vueTsConfigs.recommended,
  pluginVueA11y.configs["flat/recommended"],
  skipFormatting,
  eslintPluginPrettierRecommended,

  {
    name: "app/files-to-lint",
    files: ["**/*.{ts,mts,tsx,vue}"],
    rules: {
      "prettier/prettier": "warn",
      "prefer-const": ["error", { destructuring: "all" }],
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { ignoreRestSiblings: true },
      ],
      "@typescript-eslint/consistent-type-definitions": ["error", "type"],
      "@typescript-eslint/consistent-type-imports": "error",
      "vue/require-default-prop": "off",
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
  },
);
