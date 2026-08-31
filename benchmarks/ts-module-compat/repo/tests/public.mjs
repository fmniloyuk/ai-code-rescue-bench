import assert from "node:assert/strict";
import fs from "node:fs";

const config = JSON.parse(fs.readFileSync("tsconfig.json", "utf8"));
assert.equal(config.compilerOptions.moduleResolution, "NodeNext");
assert.equal(config.compilerOptions.module, "NodeNext");
