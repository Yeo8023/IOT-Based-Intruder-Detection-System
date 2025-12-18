import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import plotly.express as px
import datetime

# --- CONFIGURATION ---
PAGE_TITLE = "IOT Security Dashboard"
COLLECTION_NAME = "security_logs"
GCP_KEY_PATH = "serviceAccountKey.json"

# --- INITIALIZATION ---
st.set_page_config(page_title=PAGE_TITLE, layout="wide")
st.title(f"🛡️ {PAGE_TITLE}")

# Connect to Firestore (Singleton to avoid re-initializing on reload)
@st.cache_resource
def get_db():
    try:
        # Check if already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(GCP_KEY_PATH)
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        st.error(f"Failed to connect to Firestore: {e}")
        return None

db = get_db()

# --- DATA LOADING ---
def load_data():
    if not db: return pd.DataFrame()
    
    docs = db.collection(COLLECTION_NAME).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(100).stream()
    
    data = []
    for doc in docs:
        d = doc.to_dict()
        # Handle different timestamp formats if legacy data exists
        if "datetime_str" in d:
            ts = d["datetime_str"]
        else:
            # Fallback to server timestamp conversion
            ts = d.get("timestamp", datetime.datetime.now())
            
        data.append({
            "Time": ts,
            "Name": d.get("name", "Unknown"),
            "Status": d.get("status", "Unknown"),
            "Image": d.get("image_url", None)
        })
    
    return pd.DataFrame(data)

# Auto-refresh button
if st.button('🔄 Refresh Data'):
    st.cache_data.clear()

df = load_data()

if not df.empty:
    # --- METRICS ---
    col1, col2, col3 = st.columns(3)
    
    total_detections = len(df)
    intruder_count = len(df[df["Status"] == "Intruder"])
    authorized_count = len(df[df["Status"] == "Authorized"])
    
    col1.metric("Total Events (Last 100)", total_detections)
    col2.metric("🚨 Intruders Detected", intruder_count, delta_color="inverse")
    col3.metric("✅ Authorized Access", authorized_count)

    st.markdown("---")

    # --- CHARTS ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Activity Overview")
        fig = px.pie(df, names='Status', title='Intruder vs Authorized Ratio', color='Status',
                     color_discrete_map={'Intruder':'red', 'Authorized':'green'})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Recent Timeline")
        # Ensure time is datetime for plotting
        df["Time"] = pd.to_datetime(df["Time"])
        fig2 = px.histogram(df, x="Time", color="Status", nbins=20, title="Events over Time",
                            color_discrete_map={'Intruder':'red', 'Authorized':'green'})
        st.plotly_chart(fig2, use_container_width=True)

    # --- LOGS TABLE ---
    st.subheader("📝 Activity Logs")
    
    # Display formatted table
    st.dataframe(
        df[["Time", "Name", "Status", "Image"]],
        column_config={
            "Image": st.column_config.LinkColumn("Evidence Photo")
        },
        use_container_width=True
    )

    # --- GALLERY ---
    st.subheader("🚨 Intruder Evidence Gallery")
    intruders = df[df["Status"] == "Intruder"]
    
    if not intruders.empty:
        # Show last 4 intruders in a grid
        cols = st.columns(4)
        for idx, row in enumerate(intruders.head(4).itertuples()):
            with cols[idx % 4]:
                if row.Image:
                    st.image(row.Image, caption=f"{row.Time}", use_container_width=True)
                else:
                    st.caption("No Image")
    else:
        st.info("No intruders detected recently.")

else:
    st.warning("No data found in Firestore yet. Run the Gateway script to generate logs.")
