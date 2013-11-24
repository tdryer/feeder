import random
import time

from feedreader.database.models import Entry, Feed, Subscription

quotes = [
    "<h1>Marceline's Closet</h1>\n<p>Do you think it's right for Marceline to invite us to jam without Princess and BMO? It's just a jam sesh. Is that what you're gonna jam with? Yeah, man. Balloon music is the future. Listen. Pretty good. I don't think you mastered it yet. Well, duh. I just started.</p>\n<p>Oh, dude. There's a note. What's it say? Hey, guys, I had to run out, but I'll be back, blee-bloo-blop, Don't go in my house. That's it? Yeah. Just Don't go in my house in all caps... written in blood. </p>\n<h2>Hmm. What are you doing?</h2>\n<p>Eliminating desire from my heart. It helps pass the time. Come on! I can't do that! Let's play Cloud Hunt 'til she gets here. No, man, I got a mental block with Cloud Hunt! Yeah, that's what makes it awesome, 'cause I know I'll win. Oh, what?! Bring it on, brother! Now explain the rules 'cause I forget. Okay. I count to ten and you go hide somewhere. Then, I gotta try to find you. You can hide... anywhere in here. Anywhere in here, ...but Marcy's house is off limits because she said so. Okay? Got it. Okay. I'm gonna start counting. Ready? Yes. Go! </p>\n<ol>\n<li>One... </li>\n<li>Two... </li>\n<li>Three... </li>\n<li>Four... </li>\n<li>Five... </li>\n<li>Four...</li>\n</ol>\n<h3>Cloud Hunt...</h3>\n<p>GOTCHA! Huh. Hmm. AH-HA! JAKE! Get out of there! Marcelines gonna kill you! Jake! I know this isnt a mirror. What the--?! Youre doing it wrong, even! Get out! Get out!! (Finn goes inside. Jake spots him and continues mirroring him.) Dude, get out of there! Shes gonna kill us! Shell be home any minute! Did you read the note?! I mean, you read the note! You told it to me!!</p>\n<ul>\n<li>This is Jake! And this is Finn!</li>\n<li>Were not home right now, so...</li>\n<li>...leave a message! Leave a message!</li>\n</ul>\n<h4>Smells like sourdough in here.</h4>\n<p>Shes gonna kill us. Once she finds out shes gonna tie us up and eat us like a spider. You dont think I know that?! Hmmmmmmm... Well wait for the right moment and sneak out... right under her big, fat caboose. Okay, man. I can do this. Egh! Egh! Egh!! Shh, here she comes! Here she comes... Shh, shh!!</p>\n<h5>Huh. Lets get outta here.</h5>\n<p>Hello? She didnt wash hands! Is someone here? Shh!! Thats what stinks! Where are those dweebs? Uh... Yeah, hey, you guys. Are you still coming over? S jam time, so, like, call me, kay?</p>",
    "<h1>Throw it, Cake! </h1>\n<p>Eyahh! These jelly kinders arent... alive, are they? What? No, they cant even talk. Kick it! Thanks for helping me out guys. What are these buggers for, anyway? Oh, theyre decorations for my Biennial Gumball Ball. Tonight!</p>\n<p>Sounds like it gonna be large. Yes! So very large. Id like you to be there as my special guest. You want me to go with you to the ball? Heck yes. As my pal! Oh. Right. It starts at seven, so dont be late! Fionna, we got trouble! My tail is totally frizzin out! Ill check it out.</p>\n<h2>Its Ice Queen!</h2>\n<ol>\n<li>No! No retreat, girl.</li>\n<li>Hello, Fionna.</li>\n<li>And I see you brought Cake.</li>\n<li>Thats cool, right?</li>\n<li>Only if its cool that I brought... Lord Monochromicorn!</li>\n</ol>\n<p>The Prince shall be mine! Back inside! Outta my way, tomboy! Ice Queen, why are you always predatoring on dudes? Ha! You should to talk! Keeping all the babes to yourself, totally ice-blocking my game! What? Not this time! Gah! Slush Beast!</p>\n<h3>Cake! Morning-star mode!</h3>\n<p>You saved me from the Ice Queen! Oh, uh, yeah I guess. Is she gone? She must have fled. Fionna, youre so strong. And you look so beautiful in the snow. What are you doing later? I was just going to go home, I... Come with me. Lets go out. Go... out? Yeah. Lets go somewhere. What? Wed love to! Great! Meet me in the castle gardens in an hour! Yes, well be there!</p>\n<ul>\n<li>Hiya, gorgeous.</li>\n<li>H-E-Y.</li>\n<li>Accept these tokens of our esteem.</li>\n<li>Hey you didnt have to, guy...</li>\n<li>Nonsense. For you, Cake, a satchel of nepetalactone. Mo-Chro picked it himself.</li>\n</ul>\n<h4>Oh, its a date!</h4>\n<p>No, its not. Im sure when he said go out, he meant go out, not go out! Shut up, hes into you! Come on, you heard what he said. Im like his guy-friend. Well, that could change tonight. If its a date, why are you coming? Im coming to help you! Hold on, Im bringing my dulcimer. Man.</p>\n<h5>Its a conversation starter.</h5>\n<p>Fine, Ill do this if only to prove you wrong. Mm... Lets just bail, I changed my mind.</p>",
    "<h1>Dads Dungeon</h1>\n<p>Alright. Whaddaya wanna see next? A cheetah! A fart! A cookie! An external hard drive! Ooh, ooh! Change into Finn, but give him my body! BMO, your ideas are boring. What? Your head on my body isnt boring! Its weird!  Alright, Ill try to turn into a cheetah farting. I cant do the spots. Sparkles on the house? LETS SQUISH EM!</p>\n<p>Did you squish the sparkles? No. Theyre around this holo-message player. Its got a cartridge with it. Oh, snap!</p>\n<h2>Well, plop that cartridge in the slot, playah!</h2>\n<ol>\n<li>What? What was that about?</li>\n<li>Uh...</li>\n<li>Duh... duh... du-ugh...</li>\n<li>duh...</li>\n</ol>\n<p>Yeah! Okay!Hello, boys. Dad! If youre hearing this prerecorded hologram message, its because I passed on, and my spirit sparkles guided you to its secret hiding place. Right now, Im holding both of you in my hands. Youre both still little squishy babies. I made you boys something. Its a dungeon. A proper dungeon. Full of evil monsters, traps, and magic.</p>\n<h3>The whole kazoo!</h3>\n<ul>\n<li>Whoo!</li>\n<li>Whoa! Burgers and hotdogs!</li>\n<li>Yeah, yeah, YEAH!</li>\n<li>Wait, Jake!</li>\n<li>But... burgers and hotdogs..</li>\n</ul>\n<p>Whoa! Kickin! Kickin! Now, this next part of the message is just for you, Jake, so Finn, cover your ears. Jake... really, this dungeon is for Finn. I know I wont be around forever, and I wanna make something that will force Finn to toughen up. What? Now, tell Finn to uncover his ears now. Dude, take your hands off your head.</p>\n<h4>WHAT?</h4>\n<p>Alright, boys. Now to give you some incentive, at the end of the dungeon, Im going to put the family sword. Its made out of demons blood. Whoa, what the..? Whoa, dang! Give me back my blood, Joshua!</p>\n<h5>Kee Oth Rama Pancake</h5>\n<p>Blood Demon. Waaaaah! Whoa! Geez-louise! The dungeons eighty paces west of here under a dumb-lookin rock. And Finn, this dungeons gonna kick your tail. I bet you wont even get past the first trial, ya whiny baby!</p>",
    "<h1>Hug Wolf</h1>\n<p>Every hundred years, it spews evil spores across the land. Then lets burn its butt down to the roof rubbins. (The duo walks forward.) Finn, I can feel a bunch a eyeballs peepin us from the woods. Hhyuuugs!</p>\n<p>What the?! Is this an extra butt?! Quick, Jake! Burn the tree! Huuuugs! (Finn grunts and they begin circling each other) Gonna cut you up, boy! Im gonna snuggle you to pieces!</p>\n<h2>Dude! The trees about to splode its evil juice all over!</h2>\n<ul>\n<li>I didnt hug you last night.</li>\n<li>Yes, you did!</li>\n<li>My love handles still hurt!</li>\n<li>You came into my room around midnight and gave me a squeeze</li>\n<li>a really strong one!</li>\n</ul>\n<p>No! Jake, hurry! Is he crushin you, man?! No, hes just... hugging me gently! Oh...! When you see the wicker devil in tree afterlife, tell im Jake says, Hello.</p>\n<p>Hey, buddy, you okay? Didnt even tell me its name. Wha? Oh, sweet! Hahaha!</p>\n<h3>Hot to the touch!</h3>\n<ol>\n<li>Like last night!</li>\n<li>Yes. So you must be a beta hug wolf. A lower-level creature.</li>\n<li>Well, how can I get uncursed?</li>\n<li>Lemme, um... read the book a little more. Says there's no known cure.</li>\n<li>Uh... I'm scared, Jake...</li>\n<li>No hugs!!</li>\n</ol>\n<p>Hmmmm... Dude, whyre you so huggy? I just feel affectionate, I guess. Hugging helps. Hmm... You got a fever, man. I feel hot. Finn, youre hurting me. I think you need a good nights sleep.</p>\n<h4>You feelin better today?</h4>\n<p>Yeah. I feel like a million clams. Good. Hey, you think we have enough candy litter? Litter for lunch! Mmm! Huh? Not again! Whats the matter, Cinnamon Bun? Please, Finn. If youre gonna hug me again, dont make it as hard as you hugged me last night.</p>\n<h5>CB says I hugged im.</h5>\n<p>Haha. Cinnamon Bun, you got some crazy notions. I tell ya. Oh, Cinnamon Bun. What a crazy story, buddy. Yeah, buddy, but you were pretty huggy last night... buddy. Wait. You dont think I actually snuck into Cinnamon Buns room and hugged him, do you? Im just sayin you were really clingy. But no. Why would I? And dont tell me its because I have repressed emotional feelings for Cinnamon Bun.</p>",
    "<h1>Beautopia</h1>\n<p>Hey, what kind of coffee do you want? Hazelnut! Hazelnut! What if your name was Zelnut? And then I would be all like Hey, Zelnut. Thats terrible. Hey, Zelnut. Stop!</p>\n<ul>\n<li>That was awesome.</li>\n<li>See, Jake. We can trust Susan.</li>\n<li>Shes on the trolley.</li>\n<li>Keeps looking for Lubglubs.</li>\n</ul>\n<p>You hear that? Yeah.Finn and Susan Strong! Finn, help Susan. Of course I will. Excuse us for a moment, Strong. Dude, you know youre my bro, but that girl is bad news.</p>\n<ol>\n<li>What? Naw.</li>\n<li>Shes crazy, man. Shes a fish person!</li>\n<li>We dont know that!</li>\n</ol>\n<h2>Dude, she tried to eat Peppermint Butler!</h2>\n<p>Shed probably be worse if she was so scared of everything. Whatever, look she needs my help. And Im gonna help her whether youre coming with me or not. Oh, Im coming with you if only to be disruptive and obnoxious! Susan, what can we do?</p>\n<h3>I need your hero heart and your magic.</h3>\n<p>My magic? Magic of red flower. Fish people. Long ago, my people live in Beautopia. But driven out by Glubs Glubs. We come here. We too scared to fight back. This why we need your hero heart. Hyoomans! Ill be back!</p>\n<h4>Fish People!</h4>\n<p>Ill be, um, a dolphin! Come on, we swim there. No, you dont understand. Im not a fish person. Im human. We go. Grrr... What? Hey, hey. What? You no gills. We take boat.</p>\n<p>So where we headed, Susan? There. Oh, no. Oh, no. No, no, no! No, Susan, no!</p>",
    "<h1>Too Young</h1>\n<p>Finn? Finn? Finn! Where are you? I need you to try this! Ill be there in a sec! Whats the status? Good, man! Nice! Seal the deal, bro! Okay, man! Whatevs! You can do it, you hear me?! Im playin BMO--call me later, bye! Hows Finns date? I think its goin good. Unlike your game, boiiiii!</p>\n<ol>\n<li>Thats bunk!</li>\n<li>Right, Preebos?</li>\n<li>No... He is rightful ruler under kingdom law.</li>\n<li>Its complicated.</li>\n<li>I created Lemongrab.</li>\n</ol>\n<p>Wheres the key to the tower, BMO?! Tell me! AAAGH!</p>\n<h2>Okay, Finn.</h2>\n<p>Shes 13, youre 13. Just have fun! Be yourself. Wooooo! Whats that? Are you trying to make yourself 18 again? Nah. This is an instant bath serum. It makes you sweat cleaning agents. I dont bathe. I want that!</p>\n<h3>WAAAUGH!</h3>\n<p>Hot, hot, oh  WAAAAUGH! Oh... so spice! So spice! YOURE so spice! Bwaaa bwaaa bwaaaaaa! Announcing the arrival of the Earl of Lemongrab!</p>\n<ul>\n<li>Heh hah hah</li>\n<li>AAAAUGH!</li>\n<li>Oof!</li>\n<li>Ha ha ha!</li>\n</ul>\n<h4>This castle is...</h4>\n<p>in... Unacceptable Conditiiiioooon! UNACCEPTABLLLEEE! Thirty days in the dungeon! For who? Everyone in this ROOM! MMMLLUUUUUGH!!!</p>\n<p>Wait, wait! You cant give orders like that! Im in charge here, Lemongrab! TOO YOUNG! TOO YOUNG TO RULE THE KINGDOM! Watch your manners with the princess..! HHHHUUUUOOOOOOOOOOOH?! What the huh? MMMM! HAH! I am next in line to thee throne! Sooo... I will be in charge... UNTIL PRINCESS BUBBLEGUM turns... 18 again!</p>",
    "<h1>Goliad</h1>\n<p> Whatya building? Uhm, its just a little stick fort. Oh, rad! Look. Its just my size. Hey, get away from my fort, you big stinky monster! I like it when you get small, Jake. Yeah, me too. Whoa, whoa!</p>\n<p> Whoa, Peppermint butler! Finn, Jake. The Princess wants to see you. As princess of Candy Kingdom, Im in charge of a lot of candy people. They rely on me. I cant imagine what might happen to them if I was gone. And after my brush with death, at the hands of the Lich, I realized something. Im not gonna live forever Finn. I would if I could.</p>\n<ol>\n<li>Yea! Yeah!</li>\n<li>Teachers!</li>\n<li>Yeah, woo-hoo!</li>\n<li>Teach, teaching teachers.</li>\n</ol>\n<h2>But modern science just isnt there yet.</h2>\n<p>So I engineered a replacement who can live forever. I call her Goliad. Aww shes cute. Hi, Goliad. Im Finn. And Im Jake. Hi, Finn. Hi, Jake. Hi, Goliad. Hi, Finn. What did you use to make her? Oh, uhm...</p>\n<h3>Pretty standard candy creature soup.</h3>\n<p>Some acids. Some algebra. And I threw in one of my baby teeth so she had my DNA.</p>\n<h4>Wow, DNA?!</h4>\n<p>Yeah. All it takes is just one little tooth, or, a single hair. Its all it takes. Princess Bubblegum, are you okay? Yeah, Im good. Havent slept for a solid 83 hours, but... yeah, Im good.</p>\n<p>Aw, you should go to bed. I cant go to bed, Goliad has huge, mondo mama brains. I still need to fill them with knowledge... about how to rule a kingdom. What? Let us teach her. Uhh, okay. I guess that will be alright.</p>\n<ul>\n<li>Woow, woow, woow!</li>\n<li>Cmon, Goliad.</li>\n<li>See ya later, Princess!</li>\n<li>Get some sleep!</li>\n<li>Huh? Whu...? Bye guys...</li>\n</ul>",
    "<p>Got your girlfriend at my crib watching Netflix I like The Notebook swag swag swag, on you, chillin by the fire while we eaten' fondue. But something would be nothing worst birthday ever if I was your boyfriend, I'd never let you go. Swaggie when I met you girl my heart went knock knock I make good grilled cheese and I like girls. It's a Bieber world live it or die swag I like The Notebook. Baby know for sho', I'll never let you go ooh no, ooh no, ooh I'd like to be an architect, that would be cool, cause I like drawing. It's a Bieber world live it or die and all the haters I swear they look so small from up here I'm in pieces, so come fix me. I could be your Buzz Lightyear fly across the globe what you got, a billion could've never bought don't be so cold, we could be fire. Worst birthday ever got your girlfriend at my crib watching Netflix canada.</p><p>Baby know for sho', I'll never let you go ooh no, ooh no, ooh I make good grilled cheese and I like girls. When I met you girl my heart went knock knock I'd like to be an architect, that would be cool, cause I like drawing if I was your boyfriend, I'd never let you go. No one can stop me worst birthday ever I'ma make you shine bright like you're laying in the snow, burr. I'ma make you shine bright like you're laying in the snow, burr if I was your boyfriend, I'd never let you go you know I'm a real OG and baby I ain't from the TO. And all the haters I swear they look so small from up here I'ma make you shine bright like you're laying in the snow, burr baby, baby, baby, oh. We don't need no wings to fly ooh no, ooh no, ooh I like The Notebook. No matter how much I try, I can't figure out how to not be adorable swag got your girlfriend at my crib watching Netflix. When I met you girl my heart went knock knock I'm all fancy, yeah I'm popping Pellegrino I could be your Buzz Lightyear fly across the globe.</p><p>Baby know for sho', I'll never let you go I'ma make you shine bright like you're laying in the snow, burr ooh no, ooh no, ooh. Baby know for sho', I'll never let you go if I was your boyfriend, I'd never let you go it's a Bieber world live it or die. Swag swag swag, on you, chillin by the fire while we eaten' fondue I'd like to be an architect, that would be cool, cause I like drawing when I met you girl my heart went knock knock. We don't need no wings to fly I'm in pieces, so come fix me let the music blast we gon' do our dance. I think older people can appreciate my music baby know for sho', I'll never let you go when I met you girl my heart went knock knock. What you got, a billion could've never bought I think older people can appreciate my music swag. I like The Notebook you know I'm a real OG and baby I ain't from the TO no matter how much I try, I can't figure out how to not be adorable. I'ma make you shine bright like you're laying in the snow, burr I could be your Buzz Lightyear fly across the globe I'm in pieces, so come fix me.</p><p>What you got, a billion could've never bought but something would be nothing swag. If I was your boyfriend, I'd never let you go no matter how much I try, I can't figure out how to not be adorable don't be so cold, we could be fire. It's a Bieber world live it or die smile on your face, even though your heart is frowning ooh no, ooh no, ooh. Canada baby, baby, baby, oh I'm all fancy, yeah I'm popping Pellegrino. I'ma make you shine bright like you're laying in the snow, burr you know I'm a real OG and baby I ain't from the TO smile on your face, even though your heart is frowning. I'ma make you shine bright like you're laying in the snow, burr it's a Bieber world live it or die worst birthday ever. Baby, baby, baby, oh swag what you got, a billion could've never bought. I could be your Buzz Lightyear fly across the globe if I was your boyfriend, I'd never let you go if I was your boyfriend, I'd never let you go.</p>",
]
titles = [
    # Adventure Time
    'Mathematical!',
    'Whoa! Algebraic!',
    'Rhombus! Iceclops!',
    'MY HAT IS AWESOME!',
    'Do you think I have the goods, Bubblegum? Because I am into this stuff!',
    'I feel radder, faster... more adequate!',
    'Youth culture forever!',
    'Eat my sword, Ice King!',
    'Don\'t flaunt if if you\'re not gonna give it up.',
    'Werewolves: much worse than ogres.',
    'Imagination is for turbo-nerds who can\'t handle how kick-butt reality is!',
    'I\'m looking at my bits, dude. My leg is math!',
    'Uh, bleach, lighter fluid, ammonia, gasoline, I dunno. Lady stuff... Plutonium...',
    'So spice! So spice!',
    'I floop the pig.',
    'Eh. Um. Uh. I choose... sandwich.',
    'I love you, Everything burrito.',

    # Random
    'Aplia is bad and your economics professor should feel bad.',
]
urls = [
    'http://www.cs.sfu.ca/',
    'http://www.cs.sfu.ca/~ggbaker/',
    'http://www2.cs.sfu.ca/CourseCentral/470/ggbaker/',
]


def generate_dummy_entry(feed_id):
    return Entry(feed_id, random.choice(quotes), random.choice(urls),
                 random.choice(titles), 'David Yan',
                 random.randint(1, int(time.time())), "veryrandomguid")


def generate_dummy_feed(title=None, url=None):
    if not title:
        title = random.choice(titles)
    if not url:
        url = random.choice(urls)
    feed = Feed(title, url, url)
    return feed
