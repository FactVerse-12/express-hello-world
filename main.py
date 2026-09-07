import os, random, requests, subprocess, json, time
from gtts import gTTS

print("StoryToons Factory Started...")

# ===== 50 VIRAL TOPICS - HAR VIDEO ALAG =====
ALL_TOPICS = [
  {"t":"Horror - Bhootiya Haveli", "p":"haunted mansion night ghost girl pixar 3d", "m":"Lalach buri bala hai", "s":"Ek ladka purani haveli me khazana dhoondhne gaya, wahan usse ek roti hui ladki mili. Ladki ne kaha ye haveli shraapit hai. Ladke ne lalach nahi kiya aur wapas aa gaya."},
  {"t":"Love - Maa Ka Pyaar", "p":"indian mother child emotional love pixar", "m":"Maa se badhkar koi nahi", "s":"Chota Raju bimar tha, maa raat bhar jaag kar uski seva karti rahi. Subah Raju theek ho gaya."},
  {"t":"Funny - Alsi Gadha", "p":"lazy donkey funny sleeping comedy pixar", "m":"Mehnat ka fal meetha hota hai", "s":"Ek gadha din bhar sota tha, baaki janwar kaam karte the. Jab mela aaya toh sabke paas paise the, gadhe ke paas kuch nahi."},
  {"t":"Betrayal - Dhokebaaz Dost", "p":"two best friends betrayal sad cartoon", "m":"Sache dost ki kadar karo", "s":"Rohan ne apne dost ka secret dusron ko bata diya, dost ne baat karna band kar diya."},
  {"t":"Greed - Jadui Ped", "p":"magical tree gold coins greed cartoon", "m":"Jyada lalach sab khatam kar deta hai", "s":"Ek kisan ko jadui ped mila jo roz ek sone ka sikka deta tha, usne pura ped kaat diya."},
  {"t":"Horror - Raat Ka Auto", "p":"auto rickshaw midnight horror road cartoon", "m":"Anjaan logon se bacho", "s":"Raat 2 baje ek ladki ko khali auto mila, driver ka chehra nahi tha."},
  {"t":"Friendship - Sher Aur Chuha", "p":"lion and mouse friendship jungle cartoon", "m":"Chota dost bhi kaam aata hai", "s":"Sher ne chuhe ko chhod diya, baad me chuhe ne jaal kaat kar sher ko bachaya."},
  {"t":"Funny - Bandar Ka School", "p":"monkeys in classroom funny cartoon", "m":"Nakal karna buri baat", "s":"Bandar ne topper ki nakal ki, teacher ne pakad liya."},
  {"t":"Love - Behen Ka Pyar", "p":"brother sister rakhi emotional cartoon", "m":"Rishte anmol hote hain", "s":"Bhai videsh chala gaya, behen ne har saal rakhi bheji."},
  {"t":"Horror - Khali School", "p":"abandoned school ghost child horror cartoon", "m":"Jhooth bolne se dar lagta hai", "s":"Bacche ne jhooth bola ki school me bhoot hai, raat ko sach me bhoot aa gaya."},
  {"t":"Greed - Sone Ka Anda", "p":"hen golden egg greed cartoon", "m":"Sabr ka fal meetha hota hai", "s":"Ek murgi sone ka anda deti thi, malik ne lalach me use kaat diya."},
  {"t":"Funny - Hathi Ka Dance", "p":"elephant dancing funny cartoon", "m":"Hasna sehat ke liye accha hai", "s":"Hathi ne dance kiya, sab hasne lage, jungle me khushi aa gayi."},
  {"t":"Moral - Jhootha Kauwa", "p":"crow lying story cartoon", "m":"Jhooth ki umar choti hoti hai", "s":"Kauwe ne jhooth bola ki ped pe bhoot hai, koi uski baat nahi maanta tha."},
  {"t":"Love - Papa Ka Sapna", "p":"father son dream emotional cartoon", "m":"Mehnat se sapne pure hote hain", "s":"Papa ne bete ke liye cycle ka sapna dekha, din raat mehnat ki."},
  {"t":"Horror - Kuan Ka Paani", "p":"well water horror ghost cartoon night", "m":"Bina soche kaam mat karo", "s":"Gaon ke kuan se raat ko awaze aati thi, ek ladke ne jhaank kar dekha."},
  {"t":"Friendship - Tota Maina", "p":"parrot friendship cartoon jungle", "m":"Dosti me madad karni chahiye", "s":"Tota bimar tha, Maina ne uske liye dawa laayi."},
  {"t":"Greed - Do Billi", "p":"two cats fighting fish cartoon", "m":"Ladai se nuksaan hota hai", "s":"Do billi machli ke liye lad rahi thi, bandar ne machli kha li."},
  {"t":"Funny - Sher Ka Haircut", "p":"lion barber shop funny cartoon", "m":"Ghamand accha nahi", "s":"Sher ne naya haircut karwaya, sab us par hasne lage."},
  {"t":"Horror - Jungle Ki Chudail", "p":"witch jungle horror cartoon night", "m":"Himmat se dar bhagta hai", "s":"Chudail jungle me rehti thi, ek bacche ne himmat dikhayi."},
  {"t":"Moral - Mehnati Kisan", "p":"farmer working field cartoon", "m":"Mehnat kabhi bekar nahi jaati", "s":"Kisan ne sukhe khet me bhi mehnat ki, baarish hui aur fasal ug gayi."},
  {"t":"Love - Dost Ki Shaadi", "p":"friends wedding emotional cartoon", "m":"Dost hi parivar hote hain", "s":"Dost ki shaadi me sabne madad ki."},
  {"t":"Funny - Gadhe Ki Topi", "p":"donkey wearing hat funny cartoon", "m":"Dusron par haso mat", "s":"Gadhe ne topi pehni, sab hase, fir gadha raja ban gaya."},
  {"t":"Horror - Lift Ka Bhoot", "p":"elevator ghost horror cartoon", "m":"Akele lift me mat jao raat ko", "s":"Building ki lift raat ko khud chalti thi."},
  {"t":"Moral - Pipal Ka Ped", "p":"big banyan tree village cartoon", "m":"Ped lagana punya hai", "s":"Buzurg ne ped lagaya, gaon ko chhaya mili."},
  {"t":"Greed - Chor Ka Anjaam", "p":"thief stealing cartoon village", "m":"Chori kabhi chupti nahi", "s":"Chor ne chori ki, CCTV me pakda gaya."},
  {"t":"Friendship - Machli Aur Mendhak", "p":"fish frog friendship cartoon pond", "m":"Alag hoke bhi dost bana ja sakta hai", "s":"Machli aur mendhak dost ban gaye."},
  {"t":"Horror - Purana Radio
