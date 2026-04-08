import streamlit as st
import os

# --- หมวดที่ 1: Active Lock (Configuration) ---
st.set_page_config(page_title="Jigsaw Universal Assembler", layout="wide")

# บันทึกข้อควรระวังเรื่องสี V4 และ Mandatory Checklist
CHECKLIST = ["Leading Character Sweep", "Version 4 Color Validator", "Structural Clone Match"]

def init_system():
    if 'processed' not in st.session_state:
        st.session_state.processed = False

# --- หมวดที่ 2: UI Layout (ตามรูปภาพของคุณ) ---
st.title("🎬 Jigsaw Universal Assembler (Images & Video)")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📂 Upload Media Assets")
    uploaded_files = st.file_uploader("Add Files (MP4, JPG, PNG, etc.)", accept_multiple_files=True)
    
    # ส่วนเพิ่มเรื่องเสียง (Audio Selector) ที่คุณต้องการ
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

st.divider()

# --- หมวดที่ 3: Dynamic Caption & Audio Mapping ---
st.header("📝 Edit Thai Captions & Audio Mapping")

scene_data = []

if uploaded_files:
    # เรียงลำดับไฟล์ตามชื่อเพื่อให้ตรงกับลำดับฉาก (เหมือนใน Folder Downloads ของคุณ)
    sorted_files = sorted(uploaded_files, key=lambda x: x.name)
    
    for i, file in enumerate(sorted_files):
        with st.expander(f"Scene {i+1}: {file.name}", expanded=True):
            c1, c2 = st.columns([2, 1])
            with c1:
                caption = st.text_area(f"Subtitle for {file.name}:", key=f"cap_{i}")
            with c2:
                # ถ้าเป็นโหมดแยกเพลง ให้โชว์ที่อัปโหลดเพลงรายฉาก
                scene_audio = None
                if bgm_mode == "Separate Audio per Scene":
                    scene_audio = st.file_uploader(f"Audio for Scene {i+1}", type=["mp3", "wav"], key=f"aud_{i}")
            
            scene_data.append({
                "video": file.name,
                "caption": caption,
                "audio": global_bgm if bgm_mode == "Single Global BGM" else scene_audio
            })

# --- ส่วนการประมวลผล (Start Assembly) ---
if st.button("🚀 Start Assembly"):
    st.info("System initializing... [Blackbox Audit: ACTIVE]")
    
    # จำลองการทำงานของ Assembler
    results = []
    for data in scene_data:
        # ดึงชื่อไฟล์เสียงมาแสดงผล (Audit)
        audio_name = data['audio'].name if data['audio'] else "Mute"
        results.append(f"Scene: {data['video']} | Audio: {audio_name} | Text: {data['caption'][:20]}...")
    
    st.success("Assembly Completed!")
    st.write("### Final Deployment Summary")
    st.table(scene_data) # แสดงตารางสรุปเหมือนในระบบ Audit
