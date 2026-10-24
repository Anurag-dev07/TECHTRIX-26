"""
Phase 1 MVP: Computer Vision & Density Processing Engine
CONNECTED PIPELINE:
- Runs YOLOv8 and ByteTrack on input video feeds (custom video file, webcam, or realistic CCTV stream).
- Counts pedestrians and vehicles inside defined Regions of Interest (ROIs).
- Classifies zone risk status: 🟢 Green (<40%), 🟡 Yellow (40-75%), 🔴 Red (>75%).
- Connects directly to the Central Operations Web Interface via WebSockets at http://localhost:8000.
- Opens your browser automatically to complete the end-to-end prototype demo.
"""
import os
import sys
import argparse
import time
import threading
import webbrowser
import cv2
import numpy as np

# Force utf-8 encoding on standard output for Windows console
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Ensure workspace root and backend are in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(root_dir, "backend")
for p in [root_dir, backend_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend import config
from backend.cv_engine.homography import HomographyProjector
from backend.cv_engine.density import DensityEngine
from backend.cv_engine.tracker import ByteTracker
from backend.cv_engine.anomaly import AnomalyDetector
from backend.cv_engine.detector import ObjectDetector
from backend.video_sources.video_generator import CameraSimulator, VideoFileReader


def run_connected_app(
    video_source: str = "demo",
    port: int = 8000,
    open_browser: bool = True
):
    """
    Connects the Python Computer Vision Engine to the Web Interface
    to complete an end-to-end prototype demo.
    """
    print("=" * 72)
    print("  TRACER // CONNECTED COMPUTER VISION & WEB OPERATIONS PIPELINE")
    print("=" * 72)
    print(f"  * Video Source     : {video_source}")
    print(f"  * Operations UI    : http://localhost:{port}")
    print(f"  * Detection Model  : YOLOv8 (Pedestrians & Vehicles)")
    print(f"  * Tracking Engine  : ByteTrack Multi-Object Association")
    print(f"  * Density Strategy : Sparse/Moderate ROI Area + CSRNet Continuous KDE")
    print(f"  * Decision Engine  : Inflow Diversion & Emergency Priority Active")
    print("=" * 72)

    import uvicorn
    from backend.app import app, simulators, object_detector

    # If custom video source is specified, wire it to CAM_01
    if video_source != "demo":
        print(f"[Pipeline] Binding custom video source '{video_source}' to CAM_01...")
        cam_cfg = config.CAMERAS["CAM_01"]
        simulators["CAM_01"] = VideoFileReader(video_source, object_detector, cam_cfg)

    # Launch browser automatically
    if open_browser:
        def launch_web():
            time.sleep(1.2)
            url = f"http://localhost:{port}"
            print(f"\n[Pipeline] Opening connected Web Operations Center: {url}\n")
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"[Pipeline] Could not open browser: {e}")

        threading.Thread(target=launch_web, daemon=True).start()

    # Start FastAPI & WebSocket server
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


def run_batch_mp4(
    video_source: str = "demo",
    output_path: str = "phase1_output_demo.mp4",
    num_frames: int = 120
):
    """Runs batch CV video rendering without starting the web server."""
    print("=" * 70)
    print("TRACER // PHASE 1 MVP BATCH CV RECORDER")
    print("=" * 70)
    print(f"Source: {video_source}")
    print(f"Output Target: {output_path}")
    print(f"Max Frames: {num_frames}")

    cam_cfg = config.CAMERAS["CAM_01"]
    density_engine = DensityEngine(config.DENSITY_THRESHOLDS)
    tracker = ByteTracker(high_thresh=0.5, low_thresh=0.15, iou_thresh=0.25)
    anomaly_detector = AnomalyDetector()
    detector = ObjectDetector()
    homography = HomographyProjector(config.CAMERAS)

    cap = None
    sim = None
    if video_source != "demo" and os.path.exists(video_source):
        cap = cv2.VideoCapture(video_source)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 360
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
    else:
        sim = CameraSimulator("CAM_01", cam_cfg)
        width, height = 640, 360
        fps = 20

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    roi_polygon = cam_cfg["roi_polygon"]
    area_m2 = cam_cfg["area_m2"]
    max_capacity = config.GATES["GATE_A"]["max_capacity"]

    frame_idx = 0
    try:
        while frame_idx < num_frames:
            frame_idx += 1
            if cap:
                ret, frame = cap.read()
                if not ret:
                    break
                detections = detector.detect_frame(frame, cam_cfg)
            else:
                if frame_idx == 50:
                    sim.trigger_crowd_surge(True)
                raw_frame, detections = sim.step()
                frame = raw_frame

            tracks = tracker.update(detections)
            entity_points = [trk.center() for trk in tracks]

            density_info = density_engine.compute_roi_density(
                entity_points,
                roi_polygon,
                area_m2=area_m2,
                max_capacity=max_capacity
            )
            csrnet_info = density_engine.generate_csrnet_density_map(entity_points)
            alerts = anomaly_detector.evaluate_frame(
                cam_id="CAM_01",
                cam_name="Gate A Entry Turnstiles",
                current_count=density_info["count"],
                tracks=tracks,
                capacity_pct=density_info["occupancy_pct"]
            )
            annotated = detector.draw_overlays(
                frame,
                tracks,
                roi_polygon,
                cam_cfg["name"],
                density_info
            )
            out.write(annotated)

            status_tag = f"[{density_info['color']}]"
            sys.stdout.write(
                f"\rFrame {frame_idx:03d}/{num_frames} | Status: {density_info['status']:<8} {status_tag:<8} | "
                f"Count: {density_info['count']:2d}/{max_capacity} ({density_info['occupancy_pct']:5.1f}%) | "
                f"Density: {density_info['density_per_m2']:.3f} p/m2 | Tracks: {len(tracks):2d} | Alerts: {len(alerts)}"
            )
            sys.stdout.flush()
    finally:
        if cap:
            cap.release()
        out.release()

    print(f"\n\nRender complete! Saved video: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 1 MVP: CV Engine & Connected Operations Center")
    parser.add_argument("--video", type=str, default="demo", help="Input video path or 'demo'")
    parser.add_argument("--port", type=int, default=8000, help="Web Operations port")
    parser.add_argument("--batch-only", action="store_true", help="Only render output MP4 without starting web server")
    parser.add_argument("--output", type=str, default="phase1_output_demo.mp4", help="Output MP4 path for batch mode")
    parser.add_argument("--frames", type=int, default=120, help="Frames to render in batch mode")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    if args.batch_only:
        run_batch_mp4(args.video, args.output, args.frames)
    else:
        run_connected_app(args.video, args.port, not args.no_browser)
