import pandas as pd
from tqdm import tqdm
import time
from random import randint
import json


detach = """DETACH - Ending the dialogue. Saying goodbye or other similar actions.
Examples:
1. speaker_1: Okay, I have to go $$$ DETACH
speaker_2: Bye-bye $$$ DETACH
2. speaker_1: It's so nice! $$$ OTHER
speaker_2: Sorry, I need to hurry $$$ DETACH
3. speaker_1: Can you help me? $$$ OTHER
speaker_2: I can't talk right now, later $$$ DETACH
3. speaker_1: Good. $$$ OTHER
speaker_1: Let's go now. $$$ DETACH
3. speaker_1: Well, I have to go to practice. $$$ OTHER
speaker_1: See you later. $$$ DETACH
"""

refute = """REFUTE - Refusing to move on to a new topic. It is NOT disagreement. It is refusal to discuss something.
Examples:
1.  speaker_1: I’m out $$$ OTHER
speaker_2: You can’t do that, it’s my birthday $$$ REFUTE
2. speaker_1: Well, come and talk to me then. $$$ OTHER
speaker_2: Certainly not. $$$ REFUTE
3. speaker_1: Oh, God, we forgot to cheer for Daddy. $$$ OTHER
speaker_2: Never mind. $$$ REFUTE
4. speaker_1: Tell me about Jane's new boyfriend. $$$ OTHER
speaker_2: Sorry, that's none of your business. $$$ REFUTE"""


rebound = """REBOUND - Questioning the relevance, reliability of the previous statement. Must be interrogative.
Examples:
1.  speaker_1: This conversation needs Allenby. $$$ OTHER
speaker_2: Who are you to say that? $$$ REBOUND
6. speaker_1: It will help us to relax. $$$ OTHER
speaker_2: Do you really think so? $$$ REBOUND
7. speaker_1: I can do 30 push-ups a minute. $$$ OTHER
speaker_2: Really? $$$ REBOUND
8. speaker_1: I won't. $$$ OTHER
speaker_2: So what's the problem? $$$ REBOUND
9. speaker_1: Anything? $$$ OTHER
speaker_2: Do you really believe that we can do anything? $$$ REBOUND"""


rechallenge = """RECHALLENGE - Offering an alternative position. Must be interrogative.
Examples:
1.  speaker_1: Messi is the best. $$$ OTHER
speaker_2: Maybe Pele is the best one? $$$ RECHALLENGE
2. speaker_1: Mary, I really like your new dress. $$$ OTHER
speaker_2: The old one is better, don't you think so? $$$ RECHALLENGE
3. speaker_1: So that we can sit down together and listen to some music. $$$ OTHER
speaker_2: Listen to some music? And who’ll cook dinner? $$$ RECHALLENGE
4. speaker_1: She don’t have any teacher’s pets. $$$ OTHER
speaker_2: Doesn’t every teacher have a teacher’s pet? $$$ RECHALLENGE"""


check = """CHECK - Make the previous speaker repeat something. NB: Only used to ask to repeat something they did not hear.
Examples:
1. speaker_1: And they headed straight into the forest. $$$ OTHER
speaker_2: Straight into the what? $$$ CHECK
2. speaker_1: Our friendship is over. $$$ OTHER
speaker_2: What do you mean? $$$ CHECK
3. speaker_1: Do you know Sally? $$$ OTHER
speaker_2: Sally? $$$ CHECK
4. speaker_1: I think that's impossible! $$$ OTHER
speaker_2: You mean 30 push-ups? $$$ CHECK
5. speaker_1: She taught us that you can do anything that you want to do. $$$ OTHER
speaker_2: Anything? $$$ CHECK
"""


