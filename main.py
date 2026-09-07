import os, random, requests, subprocess, json, time
from gtts import gTTS

print("=== INFINITE STORYTOONS FACTORY ===")

# ===== INFINITE GENERATOR DATA =====
GENRES = ["Horror", "Funny", "Love", "Moral", "Greed", "Friendship", "Betrayal", "Mystery"]
CHARACTERS = ["Sher", "Chuha", "Bandar", "Billi", "Hathi", "Kauwa", "Gadha", "Tota", "Bhoot", "Chudail", "Raja", "Kisan", "Baccha", "Dadi", "Jadugar", "Pari", "Rakshas", "Maina", "Kutta"]
PLACES = ["Haveli", "Jungle", "School", "Gaon", "Sheher", "Kuan", "Peepal", "Hospital", "Lift", "Chhat", "Nadi", "Pahad", "Khet", "Bazaar", "Samundar", "Gufa"]
TWISTS = ["jadui khazana mila", "raat ko aawaz aayi", "dost ne dhokha diya", "sab hasne lage", "ek raaz khula", "ladai ho gayi", "madad karni padi", "sapna sach hua"]
MORALS = ["Lalach buri bala hai", "Mehnat ka fal meetha hota hai", "Sache dost ki kadar karo", "Ekta me bal hai", "Sach me hi jeet hai", "Gussa sab kharab karta hai", "Samay sabse keemti hai", "Maa se badhkar koi nahi", "Madad karna punya hai", "Jhooth ki umar choti hoti hai", "Santosh sabse bada dhan hai", "Himmat se dar bhagta hai"]

used_file = "used_topics.json"
used = []
if os.path.exists(used_file):
    try: used = json.loads(open(used_file).read())
    except: used = []

def make_unique_topic():
    for _ in range(1000): # 1000 baar try karega unique banane ke liye
        g = random.choice(GENRES)
        c1 = random.choice(CHARACTERS)
        c2 = random.choice(CHARACTERS)
        p = random.choice(PLACES)
        t = random.choice(TWISTS)
        m = random.choice(MORALS)
        if c1 == c2: continue
        topic_name = f"{g} - {c1} aur {c2} ka {t} {p} me"
        if topic_name not in used:
            prompt = f"{g} story {c1} and {c2} in {p}, {t}, pixar 3d cartoon style, vibrant, 8k"
            story = f"{p} me {c1} aur {c2} rehte the. Ek din {t}, aur sab kuch badal gaya. {c1} ne {c2} ki madad ki. Ant me sab samajh gaye."
            return {"t": topic_name, "p": prompt, "m": m, "s": story}
    return None

selected = make_unique_topic()
used.append(selected['t'])
open(used_file,'w').write(json.dumps(used[-1000:])) # Last 1000 yaad rakhega, kabhi repeat nahi

print(f"TOPIC: {selected['t']}")
print(f"MORAL: {selected['m']}")
print(f"Used Total: {len(used)}")

# ===== VOICE =====
full_text = f"{selected['s']} Is kahani se hume ye seekh milti hai ki {selected['m']}."
tts = gTTS(text=full_text, lang='hi', slow=False)
tts.save("voice.mp3")
print("Voice OK")

# ===== IMAGE - HAR TOPIC KA ALAG =====
img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(selected['p'])}?width=1080&height=1920&nologo=true&seed={random.randint(1,999999)}"
for i in range(5):
    try:
        r = requests.get(img_url, timeout=40)
        open('img.jpg','wb').write(r.content)
        if os.path.getsize('img.jpg') > 8000:
            break
    except:
        time.sleep(2)
print("Image OK")

# ===== VIDEO =====
# Background music try
has_bg = False
try:
    r = requests.get("https://cdn.pixabay.com/download/audio/2022/02/10/audio_c8c8a65064.mp3?filename=lofi-study-112191.mp3", timeout=15)
    open('bg.mp3','wb').write(r.content)
    if os.path.getsize('bg.mp3') > 10000: has_bg = True
except: has_bg = False

if has_bg:
    cmd = 'ffmpeg -y -loop 1 -i img.jpg -i voice.mp3 -i bg.mp3 -filter_complex "[1:a]volume=1.0[a1];[2:a]volume=0.12[a2];[a1][a2]amix=inputs=2:duration=longest:dropout_transition=0[a]" -map 0:v -map "[a]" -c:v libx264 -c:a aac -shortest -t 30 -pix_fmt yuv420p -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" final.mp4'
else:
    cmd = 'ffmpeg -y -loop 1 -i img.jpg -i voice.mp3 -c:v libx264 -c:a aac -shortest -t 30 -pix_fmt yuv420p -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" final.mp4'

subprocess.run(cmd, shell=True)
print("FINAL VIDEO READY")

# ===== POST TO INSTA =====
token = os.getenv("INSTA_TOKEN")
ig_id = os.getenv("INSTA_ID")
print(f"Token: {'YES' if token else 'NO'}")

if not token or not ig_id:
    print("TOKEN nahi, only video banayi")
    exit(0)

# Upload
with open('final.mp4','rb') as f:
    r = requests.post("https://catbox.moe/user/api.php", data={"reqtype":"fileupload"}, files={"fileToUpload": f}, timeout=60)
    video_url = r.text.strip()
print(f"URL: {video_url}")

# Create Container
cap = f"{selected['t']}\n\n{selected['s']}\n\n✨ Seekh: {selected['m']}\n\n#hindikahani #moralstory #storytoons #viralstory #cartoonkahani"
url = f"https://graph.facebook.com/v19.
