import os, requests, time, random, json, textwrap
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip

# --- SECRETS FROM GITHUB ---
INSTA_ID = os.getenv("INSTA_ID")
TOKEN = os.getenv("INSTA_TOKEN")

def log(m): print(m, flush=True)

TOPICS = [
    "Chuha aur Bandar ki dosti - Bandar ne chuhe ka lunch kha liya, phir kya hua?",
    "School me jhooth - Chuha exam me fail ho gaya par sabko topper bola",
    "Madad ka matlab - Bandar musibat me tha, chuhe ne help ki par badle me dhokha mila"
]

def generate_story():
    return random.choice(TOPICS)

def make_voice(text, file="voice.mp3"):
    tts = gTTS(text=text, lang='hi', slow=False)
    tts.save(file)
    return file

def make_cartoon_image(text, file="frame.jpg"):
    # Simple cartoon style frame with text
    img = Image.new('RGB', (1080, 1920), color=(255, 245, 200))
    draw = ImageDraw.Draw(img)
    # Draw simple cartoon characters (placeholder)
    draw.ellipse((200, 400, 880, 1100), fill=(255, 220, 150), outline="black", width=8)
    draw.ellipse((300, 600, 500, 800), fill="white", outline="black", width=5)
    draw.ellipse((580, 600, 780, 800), fill="white", outline="black", width=5)
    
    # Add story text
    wrapped = textwrap.wrap(text, width=28)
    y = 1250
    for line in wrapped[:8]:
        draw.text((80, y), line, fill="black", font=ImageFont.load_default(), stroke_width=2)
        y+=55
    img.save(file)
    return file

def make_video(image_path, audio_path, out="final.mp4"):
    audio = AudioFileClip(audio_path)
    clip = ImageClip(image_path).set_duration(audio.duration + 0.5)
    clip = clip.set_audio(audio)
    clip = clip.resize((1080, 1920))
    clip.write_videofile(out, fps=24, codec='libx264', audio_codec='aac')
    return out

def upload_video(file_path):
    log(f"Uploading {file_path}...")
    try:
        with open(file_path, 'rb') as f:
            r = requests.post("https://catbox.moe/user/api.php", 
            data={"reqtype": "fileupload"}, 
            files={"fileToUpload": f}, timeout=120)
        if r.status_code == 200 and "https://" in r.text:
            url = r.text.strip()
            log(f"Catbox URL: {url}")
            return url
    except Exception as e:
        log(f"Catbox fail: {e}")
    # fallback
    try:
       