confirm = """CONFIRM - Asking to confirmation the information to make sure they understood correctly.
Examples:
1.  speaker_1: Well, he rang Roman, he rang Roman a week ago. $$$ OTHER
speaker_2: Did he? $$$ CONFIRM
2. speaker_1: It will help us to relax. $$$ OTHER
speaker_2: Do you really think so? $$$ CONFIRM
3. speaker_1: I can do 30 push-ups a minute. $$$ OTHER
speaker_2: Really? $$$ CONFIRM
4. speaker_1: I play goalie myself. $$$ OTHER
speaker_2: Oh, yeah? $$$ CONFIRM
5. speaker_1: Do you believe this? $$$ OTHER
speaker_2: Is he really? $$$ CONFIRM
6. speaker_1: And who’ll cook dinner? $$$ OTHER
speaker_1: Will you? $$$ CONFIRM
7. speaker_1: I found a new way to learn Chinese and it works very well. $$$ OTHER
speaker_2: You did? $$$ CONFIRM
"""

clarify = """CLARIFY - Asking a question to get additional information to understand the previous speaker better. Can be yes-no question.
Examples:
1. speaker_1: I am going to visit Anya tomorrow.
speaker_2: Where does she live? $$$ CLARIFY
1. speaker_1: I am so sad.
speaker_1: Has anything happened? $$$ CLARIFY
2. speaker_1: She really didn’t have any teacher’s pets.
speaker_2: Do you know what she is doing now? $$$ CLARIFY
3. speaker_1: Then, she started writing children’s book.
speaker_2: Have you ever read one of the books? $$$ CLARIFY
5. speaker_1: Why? $$$ CLARIFY
speaker_1: What had you expected? $$$ CLARIFY
6. speaker_1: Do you think she is stupid? $$$ CLARIFY"""


probe = """PROBE - Requesting a confirmation of some information. The speaker themselves speculates about this information. NB: The speaker asks a question to confirm their own idea.
Examples:
1. speaker_1: Then they went to visit Roman. $$$ OTHER
speaker_2: Because Roman lives in Denning Road also? $$$ PROBE
2. speaker_1: You just sit there in a daze, gazing at the monitor and dealing with files and documents. $$$ OTHER
speaker_2: Why don't you give a full play to your energy after work? $$$ PROBE
3. speaker_1: The Filipino kid is a genius. $$$ OTHER
speaker_2: So you'll make the Stars.com deadline, and have us up and running next week? $$$ PROBE
4. speaker_1: Come by any time. $$$ OTHER
speaker_2: Shall I say around ten o'clock? $$$ PROBE
5. speaker_1: They have a big new fancy house. $$$ OTHER
speaker_2: Does Jim make a lot of money? $$$ PROBE
6. speaker_1: You said she was strict. $$$ OTHER
speaker_1: Did she have a lot of rules? $$$ PROBE
"""

declarative = """DECLARATIVE - declarative sentences, contain affirmation or denial of some facts, events, or actions. NB! If a sentence contains an order, a request or a suggesion, it is included into this category.
Examples:
1. I can’t stand him. $$$ DECLARATIVE
2. She then decided to travel alone. $$$ DECLARATIVE
3. You should not do it. $$$ DECLARATIVE
"""

interrogative = """INTERROGATIVE - contains a question of some kind. NB! An interrogative sentence may end with a dot as well as with a question mark.
Examples:
1. Do you like dancing? $$$ INTERROGATIVE
2. What has he done? $$$ INTERROGATIVE
3. You must have been there many times. $$$ INTERROGATIVE
4. I’d like to know what plans you’ve got for tomorrow. $$$ INTERROGATIVE
"""

miscellaneous = """MISCELLANEOUS - sentences (usually short) that are used to express gratitude, manifest emotions, display attention to the previous speaker, draw the speaker's attention
Examples:
1. Thank you! $$$ MISCELLANEOUS
2. Oh my god! $$$ MISCELLANEOUS
3. Great! $$$ MISCELLANEOUS
4. Sounds good. $$$ MISCELLANEOUS
5. Alright. $$$ MISCELLANEOUS
6. Hey there! $$$ MISCELLANEOUS
7. Morning! $$$ MISCELLANEOUS
8. David! $$$ MISCELLANEOUS
"""

