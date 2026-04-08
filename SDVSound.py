import streamlit as st
import pandas as pd
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import tempfile
import os

# --- หมวดที่ 1: Active Lock (Configuration) ---
st.set_page_config(page_title="Jigsaw Universal Assembler", layout="wide")

def get_reading_duration(text):
    """คำนวณเวลาอ่านธรรมชาติ (3-4 คำต่อวินาที)"""
    if not text: return 3.5
    words = len(text.split()) if " " in text else len(text) / 4
    return min(max(3.5, words * 0.8), 10.0)

# เตรียม Session State สำหรับเก็บไฟล์วิดีโอที่ Render เสร็จ
if 'final_video_path' not in st.session_state:
    st.session_state.final_video_path = None

# --- หมวดที่ 2: UI Layout ---
st.title("🎬 Jigsaw Universal Assembler (Nature Majesty Edition)")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📂 Upload Media Assets")
    uploaded_files = st.file_uploader("Add Images", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    
    st.subheader("🎵 Background Music Settings")
    bgm_mode = st.radio("Audio Mode:", ["Separate Audio per Scene", "Single Global BGM"])
    
    global_bgm_file = None
    if bgm_mode == "Single Global BGM":
        global_bgm_file = st.file_uploader("Upload Nature Majesty Sound", type=["mp3", "wav"])

with col2:
    st.header("🖥️ System Terminal")
    bgm_volume = st.slider("ระดับเสียง Background (แนะนำ 0.15 - 0.25):", 0.0, 1.0, 0.20, 0.05)
    st.info(f"💡 Status: [Blackbox Audit: Active 🔒]")

st.divider()

# --- หมวดที่ 3: Mapping & Edit ---
scene_configs = []
if uploaded_files:
    # เรียงลำดับไฟล์ตามชื่อเพื่อความเป็นระเบียบ (1, 2, 3...)
    sorted_files = sorted(uploaded_files, key=lambda x: x.name)
    st.header("📝 Edit Thai Captions & Mapping")
    
    for i, file in enumerate(sorted_files):
        with st.expander(f"Scene {i+1}: {file.name}", expanded=True):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.image(file, width=250)
                caption = st.text_area(f"Subtitle:", key=f"cap_{i}", placeholder="ใส่คำบรรยาย...")
            with c2:
                scene_audio = None
                if bgm_mode == "Separate Audio per Scene":
                    scene_audio = st.file_uploader(f"Audio Scene {i+1}", type=["mp3", "wav"], key=f"aud_{i}")
            
            scene_configs.append({
                "image_data": file,
                "audio_data": global_bgm_file if bgm_mode == "Single Global BGM" else scene_audio,
                "caption": caption,
                "duration": get_reading_duration(caption)
            })

# ==========================================
# 🚀 ระบบ RENDER ENGINE (จุดที่แก้ไขให้ภาพรวมโชว์)
# ==========================================
if st.button("🚀 Start Assembly & Show Final Video"):
    if not uploaded_files:
        st.error("กรุณาอัปโหลดไฟล์ภาพก่อนครับ")
    else:
        with st.status("🎬 กำลังประมวลผลวิดีโอรวม...", expanded=True) as status:
            try:
                final_clips = []
                for config in scene_configs:
                    # 1. เขียนไฟล์ภาพชั่วคราว
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as t_img:
                        t_img.write(config["image_data"].getvalue())
                        img_path = t_img.name

                    duration = config["duration"]
                    audio_clip = None

                    # 2. จัดการเสียงและระดับความดัง (0.2)
                    if bgm_mode == "Separate Audio per Scene" and config["audio_data"]:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as t_aud:
                            t_aud.write(config["audio_data"].getvalue())
                            audio_clip = AudioFileClip(t_aud.name).volumex(bgm_volume)
                            duration = audio_clip.duration

                    # 3. สร้าง Base Clip และใส่คำบรรยาย
                    base_clip = ImageClip(img_path).set_duration(duration)
                    
                    if config["caption"]:
                        txt_clip = TextClip(
                            config["caption"], 
                            fontsize=55, color='white', font='Arial-Bold',
                            stroke_color='black', stroke_width=2,
                            method='caption', size=(base_clip.w * 0.85, None)
                        ).set_duration(duration).set_position(('center', 'bottom'))
                        scene_video = CompositeVideoClip([base_clip, txt_clip])
                    else:
                        scene_video = base_clip

                    if audio_clip:
                        scene_video = scene_video.set_audio(audio_clip)
                    
                    final_clips.append(scene_video)

                # 4. รวมคลิปทั้งหมด
                full_video = concatenate_videoclips(final_clips, method="compose")
                
                # 5. ใส่ Global BGM (ถ้ามี) พร้อมปรับความดังเบาๆ
                if bgm_mode == "Single Global BGM" and global_bgm_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as t_bgm:
                        t_bgm.write(global_bgm_file.getvalue())
                        bgm_track = AudioFileClip(t_bgm.name).volumex(bgm_volume).set_duration(full_video.duration)
                        full_video = full_video.set_audio(bgm_track)

                # 6. บันทึกไฟล์ลง Disk (ใช้ชื่อคงที่เพื่อให้เรียกโชว์ได้)
                out_path = "final_output_render.mp4"
                full_video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac")
                
                # บันทึกพาธลง Session State เพื่อให้วิดีโอไม่หาย
                st.session_state.final_video_path = out_path
                status.update(label="✅ Render เสร็จสมบูรณ์!", state="complete")

            except Exception as e:
                st.error(f"❌ Render Error: {str(e)}")

# --- [ส่วนแสดงภาพรวมวิดีโอ - FINAL RENDERED VIDEO] ---
if st.session_state.final_video_path and os.path.exists(st.session_state.final_video_path):
    st.divider()
    st.subheader("📺 Final Rendered Video (ภาพรวม)")
    st.video(st.session_state.final_video_path)
    
    with open(st.session_state.final_video_path, "rb") as f:
        st.download_button(
            label="📥 Download Result Video",
            data=f,
            file_name="jigsaw_final_presentation.mp4",
            mime="video/mp4"
        )
