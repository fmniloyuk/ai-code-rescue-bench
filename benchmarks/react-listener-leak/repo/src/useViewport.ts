import { useEffect, useState } from "react";
import { subscribeToResize } from "./resizeSubscription";

export function useViewport() {
  const [width, setWidth] = useState(0);
  useEffect(() => subscribeToResize(window, setWidth), []);
  return width;
}