command = """COMMAND - a command, a request or an invitation.
Examples:
1. Let’s discuss this later. $$$ COMMAND
2. Let's talk about something else. $$$ COMMAND
3. Could you give me that book? $$$ COMMAND
4. How about going to London? $$$ COMMAND
"""

response = """RESPONSE - a response to a question. Can be positive, negative, or detailed. NB: Must be a response to INTERROGATIVE sentence before.
Examples:
1. speaker_1 What’s the plot of your new movie? $$$ INTERROGATIVE
speaker_2 It’s a story about a policemen who is investigating a series of strange murders. $$$ RESPONSE
2. speaker_1: Does that bother you? $$$ INTERROGATIVE
speaker_2: Not at all. $$$ RESPONSE
3. speaker_1: Have you seen the movie yet? $$$ INTERROGATIVE
speaker_1: I mean, the Avengers. $$$ DECLARATIVE
speaker_2: Yes. $$$ RESPONSE
speaker_2: I have. $$$ DECLARATIVE
"""

agree = """AGREE - Agreement with the information provided. In most cases, the information that the speaker agrees with is new to him. Yes/its synonyms or affirmation.
Examples:
1.  speaker_1: She is the best singer in the world.
speaker_2: Yeah, she is amazing. $$$ AGREE
2. speaker_1: The service at this hotel is excellent.
speaker_2: I totally agree, they're so attentive. $$$ AGREE
3. speaker_1: It's perfect day for a barbecue.
speaker_2: It sure is. $$$ AGREE
4. speaker_1: That sounds interesting.
speaker_2: Yeah. $$$ AGREE
5. speaker_1: Would you like to join us? 
speaker_2: Absolutely. $$$ AGREE
6. speaker_1: I don't like movies that are too slow-paced.
speaker_2: Neither do I, they're too boring.  $$$ AGREE
7. speaker_1: Can you recommend a good sushi place?
speaker_2: Yes, I love the one on 5th Avenue. $$$ AGREE"""

extend = """EXTEND - Adding supplementary or contradictory information to the previous statement. A declarative sentence or phrase (may include and, but, except, on the other hand)
Examples:
1.  speaker_1: I'll pay my own way.
speaker_1: I insist. $$$ EXTEND
2. speaker_1: Men shake hands.
speaker_1: women and children don't. $$$ EXTEND
3. speaker_1: You hit the white ball with your cue.
speaker_1: The white ball hits the colored balls. $$$ EXTEND
4. speaker_1: Lovely day.
speaker_2: Pity I’m on duty. $$$ EXTEND
5. speaker_1: That’s the worst insult you could throw at a Chinese stir fry.
speaker_1: What a disgrace to the wok she fried it in! $$$ EXTEND
6. speaker_1: I would die for a plate of stir fry right now!
speaker_2: Well you can keep the vegetables.  $$$ EXTEND
7. speaker_1: We’Ve always disagreed in a friendly way and we have always resolved our differences.
speaker_2: It was the same when I made this movie. $$$ EXTEND"""

disavow = """DISAVOW - Denial of knowledge or understanding of information
Examples:
1.  speaker_1: Can you recommend a good book to read?
speaker_2: I'm not familiar with any. $$$ DISAVOW
2. speaker_1: Can you tell me how to solve this math problem?
speaker_2: I'm not sure. $$$ DISAVOW
3. speaker_1: Are they dating?
speaker_2: I have no clue about it. $$$ DISAVOW
4. speaker_1: Is the new coffee blend good?
speaker_2: Maybe. $$$ DISAVOW
5. speaker_1: She's a good manager.
speaker_2: I don't know. $$$ DISAVOW
6. speaker_1: The Shining is definitely the best Steven King's work.
speaker_2: I'm not aware of this one.  $$$ DISAVOW
7. speaker_1: We have a test on Monday.
speaker_2: I had no idea about this. $$$ DISAVOW"""

