# Phase 1 Setup Guide: Face Recognition on Windows

This guide will help you set up the environment for the Face Recognition project, specifically focusing on installing `dlib` without C++ Build Tools using a pre-built wheel.

## Step 1: Check Python Version

We need to know your exact Python version to download the correct `dlib` wheel.

1.  Open Command Prompt (cmd) or PowerShell.
2.  Run the following command:
    ```bash
    python --version
    ```
    *Output Example:* `Python 3.11.5` -> This means you have version **3.11**.

## Step 2: Create a Virtual Environment

It is best practice to use a virtual environment to keep your project dependencies isolated.

1.  Navigate to your project directory:
    ```bash
    cd "c:\Local D\Educational\USM\Course\Y4S1\CPC357\assign\proj"
    ```
2.  Create the virtual environment (named `venv`):
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    *   **Command Prompt**: `venv\Scripts\activate`
    *   **PowerShell**: `.\venv\Scripts\Activate`
    *(You should see `(venv)` at the beginning of your command line)*

## Step 3: Install `dlib` (Option B: Pre-built Wheel)

Since you don't have C++ Build Tools, we will use a pre-compiled `.whl` file.

1.  **Download the Wheel**:
    *   Go to a repository that hosts dlib wheels, for example: [github.com/z-mahmud22/Dlib_Windows_Python3.x](https://github.com/z-mahmud22/Dlib_Windows_Python3.x) or search "dlib prebuilt wheel python windows".
    *   Look for a file that matches your Python version from Step 1.
        *   `cp39` = Python 3.9
        *   `cp310` = Python 3.10
        *   `cp311` = Python 3.11
        *   `cp312` = Python 3.12
    *   *Example*: If you have Python 3.11, download `dlib-19.24.99-cp311-cp311-win_amd64.whl`.
    *   **Save this file** in your project folder (`c:\Local D\Educational\USM\Course\Y4S1\CPC357\assign\proj`).

2.  **Install the Wheel**:
    *   Run the pip install command on the downloaded file. Replace `[filename]` with the actual name of the file you downloaded.
    ```bash
    pip install "dlib-19.24.99-cp311-cp311-win_amd64.whl"
    ```

## Step 4: Install Other Dependencies

Once `dlib` is successfully installed, install the remaining libraries using standard pip.
**Important**: You must use `numpy<2` because the pre-built dlib wheel is not compatible with the latest numpy 2.0.

```bash
pip install "numpy<2" opencv-python face_recognition pyserial firebase-admin google-cloud-storage
```

## Step 5: Google Cloud Setup (Phase 2)
1.  **Service Account Key**: You must have your Google Cloud Service Account JSON file.
2.  **Rename**: Rename the file to `serviceAccountKey.json`.
3.  **Place it**: Put it inside the project folder (next to `security_gateway.py`).

## Step 6: Run the Gateway
1.  **Hardware**: Ensure your Microcontroller is plugged into **COM5** (or update the script).
2.  **Run**:
    ```bash
    python security_gateway.py
    ```


1.  Ensure you have at least one image in the `known_faces/` folder (e.g., `ali.jpg`).
2.  Run the script:
    ```bash
    python face_rec_test.py
    ```
3.  Press 'q' to quit the application.
