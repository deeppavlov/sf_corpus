from revChatGPT.V3 import Chatbot
import pandas as pd
from tqdm import tqdm
import time
from random import randint
import json
import typing

api_key = ""
with open('secret.txt') as a:
    api_key = a.read()


def get_sf_classes(filename: str) -> typing.Tuple[typing.Dict[str, typing.Dict[str, str]], typing.Dict[str, str]]:
    """Creates dictionaries with speech function (sf) prompts in separate and joint format.

    Args:
        filename: Path to json file with sf classes and prompts for each of them.

    Returns:
        A tuple (sep_classes, joint_classes).
        sep_classes is a nested dictionary with separate entries for each of sf classes and separate prompt for each sfs.
        joint_classes is a dictionary with entries for each of sf classes, containing joint prompts for each sf.
    """

    joint_classes = {}
    with open(filename) as f:
        sep_classes = json.load(f)
    for key, value in sep_classes.items():
        joint_classes[key] = '\n\n'.join(value.values())
    return sep_classes, joint_classes


def get_dialogs(filename: str) -> typing.Dict[str, typing.List[str]]:
    """Gets dialogs from a given pre-annotated file.

    Args:
        filename: Path to tsv file with annotated dialogs.

    Returns:
        A dictionary with dialog ids as keys and dialogs (represented as lists) as values.
    """

    dialog_dict = {}
    dialogs_label = pd.read_csv(filename, sep='\t')[['dialog_id', 'speaker', 'utterance', 'final_label']]
    dialogs_label['utt_id'] = dialogs_label.groupby('dialog_id').cumcount()
    dialogs_no_label = dialogs_label[['dialog_id', 'speaker', 'utterance', 'utt_id']]
    dialogs_label["full_utterance"] = dialogs_label["speaker"] + ': ' + dialogs_label["utterance"]
    df_grouped = dialogs_label.groupby('dialog_id')["full_utterance"].apply(list).to_dict()
    for id, dialog in df_grouped.items():
        dialog_dict[str(id)] = f"\n".join(f"{n}. {i}" for n, i in enumerate(dialog, start=1))
    return dialogs_label, dialog_dict


def get_annotation_step1(joint_classes: typing.Dict[str, str], dialog: str) -> str:
    """Preprocesses open goals by leaving the first word and renaming some of them.

    Used for preprocessing goals from open goal annotation datasets.
    Simplified for now, more preprocessing tbd later.

    Args:
        goal: A goal.

    Returns:
      A preprocessed goal.
    """

    prompt = joint_classes['upper_level'] + \
        '\n\nAnnotate this dialog according to the instruction. Only give utterances and labels.\n' + dialog
    try:
        chatbot = Chatbot(api_key=api_key)
        response_upper = chatbot.ask(prompt)
        response_upper = '1.' + response_upper.split('1.')[1]
        print(response_upper)
    except Exception as e:
        time.sleep(120)
        get_annotation_step1(dialog)
    print('step_1 done')
    chatbot = Chatbot(api_key=api_key)
    prompt_questions = joint_classes['questions'] + \
        '\n\nAnnotate all INTERROGATIVE utterances as CHECK, CONFIRM, CLARIFY, PROBE, REBOUND, RECHALLENGE. Leave DECLARATIVE, COMMAND, MISCELLANEOUS, RESPONSE as they are.\n' + response_upper
    response_questions = chatbot.ask(prompt_questions)
    response_questions = response_questions.split('\n')
    print(response_questions)
    return response_questions


sep_classes, joint_classes = get_sf_classes('sf_classes.json')
dialogs_label, dialog_list = get_dialogs('dialogs_test.tsv')
df_dummy = pd.DataFrame(columns=['dialog_id', 'utt_id', 'gen_label'])
for id, dialog in list(dialog_list.items())[:2]:
    response = get_annotation_step1(joint_classes, dialog)
    assert len(response) == len(dialog.split('\n')), f'lens do not match for {str(dialog)} and ChatGPT {str(response)}'
    utt_ids = [x.split('. speaker')[0] for x in response]
    dialog_ids = [id] * len(dialog)
    labels = [x.split(' $$$ ')[1] for x in response]
    df_to_merge = pd.DataFrame(
        {'dialog_id': dialog_ids,
         'utt_id': utt_ids,
         'gen_label': labels
         })
    df_dummy = pd.concat([df_dummy, df_to_merge])
df_final = df_dummy.merge(dialogs_label, how="outer")
df_final.to_csv('test.tsv', sep='\t')
