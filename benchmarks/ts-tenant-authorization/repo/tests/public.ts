import assert from "node:assert/strict";
import { canEditProject } from "../src/authorization.ts";

assert.equal(
  canEditProject(
    { id: "admin-a", tenantId: "tenant-a", role: "admin" },
    { id: "p", tenantId: "tenant-b", ownerId: "someone" },
  ),
  false,
);
