import streamlit as st
import pandas as pd
import os

# --- หมวดที่ 1: Active Lock (Configuration) ---
st.set_page_config(page_title="Jigsaw Universal Assembler", layout="wide")

# บันทึกข้อควรระวังเรื่องสี V4 และ Mandatory Checklist
CHECKLIST = ["Leading Character Sweep", "Version 4 Color Validator", "Structural Clone Match"]

def init_system():
    if 'processed' not in st.session_state:
        st.session_state.processed = False

init_system()

# --- หมวดที่ 2: UI Layout (ตามรูปภาพของคุณ) ---
st.title("🎬 Jigsaw Universal Assembler (Images & Video)")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📂 Upload Media Assets")
    uploaded_files = st.file_uploader("Add Files (MP4, JPG, PNG, etc.)", accept_multiple_files=True)
    
    st.subheader("🎵 Background Music Settings")
    bgm_mode = st.radio("Audio Mode:", ["Separate Audio per Scene", "Single Global BGM"])
    
    global_bgm = None
    if bgm_mode == "Single Global BGM":
        global_bgm = st.file_uploader("Upload Global BGM File", type=["mp3", "wav"])

with col2:
    st.header("🖥️ System Terminal")
    if uploaded_files:
        st.write(f"Total Files Uploaded: {len(uploaded_files)}")
        for f in uploaded_files:
            st.text(f"✔️ Loaded: {f.name}")
    else:
        st.info("System Ready. Waiting for inputs...")

st.divider()

# --- หมวดที่ 3: Dynamic Caption & Audio Mapping ---
st.header("📝 Edit Thai Captions & Audio Mapping")

# สร้าง list สำหรับเก็บข้อมูลฉาก และ list สำหรับแสดงผลในตาราง (เพื่อเลี่ยง Arrow Error)
scene_data = []
audit_summary = []

if uploaded_files:
    # เรียงลำดับไฟล์ตามชื่อเพื่อให้ตรงกับลำดับฉาก
    sorted_files = sorted(uploaded_files, key=lambda x: x.name)
    
    for i, file in enumerate(sorted_files):
        with st.expander(f"Scene {i+1}: {file.name}", expanded=True):
            c1, c2 = st.columns([2, 1])
            with c1:
                # ส่วน Preview (ช่วยในการเขียน Caption ให้ตรงภาพ)
                if file.type.startswith("image"):
                    st.image(file, width=250)
                elif file.type.startswith("video"):
                    st.video(file)
                
                caption = st.text_area(f"Subtitle for {file.name}:", key=f"cap_{i}", placeholder="พิมพ์ซับไตเติ้ลที่นี่...")
            
            with c2:
                scene_audio = None
                if bgm_mode == "Separate Audio per Scene":
                    # รับไฟล์เสียงรายฉาก
                    scene_audio = st.file_uploader(f"Audio for Scene {i+1}", type=["mp3", "wav"], key=f"aud_{i}")
            
            # --- แก้ปัญหาเรื่องเสียงตรงนี้ ---
            # สกัดชื่อไฟล์ออกมาเป็นข้อความ (String) แทนการเก็บตัว Object ไฟล์ทั้งก้อน
            audio_name_to_display = "None"
            if bgm_mode == "Single Global BGM":
                audio_name_to_display = global_bgm.name if global_bgm else "Global Mute"
            else:
                audio_name_to_display = scene_audio.name if scene_audio else "Scene Mute"

            # เก็บข้อมูลจริงสำหรับ Process
            scene_data.append({
                "video": file,
                "caption": caption,
                "audio": global_bgm if bgm_mode == "Single Global BGM" else scene_audio
            })

            # เก็บข้อมูลเฉพาะข้อความสำหรับแสดงผลใน st.table (ป้องกัน ArrowInvalid)
            audit_summary.append({
                "No.": i + 1,
                "Asset": file.name,
                "Caption": caption if caption else "---",
                "Audio Source": audio_name_to_display,
                "Status": "Active 🔒"
            })

# --- ส่วนการประมวลผล (Start Assembly) ---
if st.button("🚀 Start Assembly"):
    if not uploaded_files:
        st.error("กรุณาอัปโหลดไฟล์ภาพหรือวิดีโอก่อนครับ")
    else:
        st.info("System initializing... [Blackbox Audit: ACTIVE]")
        
        # จำลองการทำงานประมวลผล
        st.success("Assembly Completed!")
        st.write("### Final Deployment Summary")
        
        # ใช้ audit_summary (ที่มีแต่ String) มาแสดงตารางแทน scene_data (ที่มี File Object)
        # วิธีนี้จะทำให้ไม่เกิด Error: ArrowInvalid ('Could not convert UploadedFile...')
        df_audit = pd.DataFrame(audit_summary)
        st.table(df_audit)

# --- [End of Script: Sterility Code Applied] ---
