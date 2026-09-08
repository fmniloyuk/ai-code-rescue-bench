export interface ResizeTarget {
  innerWidth: number;
  addEventListener(type: "resize", listener: () => void): void;
  removeEventListener(type: "resize", listener: () => void): void;
}

export function subscribeToResize(target: ResizeTarget, notify: (width: number) => void): () => void {
  target.addEventListener("resize", () => notify(target.innerWidth));
  return () => target.removeEventListener("resize", () => notify(target.innerWidth));
}
