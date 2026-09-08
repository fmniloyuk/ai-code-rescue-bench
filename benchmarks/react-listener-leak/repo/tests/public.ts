import assert from "node:assert/strict";
import { subscribeToResize } from "../src/resizeSubscription.ts";

class Target {
  innerWidth = 100;
  listeners = new Set<() => void>();
  addEventListener(_type: "resize", listener: () => void) { this.listeners.add(listener); }
  removeEventListener(_type: "resize", listener: () => void) { this.listeners.delete(listener); }
  emit() { for (const listener of this.listeners) listener(); }
}

const target = new Target();
const values: number[] = [];
const cleanup = subscribeToResize(target, (width) => values.push(width));
target.emit();
cleanup();
target.innerWidth = 200;
target.emit();
assert.deepEqual(values, [100]);
assert.equal(target.listeners.size, 0);
