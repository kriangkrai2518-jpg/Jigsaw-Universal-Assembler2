import streamlit as st
import pandas as pd
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import tempfile
import os

# --- หมวดที่ 1: มาตรฐานระบบ (LOCKED - Active 🔒) ---
st.set_page_config(page_title="Jigsaw Universal Assembler", layout="wide")

def get_reading_duration(text):
    """คำนวณเวลาที่เหมาะสม (ธรรมชาติ: 3-4 คำต่อวินาที)"""
    if not text: return 3.0
    words = len(text.split()) if " " in text else len(text) / 4
    return min(max(3.0, words * 0.8), 10.0)

# --- หมวดที่ 2: UI Layout ---
st.title("🎬 Jigsaw Universal Assembler (Sound Optimized)")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📂 Upload Media Assets")
    uploaded_files = st.file_uploader("Add Images", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    
    st.subheader("🎵 Background Music Settings")
    bgm_mode = st.radio("Audio Mode:", ["Separate Audio per Scene", "Single Global BGM"])
    
    global_bgm_file = None
    if bgm_mode == "Single Global BGM":
        global_bgm_file = st.file_uploader("Upload Global BGM", type=["mp3", "wav"])

with col2:
    st.header("🖥️ System Terminal")
    # เพิ่ม Slider สำหรับควบคุมความดังของเสียง Background
    bgm_volume = st.slider("ระดับเสียง Background (Volume):", 0.0, 1.0, 0.2, 0.05) 
    st.info(f"💡 Current Volume: {int(bgm_volume * 100)}% (แนะนำ 15-25%)")

st.divider()

# --- หมวดที่ 3: Mapping & Config ---
scene_configs = []
if uploaded_files:
    sorted_files = sorted(uploaded_files, key=lambda x: x.name)
    for i, file in enumerate(sorted_files):
        with st.expander(f"Scene {i+1}: {file.name}", expanded=True):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.image(file, width=200)
                caption = st.text_area(f"Subtitle:", key=f"cap_{i}")
            with c2:
                scene_audio = None
                if bgm_mode == "Separate Audio per Scene":
                    scene_audio = st.file_uploader(f"Audio", type=["mp3", "wav"], key=f"aud_{i}")
            
            scene_configs.append({
                "image_data": file,
                "audio_data": global_bgm_file if bgm_mode == "Single Global BGM" else scene_audio,
                "caption": caption,
                "auto_duration": get_reading_duration(caption)
            })

# ==========================================
# 🚀 ระบบ RENDER ENGINE (ปรับระดับเสียงให้เป็นธรรมชาติ)
# ==========================================
if st.button("🚀 Start Assembly & Render Video"):
    if not uploaded_files:
        st.error("กรุณาอัปโหลดไฟล์ภาพ")
    else:
        with st.status("🎬 Rendering... [Audio Volume Balanced]") as status:
            try:
                final_clips = []
                for config in scene_configs:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img:
                        temp_img.write(config["image_data"].getvalue())
                        img_path = temp_img.name

                    duration = config["auto_duration"]
                    audio_clip = None
                    
                    # จัดการเสียงรายฉากพร้อมปรับความดัง
                    if bgm_mode == "Separate Audio per Scene" and config["audio_data"]:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as t_aud:
                            t_aud.write(config["audio_data"].getvalue())
                            # ปรับความดังตรงนี้ (.volumex)
                            audio_clip = AudioFileClip(t_aud.name).volumex(bgm_volume)
                            duration = audio_clip.duration

                    base_clip = ImageClip(img_path).set_duration(duration)
                    
                    if config["caption"]:
                        txt_clip = TextClip(
                            config["caption"], 
                            fontsize=60, color='white', font='Arial-Bold',
                            stroke_color='black', stroke_width=2,
                            method='caption', size=(base_clip.w * 0.8, None)
                        ).set_duration(duration).set_position(('center', 'bottom'))
                        scene_video = CompositeVideoClip([base_clip, txt_clip])
                    else:
                        scene_video = base_clip

                    if audio_clip:
                        scene_video = scene_video.set_audio(audio_clip)
                    
                    final_clips.append(scene_video)

                full_video = concatenate_videoclips(final_clips, method="compose")
                
                # จัดการ Global BGM พร้อมปรับความดัง
                if bgm_mode == "Single Global BGM" and global_bgm_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as t_bgm:
                        t_bgm.write(global_bgm_file.getvalue())
                        # ปรับความดังตรงนี้ (.volumex)
                        bgm_track = AudioFileClip(t_bgm.name).volumex(bgm_volume).set_duration(full_video.duration)
                        full_video = full_video.set_audio(bgm_track)

                out_path = os.path.join(tempfile.gettempdir(), "jigsaw_balanced_render.mp4")
                full_video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac")
                st.session_state.final_render = out_path
                status.update(label="✅ Render เสร็จสมบูรณ์!", state="complete")

            except Exception as e:
                st.error(f"Render Error: {e}")

        if 'final_render' in st.session_state:
            st.video(st.session_state.final_render)
            with open(st.session_state.final_render, "rb") as f:
                st.download_button("📥 Download Video", f, "jigsaw_final.mp4")

# --- [System Status: Locked 🔒] ---
