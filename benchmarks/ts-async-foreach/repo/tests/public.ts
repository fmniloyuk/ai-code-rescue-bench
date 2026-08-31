import assert from "node:assert/strict";
import { settleAll } from "../src/settle.ts";

const calls: string[] = [];
const settled = await settleAll(
  [
    { id: "a", amountCents: 100 },
    { id: "b", amountCents: 200 },
  ],
  async (invoice) => {
    await new Promise((resolve) => setTimeout(resolve, 5));
    calls.push(invoice.id);
  },
);
assert.deepEqual(settled, ["a", "b"]);
assert.deepEqual(calls, ["a", "b"]);
