import os, requests, time, random, textwrap
from gtts import gTTS
from PIL import Image, ImageDraw
from moviepy.editor import ImageClip, AudioFileClip

INSTA_ID = os.getenv("INSTA_ID")
TOKEN = os.getenv("INSTA_TOKEN")

def log(m): print(m, flush=True)

TOPIC = "Chuha aur Bandar - Ek sachi dosti ki kahani"

def upload_video(path):
    log("Uploading to 0x0.st...")
    try:
        with open(path, 'rb') as f:
            r = requests.post("https://0x0.st", files={"file": f}, timeout=120)
            log(f"0x0 response: {r.text}")
            if r.status_code == 200 and "https://" in r.text:
                return r.text.strip()
    except Exception as e:
        log(f"0x0 error {e}")
    log("Trying litterbox...")
    try:
        with open(path, 'rb') as f:
            r = requests.post("https://litterbox.catbox.moe/resources/internals/api.php", data={"reqtype": "fileupload", "time": "72h"}, files={"fileToUpload": f}, timeout=120)
            log(f"Litter response: {r.text}")
            if "https://" in r.text:
                return r.text.strip()
    except Exception as e:
        log(f"Litter error {e}")
    return None

if __name__ == "__main__":
    if not INSTA_ID or not TOKEN:
        print("Secrets missing!"); exit(1)
    
    # Voice
    tts = gTTS(text=TOPIC, lang='hi', slow=False)
    tts.save("voice.mp3")
    
    # Image
    img = Image.new('RGB', (1080, 1920), color=(255, 245, 200))
    d = ImageDraw.Draw(img)
    d.ellipse((200, 400, 880, 1100), fill=(255, 220, 150), outline="black", width=8)
    d.ellipse((300, 600, 500, 800), fill="white", outline="black", width=5)
    d.ellipse((580, 600, 780, 800), fill="white", outline="black", width=5)
    lines = textwrap.wrap(TOPIC, width=28)
    y = 1250
    for line in lines:
        d.text((80, y), line, fill="black")
        y += 55
    img.save("frame.jpg")
    
    # Video
    audio = AudioFileClip("voice.mp3")
    clip = ImageClip("frame.jpg").set_duration(audio.duration + 0.5)
    clip = clip.set_audio(audio)
    clip.write_videofile("final.mp4", fps=24, codec='libx264', audio_codec='aac')
    
    # Upload & Post
    url = upload_video("final.mp4")
    if not url:
        log("Upload fail"); exit(1)
    
    log(f"VIDEO URL: {url}")
    api = f"https://graph.facebook.com/v19.0/{INSTA_ID}/media"
    r = requests.post(api, data={"media_type": "REELS", "video_url": url, "caption": TOPIC, "access_token": TOKEN})
    log(f"CREATE: {r.text}")
    cid = r.json().get("id")
    if not cid: exit(1)
    
    time.sleep(25)
    p_url = f"https://graph.facebook.com/v19.0/{INSTA_ID}/media_publish"
    p = requests.post(p_url, data={"creation_id": cid, "access_token": TOKEN})
    log(f"PUBLISH: {p.text}")
    log("SUCCESS - Reel Posted!")
