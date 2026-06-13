import { defineConfig } from "orval";

export default defineConfig({
  api: {
    input: {
      target: "../backend/api.yml",
    },
    output: {
      target: "src/gen/client.ts",
      schemas: "src/gen/model",
      client: "fetch",
      mode: "tags-split",
      clean: true,
    },
  },
});
