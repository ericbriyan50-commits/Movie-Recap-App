import os
import streamlit as st
import cv2
from PIL import Image
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ImageClip
import moviepy.video.fx.all as vfx
from openai import OpenAI

st.set_page_config(page_title="DeepRecap Studio", page_icon="🎬", layout="centered")

st.title("🎬 DeepRecap Automation Studio")
st.markdown("ဗီဒီယိုတည်းဖြတ်မှုများနှင့် AI Script/Caption များကို Tab ကြီးများခွဲ၍ အသေးစိတ် ထိန်းချုပ်နိုင်သော စနစ်[span_15](start_span)[span_15](end_span)[span_16](start_span)[span_16](end_span)[span_17](start_span)[span_17](end_span)[span_18](start_span)[span_18](end_span)[span_19](start_span)[span_19](end_span)[span_20](start_span)[span_20](end_span)[span_21](start_span)[span_21](end_span)[span_22](start_span)[span_22](end_span)[span_23](start_span)[span_23](end_span)[span_24](start_span)[span_24](end_span)[span_25](start_span)[span_25](end_span)[span_26](start_span)[span_26](end_span)။")
st.markdown("---")

# Sidebar / API Settings
with st.sidebar:
    st.header("⚙️ Settings & API Keys")
    api_key = st.text_input("OpenAI / OpenRouter API Key", type="password", placeholder="sk-...")
    st.markdown("---")
    st.markdown("**Account Plan:** Free (Own Key)")
    st.markdown("ဗီဒီယို တစ်ခါထုတ်လျှင် အများဆုံး ၁၀ မိနစ်[span_27](start_span)[span_27](end_span)")

# Main Input Section
uploaded_video = st.file_uploader("📥 Video ဖိုင် ရွေးပါ (MP4, MOV, MKV)", type=["mp4", "mov", "mkv", "avi"])
movie_prompt = st.text_input("💡 ဇာတ်ကားအမည် သို့မဟုတ် ဇာတ်လမ်းအကြောင်းအရာ ရေးပါ", placeholder="ဥပမာ- ရှင်သန်ရေးတောတွင်း ဇာတ်ကားအကြောင်း")

# DeepRecap Style Tabs
tab_video, tab_audio, tab_sub, tab_extra = st.tabs(["ဗီဒီယို", "အသံ", "စာတန်း", "အပို"])

