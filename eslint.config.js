import tailwindcss from "eslint-plugin-tailwindcss";
import prettier from "eslint-plugin-prettier";

export default [
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
    },
    plugins: {
      tailwindcss,
      prettier,
    },
    rules: {
      "prettier/prettier": "error", // Prettier kurallarını ESLint ile kontrol et
      "tailwindcss/classnames-order": "warn", // Tailwind sınıf sırasını kontrol et
    },
  },
];
