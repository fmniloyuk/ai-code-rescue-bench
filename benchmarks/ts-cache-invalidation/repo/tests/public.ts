import assert from "node:assert/strict";
import { UserService, type User } from "../src/userService.ts";

let record: User = { id: "u1", name: "Old" };
const cache = new Map<string, User>();
const service = new UserService(
  {
    async get() { return { ...record }; },
    async update(id, name) { record = { id, name }; return { ...record }; },
  },
  {
    async get(key) { return cache.get(key); },
    async set(key, value) { cache.set(key, value); },
    async del(key) { cache.delete(key); },
  },
);
assert.equal((await service.getUser("u1")).name, "Old");
await service.updateUser("u1", "New");
assert.equal((await service.getUser("u1")).name, "New");
