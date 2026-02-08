import streamlit as st
import pandas as pd
from datetime import datetime
import io
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.database import SessionLocal, GameDataFile

st.set_page_config(page_title="Admin Panel", page_icon="🛡️")

st.title("🛡️ Admin Panel")

# --- Authentication (Simple Password for now) ---
# In production, use a more robust auth mechanism
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    password = st.text_input("Enter Admin Password", type="password")
    if password == "admin123": # Default simple password
        st.session_state.admin_authenticated = True
        st.rerun()
    elif password:
        st.error("Incorrect password")
    st.stop()

# --- Admin Interface ---

st.sidebar.success("Authenticated as Admin")
if st.sidebar.button("Logout"):
    st.session_state.admin_authenticated = False
    st.rerun()

st.success(f"Connected to Database: {SessionLocal().bind.url}")

tab1, tab2 = st.tabs(["📤 Smart Upload", "💾 Data Viewer"])

FILE_TYPES = {
    "betting_lines": "DraftKings Betting Lines (CSV)",
    "roster": "Team Rosters (NFL_roster.csv)",
    "dvoa_offensive": "DVOA Offensive (CSV)",
    "dvoa_defensive": "DVOA Defensive (CSV)",
    "def_vs_wr": "DVOA Def vs WR (CSV)",
    "receiving_usage": "Receiving Usage (CSV)",
    "rushing_usage": "Rushing Usage (CSV)",
    "passing_base": "Passing Base Stats (CSV)",
    "receiving_alignment": "Receiver Alignment (CSV)",
    "injury_report": "Injury Report (TXT/CSV)",
}

with tab1:
    st.header("Upload Game Data")
    st.caption("Upload raw data files here. They will be saved to the database and used for analysis.")

    col1, col2 = st.columns(2)
    with col1:
        selected_week = st.number_input("Select Week", min_value=1, max_value=22, value=st.session_state.get('week', 17))
    
    with col2:
        file_type_key = st.selectbox(
            "Select File Type", 
            options=list(FILE_TYPES.keys()),
            format_func=lambda x: FILE_TYPES[x]
        )

    uploaded_file = st.file_uploader("Choose CSV/TXT file", type=['csv', 'txt'])

    if uploaded_file and st.button("💾 Save to Database", type="primary"):
        try:
            # Read content
            content = uploaded_file.getvalue().decode('utf-8')
            
            # Save to DB
            session = SessionLocal()
            
            # Check if exists (overwrite logic)
            existing = session.query(GameDataFile).filter_by(
                week=selected_week, 
                file_type=file_type_key
            ).first()
            
            if existing:
                st.warning(f"Overwriting existing {FILE_TYPES[file_type_key]} for Week {selected_week}")
                existing.content = content
                existing.filename = uploaded_file.name
                existing.uploaded_at = datetime.utcnow()
            else:
                new_file = GameDataFile(
                    week=selected_week,
                    file_type=file_type_key,
                    filename=uploaded_file.name,
                    content=content
                )
                session.add(new_file)
            
            session.commit()
            session.close()
            st.success(f"✅ Successfully saved {uploaded_file.name} as {FILE_TYPES[file_type_key]}")
            
        except Exception as e:
            st.error(f"Error saving file: {e}")

with tab2:
    st.header("Database Content")
    
    session = SessionLocal()
    files = session.query(GameDataFile).order_by(GameDataFile.week.desc(), GameDataFile.uploaded_at.desc()).all()
    session.close()
    
    if not files:
        st.info("No files found in database.")
    else:
        # Group by week
        data = []
        for f in files:
            data.append({
                "Week": f.week,
                "Type": FILE_TYPES.get(f.file_type, f.file_type),
                "Filename": f.filename,
                "Uploaded": f.uploaded_at.strftime("%Y-%m-%d %H:%M"),
                "Size (KB)": f"{len(f.content)/1024:.1f}"
            })
        
        st.dataframe(pd.DataFrame(data), use_container_width=True)
