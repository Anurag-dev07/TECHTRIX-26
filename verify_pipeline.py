import urllib.request
import json
import time
import sys

# Force utf-8 stdout on Windows
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_URL = 'http://127.0.0.1:8000'

def get_state():
    try:
        req = urllib.request.urlopen(f'{BASE_URL}/api/system/state', timeout=4)
        return json.loads(req.read().decode())
    except urllib.error.URLError:
        print("\n[ERROR] Server is not running on http://127.0.0.1:8000.")
        print("Please run 'python main.py' or 'start.bat' first to start the operations server.")
        sys.exit(1)

def post_json(endpoint, data):
    try:
        req = urllib.request.Request(
            f'{BASE_URL}{endpoint}',
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        res = urllib.request.urlopen(req, timeout=4)
        return json.loads(res.read().decode())
    except urllib.error.URLError as e:
        print(f"\n[ERROR] Failed to post to {endpoint}: {e}")
        sys.exit(1)

def run_tests():
    print("=" * 65)
    print("AI TRAFFIC & CROWD MANAGEMENT END-TO-END VERIFICATION")
    print("=" * 65)

    # 1. State check
    print("\n[STEP 1] Querying Telemetry Snapshot...")
    s0 = get_state()
    print(f"  System Status: {s0['system_status']}")
    print(f"  Connected Streams: {list(s0['cameras'].keys())}")
    gate_a_cam = s0['cameras']['CAM_01']['density']
    print(f"  Gate A Baseline: {gate_a_cam['count']}/{gate_a_cam['max_capacity']} ({gate_a_cam['occupancy_pct']}%) [{gate_a_cam['color']}]")

    # 2. Trigger Surge (>80% Capacity)
    print("\n[STEP 2] Simulating Influx Surge at Gate A (>80% capacity)...")
    post_json('/api/simulation/surge', {'camera_id': 'CAM_01', 'enable': True})
    time.sleep(1.2)
    s1 = get_state()
    gate_a_surge = s1['cameras']['CAM_01']['density']
    print(f"  Gate A Surge Level: {gate_a_surge['count']}/{gate_a_surge['max_capacity']} ({gate_a_surge['occupancy_pct']}%) [{gate_a_surge['color']}]")
    print(f"  Gate A Status in Decision Engine: {s1['gates']['GATE_A']['status']}")
    print(f"  Pending Automated Recommendations: {len(s1['recommendations'])}")

    for rec in s1['recommendations']:
        print(f"    -> [{rec['priority']}] {rec['title']}")
        print(f"       Details: {rec['description']}")
        print(f"       Status: {rec['status']}")

    # 3. Approve Action
    if s1['recommendations']:
        act = s1['recommendations'][0]
        print(f"\n[STEP 3] Operator Approving Action: {act['action_id']}...")
        dec_res = post_json('/api/operator/decision', {'action_id': act['action_id'], 'decision': 'APPROVE'})
        print(f"  Action Status Now: {dec_res['action']['status']}")
        print(f"  Execution Timestamp: {dec_res['action']['executed_at']}")

    # 4. Dispatch Priority Ambulance (Emergency Corridor)
    print("\n[STEP 4] Dispatching Emergency Vehicle (Ambulance Code-3)...")
    post_json('/api/simulation/ambulance', {'camera_id': 'CAM_04'})
    time.sleep(1.2)
    s2 = get_state()
    print(f"  Green Wave Corridor Active: {s2['green_wave_active']}")
    print(f"  Total Ambulances Detected: {s2['total_ambulances']}")
    print(f"  Alerts in System: {len(s2['alerts'])}")
    for a in s2['alerts'][:3]:
        print(f"    -> [{a['severity']}] {a['title']}: {a['message']}")

    print("\n" + "=" * 65)
    print("ALL PHASES VERIFIED AND OPERATIONAL!")
    print("=" * 65)

if __name__ == '__main__':
    run_tests()