with tab_video:
    st.markdown("### 🎞️ ဗီဒီယို ဆက်တင်များ")
    ratio_choice = st.radio("မျက်နှာပြင် အချိုး (Aspect Ratio)", ["9:16", "1:1", "4:5", "16:9"], horizontal=True)
    bg_mode = st.radio("နောက်ခံ ပုံစံ", ["Blur နောက်ခံ", "ဖြတ်ဖြတ် (Crop)"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        zoom_val = st.slider("🔍 Zoom (%)", min_value=100, max_value=150, value=110)
        enable_mirror = st.checkbox("Mirror (ဘယ်/ညာ လှန်ရန်)")
    with col2:
        pan_x = st.slider("ဘယ် / ညာ ရွှေ့", min_value=-50, max_value=50, value=0)
        pan_y = st.slider("အပေါ် / အောက် ရွှေ့", min_value=-50, max_value=50, value=0)

with tab_audio:
    st.markdown("### 🗣️ အသံ ဆက်တင်များ")
    voice_lang = st.selectbox("အသံ ဘာသာစကား", ["မြန်မာ", "English", "ไทย"])
    audio_speed = st.slider("အမြန်နှုန်း (%)", min_value=50, max_value=150, value=100)
    pitch_val = st.slider("အသံနှိမ့်မြှင့် (Hz)", min_value=-10, max_value=10, value=0)

with tab_sub:
    st.markdown("### 📝 စာတန်းထိုး (Subtitles & Caption)")
    enable_sub = st.checkbox("စာတန်းထိုး (Caption) ထည့်မည်", value=True)
    font_color = st.color_picker("စာလုံး အရောင်", "#FFFF00")
    outline_color = st.color_picker("Outline အရောင်", "#000000")
    font_size = st.slider("စာလုံး အရွယ်အစား", min_value=10, max_value=30, value=14)

with tab_extra:
    st.markdown("### 🎨 ရေစာ နှင့် Logo (Watermark & Logo)")
    enable_watermark = st.checkbox("Watermark စာသားထည့်မည်", value=False)
    watermark_text = st.text_input("Watermark စာသား", "CS Recap")
    
    uploaded_logo = st.file_uploader("🖼️ Logo ပုံ တင်ရန်", type=["png", "jpg", "jpeg"])
    logo_size = st.slider("Logo အရွယ်အစား", min_value=40, max_value=200, value=96)
    
    st.markdown("---")
    enable_ai_meta = st.checkbox("Caption + Hashtag AI ရေးပေးရန်", value=True)

st.markdown("---")
if st.button("🚀 စတင်ထုတ်ယူမည် (Render Video)"):
    if api_key and uploaded_video is not None and movie_prompt.strip() != "":
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🤖 AI ဖြင့် Script နှင့် Caption များကို ဖန်တီးနေပါပြီ...")
            client = OpenAI(api_key=api_key)
            
            # Script Generation
            script_res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional movie recap scriptwriter. Write engaging movie recap scripts in Burmese language."},
                    {"role": "user", "content": f"Write an engaging movie recap script in Burmese for: {movie_prompt}. Around 100 words."}
                ]
            )
            recap_text = script_res.choices[0].message.content
            
            # Caption & Hashtags
            meta_res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate a TikTok catchy Burmese hook caption and popular hashtags."},
                    {"role": "user", "content": f"Create caption and hashtags for: {movie_prompt}"}
                ]
            )
            meta_text = meta_res.choices[0].message.content
            
            progress_bar.progress(30)
            
            st.markdown("### 📱 Social Media Ready Kit")
            st.info(f"📝 **AI Script:**\n{recap_text}")
            st.code(meta_text, language="text")
            
            status_text.text("📥 ဗီဒီယိုဖိုင်ကို ပြင်ဆင်နေပါပြီ...")
            input_path = "temp_input.mp4"
            with open(input_path, "wb") as f:
                f.write(uploaded_video.read())
            progress_bar.progress(50)
            
            clip = VideoFileClip(input_path)
            if enable_mirror:
                clip = vfx.mirror_x(clip)
                
            # Resolution handling based on ratio
            if ratio_choice == "9:16":
                target_w, target_h = 1080, 1920
            elif ratio_choice == "1:1":
                target_w, target_h = 1080, 1080
            elif ratio_choice == "4:5":
                target_w, target_h = 1080, 1350
            else:
                target_w, target_h = 1920, 1080
                
            if bg_mode == "Blur နောက်ခံ":
                bg_clip = clip.resize(height=target_h).fx(vfx.gaussian_blur, sigma=15)
                bg_clip = bg_clip.set_duration(clip.duration)
                main_clip = clip.resize(width=target_w).set_position(("center", "center"))
                video_combined = CompositeVideoClip([bg_clip, main_clip], size=(target_w, target_h))
            else:
                video_combined = clip.resize(height=target_h)
                
            video_combined = video_combined.set_duration(clip.duration)
            progress_bar.progress(70)
            
            status_text.text("🗣️ အသံဖန်တီးနေပါပြီ (TTS)...")
            tts = gTTS(text=recap_text, lang='my', slow=False)
            audio_path = "temp_voice.mp3"
            tts.save(audio_path)
            
            voice_clip = AudioFileClip(audio_path)
            video_combined = video_combined.set_audio(voice_clip)
            video_combined.set_duration(voice_clip.duration)
            progress_bar.progress(85)
            
            if uploaded_logo is not None:
                logo_path = "temp_logo.png"
                with open(logo_path, "wb") as lf:
                    lf.write(uploaded_logo.read())
                logo = ImageClip(logo_path).resize(height=logo_size).set_duration(video_combined.duration)
                logo = logo.set_position(("right", "top")).margin(top=40, right=40, opacity=0)
                video_combined = CompositeVideoClip([video_combined, logo])
                
            progress_bar.progress(95)
            status_text.text("⚙️ Video Render လုပ်နေပါပြီ...")
            output_path = "recap_output.mp4"
            video_combined.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                preset='medium'
            )
            progress_bar.progress(100)
            status_text.text("✨ ပြီးဆုံးပါပြီ!")
            
            st.success("🎉 ဗီဒီယို အဆင်သင့်ဖြစ်ပါပြီ!")
            st.video(output_path)
            
            with open(output_path, "rb") as file:
                st.download_button(
                    label="📥 ရလဒ်ဗီဒီယိုကို Download ရယူရန်",
                    data=file,
                    file_name="deeprecap_result.mp4",
                    mime="video/mp4"
                )
                
            for f in [input_path, audio_path]:
                if os.path.exists(f):
                    os.remove(f)
                    
        except Exception as e:
            st.error(f"❌ အမှားအယွင်း ဖြစ်ပေါ်သည်: {e}")
    else:
        st.warning("⚠️ ကျေးဇူးပြု၍ API Key ထည့်ပါ၊ ဗီဒီယိုတင်ပါ နှင့် အကြောင်းအရာ ရေးပါ။")
    
