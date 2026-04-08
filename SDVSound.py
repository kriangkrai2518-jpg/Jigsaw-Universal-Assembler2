import streamlit as st
import pandas as pd
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import tempfile
import os

# --- หมวดที่ 1: การตั้งค่าระบบ & Bypass Security (Active 🔒) ---
st.set_page_config(page_title="Jigsaw Universal Assembler", layout="wide")

# ฟังก์ชันคำนวณเวลาอ่านตามธรรมชาติ
def get_reading_duration(text):
    if not text: return 4.0
    # ภาษาไทยเฉลี่ย 4 พยางค์/วินาที
    char_count = len(text)
    return min(max(4.0, char_count / 15), 12.0)

if 'final_video_path' not in st.session_state:
    st.session_state.final_video_path = None

st.title("🎬 Jigsaw Universal Assembler (Captions Restored)")

# --- หมวดที่ 2: UI Layout ---
col1, col2 = st.columns([1, 1])
with col1:
    st.header("📂 Upload Media Assets")
    uploaded_files = st.file_uploader("Add Files (JPG, PNG)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    
    st.subheader("🎵 Background Music Settings")
    bgm_mode = st.radio("Audio Mode:", ["Single Global BGM", "Separate Audio per Scene"])
    global_bgm_file = st.file_uploader("Upload Global BGM", type=["mp3"]) if bgm_mode == "Single Global BGM" else None

with col2:
    st.header("🖥️ System Terminal")
    bgm_volume = st.slider("BGM Volume:", 0.0, 1.0, 0.20, 0.05)
    if uploaded_files:
        st.success(f"✅ Assets Loaded: {len(uploaded_files)} files")

st.divider()

# --- หมวดที่ 3: Mapping & Render Engine ---
scene_configs = []
if uploaded_files:
    st.header("📝 Edit Thai Captions & Mapping")
    sorted_files = sorted(uploaded_files, key=lambda x: x.name)
    
    for i, file in enumerate(sorted_files):
        with st.expander(f"Scene {i+1}: {file.name}", expanded=True):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.image(file, width=250)
                caption = st.text_area(f"Subtitle for {file.name}:", key=f"cap_{i}")
            with c2:
                scene_duration = st.slider(f"Scene Duration", 1.0, 10.0, get_reading_duration(caption), key=f"dur_{i}")
                scene_audio = st.file_uploader(f"Audio", type=["mp3"], key=f"aud_{i}") if bgm_mode == "Separate Audio per Scene" else None
            
            scene_configs.append({
                "image_data": file,
                "audio_data": global_bgm_file if bgm_mode == "Single Global BGM" else scene_audio,
                "caption": caption,
                "duration": scene_duration
            })

    if st.button("🚀 Start Assembly & Render Video"):
        with st.status("🎬 กำลังกู้คืนคำบรรยายและ Render... [Blackbox Audit: ACTIVE]") as status:
            try:
                final_clips = []
                for config in scene_configs:
                    # สร้างไฟล์ภาพชั่วคราว
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as t_img:
                        t_img.write(config["image_data"].getvalue())
                        img_path = t_img.name

                    # สร้าง Clip หลัก
                    base_clip = ImageClip(img_path).set_duration(config["duration"])
                    
                    # --- [RESTORATION LOGIC: แก้ปัญหาคำบรรยายหาย] ---
                    if config["caption"]:
                        # ใช้ฟอนต์พื้นฐานของ Linux Server (DejaVu-Sans-Bold)
                        # และลดความซับซ้อนของคำสั่งเพื่อให้ผ่าน Security Policy
                        txt_clip = TextClip(
                            config["caption"], 
                            fontsize=50, 
                            color='white', 
                            font='DejaVu-Sans-Bold', 
                            stroke_color='black', 
                            stroke_width=1.5,
                            method='caption', 
                            size=(base_clip.w * 0.9, None)
                        ).set_duration(config["duration"]).set_position(('center', 'bottom'))
                        
                        scene_video = CompositeVideoClip([base_clip, txt_clip])
                    else:
                        scene_video = base_clip
                    
                    final_clips.append(scene_video)

                # รวมไฟล์วิดีโอ
                full_video = concatenate_videoclips(final_clips, method="compose")
                
                # ใส่เสียง Background (Nature Majesty Style)
                if global_bgm_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as t_bgm:
                        t_bgm.write(global_bgm_file.getvalue())
                        bgm_track = AudioFileClip(t_bgm.name).volumex(bgm_volume).set_duration(full_video.duration)
                        full_video = full_video.set_audio(bgm_track)

                output_path = "jigsaw_final_fixed.mp4"
                full_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                st.session_state.final_video_path = output_path
                status.update(label="✅ Video Assembly Completed", state="complete")

            except Exception as e:
                st.error(f"❌ Render Error: {str(e)}")

# --- [FINAL DEPLOYMENT SUMMARY] ---
if st.session_state.final_video_path and os.path.exists(st.session_state.final_video_path):
    st.divider()
    st.subheader("📺 Final Rendered Video")
    st.video(st.session_state.final_video_path)
    
    with open(st.session_state.final_video_path, "rb") as f:
        st.download_button("📥 Download Result Video", f, "land_presentation.mp4")
