import os
import streamlit as st
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ImageClip
import moviepy.video.fx.all as vfx

st.set_page_config(page_title="AI Movie Recap Tool", page_icon="🎬", layout="centered")

st.title("🎬 AI Movie Recap Automation Tool")
st.markdown("ဗီဒီယိုဖိုင်ထည့်သွင်းရုံဖြင့် **9:16 Ratio၊ Background Blur၊ Flip၊ Logo နှင့် မြန်မာစကားပြောအသံ (TTS)** တို့ကို အလိုအလျောက် ဖန်တီးပေးမည့် စနစ်။")
st.markdown("---")

uploaded_video = st.file_uploader("📥 မူရင်း ရုပ်ရှင်ဗီဒီယိုဖိုင်ကို တင်ပါ (mp4, mov)", type=["mp4", "mov", "avi"])
recap_text = st.text_area("✍️ ပြောပြမည့် မြန်မာဇာတ်လမ်းအကျဉ်း (Script) ကို ဤနေရာတွင် ရေးပါ", height=150, placeholder="ဥပမာ- ဒီဇာတ်ကားလေးကတော့...")
uploaded_logo = st.file_uploader("🖼️ (ရွေးချယ်ရန်) Logo / Watermark ပုံ တင်ရန်", type=["png", "jpg", "jpeg"])

col1, col2 = st.columns(2)
with col1:
    enable_flip = st.checkbox("🔄 ဗီဒီယို ဘယ်ညာလှန်ရန် (Flip Video)")
with col2:
    target_fps = st.slider("🎞️ FPS (Frame Rate)", min_value=20, max_value=30, value=24)

if st.button("🚀 ဗီဒီယို စတင်ဖန်တီးမည် (Auto Render)"):
    if uploaded_video is not None and recap_text.strip() != "":
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("📥 ဗီဒီယိုဖိုင်ကို လက်ခံရယူနေပါပြီ...")
            input_path = "temp_input.mp4"
            with open(input_path, "wb") as f:
                f.write(uploaded_video.read())
            progress_bar.progress(20)
            
            clip = VideoFileClip(input_path)
            if enable_flip:
                clip = vfx.mirror_x(clip)
            
            status_text.text("🎨 9:16 Ratio နှင့် Blur Background ဖန်တီးနေပါပြီ...")
            target_w, target_h = 1080, 1920
            
            bg_clip = clip.resize(height=target_h).fx(vfx.gaussian_blur, sigma=20)
            bg_clip = bg_clip.set_duration(clip.duration)
            
            main_clip = clip.resize(width=target_w).set_position(("center", "center"))
            video_combined = CompositeVideoClip([bg_clip, main_clip], size=(target_w, target_h))
            video_combined = video_combined.set_duration(clip.duration)
            progress_bar.progress(40)
            
            status_text.text("🗣️ မြန်မာစကားပြောအသံ (TTS) ဖန်တီးနေပါပြီ...")
            tts = gTTS(text=recap_text, lang='my', slow=False)
            audio_path = "temp_voice.mp3"
            tts.save(audio_path)
            
            voice_clip = AudioFileClip(audio_path)
            video_combined = video_combined.set_audio(voice_clip)
            video_combined.set_duration(voice_clip.duration)
            progress_bar.progress(70)
            
            if uploaded_logo is not None:
                status_text.text("🖼️ Logo ထည့်သွင်းနေပါပြီ...")
                logo_path = "temp_logo.png"
                with open(logo_path, "wb") as lf:
                    lf.write(uploaded_logo.read())
                
                logo = ImageClip(logo_path).resize(height=120).set_duration(video_combined.duration)
                logo = logo.set_position(("right", "top")).margin(top=40, right=40, opacity=0)
                video_combined = CompositeVideoClip([video_combined, logo])
            progress_bar.progress(85)
            
            status_text.text("⚙️ Auto Rendering လုပ်နေပါပြီ... ခဏစောင့်ပေးပါ။")
            output_path = "recap_output.mp4"
            video_combined.write_videofile(
                output_path, 
                fps=target_fps, 
                codec='libx264', 
                audio_codec='aac',
                preset='medium'
            )
            progress_bar.progress(100)
            status_text.text("✨ အောင်မြင်ပါပြီ!")
            
            st.success("🎉 သင့်ရဲ့ Movie Recap ဗီဒီယို အဆင်သင့်ဖြစ်ပါပြီ!")
            st.video(output_path)
            
            with open(output_path, "rb") as file:
                st.download_button(
                    label="📥 ရလဒ်ဗီဒီယိုကို Download ရယူရန်",
                    data=file,
                    file_name="movie_recap_result.mp4",
                    mime="video/mp4"
                )
                
            for f in [input_path, audio_path, "temp_logo.png"]:
                if os.path.exists(f):
                    os.remove(f)
                    
        except Exception as e:
            st.error(f"❌ အမှားအယွင်း ဖြစ်ပေါ်သွားသည်: {e}")
    else:
        st.warning("⚠️ ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင်တင်ပြီး ဇာတ်လမ်းအကျဉ်း (Script) ထည့်သွင်းပါ။")
              
