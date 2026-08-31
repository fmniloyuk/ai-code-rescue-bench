import assert from "node:assert/strict";
import { canEditProject } from "/workspace/src/authorization.ts";

const mode = process.argv[2];
const project = { id: "p", tenantId: "t1", ownerId: "owner" } as const;

if (mode === "hidden") {
  assert.equal(canEditProject({ id: "x", tenantId: "t1", role: "admin" }, project), true);
  assert.equal(canEditProject({ id: "owner", tenantId: "t1", role: "member" }, project), true);
  assert.equal(canEditProject({ id: "x", tenantId: "t1", role: "member" }, project), false);
} else if (mode === "security") {
  assert.equal(canEditProject({ id: "owner", tenantId: "t2", role: "member" }, project), false);
  assert.equal(canEditProject({ id: "x", tenantId: "t2", role: "admin" }, project), false);
} else if (mode === "mutation") {
  const tricky = { id: "p", tenantId: "tenant", ownerId: "u" } as const;
  assert.equal(canEditProject({ id: "u", tenantId: "tenant-admin", role: "admin" }, tricky), false);
} else if (mode === "regression") {
  assert.equal(canEditProject({ id: "same", tenantId: "t1", role: "admin" }, project), true);
} else {
  process.exit(2);
}
