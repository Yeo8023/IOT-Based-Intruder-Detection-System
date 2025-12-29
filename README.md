# 🛡️ IOT-Based Intruder Detection System

A smart security system that uses facial recognition to detect intruders and alerts through hardware buzzer and cloud logging.

## 📋 Features

- **Real-time Face Recognition** - Identifies authorized users vs intruders
- **Hardware Integration** - PIR motion sensor + buzzer alarm on ESP32 microcontroller
- **Cloud Logging** - Stores events and intruder photos in Firebase
- **Web Dashboard** - Monitor security logs and view intruder evidence gallery
- **Smart Alerts** - Welcome beep for authorized users, loud alarm for intruders

## 🌍 SDG 11 Impact Analysis

**Goal 11: Sustainable Cities and Communities**
*Target 11.7: Provide universal access to safe, inclusive and accessible, green and public spaces.*

This project directly contributes to Smart City safety by:
1.  **Automated Surveillance**: Reducing the need for manual guarding of public/private spaces using 24/7 IoT monitoring.
2.  **Crime Deterrence**: Immediate localized alarms (Buzzer) and cloud evidence storage deter unauthorized access.
3.  **Data-Driven Security**: The centralized dashboard allows security personnel to monitor multiple entry points remotely, ensuring efficient resource allocation for urban safety.

## 🔧 Hardware Requirements

- Maker Feather AIoT S3 (ESP32-S3) microcontroller
- PIR Motion Sensor (connected to GPIO 4)
- Passive Buzzer (connected to GPIO 39)
- Laptop/PC with webcam

## 💻 Software Requirements

- Python 3.8 or higher
- Arduino IDE (for microcontroller)
- Google Firebase account

## 🚀 Quick Setup

### 1. Check Your Python Version

```bash
python --version
# Example output: Python 3.10.5 → You need Python 3.10 wheels
```

Note your Python version (3.9, 3.10, 3.11, etc.) for the next step.

### 2. Create Virtual Environment (Recommended)

```bash
# Navigate to project directory
cd IOT-Based-Intruder-Detection-System

# Create and activate virtual environment
python -m venv venv

# Activate:
# Windows CMD: venv\Scripts\activate
# Windows PowerShell: .\venv\Scripts\Activate
# Linux/Mac: source venv/bin/activate
```

### 3. Install Python Dependencies

**For Windows users**, you must install `dlib` manually first (it requires C++ tools otherwise).

1.  **Download the correct wheel:**
    Go to the [Dlib Repository](https://github.com/z-mahmud22/Dlib_Windows_Python3.x) and download the `.whl` file matching your Python version:
    *   `cp39` → Python 3.9
    *   `cp310` → Python 3.10 (*Recommended*)
    *   `cp311` → Python 3.11

    *Save the file inside this project folder.*

2.  **Install the wheel:**
    ```bash
    # Example for Python 3.10 (Update filename if yours is different)
    pip install dlib-19.22.99-cp310-cp310-win_amd64.whl
    ```

3.  **Install remaining dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 4. Setup Firebase

1. Create a Firebase project at https://console.firebase.google.com
2. Enable Firestore Database and Storage
3. Download service account key as `serviceAccountKey.json`
4. Place it in the project root directory

### 5. Configure Arduino

1. Open `arduinocode.ino` in Arduino IDE
2. Select board: **Tools → Board → ESP32 Arduino → Cytron Maker Feather AIoT S3**
3. Select your COM port: **Tools → Port → COMX**
4. Upload the code to the microcontroller

### 6. Add Known Faces

1. Create a `known_faces` folder in the project root
2. Add photos of authorized people (one face per image)
3. Name files: `PersonName.jpg` or `PersonName1.jpg`, `PersonName2.jpg`
   - Tip: Multiple photos per person improves recognition

### 7. Update COM Port

Edit `security_gateway.py` line 15:
```python
SERIAL_PORT = "COM3"  # Change to your microcontroller's COM port
```

## ▶️ Running the System

### Start Security Gateway (Main System)

```bash
python security_gateway.py
```

This will:
- Connect to Firebase
- Connect to Arduino via serial
- Wait for motion detection
- Perform face recognition when motion is detected

### Start Dashboard (Optional)

```bash
streamlit run dashboard.py
```

Access at: http://localhost:8501

## 📖 How It Works

1. **PIR sensor detects motion** → Arduino sends "MOTION" signal to Python
2. **Camera captures image** → Python performs face recognition
3. **If authorized** → Welcome beep plays, logs to Firebase
4. **If intruder** → Loud alarm plays, saves photo, uploads to cloud
5. **View logs** → Dashboard shows all events and intruder photos

## 📁 Project Structure

```
IOT-Based-Intruder-Detection-System/
├── arduinocode.ino              # Microcontroller code
├── security_gateway.py          # Main detection system (Edge)
├── dashboard.py                 # Web dashboard (Cloud/App)
├── Dockerfile                   # Cloud Run container config
├── requirements.txt             # Project dependencies
├── requirements_dashboard.txt   # Optimized Cloud dependencies
├── serviceAccountKey.json       # Firebase credentials
├── dlib-19.22.99-cp310-*.whl    # Facial recognition wheel
├── known_faces/                 # Authorized people photos
├── intruders/                   # Captured intruder photos
└── .gitignore                   # Git configuration
```

## 🎛️ Configuration

Edit `security_gateway.py` to customize:

- `SERIAL_PORT` - Arduino COM port (line 15)
- `TOLERANCE` - Face recognition sensitivity (line 23, lower = stricter)
- `PREVIEW_DURATION_SECONDS` - Camera preview time (line 27)

## ❓ Troubleshooting

**Camera not opening?**
- Make sure no other application is using the camera
- Try running as administrator

**Arduino not connecting?**
- Check COM port in Device Manager
- Install CP210x USB driver if needed

**Face recognition not working?**
- Ensure good lighting in photos and detection
- Add 2-3 photos per person from different angles
- Adjust `TOLERANCE` value (0.4-0.6 range)

## 📝 License

This project is for educational purposes: CPC357 Project

## 👥 Group Members

| Name | Matric No. |
| :--- | :--- |
| **Lim Yong Jun** | 164598 |
| **Yeo Din Song** | 163369 |
