import { useEffect } from "react";
import { useIl7Kernel } from "../hooks/useIl7Kernel";

// Simulate 8-second vitality windows
export function useMockEegService() {
  const { dispatch, state } = useIl7Kernel();

  useEffect(() => {
    if (state.il7State !== "SENSED") return;

    const interval = setInterval(() => {
      // Fake realistic vitality oscillation
      const base = 0.8 + Math.random() * 0.4;
      const vitality = base + Math.sin(Date.now() / 10000) * 0.2;
      dispatch({ type: "EEG_VITALITY", vitality });
    }, 8000);

    return () => clearInterval(interval);
  }, [state.il7State, dispatch]);
}