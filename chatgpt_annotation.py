from revChatGPT.V3 import Chatbot
import pandas as pd
from tqdm import tqdm
import time
from random import randint
import json

api_key = ""
with open('secret.txt') as a:
    api_key = a.read()

detach = """DETACH - Ending the dialogue. Saying goodbye or other similar actions.
Examples:
1. speaker_1: Okay, I have to go - DETACH
speaker_2: Bye-bye - DETACH
2. speaker_1: It's so nice! - OTHER
speaker_2: Sorry, I need to hurry - DETACH
3. speaker_1: Can you help me? - OTHER
speaker_2: I can't talk right now, later - DETACH
3. speaker_1: Good. - OTHER
speaker_1: Let's go now. - DETACH
3. speaker_1: Well, I have to go to practice. - OTHER
speaker_1: See you later. - DETACH"""

refute = """REFUTE - Refusing to move on to a new topic. It is NOT disagreement. It is refusal to discuss something.
Examples:
1.  speaker_1: I’m out - OTHER
speaker_2: You can’t do that, it’s my birthday - REFUTE
2. speaker_1: Well, come and talk to me then. - OTHER
speaker_2: Certainly not. - REFUTE
3. speaker_1: Oh, God, we forgot to cheer for Daddy. - OTHER
speaker_2: Never mind. - REFUTE
4. speaker_1: Tell me about Jane's new boyfriend. - OTHER
speaker_2: Sorry, that's none of your business. - REFUTE"""


rebound = """REBOUND - Questioning the relevance, reliability of the previous statement, often an interrogative sentence, but not always.
Examples:
1.  speaker_1: This conversation needs Allenby. - OTHER
speaker_2: Oh he’s in London. So what can we do? - REBOUND
2. speaker_1: Mary, I really like your new dress. - OTHER
speaker_2: You don't know anything about fashion. - REBOUND
3. speaker_1: I think the sun is going to explode soon. - OTHER
speaker_2: But who are you to say so, you don't know anything about cosmology. - REBOUND
4. speaker_1: I heard a story about a robbery in Amsterdam - OTHER
speaker_2: That was fake news, forget about it. - REBOUND
6. speaker_1: It will help us to relax. - OTHER
speaker_2: Do you really think so? - REBOUND
7. speaker_1: I can do 30 push-ups a minute. - OTHER
speaker_2: Really? - REBOUND
8. speaker_1: I won't. - OTHER
speaker_2: So what's the problem? - REBOUND
9. speaker_1: Anything? - OTHER
speaker_2: Do you really believe that we can do anything? - REBOUND"""


rechallenge = """RECHALLENGE - Offering an alternative position, often an interrogative sentence.
Examples:
1.  speaker_1: Messi is the best. - OTHER
speaker_2: Maybe Pele is the best one? - RECHALLENGE
2. speaker_1: Mary, I really like your new dress. - OTHER
speaker_2: The old one is better, don't you think so? - RECHALLENGE
3. speaker_1: So that we can sit down together and listen to some music. - OTHER
speaker_2: Listen to some music? And who’ll cook dinner? - RECHALLENGE
4. speaker_1: She don’t have any teacher’s pets. - OTHER
speaker_2: Doesn’t every teacher have a teacher’s pet? - RECHALLENGE
5. speaker_1: I love Moschino. - OTHER
speaker_2: Oh, gross, I think Gucci is so much better! - RECHALLENGE"""


check = """CHECK - Getting the previous speaker to repeat an element or the entire statement that the speaker has not heard or understood.
Examples:
1. speaker_1: And they headed straight into the forest. - OTHER
speaker_2: Straight into the what? - CHECK
2. speaker_1: Our friendship is over. - OTHER
speaker_2: What do you mean? - CHECK
3. speaker_1: Do you know Sally? - OTHER
speaker_2: Sally? - CHECK
4. speaker_1: I think that's impossible! - OTHER
speaker_2: You mean 30 push-ups? - CHECK
5. speaker_1: May I turn on the radio then? - OTHER
speaker_2: Turn on the radio? CHECK
6. speaker_1: But let’s go to a disco after dinner. - OTHER
speaker_2: To a disco? - CHECK
7. speaker_1: She taught us that you can do anything that you want to do. - OTHER
speaker_2: Anything? - CHECK"""


