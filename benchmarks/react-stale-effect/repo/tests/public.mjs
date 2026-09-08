import assert from "node:assert/strict";
import fs from "node:fs";

const source = fs.readFileSync("src/UserPanel.tsx", "utf8");
const effect = source.match(/useEffect\([\s\S]*?\},\s*\[([^\]]*)\]\s*\)/);
assert.ok(effect, "useEffect dependency array not found");
assert.match(effect[1], /\buserId\b/);
