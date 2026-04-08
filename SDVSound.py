import streamlit as st
import pandas as pd
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import tempfile
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap

# --- หมวดที่ 1: มาตรฐานระบบ (Locked 🔒) ---
st.set_page_config(page_title="Jigsaw Universal Assembler", layout="wide")

def get_reading_duration(text):
    if not text: return 4.0
    return min(max(4.0, len(text) / 15), 12.0)

# ฟังก์ชันวาดภาษาไทยพร้อมระบบตัดบรรทัดและปรับขนาดใหม่
def draw_thai_caption(image_data, text):
    img = Image.open(image_data).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    if text:
        font_path = "Kanit-Bold.ttf"
        
        try:
            # ปรับขนาด font ลงเหลือ 4% ของความสูงภาพ (Professional Size)
            font_size = int(height * 0.02) 
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # ระบบตัดบรรทัดอัตโนมัติ (Wrap Text) เพื่อป้องกันตัวหนังสือทะลุขอบ
        # กำหนดให้หนึ่งบรรทัดมีประมาณ 50-60 ตัวอักษร
        wrapped_text = textwrap.fill(text, width=50) 

        # คำนวณตำแหน่ง (Bottom Center)
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) / 2
        y = height - text_height - 100 # ยกขึ้นจากขอบล่าง 100px เพื่อความสวยงาม

        # วาด Outline สีดำ (บางลงเหลือ 2px เพื่อให้เข้ากับฟอนต์ที่เล็กลง)
        outline_color = "black"
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                draw.multiline_text((x+dx, y+dy), wrapped_text, font=font, fill=outline_color, align="center")
        
        # วาดตัวหนังสือสีขาว
        draw.multiline_text((x, y), wrapped_text, font=font, fill="white", align="center")
    
    return np.array(img)

if 'final_video_path' not in st.session_state:
    st.session_state.final_video_path = None

st.title("🎬 Jigsaw Master (Font Size Optimized)")

# --- หมวดที่ 2: UI Layout (Locked Style 100%) ---
col1, col2 = st.columns([1, 1])
with col1:
    st.header("📂 Assets")
    uploaded_files = st.file_uploader("Add Images", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    bgm_mode = st.radio("Audio Mode:", ["Single Global BGM", "Separate Audio"])
    global_bgm = st.file_uploader("Upload BGM", type=["mp3"]) if bgm_mode == "Single Global BGM" else None

with col2:
    st.header("🖥️ System Terminal")
    bgm_volume = st.slider("BGM Volume:", 0.0, 1.0, 0.20, 0.05)
    st.info("Status: Font Size set to 4% | Auto-Wrap: Enabled")

st.divider()

# --- หมวดที่ 3: Render Engine ---
if uploaded_files:
    scene_configs = []
    # เรียงลำดับตามชื่อไฟล์
    sorted_files = sorted(uploaded_files, key=lambda x: x.name)
    
    for i, file in enumerate(sorted_files):
        with st.expander(f"Scene {i+1}: {file.name}", expanded=True):
            cap = st.text_area(f"Subtitle:", key=f"cap_{i}")
            dur = st.slider(f"Duration", 1.0, 15.0, get_reading_duration(cap), key=f"dur_{i}")
            scene_configs.append({"file": file, "cap": cap, "dur": dur})

    if st.button("🚀 Render Final Video"):
        with st.status("🎬 Rendering with Optimized Font Size...") as status:
            try:
                final_clips = []
                for config in scene_configs:
                    processed_img = draw_thai_caption(config["file"], config["cap"])
                    clip = ImageClip(processed_img).set_duration(config["dur"])
                    final_clips.append(clip)

                full_video = concatenate_videoclips(final_clips, method="compose")
                
                if global_bgm:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as t:
                        t.write(global_bgm.getvalue())
                        audio = AudioFileClip(t.name).volumex(bgm_volume).set_duration(full_video.duration)
                        full_video = full_video.set_audio(audio)

                out_file = "jigsaw_optimized_font.mp4"
                full_video.write_videofile(out_file, fps=24, codec="libx264")
                st.session_state.final_video_path = out_file
                status.update(label="✅ Render Completed!", state="complete")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ส่วนแสดงผลภาพรวมวิดีโอ
if st.session_state.final_video_path:
    st.divider()
    st.subheader("📺 ภาพรวมวิดีโอ (Final Rendered Video)")
    st.video(st.session_state.final_video_path)
    with open(st.session_state.final_video_path, "rb") as f:
        st.download_button("📥 Download Video", f, "land_sales_optimized.mp4")