disagree = """DISAGREE - Negative answers or nos to a question or denial of a statement. In most cases, the information that the speaker disagrees with is new to him.
Examples:
1.  speaker_1: She is the best choice for this position.
speaker_2: That's not true. $$$ DISAGREE
2. speaker_1: That movie was so boring, I fell asleep halfway through.
speaker_2: As for me, it was pretty interesting. $$$ DISAGREE
3. speaker_1: Katty is perfect, right?
speaker_2: I don't think so. $$$ DISAGREE
4. speaker_1: Can you help me?
speaker_2: I'm actually very busy right now. $$$ DISAGREE
5. speaker_1: Do you think Beyonce is overrated?
speaker_2: No way, she's a queen! $$$ DISAGREE
6. speaker_1: I think the first movie is the best one.
speaker_2: I prefer the later ones when the story gets darker.  $$$ DISAGREE
7. speaker_1: Harry Potter movies are too dark, aren't they?
speaker_2: They are just appropriate for the tone of the books.  $$$ DISAGREE"""

affirm = """AFFIRM - A positive answer to a question or confirmation of the information provided. Yes/its synonyms or affirmation. The speaker usually confirms the information that he already knew before.
Examples:
1.  speaker_1: David always makes a mess in our room.
speaker_2: Yeah, he does. $$$ AFFIRM
2. speaker_1: Is it true they ended up together?
speaker_2: Their wedding was last month. $$$ AFFIRM
3. speaker_1: Are you moving to Paris?
speaker_2: Yeah, that's true. $$$ AFFIRM
4. speaker_1: Is it going to rain later today?
speaker_2: The forecast says so. $$$ AFFIRM
5. speaker_1: Can I bring my own food into the theater?
speaker_2: You can bring your own snacks. $$$ AFFIRM
6. speaker_1: I heard you're fluent in Spanish.
speaker_2: I grew up speaking it at home.  $$$ AFFIRM
7. speaker_1: You defended our project and got excellent feedback, yeah?
speaker_2: We did it. $$$ AFFIRM"""

resolve = """RESOLVE - A detailed answer to the question asked. This does not include negative or positive answers, as well as expressions of agreement or disagreement, understanding or lack of understanding.
Examples:
1.  speaker_1: Who is your favorite character in Harry Potter?
speaker_2: Hermione Granger. $$$ RESOLVE
2. speaker_1: How do you feel about the grading system?
speaker_2: I think it's fair and necessary to measure student progress. $$$ RESOLVE
3. speaker_1: Do you think online learning is as effective as in-person learning?
speaker_2: It can be just as effective if done properly, but there are some drawbacks. $$$ RESOLVE
4. speaker_1: What is your major?
speaker_2: Linguistics. $$$ RESOLVE
5. speaker_1: What's your opinion on homeschooling?
speaker_2: I think it can work well for some families, but it's not for everyone. $$$ RESOLVE
6. speaker_1: Do you speak Spanish or German?
speaker_2: Actually, both.  $$$ RESOLVE
7. speaker_1: Do you have any tips for packing efficiently?
speaker_2: Roll your clothes instead of folding them. $$$ RESOLVE"""


accept = """ACCEPT - expressing gratitude.
Examples:
1.  speaker_1: I helped you fix your computer.
speaker_2: I'm very grateful for your help. $$$ ACCEPT
2. speaker_1: You are a great mentor to me.
speaker_2: Thank you! $$$ ACCEPT
3. speaker_1: I made dinner for you.
speaker_2: I appreciate this so much. $$$ ACCEPT
4. speaker_1: Congratulations! 
speaker_2: Thank you so much. $$$ ACCEPT
5. speaker_1: I'll drive you to the airport tomorrow morning.
speaker_2: Thank you, that's a huge help! $$$ ACCEPT"""

