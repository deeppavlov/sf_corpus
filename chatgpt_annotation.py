from revChatGPT.V3 import Chatbot
import pandas as pd
from tqdm import tqdm
import time
from random import randint
import json

api_key = ""
with open('secret.txt') as a:
    api_key = a.read()


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
