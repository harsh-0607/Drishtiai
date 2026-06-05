import React, { useEffect, useMemo, useRef, useState } from "react";
import Camera from "./components/Camera";

export default function App() {
  const [text, setText] = useState<string>("");

  return (
    <main
      style={{ minHeight: "100vh", background: "#000", color: "#fff", padding: 16 }}
      aria-label="DRISHTI AI"
    >
      <h1 style={{ fontSize: 22, marginBottom: 12 }}>DRISHTI AI</h1>
      <Camera language="hi" onSceneText={setText} />
      <section aria-label="Latest description" style={{ marginTop: 12 }}>
        <div style={{ fontSize: 18, lineHeight: 1.5 }}>{text}</div>
      </section>
    </main>
  );
}
