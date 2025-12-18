import cv2
import face_recognition
import os
import datetime
import time
import serial
import serial.tools.list_ports
import numpy as np

# Cloud Libraries
import firebase_admin
from firebase_admin import credentials, firestore, storage

# --- CONFIGURATION ---
SERIAL_PORT = "COM5"
BAUD_RATE = 9600
KNOWN_FACES_DIR = "known_faces"
INTRUDERS_DIR = "intruders"
GCP_KEY_PATH = "serviceAccountKey.json"
BUCKET_NAME = "intruder-detection-image"
COLLECTION_NAME = "security_logs"

TOLERANCE = 0.5
MODEL = "hog"

# --- GLOBAL VARIABLES ---
db = None
bucket = None
ser = None

# --- INITIALIZATION FUNCTIONS ---

def initialize_gcp():
    """Initializes Google Cloud Firestore and Storage."""
    global db, bucket
    try:
        if not os.path.exists(GCP_KEY_PATH):
            print(f"[ERROR] GCP Key not found at {GCP_KEY_PATH}. Cloud logging detected disabled.")
            return

        cred = credentials.Certificate(GCP_KEY_PATH)
        firebase_admin.initialize_app(cred, {
            'storageBucket': BUCKET_NAME
        })
        db = firestore.client()
        bucket = storage.bucket()
        print("[INFO] Google Cloud Connected Successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to connect to GCP: {e}")

def initialize_serial():
    """Initializes Serial Connection to Microcontroller."""
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        # Allow time for arduino reset
        time.sleep(2) 
        print(f"[INFO] Serial Connected on {SERIAL_PORT}")
    except serial.SerialException:
        print(f"[WARNING] Could not connect to {SERIAL_PORT}. Running in Simulated Mode (No Hardware).")
        ser = None

# --- HELPER FUNCTIONS ---

def trigger_buzzer():
    """Sends command to Microcontroller to sound the alarm."""
    if ser:
        try:
            ser.write(b"ALARM_ON\n")
            print("[Sent] ALARM_ON signal to hardware.")
        except Exception as e:
            print(f"[ERROR] Serial write failed: {e}")
    else:
        print("[SIMULATION] Hardware Alarm Triggered (Buzzer ON)")

def upload_image_to_bucket(local_path):
    """Uploads file to GCS and returns public URL."""
    if not bucket:
        return "No Cloud Connection"
    
    try:
        filename = os.path.basename(local_path)
        blob = bucket.blob(filename)
        blob.upload_from_filename(local_path)
        blob.make_public()
        print(f"[CLOUD] Image uploaded: {blob.public_url}")
        return blob.public_url
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return "Upload Failed"

def log_event_to_firestore(name, status, image_url=None):
    """Logs the security event to Firestore."""
    if not db:
        return

    data = {
        "timestamp": firestore.SERVER_TIMESTAMP,
        "datetime_str": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unix_timestamp": time.time(),
        "name": name,
        "status": status,
        "device": "Laptop_Gateway"
    }
    if image_url:
        data["image_url"] = image_url

    try:
        db.collection(COLLECTION_NAME).add(data)
        print(f"[CLOUD] Event logged to Firestore: {status} - {name}")
    except Exception as e:
        print(f"[ERROR] Firestore log failed: {e}")

# --- CORE LOGIC ---

def load_known_faces(directory):
    # Reusing the robust logic from Phase 1
    encodings = []
    names = []
    if not os.path.exists(directory):
        os.makedirs(directory)
        return [], []

    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            path = os.path.join(directory, filename)
            try:
                img = cv2.imread(path)
                if img is None: continue
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype('uint8')
                face_encs = face_recognition.face_encodings(rgb)
                if face_encs:
                    encodings.append(face_encs[0])
                    # Name Parsing
                    basename = os.path.splitext(filename)[0]
                    if "_" in basename:
                         name_part = basename.rsplit('_', 1)[0]
                         suffix = basename.rsplit('_', 1)[1]
                         if suffix.isdigit() or len(suffix) < 3:
                             final_name = name_part
                         else:
                             final_name = basename
                    else:
                        final_name = basename
                    names.append(final_name.title())
            except:
                pass
    return encodings, names

