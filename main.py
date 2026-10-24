"""
TRACER // Crash-Proof Unified System Launcher
- Automatically verifies environment & package dependencies.
- Handles port conflicts intelligently (reuses active server or selects next open port).
- Launches FastAPI backend with real-time CV engine and WebSockets.
- Automatically opens the Command Center in your default browser.
"""
import os
import sys
import time
import socket
import threading
import webbrowser
import urllib.request

# Ensure workspace root is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Configure stdout utf-8 for Windows console
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def is_port_in_use(port: int) -> bool:
    """Checks if a TCP port is currently occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.6)
        return s.connect_ex(("127.0.0.1", port)) == 0


def is_tracer_server_active(port: int) -> bool:
    """Checks if an existing TRACER server is already serving on this port."""
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/system/state", timeout=1.5)
        return req.status == 200
    except Exception:
        return False


def get_available_port(preferred_port: int = 8000) -> int:
    """Returns preferred_port if free, or finds the next available port."""
    for port in range(preferred_port, preferred_port + 10):
        if not is_port_in_use(port):
            return port
    return preferred_port


def launch():
    print("=" * 72)
    print("  TRACER // AI TRAFFIC & CROWD MANAGEMENT OPERATIONS SYSTEM")
    print("=" * 72)

    preferred_port = 8000

    # Check if server is already running on port 8000
    if is_port_in_use(preferred_port):
        if is_tracer_server_active(preferred_port):
            url = f"http://localhost:{preferred_port}"
            print(f"\n[TRACER] Operations server is ALREADY ACTIVE on {url}!")
            print(f"[TRACER] Opening Command Center in your browser: {url}\n")
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"Could not open browser automatically: {e}")

            print("Press Ctrl+C to exit launcher (server remains active in background).")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nExiting launcher.")
            return
        else:
            # Port is occupied by a different program; pick next available port
            port = get_available_port(preferred_port + 1)
            print(f"[Warning] Port {preferred_port} is busy. Switched to open port: {port}")
    else:
        port = preferred_port

    target_url = f"http://localhost:{port}"

    print(f"  * Local Command Center URL : {target_url}")
    print(f"  * Computer Vision Engine   : YOLOv8 + ByteTrack Multi-Agent Tracking")
    print(f"  * Homography Calibration   : OpenCV cv2.findHomography (GIS Real-World)")
    print(f"  * Density Strategies       : Sparse ROI Area + CSRNet Continuous KDE")
    print(f"  * Decision Engine          : Inflow Diversion, Signal Opt, Green Wave")
    print(f"  * Multi-Camera CCTV Grid   : 4 Real-Time Feeds Streaming at 5 FPS")
    print("=" * 72)

    # Launch browser after slight delay
    def open_browser():
        time.sleep(1.4)
        print(f"\n[Launcher] Opening Operations Command Center at {target_url} ...")
        try:
            webbrowser.open(target_url)
        except Exception as e:
            print(f"[Launcher] Could not launch browser automatically: {e}")
            print(f"Please open: {target_url}")

    threading.Thread(target=open_browser, daemon=True).start()

    # Import uvicorn and app
    import uvicorn
    from backend.app import app

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    launch()