confirm = """CONFIRM - Asking for a confirmation of the information received. The speaker wants to make sure that they understood correctly.
Examples:
1.  speaker_1: Well, he rang Roman, he rang Roman a week ago. - OTHER
speaker_2: Did he? - CONFIRM
2. speaker_1: It will help us to relax. - OTHER
speaker_2: Do you really think so? - CONFIRM
3. speaker_1: I can do 30 push-ups a minute. - OTHER
speaker_2: Really? - CONFIRM
4. speaker_1: I play goalie myself. - OTHER
speaker_2: Oh, yeah? - CONFIRM
5. speaker_1: Do you believe this? - OTHER
speaker_2: Is he really? - CONFIRM
6. speaker_1: And who’ll cook dinner? - OTHER
speaker_1: Will you? - CONFIRM
7. speaker_1: I found a new way to learn Chinese and it works very well. - OTHER
speaker_2: You did? - CONFIRM"""

clarify = """CLARIFY - Asking a question to get additional information to understand the previous speaker better; requesting to clarify the information receieved.
Examples:
1. speaker_1: I am going to visit Anya tomorrow. - OTHER
speaker_2: Where does she live? - CLARIFY
2. speaker_1: She really didn’t have any teacher’s pets. - OTHER
speaker_2: Do you know what she is doing now? - CLARIFY
3. speaker_1: Then, she started writing children’s book. - OTHER
speaker_2: Have you ever read one of the books? - CLARIFY
4. speaker_1: I was rather disappointed. - OTHER
speaker_2: Why? - CLARIFY
5. speaker_1: Why? - CLARIFY
speaker_1: What had you expected? - CLARIFY
6. speaker_2: Of course, tomorrow evening there will be a most exciting game. - OTHER
speaker_1: Who plays who? - CLARIFY
7. speaker_1: Right. - OTHER
speaker_1: What present should we give him this time? - CLARIFY
8. speaker_1: What present should we give him this time? - CLARIFY
speaker_1: By the way, how old is he? - CLARIFY
9. speaker_1: You should take the initiative and make some changes first. - OTHER
speaker_2: What should I do then? - CLARIFY"""


probe = """PROBE - Requesting a confirmation of the information necessary to make clear the previous speaker's statement. The speaker themselves speculates about the information that they want to be confirmed.
Examples:
1. speaker_1: Then they went to visit Roman. - OTHER
speaker_2: Because Roman lives in Denning Road also? - PROBE
2. speaker_1: You just sit there in a daze, gazing at the monitor and dealing with files and documents. - OTHER
speaker_2: Why don't you give a full play to your energy after work? - PROBE
3. speaker_1: Great. - OTHER
speaker_2: Is it a two bedroom house? - PROBE
4. speaker_1: The Filipino kid is a genius. - OTHER
speaker_2: So you'll make the Stars.com deadline, and have us up and running next week? - PROBE
5. speaker_1: Come by any time. - OTHER
speaker_2: Shall I say around ten o'clock? - PROBE
6. speaker_1: They have a big new fancy house. - OTHER
speaker_2: Does Jim make a lot of money? - PROBE
7. speaker_1: You said she was strict. - OTHER
speaker_1: Did she have a lot of rules? - PROBE
NB: The speaker asks a question to confirm their own idea."""

declarative = """DECLARATIVE - declarative sentences, contain affirmation or denial of some facts, events, or actions. NB! If a sentence contains an order, a request or a suggesion, it is included into this category.
Examples:
1. I can’t stand him. - DECLARATIVE
2. She then decided to travel alone. - DECLARATIVE
3. You should not do it. - DECLARATIVE"""

