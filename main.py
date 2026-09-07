import os, requests, time, textwrap
from gtts import gTTS
from PIL import Image, ImageDraw
from moviepy.editor import ImageClip, AudioFileClip

INSTA_ID = os.getenv("INSTA_ID")
TOKEN = os.getenv("INSTA_TOKEN")

def log(m): print(m, flush=True)

TOPIC = "Chuha aur Bandar - Ek sachi dosti ki kahani"

def upload_video(path):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # 1. Litterbox - catbox ka hi dusra version, 72hr tak rehta hai - BEST
    try:
        log("Trying litterbox...")
        with open(path, 'rb') as f:
            r = requests.post(
                "https://litterbox.catbox.moe/resources/internals/api.php",
                data={"reqtype": "fileupload", "time": "72h"},
                files={"fileToUpload": f},
                headers=headers, timeout=90
            )
            log(f"litterbox: {r.text[:200]}")
            if "https://" in r.text:
                return r.text.strip()
    except Exception as e: log(f"litterbox fail {e}")

    # 2. Uguu.se - bahut reliable hai
    try:
        log("Trying uguu.se...")
        with open(path, 'rb') as f:
            r = requests.post("https://uguu.se/upload.php", files={"files[]": f}, headers=headers, timeout=90)
            j = r.json()
            log(f"uguu: {j}")
            if j.get("files") and len(j["files"])>0:
                return j["files"][0]["url"]
    except Exception as e: log(f"uguu fail {e}")

    # 3. Transfer.sh - old but still works
    try:
        log("Trying transfer.sh...")
        with open(path, 'rb') as f:
            r = requests.put(f"https://transfer.sh/{os.path.basename(path)}", data=f, headers=headers, timeout=60)
            log(f"transfer: {r.text[:200]}")
            if "https://transfer.sh" in r.text:
                return r.text.strip()
    except Exception as e: log(f"transfer fail {e}")

    # 4. FileBin
    try:
        log("Trying filebin.net...")
        bin_id = "factverse123"
        with open(path, 'rb') as f:
            r = requests.post(f"https://filebin.net/archive/{bin_id}/{os.path.basename(path)}", data=f, headers={"bin": bin_id, "filename": os.path.basename(path)}, timeout=60)
            log(f"filebin: {r.text[:200]}")
            # filebin direct link format
            return f"https://filebin.net/archive/{bin_id}/{os.path.basename(path)}/raw"
    except Exception as e: log(f"filebin fail {e}")

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
    log(f"Video size: {size} bytes - OK")

    url = upload_video("final.mp4")
    log(f"FINAL URL: {url}")
    if not url:
        log("All uploads failed - Try again after 2 min"); exit(1)

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
            log(f"Transcoding error: {s}"); exit(1)

    p = requests.post(f"https://graph.facebook.com/v19.0/{INSTA_ID}/media_publish", data={"creation_id": cid, "access_token": TOKEN})
    log(f"PUBLISH: {p.text}")

    if "id" in p.text:
        log("SUCCESS - Reel Posted on storytoons___!")
    else:
        log("Publish failed - check permissions"); exit(1)
