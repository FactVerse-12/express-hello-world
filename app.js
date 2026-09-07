const express = require('express');
const app = express();
const PORT = process.env.PORT || 10000;

const IG_USER_ID = process.env.IG_USER_ID;
const ACCESS_TOKEN = process.env.ACCESS_TOKEN;

const stories = [
  {topic:"Horror", caption:"Raat ke 3 baje usne darwaze pe dastak suni... 👻 Full story in comments! #horror #storytoons\nFollow @story.toons.official"},
  {topic:"Love", caption:"Usne kaha, pyar kabhi khatam nahi hota ❤️ Follow @story.toons.official #lovestory"},
  {topic:"Motivation", caption:"Haar mat mano, kal tumhara hai! 💪 #motivation #storytoons"},
  {topic:"Moral", caption:"Ek choti si kahani jo zindagi badal degi ✨ #moralstory"}
];

app.get('/', (req,res) => {
  res.send(`<h1 style="font-family:sans-serif">StoryToons Bot LIVE 🤖</h1><p>Topic: ${stories[Math.floor(Math.random()*stories.length)].topic}</p><a href="/post-story"><button style="padding:20px;font-size:22px;background:green;color:white;border-radius:10px">CLICK TO POST NOW</button></a>`);
});

app.get('/post-story', async (req,res) => {
  try {
    const story = stories[Math.floor(Math.random()*stories.length)];
    const imageUrl = `https://picsum.photos/1080/1080?random=${Date.now()}`;
    const createUrl = `https://graph.facebook.com/v20.0/${IG_USER_ID}/media`;
    const form1 = new URLSearchParams({ image_url: imageUrl, caption: story.caption, access_token: ACCESS_TOKEN });
    const r1 = await fetch(createUrl, { method: 'POST', body: form1 });
    const d1 = await r1.json();
    if(!d1.id) return res.json({error:"Create failed", d1});
    await new Promise(r=>setTimeout(r, 3000));
    const pubUrl = `https://graph.facebook.com/v20.0/${IG_USER_ID}/media_publish`;
    const form2 = new URLSearchParams({ creation_id: d1.id, access_token: ACCESS_TOKEN });
    const r2 = await fetch(pubUrl, { method: 'POST', body: form2 });
    const d2 = await r2.json();
    res.json({ success:true, topic: story.topic, posted: d2 });
  } catch(e){ res.json({error:e.message}) }
});

app.listen(PORT, ()=>console.log("Live"));
