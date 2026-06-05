import React, { useState } from "react";
import Camera from "./components/Camera";
import { useRegisterSW } from "./hooks/useRegisterSW";

export default function App() {
  const [text, setText] = useState<string>("");
  const { ready } = useRegisterSW();

  return (
    <main
      style={{ minHeight: "100vh", background: "#000", color: "#fff", padding: 16 }}
      aria-label="DRISHTI AI"
    >
      <h1 style={{ fontSize: 24, marginBottom: 12 }}>DRISHTI AI</h1>
      <div role="status" aria-label="Offline status" style={{ marginBottom: 12 }}>
        PWA: {ready ? "enabled" : "loading"}
      </div>

      <Camera mode="stream" language="hi" onSceneText={setText} />

      <section aria-label="Latest description" style={{ marginTop: 12 }}>
        <div style={{ fontSize: 18, lineHeight: 1.5 }}>{text}</div>
      </section>
    </main>
  );
}
