// App.jsx
import { useState, Suspense } from "react";
import { motion } from "framer-motion";
import StarBackground from "./StarBackground";
import "./App.css";

const MODES = [
  { key: "emotion", label: "Emotion" },
  { key: "alphabet", label: "Alphabet (OCR)" },
  { key: "exercise", label: "Exercise" },
  { key: "object", label: "Objects" },
];

export default function App() {
  const [mode, setMode] = useState("emotion");

  return (
    <div className="app">
      {/* 3D Stars Background */}
      <StarBackground />

      <motion.h1
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 1 }}
        className="title"
      >
        AI Vision Console
      </motion.h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 1 }}
        className="subtitle"
      >
        {mode ? `Current Mode: ${MODES.find((m) => m.key === mode)?.label}` : "Select a mode to begin"}
      </motion.p>

      {/* Buttons */}
      <div className="controls">
        {MODES.map((m) => (
          <motion.button
            key={m.key}
            onClick={() => setMode(m.key)}
            className={`futuristic-btn ${mode === m.key ? "active" : ""}`}
            whileHover={{ scale: 1.1, boxShadow: "0px 0px 20px #00f" }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: "spring", stiffness: 200 }}
          >
            {m.label}
          </motion.button>
        ))}
      </div>

      {/* Video feed */}
      <motion.div
        className="viewer"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <img
          src={`http://localhost:5000/video_feed?mode=${mode}`}
          alt="video stream"
          className="stream"
        />
      </motion.div>

      <footer className="footer">
        Backend: Flask • Vision: OpenCV, MediaPipe, FER, YOLOv8
      </footer>
    </div>
  );
}
