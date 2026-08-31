import assert from "node:assert/strict";
import fs from "node:fs";
import { spawnSync } from "node:child_process";

const mode = process.argv[2];
const tsconfig = JSON.parse(fs.readFileSync("/workspace/tsconfig.json", "utf8"));
const pkg = JSON.parse(fs.readFileSync("/workspace/package.json", "utf8"));
const source = fs.readFileSync("/workspace/src/index.ts", "utf8");

if (mode === "hidden") {
  const result = spawnSync("tsc", ["--noEmit"], { cwd: "/workspace", encoding: "utf8" });
  assert.equal(result.status, 0, result.stderr || result.stdout);
} else if (mode === "security") {
  assert.equal(pkg.type, "module");
  assert.equal(tsconfig.compilerOptions.module, "NodeNext");
} else if (mode === "mutation") {
  assert.match(source, /from\s+["']\.\/config\.js["']/);
} else if (mode === "regression") {
  assert.equal(tsconfig.compilerOptions.strict, true);
} else {
  process.exit(2);
}
