import cv2
import face_recognition
import os
import datetime
import numpy as np

# --- Configuration ---
KNOWN_FACES_DIR = "known_faces"
INTRUDERS_DIR = "intruders"
TOLERANCE = 0.5  # Lowered to 0.5 for stricter matching (Reduces False Positives)
MODEL = "hog"    # Use "cnn" for more accuracy if you have GPU (CUDA setup required), else "hog"
FRAME_THICKNESS = 3
FONT_THICKNESS = 2

def load_known_faces(directory):
    """q
    Loads face images from the directory and encodes them.
    Returns:
        known_face_encodings (list): List of 128-d face encodings.
        known_face_names (list): List of corresponding names.
    """
    known_face_encodings = []
    known_face_names = []

    print(f"[INFO] Loading known faces from '{directory}'...")
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"[WARNING] '{directory}' directory not found. Created it.")
        return [], []

    files = os.listdir(directory)
    if not files:
        print(f"[WARNING] No images found in '{directory}'. Please add .jpg or .png files.")
        
    for filename in files:
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(directory, filename)
            try:
                # Use OpenCV to load, it is more robust than face_recognition.load_image_file
                image = cv2.imread(filepath)
                if image is None:
                    print(f"  - [WARNING] Could not read image {filename}. Check file integrity.")
                    continue

                # Convert to RGB (OpenCV loads as BGR)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Force uint8 and standard shape
                rgb_image = rgb_image.astype('uint8')

                # Get encoding
                encodings = face_recognition.face_encodings(rgb_image)
                
                if encodings:
                    encoding = encodings[0]
                    known_face_encodings.append(encoding)
                    
                    # Use filename without extension as name
                    # Clean up name: remove numbers/underscores at end (e.g. "Ali_02" -> "Ali")
                    basename = os.path.splitext(filename)[0]
                    if "_" in basename:
                         name_part = basename.rsplit('_', 1)[0]
                         suffix = basename.rsplit('_', 1)[1]
                         if suffix.isdigit() or len(suffix) < 3:
                             name = name_part
                         else:
                             name = basename
                    else:
                        name = basename
                    
                    known_face_names.append(name.title()) 
                    print(f"  - Loaded: {name}")
                else:
                    print(f"  - [WARNING] No face found in {filename}, skipping.")
            except Exception as e:
                print(f"  - [ERROR] Could not process {filename}: {e}")

    return known_face_encodings, known_face_names

def save_intruder(frame):
    """
    Saves the frame to the intruders directory with a timestamp.
    """
    if not os.path.exists(INTRUDERS_DIR):
        os.makedirs(INTRUDERS_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"intruder_{timestamp}.jpg"
    filepath = os.path.join(INTRUDERS_DIR, filename)
    
    cv2.imwrite(filepath, frame)
    print(f"[ALERT] Intruder detected! Snapshot saved: {filename}")

def main():
    # 1. Load Known Faces
    known_encodings, known_names = load_known_faces(KNOWN_FACES_DIR)
    
    # 2. Setup Webcam
    print("[INFO] Starting webcam...")
    video_capture = cv2.VideoCapture(0)
    
    if not video_capture.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    print("[INFO] Webcam started. Press 'q' to quit.")

    # Variables for 'save_intruder' cooldown (optional, to avoid spamming files)
    last_intruder_time = 0 
    INTRUDER_COOLDOWN = 2 # seconds

    while True:
        # 3. Capture Frame
        ret, frame = video_capture.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        # Convert the image from BGR (OpenCV) to RGB (face_recognition)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Force conversion to uint8 (dlib requires 8-bit images)
        # We also ensure it's contiguous in memory
        rgb_frame = rgb_frame.astype('uint8').copy()

        # 4. Detect Faces
        face_locations = face_recognition.face_locations(rgb_frame, model=MODEL)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Loop through each face found in the current frame
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Calculate distance to known faces
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            name = "INTRUDER"
            color = (0, 0, 255) # Red for intruder
            
            # Find the best match (smallest distance)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] < TOLERANCE:
                    name = known_names[best_match_index]
                    color = (0, 255, 0) # Green for known

            # 5. Draw Results
            cv2.rectangle(frame, (left, top), (right, bottom), color, FRAME_THICKNESS)
            
            # Draw label with background
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), FONT_THICKNESS)

            # 6. Handle Intruder Event
            if name == "INTRUDER":
                current_time = datetime.datetime.now().timestamp()
                if current_time - last_intruder_time > INTRUDER_COOLDOWN:
                    save_intruder(frame)
                    last_intruder_time = current_time

        # 7. Display Result
        cv2.imshow('Smart Urban Security - Phase 1', frame)

        # Quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
