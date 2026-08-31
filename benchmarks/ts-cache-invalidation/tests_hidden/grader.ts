import assert from "node:assert/strict";
import { UserService, type User } from "/workspace/src/userService.ts";

const mode = process.argv[2];

function fixture(failUpdate = false) {
  let record: User = { id: "u1", name: "Old" };
  const values = new Map<string, User>();
  const deletes: string[] = [];
  const service = new UserService(
    {
      async get() { return { ...record }; },
      async update(id, name) {
        if (failUpdate) throw new Error("db failed");
        record = { id, name };
        return { ...record };
      },
    },
    {
      async get(key) { return values.get(key); },
      async set(key, value) { values.set(key, value); },
      async del(key) { deletes.push(key); values.delete(key); },
    },
  );
  return { service, values, deletes };
}

if (mode === "hidden") {
  const { service, values, deletes } = fixture(true);
  values.set("user:u1", { id: "u1", name: "Old" });
  await assert.rejects(service.updateUser("u1", "New"));
  assert.deepEqual(deletes, []);
  assert.equal(values.get("user:u1")?.name, "Old");
} else if (mode === "security") {
  const { service, values, deletes } = fixture();
  values.set("user:u2", { id: "u2", name: "Other" });
  await service.updateUser("u1", "New");
  assert.deepEqual(deletes, ["user:u1"]);
  assert.equal(values.get("user:u2")?.name, "Other");
} else if (mode === "mutation") {
  const { service, deletes } = fixture();
  await service.updateUser("u1", "A");
  await service.updateUser("u1", "B");
  assert.deepEqual(deletes, ["user:u1", "user:u1"]);
} else if (mode === "regression") {
  const { service } = fixture();
  assert.equal((await service.getUser("u1")).name, "Old");
} else {
  process.exit(2);
}