register = """REGISTER - Repetition of words or phrases after the interlocutor, exclamations, emotional expressions
Examples:
1.  speaker_1: She bought a toy for my little sister.
speaker_2: It's so cute. $$$ REGISTER
2. speaker_1: Thank you very much!
speaker_2: You're welcome. $$$ REGISTER
3. speaker_1: Katy is so beautiful.
speaker_2: Yeah, so beautiful. $$$ REGISTER
4. speaker_1: I've got two tickets for Taylor Swift's concert.
speaker_2: Wow, so cool! $$$ REGISTER
5. speaker_1: He was absolutely right.
speaker_2: Absolutely right. $$$ REGISTER
6. speaker_1: I got promoted to manager today!
speaker_2: Congratulations!  $$$ REGISTER
7. speaker_1: I'm thinking of taking a trip to Europe this summer.
speaker_2: Wow! $$$ REGISTER
8. speaker_1: I failed my driving test again.
speaker_2: Oh, don't worry!  $$$ REGISTER
9. speaker_1: My favorite food is sushi.
speaker_2: Yeah $$$ REGISTER"""

contradict = """CONTRADICT - Contradicting previous information, mostly a speaker already knew before.
Examples:
1.  speaker_1: This book is a classic.
speaker_1: Actually, it's not well-regarded in literary circles. $$$ CONTRADICT
2. speaker_1: Is the music too loud for you?
speaker_1: Not at all. $$$ CONTRADICT
3. speaker_1: Are you a fan of horror movies?
speaker_1: No, I can't stand them. $$$ CONTRADICT
4. speaker_1: Do you like this color?
speaker_2: No, it's too bright for my taste.  $$$ CONTRADICT
5. speaker_1: I believe this is the best restaurant in town.
speaker_2: In fact, the restaurant has terrible reviews and a low rating. $$$ CONTRADICT
6. speaker_1: I have never broken a bone in my body.
speaker_2: You broke your arm when you were a kid.  $$$ CONTRADICT
7. speaker_1: The train is coming at 3 PM.
speaker_2: Actually, it's coming at 4 PM. $$$ CONTRADICT"""

engage = """ENGAGE - Greeting or drawing attention
Examples:
1.  speaker_1: Hey! $$$ ENGAGE
speaker_2: Hi! $$$ ENGAGE
2. speaker_1: Mary!$$$ ENGAGE
3. speaker_1: Good morning! $$$ ENGAGE
speaker_2: Hey, Steve! $$$ ENGAGE
4. speaker_1: Good evening! $$$ ENGAGE
speaker_1: How are you? $$$ ENGAGE
5. speaker_1: Hey, man! $$$ ENGAGE
6. speaker_1: Come on, Tara $$$ ENGAGE"""


enhance = """ENHANCE - Adding details to the previous statement, adding information about time, place, reason, etc.
Examples:
1.  speaker_1: Katty Perry is a great performer. $$$ OTHER
speaker_1: We've been to her show in Las Vegas. $$$ ENHANCE
2. speaker_1: I need to buy a new dress for this evening. $$$ OTHER
speaker_1: It has to be in the disco style. $$$ ENHANCE
3. speaker_1: I think the sun is going to explode soon. $$$ OTHER
speaker_1: It's becoming hotter every year. $$$ ENHANCE
4. speaker_1: I heard a story about a robbery in Amsterdam $$$ OTHER
speaker_1: An old lady was robbed of her dog. $$$ ENHANCE
5. speaker_1: You're his best friend. $$$ OTHER
speaker_1: Since his childhood. $$$ ENHANCE
6. speaker_1: This is her favourite song. $$$ OTHER
speaker_1: I knew this from her feed on VK. $$$ ENHANCE
7. speaker_1: This is the newest theory about implementing new technology to our project. $$$ OTHER
speaker_1: It was developed by Mr.Sadman. $$$ ENHANCE"""

