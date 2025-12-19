# Deploying to Google Cloud Run (GitHub Method)

Since you have your code on GitHub, the easiest way to deploy is using the **Google Cloud Console website**.

## Step 1: Ensure GitHub is Up-to-Date
I have already pushed the `Dockerfile` and `dashboard.py` updates to your repository.

## Step 2: Open Google Cloud Run
1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
2.  Search for **"Cloud Run"** in the top search bar and click it.
3.  Click **"CREATE SERVICE"** (top of the page).

## Step 3: Configure the Service
1.  **Source**: Select **"Continuously deploy new revisions from a source repository"**.
2.  **Click "SET UP CLOUD BUILD"**:
    -   **Provider**: GitHub.
    -   **Repository**: Select `IOT-Based-Intruder-Detection-System`.
    -   **Branch**: `^main$`.
    -   **Build Type**: Select **Dockerfile** (Source location: `/Dockerfile`).
    -   Click **SAVE**.

## Step 4: Service Settings
1.  **Service Name**: `security-dashboard`.
2.  **Region**: `asia-southeast1` (Singapore).
3.  **Authentication**: Select **"Allow unauthenticated invocations"** (This makes the website public).
4.  Expand **"Container, Networking, Security"** (Optional but recommended):
    -   Under **Settings**, set Memory to **512 MiB** or **1 GiB** (Streamlit can use a bit of RAM).
5.  Click **CREATE**.

## Step 5: Wait for Build
-   You will see a "Building and Deploying" screen.
-   Wait 2-3 minutes.
-   Once done, you will see a **green checkmark** and a URL at the top (e.g., `https://security-dashboard-xyz.run.app`).

## Troubleshooting
-   **"Build Failed"**: Click the "Logs" tab to see why.
-   **"Permission Denied"**: Check if the "Default Compute Service Account" has "Cloud Datastore User" role in IAM.
