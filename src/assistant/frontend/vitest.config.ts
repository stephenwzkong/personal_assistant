import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config";
import path from "path";

const nm = path.resolve(__dirname, "node_modules");

export default mergeConfig(
  viteConfig,
  defineConfig({
    resolve: {
      alias: [
        // When test files (outside project root) import bare specifiers,
        // redirect them to this project's node_modules so Vite can find them.
        // Scoped packages: @scope/pkg, @scope/pkg/subpath
        {
          find: /^(@[^/]+\/[^/]+)(\/.*)?$/,
          replacement: `${nm}/$1$2`,
        },
        // Unscoped packages with subpaths: msw/node, react-router/...
        // (we only redirect if the import has a subpath to avoid colliding with actual files)
        {
          find: /^(msw|react|react-dom|react-router|vitest)(\/.*)?$/,
          replacement: `${nm}/$1$2`,
        },
      ],
    },
    test: {
      globals: true,
      environment: "jsdom",
      setupFiles: ["../../../tests/unit/frontend/setup.ts"],
      include: ["../../../tests/unit/frontend/**/*.test.{ts,tsx}"],
      css: false,
    },
  })
);
