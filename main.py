import os, random, asyncio, requests, subprocess, time
import edge_tts

VOICE = "hi-IN-SwaraNeural"
PAGE_NAME = "storytoons_____"

# Tumhare 4 Modules
CHARACTERS = {
    "Horror": "creepy cute cartoon ghost kid, big eyes, pixar style, dark forest background, consistent character",
    "Love": "cute cartoon couple boy and girl, indian kids Gattu Chinki in love, pixar style, romantic background",
    "Funny": "cute orange cartoon cat Chintu wearing blue tshirt, funny face, pixar style",
    "Mystery": "cute baby elephant Dholu detective with hat, pixar style, mysterious background"
}

STORIES = {
    "Horror": "Ek raat Chintu ko jungle me roshni dikhi, wahan ek bhooton ka laddoo tha, khate hi uski parchai bolne lagi",
    "Love": "Gattu ne Chinki ke liye chand se tara todne ka wada kiya, fir usko asli tara jamin par mil gaya",
    "Funny": "Dholu ne socha chand cheese se bana hai, usko khane ke liye usne lambi seedhi lagayi",
    "Mystery": "Gaon me sabke jute gayab ho rahe the, Chintu ne dekha raat ko jute khud chal rahe hain"
}

def make_image(prompt, i):
    # Best Cartoon Reel Banegi - 1080x1920
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1080&height=1920&nologo=true&seed={random.randint(1,99999)}"
    r = requests.get(url, timeout=60)
    open(f"s{i}.jpg",'wb').write(r.content)
    return f"s{i}.jpg"

async def make_voice(text):
    await edge_tts.Communicate(text, VOICE, rate="-5%", volume="+10%").save("voice.mp3")

def make_video_with_music(imgs):
    # Background Music Download (royalty free)
    try:
        # Free music
        music_url = "https://cdn.pixabay.com/download/audio/2022/03/10/audio_c8c8a650f6.mp3"
        open("bg.mp3","wb").write(requests.get(music_url).content)
    except: pass

    per = 6.0 # har image 6 sec
    with open("list.txt","w") as f:
        for im in imgs:
            f.write(f"file '{im}'\nduration {per}\n")
        f.write(f"file '{imgs[-1]}'\n")

    # 1. Image + Voice = base video
    os.system('ffmpeg -y -f concat -safe 0 -i list.txt -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -r 30 base.mp4')
    # 2. Voice + Background Music Mix
    os.system('ffmpeg -y -i base.mp4 -i voice.mp3 -i bg.mp3 -filter_complex "[1:a][2:a]amix=inputs=2:duration=shortest:dropout_transition=0:weights=1 0.3[a]" -map 0:v -map "[a]" -c:v libx264 -shortest final_reel.mp4')

def post_to_instagram():
    token = os.environ.get('INSTA_TOKEN')
    ig_id = os.environ.get('INSTA_ID')
    if not token:
        print("TOKEN nahi mila, sirf video banayi hai, post nahi hui")
        return

    # Catbox pe upload karke public link lo
    with open("final_reel.mp4","rb") as f:
        r = requests.post("https://catbox.moe/user/api.php", data={"reqtype":"fileupload"}, files={"fileToUpload": f})
        public_url = r.text.strip()
    print("Video URL:", public_url)

    caption = f"Aaj ki Kahani - Follow {PAGE_NAME} ❤️ #storytoons #hindikahani #cartoonstory"
    # 1. Container banao
    res = requests.post(f"https://graph.facebook.com/v20.0/{ig_id}/media", data={"media_type":"REELS","video_url":public_url,"caption":caption,"access_token":token}).json()
    print(res)
    cid = res.get('id')
    # 2. Wait
    for _ in range(12):
        time.sleep(5)
        s = requests.get(f"https://graph.facebook.com/v20.0/{cid}?fields=status_code&access_token={token}").json()
        if s.get('status_code')=='FINISHED': break
    # 3. Publish
    pub = requests.post(f"https://graph.facebook.com/v20.0/{ig_id}/media_publish", data={"creation_id":cid,"access_token":token}).json()
    print("PUBLISHED:", pub)

async def main():
    topic = random.choice(list(STORIES.keys())) # Horror, Love, Funny, Mystery
    story = STORIES[topic]
    char_prompt = CHARACTERS[topic]

    title = f"{topic} Kahani"
    voice_text = f"Namaste dosto, {PAGE_NAME} me swagat hai. Aaj ki {topic} kahani. {story}. Aage kya hua janne ke liye follow karo."

    prompts = [f"{char_prompt}, {story} scene {i+1}, 4k" for i in range(5)]
    imgs = [make_image(p,i) for i,p in enumerate(prompts)]
    await make_voice(voice_text)
    make_video_with_music(imgs)
    post_to_instagram()

if __name__ == "__main__":
    asyncio.run(main())
