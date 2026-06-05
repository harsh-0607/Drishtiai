# Frontend

This repo currently contains only the `Camera.tsx` component.

To run a full frontend, scaffold a Vite + React + TypeScript app and place this file at:
`frontend/src/components/Camera.tsx`

Minimal steps:

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm run dev
```

Then import and render the camera in `src/App.tsx`:

```tsx
import Camera from "./components/Camera";

export default function App() {
  return <Camera language="hi" />;
}
```
