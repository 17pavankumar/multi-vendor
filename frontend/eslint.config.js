import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import globals from "globals";

export default [
  { ignores: ["dist"] },
  {
    files: ["**/*.{js,jsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: "latest",
        ecmaFeatures: { jsx: true },
        sourceType: "module",
      },
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
      "no-unused-vars": ["error", { varsIgnorePattern: "^[A-Z_]" }],
      // This project deliberately uses plain fetch + useState for data
      // fetching instead of TanStack Query (explicit project choice —
      // fewer dependencies over the more common pairing), which means
      // every list/detail page's "fetch on mount, track loading/error"
      // effect calls setState synchronously in the effect body. That's
      // exactly what this rule flags; it's the intended pattern here,
      // not an oversight to fix by contorting each effect around it.
      "react-hooks/set-state-in-effect": "off",
    },
  },
];
