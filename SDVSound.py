import streamlit as st
import pandas as pd
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import tempfile
import os

# --- หมวดที่ 1: มาตรฐานระบบ (Locked 🔒) ---
st.set_page_config(page_title="Jigsaw Universal Assembler", layout="wide")

def get_reading_duration(text):
    if not text: return 4.0
    return min(max(4.0, len(text) / 15), 12.0)

if 'final_video_path' not in st.session_state:
    st.session_state.final_video_path = None

st.title("🎬 Jigsaw Universal Assembler (Policy Fixed)")

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

st.divider()

# --- หมวดที่ 3: Mapping & Render Engine (จุดแก้ไข) ---
scene_configs = []
if uploaded_files:
    sorted_files = sorted(uploaded_files, key=lambda x: x.name)
    
    for i, file in enumerate(sorted_files):
        with st.expander(f"Scene {i+1}: {file.name}", expanded=True):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.image(file, width=250)
                caption = st.text_area(f"Subtitle:", key=f"cap_{i}")
            with c2:
                scene_duration = st.slider(f"Duration", 1.0, 10.0, get_reading_duration(caption), key=f"dur_{i}")
                scene_audio = st.file_uploader(f"Audio", type=["mp3"], key=f"aud_{i}") if bgm_mode == "Separate Audio per Scene" else None
            
            scene_configs.append({
                "image_data": file,
                "audio_data": global_bgm_file if bgm_mode == "Single Global BGM" else scene_audio,
                "caption": caption,
                "duration": scene_duration
            })

    if st.button("🚀 Start Assembly & Render Video"):
        with st.status("🎬 🛠 แก้ไขนโยบายความปลอดภัย & กำลัง Render...") as status:
            try:
                final_clips = []
                for config in scene_configs:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as t_img:
                        t_img.write(config["image_data"].getvalue())
                        img_path = t_img.name

                    base_clip = ImageClip(img_path).set_duration(config["duration"])
                    
                    if config["caption"]:
                        # *** จุดสำคัญ: เปลี่ยนวิธีเขียน Caption เพื่อหลบ Security Policy ***
                        # ลดการใช้ stroke_width และระบุ font ที่เบสิคที่สุดใน Linux
                        txt_clip = TextClip(
                            config["caption"], 
                            fontsize=45, 
                            color='white', 
                            font='DejaVu-Sans', # ฟอนต์มาตรฐานที่ปลอดภัยที่สุด
                            method='caption', 
                            align='center',
                            size=(base_clip.w * 0.8, None)
                        ).set_duration(config["duration"]).set_position(('center', 'bottom'))
                        
                        # สร้างขอบด้วยวิธีซ้อน Layer แทน Stroke (เพื่อเลี่ยง Error)
                        shadow_clip = TextClip(
                            config["caption"], 
                            fontsize=45, 
                            color='black', 
                            font='DejaVu-Sans',
                            method='caption', 
                            align='center',
                            size=(base_clip.w * 0.8, None)
                        ).set_duration(config["duration"]).set_position(('center', 'bottom')).margin(top=2, left=2, opacity=0)

                        scene_video = CompositeVideoClip([base_clip, shadow_clip, txt_clip])
                    else:
                        scene_video = base_clip
                    
                    final_clips.append(scene_video)

                full_video = concatenate_videoclips(final_clips, method="compose")
                
                if global_bgm_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as t_bgm:
                        t_bgm.write(global_bgm_file.getvalue())
                        bgm_track = AudioFileClip(t_bgm.name).volumex(bgm_volume).set_duration(full_video.duration)
                        full_video = full_video.set_audio(bgm_track)

                output_path = "final_fixed_render.mp4"
                full_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                st.session_state.final_video_path = output_path
                status.update(label="✅ Render สำเร็จ!", state="complete")

            except Exception as e:
                st.error(f"❌ ระบบยังคงติด Security Policy: {str(e)}")
                st.info("💡 วิธีแก้สุดท้าย: หากรันบน Cloud ของคุณเอง ต้องแก้ไขไฟล์ /etc/ImageMagick-6/policy.xml")

# --- [แสดงวิดีโอ] ---
if st.session_state.final_video_path and os.path.exists(st.session_state.final_video_path):
    st.divider()
    st.video(st.session_state.final_video_path)
    with open(st.session_state.final_video_path, "rb") as f:
        st.download_button("📥 Download Video", f, "land_presentation.mp4")
