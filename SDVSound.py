import streamlit as st
import pandas as pd
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import tempfile
import os

# --- หมวดที่ 1: Active Lock (Configuration) ---
st.set_page_config(page_title="Jigsaw Universal Assembler", layout="wide")

# --- หมวดที่ 2: UI Layout (ตามรูปภาพล่าสุดของคุณ) ---
st.title("🎬 Jigsaw Universal Assembler (Images & Video)")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📂 Upload Media Assets")
    uploaded_files = st.file_uploader("Add Files (JPG, PNG)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    
    st.subheader("🎵 Background Music Settings")
    bgm_mode = st.radio("Audio Mode:", ["Separate Audio per Scene", "Single Global BGM"])
    
    global_bgm_file = None
    if bgm_mode == "Single Global BGM":
        global_bgm_file = st.file_uploader("Upload Global BGM File", type=["mp3", "wav"])

with col2:
    st.header("🖥️ System Terminal")
    if uploaded_files:
        st.write(f"✅ Loaded Assets: {len(uploaded_files)} files")
        for f in uploaded_files:
            st.text(f"✔️ {f.name}")
    else:
        st.info("System Ready. Waiting for inputs...")

st.divider()

# --- หมวดที่ 3: Dynamic Caption & Audio Mapping ---
st.header("📝 Edit Thai Captions & Audio Mapping")

scene_configs = []

if uploaded_files:
    sorted_files = sorted(uploaded_files, key=lambda x: x.name)
    
    for i, file in enumerate(sorted_files):
        with st.expander(f"Scene {i+1}: {file.name}", expanded=True):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.image(file, width=250)
                caption = st.text_area(f"Subtitle for {file.name}:", key=f"cap_{i}")
            
            with c2:
                scene_audio = None
                if bgm_mode == "Separate Audio per Scene":
                    scene_audio = st.file_uploader(f"Audio for Scene {i+1}", type=["mp3", "wav"], key=f"aud_{i}")
            
            # เก็บค่า Config สำหรับการ Render
            scene_configs.append({
                "image_data": file,
                "audio_data": global_bgm_file if bgm_mode == "Single Global BGM" else scene_audio,
                "caption": caption
            })

# ==========================================
# 🚀 ระบบ RENDER VIDEO รวม (ส่วนที่ต่อเติมใหม่)
# ==========================================
if st.button("🚀 Start Assembly & Render Video"):
    if not uploaded_files:
        st.error("กรุณาอัปโหลดไฟล์ภาพก่อนทำการ Render")
    else:
        with st.status("🎬 กำลังประมวลผลวิดีโอรวม [Blackbox Audit: ACTIVE]...", expanded=True) as status:
            try:
                clips = []
                
                for config in scene_configs:
                    # 1. จัดการไฟล์ภาพชั่วคราว
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img:
                        temp_img.write(config["image_data"].getvalue())
                        temp_img_path = temp_img.name

                    # 2. จัดการไฟล์เสียงชั่วคราว
                    if config["audio_data"]:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_aud:
                            temp_aud.write(config["audio_data"].getvalue())
                            temp_aud_path = temp_aud.name
                        
                        # สร้าง Clip ภาพที่มีความยาวเท่ากับเสียง
                        audio_clip = AudioFileClip(temp_aud_path)
                        img_clip = ImageClip(temp_img_path).set_duration(audio_clip.duration)
                        img_clip = img_clip.set_audio(audio_clip)
                    else:
                        # ถ้าไม่มีเสียง ให้ยาว 3 วินาทีเป็นค่าเริ่มต้น
                        img_clip = ImageClip(temp_img_path).set_duration(3)
                    
                    clips.append(img_clip)
                    st.write(f"✔️ รวมฉาก {config['image_data'].name} สำเร็จ")

                # 3. รวมคลิปทั้งหมดเข้าด้วยกัน
                final_video = concatenate_videoclips(clips, method="compose")
                
                # 4. บันทึกไฟล์วิดีโอรวม
                output_path = os.path.join(tempfile.gettempdir(), "jigsaw_final_render.mp4")
                final_video.write_videofile(output_path, fps=24, codec="libx264")
                
                st.session_state.final_video_path = output_path
                status.update(label="✅ Render วิดีโอเสร็จสมบูรณ์!", state="complete", expanded=False)

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการ Render: {str(e)}")

        # --- [DISPLAY FINAL VIDEO] ---
        if 'final_video_path' in st.session_state:
            st.divider()
            st.subheader("📺 Final Rendered Video")
            st.video(st.session_state.final_video_path)
            
            # ปุ่ม Download ไฟล์ผลลัพธ์
            with open(st.session_state.final_video_path, "rb") as file:
                st.download_button(
                    label="📥 Download Result Video",
                    data=file,
                    file_name="jigsaw_universal_final.mp4",
                    mime="video/mp4"
                )

# --- [System Status: Locked] ---
# Sterility Code: sterility
