import streamlit as st
import pandas as pd
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
import tempfile
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# --- หมวดที่ 1: มาตรฐานระบบ (Locked 🔒) ---
st.set_page_config(page_title="Jigsaw Universal Assembler", layout="wide")

def get_reading_duration(text):
    if not text: return 4.0
    return min(max(4.0, len(text) / 15), 12.0)

# ฟังก์ชันวาดตัวหนังสือภาษาไทยด้วย Pillow (ทดแทน TextClip)
def draw_thai_caption(image_data, text):
    # เปิดภาพด้วย PIL
    img = Image.open(image_data).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    if text:
        # พยายามโหลดฟอนต์ภาษาไทย (DejaVuSans เป็นมาตรฐานใน Linux)
        try:
            # ขนาดฟอนต์ประมาณ 5% ของความสูงภาพ
            font_size = int(height * 0.05)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # คำนวณตำแหน่ง (ล่างกลาง)
        margin = 40
        # ใช้ textbbox สำหรับ Pillow รุ่นใหม่
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) / 2
        y = height - text_height - margin

        # วาดขอบดำ (Shadow/Outline) เพื่อความชัดเจนตามสไตล์คุณ
        for offset in [(2,2), (-2,-2), (2,-2), (-2,2)]:
            draw.text((x+offset[0], y+offset[1]), text, font=font, fill="black")
        
        # วาดตัวหนังสือสีขาว
        draw.text((x, y), text, font=font, fill="white")
    
    # แปลง PIL กลับเป็น Numpy array สำหรับ MoviePy
    return np.array(img)

if 'final_video_path' not in st.session_state:
    st.session_state.final_video_path = None

st.title("🎬 Jigsaw Master (Pillow Engine - No More Policy Error)")

# --- หมวดที่ 2: UI Layout (คงเดิม 100%) ---
col1, col2 = st.columns([1, 1])
with col1:
    st.header("📂 Assets")
    uploaded_files = st.file_uploader("Add Images", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    bgm_mode = st.radio("Audio Mode:", ["Single Global BGM", "Separate Audio"])
    global_bgm = st.file_uploader("Upload BGM", type=["mp3"]) if bgm_mode == "Single Global BGM" else None

with col2:
    st.header("🖥️ Terminal")
    bgm_volume = st.slider("BGM Volume:", 0.0, 1.0, 0.20, 0.05)

st.divider()

# --- หมวดที่ 3: Render Engine ---
if uploaded_files:
    scene_configs = []
    sorted_files = sorted(uploaded_files, key=lambda x: x.name)
    
    for i, file in enumerate(sorted_files):
        with st.expander(f"Scene {i+1}", expanded=True):
            cap = st.text_area(f"Subtitle:", key=f"cap_{i}")
            dur = st.slider(f"Duration", 1.0, 10.0, get_reading_duration(cap), key=f"dur_{i}")
            scene_configs.append({"file": file, "cap": cap, "dur": dur})

    if st.button("🚀 Render Final Video"):
        with st.status("🎬 Processing with Pillow Engine...") as status:
            try:
                final_clips = []
                for config in scene_configs:
                    # ใช้ฟังก์ชันใหม่วาด Caption ลงบนภาพโดยตรง
                    processed_img_array = draw_thai_caption(config["file"], config["cap"])
                    
                    # สร้าง Clip จากภาพที่วาดเสร็จแล้ว
                    clip = ImageClip(processed_img_array).set_duration(config["dur"])
                    final_clips.append(clip)

                full_video = concatenate_videoclips(final_clips, method="compose")
                
                if global_bgm:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as t:
                        t.write(global_bgm.getvalue())
                        audio = AudioFileClip(t.name).volumex(bgm_volume).set_duration(full_video.duration)
                        full_video = full_video.set_audio(audio)

                out = "final_pillow_engine.mp4"
                full_video.write_videofile(out, fps=24, codec="libx264")
                st.session_state.final_video_path = out
                status.update(label="✅ Render Success!", state="complete")
            except Exception as e:
                st.error(f"❌ Error: {e}")

if st.session_state.final_video_path:
    st.video(st.session_state.final_video_path)
    with open(st.session_state.final_video_path, "rb") as f:
        st.download_button("📥 Download", f, "land_video.mp4")