elaborate = """ELABORATE - Clarifying or rephrasing the previous statement or giving examples to it.
Examples:
1.  speaker_1: Then stay away. $$$ OTHER
speaker_1: No one is keeping you from doing that. $$$ ELABORATE
2. speaker_1: I bought some useful staff today. $$$ OTHER
speaker_1: I mean evrything we need for our party. $$$ ELABORATE
3. speaker_1: I heard the public transportation in that city is very good. $$$ OTHER
speaker_1: I heard that it costs not so much in comparison to other cities and still in great condition. $$$ ELABORATE
4. speaker_1: Ariana Grande canceled her tour. $$$ OTHER
speaker_2: We need to refund the tickets. $$$ ELABORATE
5. speaker_1: I'm so disappointed by his indifference. $$$ OTHER
speaker_1: He forgot about my birthday. $$$ ELABORATE"""

acknowledge = """ACKNOWLEDGE - Indicating knowledge or understanding of the information provided
Examples:
1.  speaker_1: This house doesn't belong to him. $$$ OTHER
speaker_2: I knew it. $$$ ACKNOWLEDGE
2. speaker_1: This's my personal task $$$ OTHER
speaker_2:  I see. $$$ ACKNOWLEDGE
3. speaker_1: I'm a fan of horror movies. $$$ OTHER
speaker_2: I'm aware of this fact. $$$ ACKNOWLEDGE
4. speaker_1: She is the most arrogant lady in the city $$$ OTHER
speaker_2: I knew it from the very beginning. $$$ ACKNOWLEDGE
5. speaker_1: I'm in love with her $$$ OTHER
speaker_2: I understand why. $$$ ACKNOWLEDGE
6. speaker_1: Is it the best recipe? $$$ OTHER
speaker_2: I'm sure. $$$ ACKNOWLEDGE
7. speaker_1: He'll buy this castle. $$$ OTHER
speaker_2: I have no doubts about it. $$$ ACKNOWLEDGE
8. speaker_1: Katy is a future pop star $$$ OTHER
speaker_2: I know that for sure. $$$ ACKNOWLEDGE
9. speaker_1: He kissed her at school. $$$ OTHER
speaker_2: I know $$$ ACKNOWLEDGE"""

dict_prompts = {
    'misc':
    {
        'DETACH': detach,
        'REGISTER': register,
        'ENGAGE': engage,
        'ACCEPT': accept
    },
    "decl": {
        'REFUTE': refute,
        'EXTEND': extend,
        'ELABORATE': elaborate,
        'ENHANCE': enhance,
        'AGREE': agree,
        'AFFIRM': affirm,
        'DISAVOW': disavow,
        'ACKNOWLEDGE': acknowledge,
        'DISAGREE': disagree,
        'RESOLVE': resolve,
        'CONTRADICT': contradict
    },
    'questions':
    {
        'CHECK': check,
        'CONFIRM': confirm,
        'CLARIFY': clarify,
        'PROBE': probe,
        'REBOUND': rebound,
        'RECHALLENGE': rechallenge
    },
    'upper_level':
    {
        'DECLARATIVE': declarative,
        'MISCELLANEOUS': miscellaneous,
        'INTERROGATIVE': interrogative,
        'COMMAND': command
        # 'RESPONSE': response
    }
}

count = 0
dict_labels_masked = {}
dict_names = {}
for group, value in dict_prompts.items():
    dict_labels_masked[group] = {}
    for sf, prompt in value.items():
        dict_labels_masked[group][sf] = prompt.replace(sf, f'LABEL_{count}')
        dict_names[f'LABEL_{count}'] = sf
        count += 1

with open('sf_classes.json', 'w') as a:
    json.dump(dict_prompts, a)

with open('sf_classes_masked.json', 'w') as a:
    json.dump({'masked_prompts': dict_labels_masked, 'masks_to_labels': dict_names}, a)
