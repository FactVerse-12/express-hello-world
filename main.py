import os, requests, time, textwrap
from gtts import gTTS
from PIL import Image, ImageDraw
from moviepy.editor import ImageClip, AudioFileClip

INSTA_ID = os.getenv("INSTA_ID")
TOKEN = os.getenv("INSTA_TOKEN")

def log(m): print(m, flush=True)

TOPIC = "Chuha aur Bandar - Ek sachi dosti ki kahani"

def upload_video(path):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # 1. 0x0.st - best for GitHub Actions
    try:
        log("Uploading to 0x0.st...")
        with open(path, 'rb') as f:
            r = requests.post("https://0x0.st", files={"file": f}, headers=headers, timeout=90)
            log(f"0x0: {r.text}")
            if "https://0x0.st" in r.text:
                return r.text.strip()
    except Exception as e: log(f"0x0 fail {e}")

    # 2. catbox with header
    try:
        log("Uploading to catbox.moe...")
        with open(path, 'rb') as f:
            r = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": f},
                headers=headers,
                timeout=90
            )
            log(f"catbox: {r.text}")
            if "https://" in r.text and "catbox" in r.text:
                return r.text.strip()
    except Exception as e: log(f"catbox fail {e}")

    # 3. file.io - direct link
    try:
        log("Trying file.io...")
        with open(path, 'rb') as f:
            r = requests.post("https://file.io", files={"file": f}, headers=headers, timeout=60)
            j = r.json()
            log(f"file.io: {r.text[:200]}")
            if j.get("success"):
                return j["link"]
    except Exception as e: log(f"file.io fail {e}")

    return None

if __name__ == "__main__":
    if not INSTA_ID or not TOKEN:
        print("Secrets missing!"); exit(1)

    log(f"Using ID: {INSTA_ID}")

    tts = gTTS(text=TOPIC, lang='hi', slow=False)
    tts.save("voice.mp3")

    img = Image.new('RGB', (1080, 1920), color=(255, 245, 200))
    d = ImageDraw.Draw(img)
    d.ellipse((200, 400, 880, 1100), fill=(255, 220, 150), outline="black", width=8)
    d.ellipse((300, 600, 500, 800), fill="white", outline="black", width=5)
    d.ellipse((580, 600, 780, 800), fill="white", outline="black", width=5)
    lines = textwrap.wrap(TOPIC, width=28)
    y = 1250
    for line in lines[:8]:
        d.text((80, y), line, fill="black")
        y += 55
    img.save("frame.jpg")

    audio = AudioFileClip("voice.mp3")
    clip = ImageClip("frame.jpg").set_duration(audio.duration + 0.5)
    clip = clip.set_audio(audio)
    
    clip.write_videofile(
        "final.mp4", 
        fps=24, 
        codec='libx264', 
        audio_codec='aac',
        preset='ultrafast',
        ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    )

    size = os.path.getsize("final.mp4")
    log(f"Video size: {size} bytes")
    if size < 50000:
        log("Video too small!"); exit(1)

    url = upload_video("final.mp4")
    log(f"FINAL URL: {url}")
    if not url:
        log("Upload failed"); exit(1)

    api = f"https://graph.facebook.com/v19.0/{INSTA_ID}/media"
    r = requests.post(api, data={"media_type": "REELS", "video_url": url, "caption": TOPIC, "access_token": TOKEN})
    log(f"CREATE: {r.text}")
    cid = r.json().get("id")
    if not cid: exit(1)

    for i in range(15):
        time.sleep(10)
        s = requests.get(f"https://graph.facebook.com/v19.0/{cid}?fields=status_code,status&access_token={TOKEN}").json()
        log(f"Status {i}: {s}")
        if s.get("status_code")=="FINISHED": break
        if s.get("status_code")=="ERROR":
            log("Insta Transcoding ERROR"); exit(1)

    p = requests.post(f"https://graph.facebook.com/v19.0/{INSTA_ID}/media_publish", data={"creation_id": cid, "access_token": TOKEN})
    log(f"PUBLISH: {p.text}")
    
    if "id" in p.text:
        log("SUCCESS - Reel Posted!")
    else:
        log("Publish failed")
        exit(1)
