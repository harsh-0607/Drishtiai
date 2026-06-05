import React, { useEffect, useMemo, useRef, useState } from "react";

type WsStatus = "connecting" | "open" | "closed" | "error";

type StreamMsg =
  | { type: "scene"; message: string; language?: string }
  | { type: "obstacle"; message: { obstacles: any[] } }
  | { type: "face"; message: any };

export interface CameraProps {
  language?: string;
  userId?: string;
  mode?: "scene" | "stream";
  onSceneText?: (text: string) => void;
  onStreamMessage?: (msg: StreamMsg) => void;
}

const FPS = 2;
const INTERVAL_MS = 1000 / FPS;

function getWsUrl(path: string) {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}${path}`;
}

export default function Camera({
  language = "hi",
  userId,
  mode = "stream",
  onSceneText,
  onStreamMessage,
}: CameraProps) {
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
    if (userId) params.set("user_id", userId);

    const endpoint = mode === "scene" ? "/ws/scene" : "/ws/stream";
    return getWsUrl(`${endpoint}?${params.toString()}`);
  }, [language, userId, mode]);

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
    void startCamera();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const ws = new WebSocket(wsUrl);
    ws.binaryType = "arraybuffer";
    wsRef.current = ws;
    setWsStatus("connecting");

    ws.onopen = () => setWsStatus("open");
    ws.onclose = () => setWsStatus("closed");
    ws.onerror = () => setWsStatus("error");

    ws.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data) as any;
        if (data?.status === "success" && typeof data.text === "string") {
          // /ws/scene format
          setLastText(data.text);
          onSceneText?.(data.text);
          return;
        }

        if (data?.type) {
          // /ws/stream format
          if (data.type === "scene" && typeof data.message === "string") {
            setLastText(data.message);
            onSceneText?.(data.message);
          }
          onStreamMessage?.(data as StreamMsg);
        }
      } catch {
        // ignore
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
  }, [wsUrl, onSceneText, onStreamMessage]);

  useEffect(() => {
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
      if (!video || video.readyState < 2) return;
      if (!canvas) return;

      const w = video.videoWidth || 640;
      const h = video.videoHeight || 360;
      if (w === 0 || h === 0) return;

      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext("2d", { alpha: false });
      if (!ctx) return;

      ctx.drawImage(video, 0, 0, w, h);

      const blob: Blob | null = await new Promise((resolve) =>
        canvas.toBlob(resolve, "image/jpeg", 0.7)
      );
      if (!blob) return;

      try {
        const buf = await blob.arrayBuffer();
        ws.send(buf);
      } catch (err) {
        console.error(err);
      }
    }

    stopTimer();
    timerRef.current = window.setInterval(() => {
      void sendFrame();
    }, INTERVAL_MS);

    return () => {
      stopTimer();
    };
  }, [wsStatus]);

  useEffect(() => {
    return () => {
      try {
        streamRef.current?.getTracks().forEach((t) => t.stop());
      } finally {
        streamRef.current = null;
      }
    };
  }, []);

  return (
    <section
      aria-label="Camera view and assistant output"
      role="region"
      style={{ display: "grid", gap: 12 }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
        <div aria-label="Connection status" role="status">
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

      <canvas ref={canvasRef} aria-hidden="true" style={{ display: "none" }} />

      <div
        role="status"
        aria-live="polite"
        aria-label="Latest assistant message"
        style={{ fontSize: 18, lineHeight: 1.5 }}
      >
        {lastText || "Waiting for response…"}
      </div>

      <button
        type="button"
        aria-label="Replay last message"
        onClick={() => {
          if (!lastText) return;
          try {
            const u = new SpeechSynthesisUtterance(lastText);
            u.lang = language;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(u);
          } catch {
            // ignore
          }
        }}
        style={{ padding: 16, fontSize: 18, minHeight: 60 }}
      >
        Replay
      </button>
    </section>
  );
}