def process_camera(known_encodings, known_names):
    """
    Opens camera, checks for ONE frame (or short duration), handles logic, then closes.
    """
    print("[ACTION] opening Camera for Verification...")
    cap = cv2.VideoCapture(0)
    
    # Warmup
    if not cap.isOpened():
        print("[ERROR] Camera failure.")
        return

    # Try to grab a valid frame for a few attempts
    frame = None
    for _ in range(5): 
        ret, temp_frame = cap.read()
        if ret:
            frame = temp_frame
            break
        time.sleep(0.1)

    if frame is None:
        print("[ERROR] Could not capture image.")
        cap.release()
        return

    # Process Frame
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype('uint8')
    face_locs = face_recognition.face_locations(rgb_frame, model=MODEL)
    face_encs = face_recognition.face_encodings(rgb_frame, face_locs)

    person_name = "Unknown"
    is_intruder = True

    if not face_locs:
        print("[RESULT] No face detected.")
        cap.release()
        return

    # Check matches (Best Match Logic)
    for encoding in face_encs:
        # Distance check
        distances = face_recognition.face_distance(known_encodings, encoding)
        if len(distances) > 0:
            best_idx = np.argmin(distances)
            if distances[best_idx] < TOLERANCE:
                person_name = known_names[best_idx]
                is_intruder = False
                break # Found a known person, stop checking
    
    # --- VISUALIZATION & DECISION ---
    
    # Draw results on frame for user feedback
    top, right, bottom, left = (face_locs[0]) # Use first detected face for visualization
    color = (0, 0, 255) if is_intruder else (0, 255, 0)
    label = "INTRUDER" if is_intruder else person_name
    
    # Draw box and label
    cv2.rectangle(frame, (left, top), (right, bottom), color, 3)
    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
    cv2.putText(frame, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)
    
    # Show the result for 3 seconds
    cv2.imshow('Security Provision', frame)
    cv2.waitKey(3000) 

    if not is_intruder:
        # Case A: Authorized
        print(f"✅ Welcome, {person_name}!")
        log_event_to_firestore(person_name, "Authorized")
    else:
        # Case B: Intruder
        print("🚨 INTRUDER DETECTED! 🚨")
        
        # 1. Hardware Action
        trigger_buzzer()
        
        # 2. Save Image
        if not os.path.exists(INTRUDERS_DIR): os.makedirs(INTRUDERS_DIR)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        img_name = f"intruder_{ts}.jpg"
        local_path = os.path.join(INTRUDERS_DIR, img_name)
        cv2.imwrite(local_path, frame)
        print(f"[EVIDENCE] Saved to {local_path}")
        
        # 3. Cloud Upload
        url = upload_image_to_bucket(local_path)
        
        # 4. Log
        log_event_to_firestore("Unknown", "Intruder", url)

    cap.release()
    cv2.destroyAllWindows()
    print("[ACTION] Camera Closed. Returning to Listen Mode.")

# --- MAIN LOOP ---

def main():
    print("--- SMART SECURITY GATEWAY STARTED ---")
    
    # Setup
    initialize_gcp()
    initialize_serial()
    
    # Pre-load faces
    print("[INFO] Loading Face Database...")
    known_encs, known_names = load_known_faces(KNOWN_FACES_DIR)
    print(f"[INFO] {len(known_names)} authorized people loaded.")

    print("\n[LISTENING] Waiting for 'MOTION' signal from Serial...")
    
    while True:
        if ser:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        print(f"[SERIAL] Received: {line}")
                        if "MOTION" in line:
                            process_camera(known_encs, known_names)
                            # Clear buffer to avoid repeat triggers
                            ser.reset_input_buffer()
            except Exception as e:
                print(f"[ERROR] Serial Loop: {e}")
                time.sleep(1)
        else:
            # Simulation fallback: Manual Input
            cmd = input("[SIMULATION] Type 'm' + Enter to simulate MOTION, or 'q' to quit: ")
            if cmd.lower() == 'm':
                process_camera(known_encs, known_names)
            elif cmd.lower() == 'q':
                break
        
        time.sleep(0.1)

if __name__ == "__main__":
    main()
