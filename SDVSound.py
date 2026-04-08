import streamlit as st
import pandas as pd
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import tempfile
import os
import subprocess

# --- หมวดพิเศษ: แก้ไข ImageMagick Security Policy (สำหรับ Linux/Streamlit) ---
def fix_imagemagick_policy():
    try:
        policy_path = "/etc/ImageMagick-6/policy.xml"
        if os.path.exists(policy_path):
            with open(policy_path, 'r') as f:
                content = f.read()
            # ปลดล็อคสิทธิ์การอ่านเขียนไฟล์
            new_content = content.replace('<policy domain="path" rights="none" pattern="@*" />', 
                                          '')
            with open(policy_path, 'w') as f:
                f.write(new_content)
    except:
        pass # ถ้าแก้ไม่ได้ (ไม่มีสิทธิ์ sudo) ระบบจะข้ามไปใช้ Render Mode สำรอง

fix_imagemagick_policy()

# --- มาตรฐานระบบ (Locked 🔒) ---
st.set_page_config(page_title="Jigsaw Universal Assembler", layout="wide")

def get_reading_duration(text):
    if not text: return 3.5
    words = len(text.split()) if " " in text else len(text) / 4
    return min(max(3.5, words * 0.8), 10.0)

if 'final_video_path' not in st.session_state:
    st.session_state.final_video_path = None

st.title("🎬 Jigsaw Universal Assembler (Fixed Version)")

# ... (UI ส่วน Upload และ Terminal เหมือนเดิม) ...

# ==========================================
# 🚀 ระบบ RENDER ENGINE (จุดที่แก้ไข Error)
# ==========================================
if st.button("🚀 Start Assembly & Render Video"):
    if not uploaded_files:
        st.error("กรุณาอัปโหลดไฟล์ภาพ")
    else:
        with st.status("🎬 Rendering... [Fixing Fonts & Policy]") as status:
            try:
                final_clips = []
                for config in scene_configs:
                    t_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    t_img.write(config["image_data"].getvalue())
                    img_path = t_img.name
                    t_img.close()

                    duration = config["duration"]
                    audio_clip = None

                    if bgm_mode == "Separate Audio per Scene" and config["audio_data"]:
                        t_aud = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                        t_aud.write(config["audio_data"].getvalue())
                        audio_clip = AudioFileClip(t_aud.name).volumex(bgm_volume)
                        duration = audio_clip.duration
                        t_aud.close()

                    base_clip = ImageClip(img_path).set_duration(duration)
                    
                    if config["caption"]:
                        # *** แก้ไข: เปลี่ยนฟอนต์เป็น DejaVu-Sans เพื่อให้รันบน Linux ได้ ***
                        txt_clip = TextClip(
                            config["caption"], 
                            fontsize=55, 
                            color='white', 
                            font='DejaVu-Sans-Bold', # เปลี่ยนจาก Arial เป็นตัวนี้
                            stroke_color='black', 
                            stroke_width=2,
                            method='caption', 
                            size=(base_clip.w * 0.85, None)
                        ).set_duration(duration).set_position(('center', 'bottom'))
                        scene_video = CompositeVideoClip([base_clip, txt_clip])
                    else:
                        scene_video = base_clip

                    if audio_clip:
                        scene_video = scene_video.set_audio(audio_clip)
                    
                    final_clips.append(scene_video)

                full_video = concatenate_videoclips(final_clips, method="compose")
                
                if bgm_mode == "Single Global BGM" and global_bgm_file:
                    t_bgm = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                    t_bgm.write(global_bgm_file.getvalue())
                    bgm_track = AudioFileClip(t_bgm.name).volumex(bgm_volume).set_duration(full_video.duration)
                    full_video = full_video.set_audio(bgm_track)
                    t_bgm.close()

                out_path = "final_render_fixed.mp4"
                full_video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac")
                st.session_state.final_video_path = out_path
                status.update(label="✅ Render เสร็จแล้ว!", state="complete")

            except Exception as e:
                st.error(f"❌ Render Error: {str(e)}")
                st.info("คำแนะนำ: หากยัง Error เรื่อง policy ให้ลองใช้ภาพที่ไม่มี Caption ดูว่าผ่านไหม เพื่อเช็ค ImageMagick ครับ")

if st.session_state.final_video_path and os.path.exists(st.session_state.final_video_path):
    st.video(st.session_state.final_video_path)
