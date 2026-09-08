declare module "react" {
  export function useEffect(effect: () => void | (() => void), deps: readonly unknown[]): void;
  export function useState<T>(initial: T): [T, (value: T) => void];
}
