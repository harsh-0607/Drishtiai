import { useEffect, useState } from "react";

export function useRegisterSW() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!("serviceWorker" in navigator)) return;

    const register = async () => {
      try {
        const reg = await navigator.serviceWorker.register("/sw.js");
        if (reg.active) setReady(true);
      } catch {
        // ignore
      }
    };

    void register();
  }, []);

  return { ready };
}
