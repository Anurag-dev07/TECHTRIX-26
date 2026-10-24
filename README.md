# TRACER // AI-Powered Traffic & Crowd Management System

An operational, real-time Computer Vision and Decision Support System engineered for city operation centers, public event venues, and emergency responders.

---

## System Architecture & Implemented Phases

### Phase 1: Computer Vision & Density Processing Engine
- **Object Detection & Classification**:
  - Distinguishes **Persons** (pedestrians) and **Vehicles** (cars, buses, motorcycles, ambulances).
  - Flexible architecture supporting YOLOv8 weights or high-fidelity simulated multi-agent video streams.
- **ByteTrack Tracking**:
  - Two-stage association (high-confidence detections first, occluded/low-confidence second) to trace trajectories and prevent double-counting.
  - Computes velocity vectors $(\Delta x, \Delta y)$ and trajectory tails.
- **Density Mapping Strategy**:
  - **Sparse / Moderate Areas**: Counts bounding boxes within defined Regions of Interest (ROIs/Polygons).
    $$\text{Density} = \frac{\text{Count of Entities}}{\text{Polygon Area } (m^2)}$$
  - **Ultra-Dense Crowds**: CSRNet-inspired continuous 2D Gaussian Kernel Density Estimation (KDE) convolution producing spatial heatmaps and integrated headcount.
- **Anomalies & Emergency Detection**:
  - **Headcount Spike Detection**: Tracks rate of change ($\Delta N / \Delta t$) to flag stampede risks.
  - **Movement Vector Turbulence**: Measures velocity drop and angular divergence (stagnation & choke-point blockage).
  - **Priority Vehicles**: Flags ambulances and emergency vehicles immediately with priority status.

---

### Phase 2: GIS Spatial Mapping & Heatmap Backend
- **Homography Coordinate Registration**:
  - Maps 2D camera pixel coordinates $(u, v)$ to Real-World Geodetic coordinates $(\text{Lat}, \text{Lng})$ using OpenCV perspective transformation (`cv2.findHomography` and `cv2.perspectiveTransform`).
- **Continuous Color-Coded Heatmap**:
  - 🟢 **Green**: Safe capacity ($< 40\%$)
  - 🟡 **Yellow**: Moderate / Monitor ($40\% - 75\%$)
  - 🔴 **Red**: Critical / Overcrowded ($> 75\%$)
- **Live WebSockets**:
  - High-frequency WebSocket endpoint `/ws/telemetry` broadcasting live annotated video frames, tracked coordinates, and density metrics.

---

### Phase 3: The Recommendation & Decision Engine
- **Rules-Based State Machine**:
  - **Inflow Diversion Rule**: When Gate A density exceeds 80%, flags Gate A as `BLOCKED` and computes the lowest-occupancy alternative (e.g. Gate C at 17.5%).
  - **Traffic Signal Optimization**: Dynamically adjusts green light timings at nearby intersections based on queue occupancy.
  - **Emergency Priority Corridor (Green Wave)**: When an emergency vehicle is detected, activates green signals along its route and sets diversion warnings on adjacent roads.
- **Operator Decision Workflow**:
  - Every recommendation card provides **Approve & Enforce** and **Override** controls.

---

### Phase 4: Centralized Authority Dashboard
- **Modern White Enterprise Theme**:
  - Clean, accessible light mode interface styled with Stripe/Apple aesthetic.
  - Interactive **Visual CAPTCHA & Authentication Portal** (default login: `admin` / `admin123`).
- **Organized Tabbed Sections**:
  1. 🗺️ **GIS Density & Heat Map**: Dedicated full-width interactive map with real-time intensity and radius sliders, gate capacity progress bars, and signal statuses.
  2. 📹 **Multi-Camera CCTV Grid**: 4 live camera feeds rendering YOLO bounding boxes, ByteTrack IDs, trajectory tails, and HUD statistics.
  3. ⚡ **Decision Engine**: Clean simulation testing controls ("Trigger Surge" & "Dispatch Ambulance") and action cards with one-click **[Approve & Enforce]** and **[Override]** buttons.
  4. 🔔 **Alert Feed**: Chronological log of crowd surges, stampede turbulence, and priority ambulance events.

---

## Quick Start & Running Locally

### 1. Launch Central Authority Dashboard & Operations Server
```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```
Then open your browser to **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

### 2. Run Phase 1 MVP Standalone Script
To run the standalone Python script demonstrating YOLO, ByteTrack, and ROI density rendering:
```bash
python phase1_mvp.py --frames 120 --output phase1_output_demo.mp4
```
This generates an annotated video `phase1_output_demo.mp4` with custom ROI zones and risk classifications.

### 3. Run Pipeline Verification Test
```bash
python verify_pipeline.py
```

---

## Public Datasets for Prototyping
- **Crowd Counting**: ShanghaiTech Dataset, UCF-QNRF, CrowdHuman
- **Traffic Analytics**: UA-DETRAC, CityFlow, MIO-TCD
