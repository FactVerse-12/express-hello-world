import os, random, requests, subprocess, json, time
from gtts import gTTS
print("=== INFINITE FACTORY ===")
GENRES=["Horror","Funny","Love","Moral","Greed","Friendship","Betrayal","Mystery"]
CHARACTERS=["Sher","Chuha","Bandar","Billi","Hathi","Kauwa","Gadha","Tota","Bhoot","Chudail","Raja","Kisan","Baccha","Dadi","Jadugar","Pari","Rakshas","Maina","Kutta"]
PLACES=["Haveli","Jungle","School","Gaon","Sheher","Kuan","Peepal","Hospital","Lift","Chhat","Nadi","Pahad","Khet","Bazaar","Samundar","Gufa"]
TWISTS=["jadui khazana mila","raat ko aawaz aayi","dost ne dhokha diya","sab hasne lage","ek raaz khula","ladai ho gayi","madad karni padi","sapna sach hua"]
MORALS=["Lalach buri bala hai","Mehnat ka fal meetha hota hai","Sache dost ki kadar karo","Ekta me bal hai","Sach me hi jeet hai","Gussa sab kharab karta hai","Samay sabse keemti hai","Maa se badhkar koi nahi","Madad karna punya hai","Jhooth ki umar choti hoti hai"]
used_file="used_topics.json"
used=[]
if os.path.exists(used_file):
    try: used=json.loads(open(used_file).read())
    except: used=[]
def make_topic():
    for _ in range(1000):
        g=random.choice(GENRES);c1=random.choice(CHARACTERS);c2=random.choice(CHARACTERS);p=random.choice(PLACES);t=random.choice(TWISTS);m=random.choice(MORALS)
        if c1==c2: continue
        name=f"{g} - {c1} aur {c2} ka {t} {p} me"
        if name not in used:
            prompt=f"{g} story {c1} and {c2} in {p} {t} pixar 3d cartoon"
            story=f"{p} me {c1} aur {c2} rehte the. Ek din {t}, sab badal gaya."
            return {"t":name,"p":prompt,"m":m,"s":story}
    return {"t":"Moral - Kisan aur Sher Khet me","p":"farmer lion cartoon","m":"Mehnat ka fal meetha","s":"Khet me kisan aur sher dost ban gaye"}
sel=make_topic()
used.append(sel['t'])
open(used_file,'w').write(json.dumps(used[-1000:]))
print(f"TOPIC: {sel['t']}")
print(f"TOTAL USED: {len(used)}")
text=f"{sel['s']} Is kahani se seekh milti hai ki {sel['m']}."
gTTS(text=text, lang='hi', slow=False).save("voice.mp3")
print("Voice OK")
img_url="https://image.pollinations.ai/prompt/"+requests.utils.quote(sel['p'])+f"?width=1080&height=1920&nologo=true&seed={random.randint(1,999999)}"
for i in range(5):
    try:
        r=requests.get(img_url, timeout=40)
        open('img.jpg','wb').write(r.content)
        if os.path.getsize('img.jpg')>8000: break
    except: time.sleep(2)
print("Image OK")
cmd='ffmpeg -y -loop 1 -i img.jpg -i voice.mp3 -c:v libx264 -c:a aac -shortest -t 30 -pix_fmt yuv420p -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" final.mp4'
subprocess.run(cmd, shell=True)
print("VIDEO READY")
token=os.getenv("INSTA_TOKEN")
ig_id=os.getenv("INSTA_ID")
if not token or not ig_id:
    print("No token")
    exit(0)
with open('final.mp4','rb') as f:
    r=requests.post("https://catbox.moe/user/api.php", data={"reqtype":"fileupload"}, files={"fileToUpload": f}, timeout=60)
    vurl=r.text.strip()
print(f"URL {vurl}")
b="https://graph.facebook.com/v19.0"
cap=f"{sel['t']}\n\n{sel['s']}\n\nSeekh: {sel['m']}\n\n#hindikahani #moralstory"
r=requests.post(f"{b}/{ig_id}/media", data={"video_url":vurl,"caption":cap,"media_type":"REELS","access_token":token})
print(r.text)
jid=r.json().get('id')
if not jid: exit(0)
time.sleep(30)
pub=requests.post(f"{b}/{ig_id}/media_publish", data={"creation_id":jid,"access_token":token})
print(pub.text)
