import parser from "/usr/local/lib/node_modules/@typescript-eslint/parser/dist/index.js";

export default [
  {
    files: ["**/*.ts"],
    languageOptions: {
      parser,
      parserOptions: { ecmaVersion: "latest", sourceType: "module" },
    },
    rules: {
      eqeqeq: "error",
      "no-var": "error",
      "no-eval": "error",
    },
  },
];
