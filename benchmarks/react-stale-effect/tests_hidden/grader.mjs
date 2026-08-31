import assert from "node:assert/strict";
import fs from "node:fs";

const mode = process.argv[2];
const source = fs.readFileSync("/workspace/src/UserPanel.tsx", "utf8");
const effect = source.match(/useEffect\([\s\S]*?\},\s*\[([^\]]*)\]\s*\)/);
assert.ok(effect, "effect dependency array missing");
const deps = effect[1].split(",").map((value) => value.trim()).filter(Boolean);

if (mode === "hidden") {
  assert.ok(deps.includes("userId"));
  assert.ok(deps.includes("fetchUser"));
} else if (mode === "security") {
  assert.ok(deps.includes("userId"), "user context changes must trigger a reload");
} else if (mode === "mutation") {
  assert.match(source, /let\s+active\s*=\s*true/);
  assert.match(source, /active\s*=\s*false/);
  assert.match(source, /if\s*\(active\)\s*setName/);
} else if (mode === "regression") {
  const config = JSON.parse(fs.readFileSync("/workspace/tsconfig.json", "utf8"));
  assert.equal(config.compilerOptions.strict, true);
} else {
  process.exit(2);
}
