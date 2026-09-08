import assert from "node:assert/strict";
import { subscribeToResize } from "/workspace/src/resizeSubscription.ts";

const mode = process.argv[2];
class Target {
  innerWidth = 10;
  listeners = new Set<() => void>();
  added: Array<() => void> = [];
  removed: Array<() => void> = [];
  addEventListener(_type: "resize", listener: () => void) { this.added.push(listener); this.listeners.add(listener); }
  removeEventListener(_type: "resize", listener: () => void) { this.removed.push(listener); this.listeners.delete(listener); }
  emit() { for (const listener of [...this.listeners]) listener(); }
}

if (mode === "hidden") {
  const target = new Target();
  const cleanup = subscribeToResize(target, () => undefined);
  cleanup();
  assert.equal(target.added[0], target.removed[0]);
} else if (mode === "security") {
  const target = new Target();
  let calls = 0;
  const cleanup = subscribeToResize(target, () => { calls += 1; });
  cleanup();
  target.emit();
  assert.equal(calls, 0);
} else if (mode === "mutation") {
  const target = new Target();
  let a = 0;
  let b = 0;
  const cleanA = subscribeToResize(target, () => { a += 1; });
  const cleanB = subscribeToResize(target, () => { b += 1; });
  cleanA();
  target.emit();
  assert.equal(a, 0);
  assert.equal(b, 1);
  cleanB();
  assert.equal(target.listeners.size, 0);
} else if (mode === "regression") {
  const target = new Target();
  const values: number[] = [];
  const cleanup = subscribeToResize(target, (width) => values.push(width));
  target.innerWidth = 77;
  target.emit();
  cleanup();
  assert.deepEqual(values, [77]);
} else {
  process.exit(2);
}
