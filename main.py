import os
import requests
import time
import random
import textwrap
from gtts import gTTS
from PIL import Image, ImageDraw
from moviepy.editor import ImageClip, AudioFileClip

INSTA_ID = os.getenv("INSTA_ID")
TOKEN = os.getenv("INSTA_TOKEN")

def log(m):
    print(m, flush=True)

TOPICS = [
    "Chuha aur Bandar ki dosti - Bandar ne chuhe ka lunch kha liya",
    "School me jhooth - Chuha fail ho gaya par topper bola",
    "Madad ka badla - Bandar musibat me tha"
]

def make_voice(text):
    tts = gTTS(text=text, lang='hi', slow=False)
    tts.save("voice.mp3")
    return "voice.mp3"

def make_image(text):
    img = Image.new('RGB', (1080, 1920), color=(255, 245, 200))
    draw = ImageDraw.Draw(img)
    draw.ellipse((200, 400, 880, 1100), fill=(255, 220, 150), outline="black", width=8)
    draw.ellipse((300, 600, 500, 800), fill="white", outline="black", width=5)
    draw.ellipse((580, 600, 780, 800), fill="white", outline="black", width=5)
    lines = textwrap.wrap(text, width=28)
    y = 1250
    for line in lines[:8]:
        draw.text((80, y), line, fill="black")
        y += 55
    img.save("frame.jpg")
    return "frame.jpg"

def make_video(img_path, audio_path):
    audio = AudioFileClip(audio_path)
    clip = ImageClip(img_path).set_duration(audio.duration + 0.5)
    clip = clip.set_audio(audio)
   def make_video(img_path, audio_path):
    audio = AudioFileClip(audio_path)
    clip = ImageClip(img_path).set_duration(audio.duration + 0.5)
    clip = clip.set_audio(audio)
    clip.write_videofile("final.mp4", fps=24, codec='libx264', audio_codec='aac')
    return "final.mp4" 
    clip.write_videofile("final.mp4", fps=24, codec='libx264', audio_codec='aac')
    return "final.mp4"

def upload_video(path):
    log("Uploading to catbox...")
    try:
        with open(path, 'rb') as f:
            r = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f}, timeout=120)
            if r.status_code == 200 and "https://" in r.text:
                log(f"URL: {r.text.strip()}")
                return r.text.strip()
    except Exception as e:
        log(f"Catbox error {e}")
    return None

def create_reel(video_url, caption):
    url = f"https://graph.facebook.com/v19.0/{INSTA_ID}/media"
    data = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": TOKEN
    }
    r = requests.post(url, data=data)
    log(f"CREATE: {r.text}")
    if "error" in r.text:
        return False
    cid = r.json().get("id")
    if not cid:
        return False
    for i in range(12):
        s_url = f"https://graph.facebook.com/v19.0/{cid}?fields=status_code&access_token={TOKEN}"
        s = requests.get(s_url).json()
        log(f"Status {i}: {s}")
        if s.get("status_code") == "FINISHED":
            break
        time.sleep(10)
    p_url = f"https://graph.facebook.com/v19.0/{INSTA_ID}/media_publish"
    p = requests.post(p_url, data={"creation_id": cid, "access_token": TOKEN})
    log(f"PUBLISH: {p.text}")
    return "id" in p.text

if __name__ == "__main__":
    if not INSTA_ID or not TOKEN:
        log("Secrets missing!")
        exit(1)
    story = random.choice(TOPICS)
    log(f"Story: {story}")
    v = make_voice(story)
    im = make_image(story)
    final = make_video(im, v)
    public = upload_video(final)
    if not public:
        log("Upload fail")
        exit(1)
    ok = create_reel(public, story)
    if ok:
        log("SUCCESS")
    else:
        log("Publish fail - check permission #10")
