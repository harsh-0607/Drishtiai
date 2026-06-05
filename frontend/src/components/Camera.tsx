import React, { useEffect, useMemo, useRef, useState } from "react";

type WsStatus = "connecting" | "open" | "closed" | "error";

type SceneResponse =
  | { status: "success"; text: string }
  | { status: "error"; text?: string };

export interface CameraProps {
  /** Optional language code (e.g. 'hi', 'en'). Defaults to 'hi'. */
  language?: string;
  /** Called when a new scene description arrives. */
  onSceneText?: (text: string) => void;
}

const FPS = 2;
const INTERVAL_MS = 1000 / FPS;

function getWsUrl(path: string) {
  // Support localhost dev and https production.
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}${path}`;
}

export default function Camera({ language = "hi", onSceneText }: CameraProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<number | null>(null);

  const [wsStatus, setWsStatus] = useState<WsStatus>("connecting");
  const [lastText, setLastText] = useState<string>("");
  const [cameraError, setCameraError] = useState<string>("");

  const wsUrl = useMemo(() => {
    const params = new URLSearchParams({ language });
    return getWsUrl(`/ws/scene?${params.toString()}`);
  }, [language]);

  useEffect(() => {
    let cancelled = false;

    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: {
            facingMode: { ideal: "environment" },
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
        });

        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }

        streamRef.current = stream;
        const video = videoRef.current;
        if (!video) return;

        video.srcObject = stream;
        // iOS Safari needs these for inline playback.
        video.playsInline = true;
        video.muted = true;

        await video.play();
      } catch (err) {
        console.error(err);
        setCameraError(
          "Camera permission denied or camera unavailable. Please allow camera access."
        );
      }
    }

    startCamera();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    // WebSocket setup
    const ws = new WebSocket(wsUrl);
    ws.binaryType = "arraybuffer";
    wsRef.current = ws;

    setWsStatus("connecting");

    ws.onopen = () => setWsStatus("open");
    ws.onclose = () => setWsStatus("closed");
    ws.onerror = () => setWsStatus("error");

    ws.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data) as SceneResponse;
        if (data.status === "success" && typeof data.text === "string") {
          setLastText(data.text);
          onSceneText?.(data.text);
        }
      } catch {
        // Ignore non-JSON responses
      }
    };

    return () => {
      try {
        ws.close();
      } catch {
        // ignore
      }
      wsRef.current = null;
    };
  }, [wsUrl, onSceneText]);

  useEffect(() => {
    // Frame capture loop at 2fps
    function stopTimer() {
      if (timerRef.current != null) {
        window.clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }

    async function sendFrame() {
      const ws = wsRef.current;
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      if (!video || video.readyState < 2) return; // HAVE_CURRENT_DATA
      if (!canvas) return;

      const w = video.videoWidth || 640;
      const h = video.videoHeight || 360;
      if (w === 0 || h === 0) return;

      canvas.width = w;
      canvas.height = h;

      const ctx = canvas.getContext("2d", { alpha: false });
      if (!ctx) return;

      ctx.drawImage(video, 0, 0, w, h);

      // Convert to JPEG blob (quality 0.7)
      const blob: Blob | null = await new Promise((resolve) =>
        canvas.toBlob(resolve, "image/jpeg", 0.7)
      );
      if (!blob) return;

      // Send as raw binary
      try {
        const buf = await blob.arrayBuffer();
        ws.send(buf);
      } catch (err) {
        console.error(err);
      }
    }

    // Start capturing only once camera is likely running.
    stopTimer();
    timerRef.current = window.setInterval(() => {
      // Use a microtask boundary to keep UI responsive
      void sendFrame();
    }, INTERVAL_MS);

    return () => {
      stopTimer();
    };
  }, [wsStatus]);

  useEffect(() => {
    // Cleanup: stop media tracks on unmount
    return () => {
      try {
        const stream = streamRef.current;
        stream?.getTracks().forEach((t) => t.stop());
      } finally {
        streamRef.current = null;
      }
    };
  }, []);

  return (
    <section
      aria-label="Camera view and scene description"
      role="region"
      style={{ display: "grid", gap: 12 }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
        <div aria-label="WebSocket connection status" role="status">
          Connection: {wsStatus}
        </div>
      </div>

      {cameraError ? (
        <div role="alert" aria-live="assertive">
          {cameraError}
        </div>
      ) : null}

      <video
        ref={videoRef}
        aria-label="Rear camera preview"
        role="img"
        style={{ width: "100%", maxHeight: 420, background: "#000" }}
      />

      {/* Offscreen canvas for frame capture */}
      <canvas
        ref={canvasRef}
        aria-hidden="true"
        style={{ display: "none" }}
      />

      <div
        role="status"
        aria-live="polite"
        aria-label="Latest scene description"
        style={{ fontSize: 16, lineHeight: 1.4 }}
      >
        {lastText || "Waiting for description…"}
      </div>

      <button
        type="button"
        aria-label="Replay last description"
        onClick={() => {
          if (!lastText) return;
          try {
            const utterance = new SpeechSynthesisUtterance(lastText);
            // Best-effort language
            utterance.lang = language;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
          } catch {
            // ignore
          }
        }}
        style={{ padding: 12, fontSize: 16 }}
      >
        Replay
      </button>
    </section>
  );
}
