import os, requests, time, random, textwrap
from gtts import gTTS
from PIL import Image, ImageDraw
from moviepy.editor import ImageClip, AudioFileClip

INSTA_ID = os.getenv("INSTA_ID")
TOKEN = os.getenv("INSTA_TOKEN")

def log(m): print(m, flush=True)

TOPIC = "Chuha aur Bandar - Ek sachi dosti ki kahani"

def upload_video(path):
    # 1. Try transfer.sh
    try:
        log("Trying transfer.sh...")
        with open(path, 'rb') as f:
            r = requests.put(f"https://transfer.sh/{os.path.basename(path)}", data=f, timeout=60)
            log(f"transfer: {r.text[:200]}")
            if "https://" in r.text:
                return r.text.strip()
    except Exception as e: log(f"transfer fail {e}")

    # 2. Try tmpfiles.org
    try:
        log("Trying tmpfiles.org...")
        with open(path, 'rb') as f:
            r = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=60)
            log(f"tmpfiles: {r.text[:300]}")
            j = r.json()
            if j.get("status")=="success":
                url = j["data"]["url"].replace("tmpfiles.org/dl/", "tmpfiles.org/dl/")
                # make direct link
                return url
    except Exception as e: log(f"tmpfiles fail {e}")

    # 3. Try file.io
    try:
        log("Trying file.io...")
        with open(path, 'rb') as f:
            r = requests.post("https://file.io", files={"file": f}, timeout=60)
            log(f"file.io: {r.text[:300]}")
            j = r.json()
            if j.get("success"):
                return j.get("link")
    except Exception as e: log(f"file.io fail {e}")

    # 4. Try gofile.io
    try:
        log("Trying gofile...")
        # get server
        s = requests.get("https://api.gofile.io/servers", timeout=20).json()
        server = s["data"]["servers"][0]["name"]
        with open(path, 'rb') as f:
            r = requests.post(f"https://{server}.gofile.io/contents/uploadfile", files={"file": f}, timeout=90)
            log(f"gofile: {r.text[:400]}")
            j = r.json()
            if j["status"]=="ok":
                return j["data"]["directLink"]
    except Exception as e: log(f"gofile fail {e}")

    return None

if __name__ == "__main__":
    if not INSTA_ID or not TOKEN:
        print("Secrets missing!"); exit(1)

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
    clip.write_videofile("final.mp4", fps=24, codec='libx264', audio_codec='aac')

    url = upload_video("final.mp4")
    log(f"FINAL URL: {url}")
    if not url:
        log("All uploads failed"); exit(1)

    api = f"https://graph.facebook.com/v19.0/{INSTA_ID}/media"
    r = requests.post(api, data={"media_type": "REELS", "video_url": url, "caption": TOPIC, "access_token": TOKEN})
    log(f"CREATE: {r.text}")
    cid = r.json().get("id")
    if not cid: exit(1)

    for i in range(12):
        time.sleep(10)
        s = requests.get(f"https://graph.facebook.com/v19.0/{cid}?fields=status_code&access_token={TOKEN}").json()
        log(f"Status {i}: {s}")
        if s.get("status_code")=="FINISHED": break

    p = requests.post(f"https://graph.facebook.com/v19.0/{INSTA_ID}/media_publish", data={"creation_id": cid, "access_token": TOKEN})
    log(f"PUBLISH: {p.text}")
    log("SUCCESS - Reel Posted!" if "id" in p.text else "Publish failed - check Instagram permissions")
