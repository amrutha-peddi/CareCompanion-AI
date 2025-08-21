import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from flask import Flask, Response, request, send_from_directory
from flask_cors import CORS
import cv2
import time
import numpy as np

# Optional imports
try:
    from fer import FER
except Exception:
    FER = None

try:
    import pytesseract
    TESSERACT_OK = True
except Exception:
    TESSERACT_OK = False

import mediapipe as mp

# YOLOv8
YOLO = None
try:
    from ultralytics import YOLO as _YOLO
    YOLO = _YOLO("yolov8n.pt")
except Exception:
    YOLO = None

# React build directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST_DIR = os.path.join(BASE_DIR, "dist")

app = Flask(__name__, static_folder=DIST_DIR, static_url_path="")
CORS(app)

# Mediapipe setups
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


# ------------------ UTILITIES ------------------ #
def draw_hud(frame, mode, fps):
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (20, 20), (380, 140), (255, 255, 255), -1)
    frame = cv2.addWeighted(overlay, 0.15, frame, 0.85, 0)
    cv2.putText(frame, f"Mode: {mode.upper()}", (32, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
    cv2.putText(frame, f"FPS: {fps:.1f}", (32, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
    return frame


def put_badge(frame, text, org=(30, 180), color=(0, 255, 180)):
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


def angle_3pts(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosang = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0)))


# ------------------ PROCESSOR CLASS ------------------ #
class Processor:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("⚠️ Could not open webcam")
        self.emotion_detector = FER(mtcnn=True) if FER else None
        self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.squat_state, self.curl_state = "up", "down"
        self.squat_count, self.curl_count = 0, 0
        self.last_time = time.time()
        self.fps = 0.0

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            # return a blank frame with error message
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            put_badge(frame, "⚠️ Camera not available", (100, 240), (0, 0, 255))
        return frame

    def update_fps(self):
        t = time.time()
        dt = t - self.last_time
        self.last_time = t
        self.fps = 1.0 / dt if dt > 0 else 0.0

    # ---- Processing modes (same as your code) ---- #
    def run_emotion(self, frame): ...
    def run_alphabet(self, frame): ...
    def run_exercise(self, frame): ...
    def run_object(self, frame): ...


processor = Processor()


# ------------------ STREAM ------------------ #
def gen_stream(mode="emotion"):
    print(f"▶️ Streaming started in mode: {mode}")
    while True:
        frame = processor.read()
        if mode == "emotion":
            frame = processor.run_emotion(frame)
        elif mode == "alphabet":
            frame = processor.run_alphabet(frame)
        elif mode == "exercise":
            frame = processor.run_exercise(frame)
        elif mode == "object":
            frame = processor.run_object(frame)
        else:
            put_badge(frame, "Unknown mode", (30, 180), (0, 0, 255))

        processor.update_fps()
        frame = draw_hud(frame, mode, processor.fps)

        ok, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ok:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route("/video_feed")
def video_feed():
    mode = request.args.get("mode", "emotion").lower()
    return Response(gen_stream(mode), mimetype="multipart/x-mixed-replace; boundary=frame")


# ------------------ REACT ROUTES ------------------ #
@app.route("/")
def serve_react():
    return send_from_directory(app.static_folder, "index.html")


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/video_feed"):
        return Response("Not Found", status=404)
    return send_from_directory(app.static_folder, "index.html")


# ------------------ MAIN ------------------ #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