interrogative = """INTERROGATIVE - contains a question of some kind. NB! An interrogative sentence may end with a dot as well as with a question mark.
Examples:
1. Do you like dancing? - INTERROGATIVE
2. What has he done? - INTERROGATIVE
3. You must have been there many times. - INTERROGATIVE
4. I’d like to know what plans you’ve got for tomorrow. - INTERROGATIVE"""

miscellaneous = """MISCELLANEOUS - sentences (usually short) that are used to express gratitude, manifest emotions, display attention to the previous speaker, draw the speaker's attention
Examples:
1. Thank you! - MISCELLANEOUS
2. Oh my god! - MISCELLANEOUS
3. Great! - MISCELLANEOUS
4. Sounds good. - MISCELLANEOUS
5. Alright. - MISCELLANEOUS
6. Hey there! - MISCELLANEOUS
7. Morning! - MISCELLANEOUS
8. David! - MISCELLANEOUS"""

command = """COMMAND - a command, a request or an invitation.
Examples:
1. Let’s discuss this later. - COMMAND
2. Let's talk about something else. - COMMAND
3. Could you give me that book? - COMMAND
4. How about going to London? - COMMAND"""

response = """RESPONSE - a response to a question. Can be positive, negative, or detailed.
Examples:
1. speaker_1 What’s the plot of your new movie? - INTERROGATIVE
speaker_2 It’s a story about a policemen who is investigating a series of strange murders. - RESPONSE
2. speaker_1: Does that bother you? - INTERROGATIVE
speaker_2: Not at all. - RESPONSE
3. speaker_1: Have you seen the movie yet? - INTERROGATIVE
speaker_1: I mean, the Avengers. - DECLARATIVE
speaker_2: Yes. - RESPONSE
speaker_2: I have. - DECLARATIVE"""

# Uncomment if you want to add sth to json
# with open('sf_classes.json', 'w') as fp:
#     json.dump(dict_labels, fp)


dict_labels = {
    # 'disagreement':
    # {
    #     'DETACH': detach,
    #     'REFUTE': refute
    # },
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
        'COMMAND': command,
        'RESPONSE': response
    }
}


def get_sf_classes():
    joint_classes = {}
    with open('sf_classes.json') as f:
        sep_classes = json.load(f)
    for key, value in sep_classes.items():
        joint_classes[key] = '\n\n'.join(value.values())
    return sep_classes, joint_classes


def read_dialogs(filename):
    dialogs_label = pd.read_csv(filename, sep='\t')[['dialog_id', 'speaker', 'utterance', 'final_label']]
    dialogs_label['utt_id'] = dialogs_label.groupby('dialog_id').cumcount()
    dialogs_no_label = dialogs_label[['dialog_id', 'speaker', 'utterance', 'utt_id']]
    dialogs_label["full_utterance"] = dialogs_label["speaker"] + ': ' + dialogs_label["utterance"]
    df_grouped = dialogs_label.groupby('dialog_id')["full_utterance"].apply(list)
    dialog_list = ["\n".join(f"{n}. {i}" for n, i in enumerate(dialog, start=1)) for dialog in df_grouped]
    return dialog_list


def get_annotation_step1(joint_classes, dialog):
    prompt = joint_classes['upper_level'] + '\n\nAnnotate this dialog according to the instruction.\n' + dialog
    try:
        chatbot = Chatbot(api_key=api_key)
        response = chatbot.ask(prompt)
        print(response)
    except Exception as e:
        time.sleep(120)
        get_annotation_step1(dialog)
    return response


sep_classes, joint_classes = get_sf_classes()
dialog_list = read_dialogs('dialogs_test.tsv')
get_annotation_step1(joint_classes, dialog_list[0])
