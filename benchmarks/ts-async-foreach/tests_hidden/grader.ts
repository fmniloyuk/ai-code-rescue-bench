import assert from "node:assert/strict";
import { settleAll } from "/workspace/src/settle.ts";

const mode = process.argv[2];

if (mode === "hidden") {
  const calls: string[] = [];
  await assert.rejects(
    settleAll(
      [{ id: "one", amountCents: 1 }, { id: "two", amountCents: 2 }, { id: "three", amountCents: 3 }],
      async (invoice) => {
        calls.push(invoice.id);
        if (invoice.id === "two") throw new Error("declined");
      },
    ),
  );
  assert.deepEqual(calls, ["one", "two"]);
} else if (mode === "security") {
  let active = 0;
  let maxActive = 0;
  await settleAll([{ id: "1", amountCents: 1 }, { id: "2", amountCents: 1 }], async () => {
    active += 1;
    maxActive = Math.max(maxActive, active);
    await new Promise((resolve) => setTimeout(resolve, 2));
    active -= 1;
  });
  assert.equal(maxActive, 1);
} else if (mode === "mutation") {
  const ids = Array.from({ length: 20 }, (_, index) => ({ id: String(index), amountCents: index }));
  const result = await settleAll(ids, async () => new Promise((resolve) => setTimeout(resolve, 0)));
  assert.deepEqual(result, ids.map((item) => item.id));
} else if (mode === "regression") {
  let calls = 0;
  assert.deepEqual(await settleAll([], async () => { calls += 1; }), []);
  assert.equal(calls, 0);
} else {
  process.exit(2);
}
