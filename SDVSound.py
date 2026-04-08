import streamlit as st
import pandas as pd
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import tempfile
import os

# --- หมวดที่ 1: มาตรฐานระบบ (Locked 🔒) ---
st.set_page_config(page_title="Jigsaw Universal Assembler", layout="wide")

# ฟังก์ชันคำนวณเวลาอ่านธรรมชาติ
def get_reading_duration(text):
    if not text: return 3.5
    words = len(text.split()) if " " in text else len(text) / 4
    return min(max(3.5, words * 0.8), 10.0)

# ล็อค Session State สำหรับวิดีโอ
if 'final_video_path' not in st.session_state:
    st.session_state.final_video_path = None

st.title("🎬 Jigsaw Universal Assembler (Master Fixed)")

# --- หมวดที่ 2: UI Layout ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📂 Upload Media Assets")
    # ตัวแปรสำคัญ: uploaded_files ต้องประกาศให้ชัดเจน
    uploaded_files = st.file_uploader("Add Images", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    
    st.subheader("🎵 Background Music")
    bgm_mode = st.radio("Audio Mode:", ["Single Global BGM", "Separate Audio per Scene"])
    global_bgm_file = st.file_uploader("Upload BGM", type=["mp3", "wav"]) if bgm_mode == "Single Global BGM" else None

with col2:
    st.header("🖥️ System Terminal")
    bgm_volume = st.slider("ระดับเสียง BGM:", 0.0, 1.0, 0.20, 0.05)
    if uploaded_files:
        st.success(f"✅ Assets Loaded: {len(uploaded_files)} files")

st.divider()

# --- หมวดที่ 3: Mapping & Engine ---
scene_configs = []
if uploaded_files:
    st.header("📝 Edit Thai Captions")
    # เรียงลำดับภาพเพื่อความถูกต้อง
    sorted_files = sorted(uploaded_files, key=lambda x: x.name)
    
    for i, file in enumerate(sorted_files):
        with st.expander(f"Scene {i+1}: {file.name}", expanded=True):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.image(file, width=200)
                caption = st.text_area(f"Subtitle:", key=f"cap_{i}")
            with c2:
                scene_audio = st.file_uploader(f"Audio", type=["mp3"], key=f"aud_{i}") if bgm_mode == "Separate Audio per Scene" else None
            
            scene_configs.append({
                "image_data": file,
                "audio_data": global_bgm_file if bgm_mode == "Single Global BGM" else scene_audio,
                "caption": caption,
                "duration": get_reading_duration(caption)
            })

    #ปุ่ม Render (ย้ายมาไว้ข้างในเงื่อนไขที่มี uploaded_files เพื่อแก้ NameError)
    if st.button("🚀 Start Assembly & Render Video"):
        with st.status("🎬 กำลัง Render... [Fixing Security Policy]") as status:
            try:
                final_clips = []
                for config in scene_configs:
                    # สร้างไฟล์ภาพชั่วคราว
                    t_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    t_img.write(config["image_data"].getvalue())
                    img_path = t_img.name
                    t_img.close()

                    duration = config["duration"]
                    
                    # สร้าง Clip หลัก
                    base_clip = ImageClip(img_path).set_duration(duration)
                    
                    # ส่วนของ Caption (ใส่ Try-Except เพื่อไม่ให้ระบบล่มถ้า ImageMagick ติด Policy)
                    if config["caption"]:
                        try:
                            txt_clip = TextClip(
                                config["caption"], 
                                fontsize=50, color='white', font='DejaVu-Sans-Bold',
                                stroke_color='black', stroke_width=2,
                                method='caption', size=(base_clip.w * 0.8, None)
                            ).set_duration(duration).set_position(('center', 'bottom'))
                            scene_video = CompositeVideoClip([base_clip, txt_clip])
                        except:
                            st.warning("⚠️ ข้ามการใส่ Caption เนื่องจากข้อจำกัดของระบบ แต่ภาพจะยังอยู่")
                            scene_video = base_clip
                    else:
                        scene_video = base_clip
                    
                    final_clips.append(scene_video)

                # รวมไฟล์
                full_video = concatenate_videoclips(final_clips, method="compose")
                
                # ใส่เสียงและปรับ Volume
                if global_bgm_file:
                    t_bgm = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                    t_bgm.write(global_bgm_file.getvalue())
                    bgm_track = AudioFileClip(t_bgm.name).volumex(bgm_volume).set_duration(full_video.duration)
                    full_video = full_video.set_audio(bgm_track)

                output_name = "final_jigsaw_result.mp4"
                full_video.write_videofile(output_name, fps=24, codec="libx264")
                st.session_state.final_video_path = output_name
                status.update(label="✅ Render เสร็จแล้ว!", state="complete")

            except Exception as e:
                st.error(f"❌ Error ระหว่าง Render: {e}")

# แสดงผลวิดีโอรวม
if st.session_state.final_video_path and os.path.exists(st.session_state.final_video_path):
    st.divider()
    st.subheader("📺 Final Result (วิดีโอรวม)")
    st.video(st.session_state.final_video_path)
    with open(st.session_state.final_video_path, "rb") as f:
        st.download_button("📥 Download", f, "land_sale.mp4")
