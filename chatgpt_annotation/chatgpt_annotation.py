import os
from revChatGPT.V3 import Chatbot 
import pandas as pd
from tqdm import tqdm
import time
from random import randint
import json
import typing
import re
import sys

api_key = ""
with open('secret.txt') as a:
    api_key = a.read()


def get_sf_classes(filename: str, masked: bool = False) -> typing.Union[
        typing.Tuple[typing.Dict[str, typing.Dict[str, str]], typing.Dict[str, str]],
        typing.Tuple[typing.Dict[str, str], typing.Dict[str, typing.Dict[str, str]], typing.Dict[str, str]]]:
    """Creates dictionaries with speech function (sf) prompts in separate and joint format.

    Args:
        filename: Path to json file with sf classes and prompts for each of them.
        masked: If True, SF labels are masked as LABEL_{NUM}, and the function is expected to return a dictionary 
        of masks-labels correspondence as well

    Returns:
        A tuple (sep_classes, joint_classes) or (mask_to_label, sep_classes, joint_classes) depending on masked parameter.
        mask_to_label is a dictionary with entrues for each mask and the corresponding underlying label.
        sep_classes is a nested dictionary with separate entries for each of sf classes and separate prompt for each sfs.
        joint_classes is a dictionary with entries for each of sf classes, containing joint prompts for each sf.
    """

    joint_classes = {}
    with open(filename) as f:
        filetext = json.load(f)
    if masked:
        sep_classes = filetext['masked_prompts']
        for key, value in sep_classes.items():
            joint_classes[key] = '\n\n'.join(value.values())
        mask_to_label = filetext['masks_to_labels']
        return mask_to_label, sep_classes, joint_classes
    else:
        for key, value in filetext.items():
            joint_classes[key] = '\n\n'.join(value.values())
        return filetext, joint_classes


def get_dialogs(filename: str) -> typing.Tuple[pd.DataFrame, typing.Dict[str, typing.List[str]]]:
    """Gets dialogs from a given pre-annotated file.

    Args:
        filename: Path to tsv file with annotated dialogs.

    Returns:
        A tuple (dialogs_label, dialog_dict).
        dialogs_label is a dataframe with dialog information and columns ['dialog_id', 'speaker', 'utterance', 'final_label',
        'utt_id', 'full_utterance']
        dialog_dict is a dictionary with dialog ids as keys and dialog texts as values.
    """

    dialog_dict = {}
    dialogs_label = pd.read_csv(filename, sep='\t')[['dialog_id', 'speaker', 'utterance', 'final_label']]
    dialogs_label['utt_id'] = dialogs_label.groupby('dialog_id').cumcount()
    dialogs_label["full_utterance"] = dialogs_label["speaker"] + ': ' + dialogs_label["utterance"]
    df_grouped = dialogs_label.groupby('dialog_id')["full_utterance"].apply(list).to_dict()
    for id, dialog in df_grouped.items():
        dialog_dict[str(id)] = f"\n".join(f"{n}. {i}" for n, i in enumerate(dialog, start=1))
    return dialogs_label, dialog_dict


def get_annotation(joint_classes: typing.Dict[str, str], dialog: str, print_all: bool = False) -> str:
    """Concatenates prompts, specific instructions and dialogs and sends requests to ChatGPT API to get an annotated dialog.

    Args:
        joint_classes: A dictionary of prompts with separate entry for each class / step of annotation.
        dialog: string representation of a non-annotated dialog.
        print_all: if True, print all output (chatGPT generation results after each step).

    Returns:
      ChatGPT response with annotation.
    """

    if print_all:
        print_to = sys.stdout
    else:
        print_to = None
    prompt = joint_classes['upper_level'] + \
        '\n\nSTEP 1. Annotate this dialog according to the instruction. Only give utterances and labels. Use $$$ to separate utterances and labels.\n' + dialog
    chatbot = Chatbot(api_key=api_key)
    response_upper = chatbot.ask(prompt)
    # to get rid of all extra chatGPT stuff that may be generated before the response
    response_upper = '1.' + re.split(r'\b1\.', response_upper, maxsplit=1)[1]
    print(response_upper, file=print_to)
    print('response_upper done')
    chatbot = Chatbot(api_key=api_key)
    prompt_questions = joint_classes['questions'] + \
        '\n\nSTEP 2. Annotate all INTERROGATIVE utterances as CHECK, CONFIRM, CLARIFY, PROBE, REBOUND, RECHALLENGE. Leave DECLARATIVE, COMMAND, MISCELLANEOUS as they are.\n' + \
        response_upper + '\nReturn only the dialog in annotated format. '
    response_questions = chatbot.ask(prompt_questions)
    print(response_questions, file=print_to)
    print('response_questions done')
    chatbot = Chatbot(api_key=api_key)
    prompt_misc = joint_classes['misc'] + \
        '\n\nSTEP 3. Annotate all MISCELLANEOUS utterances as DETACH, ENGAGE, ACCEPT, REGISTER. Leave all other sentences as they are.\n' + \
        response_questions + '\nReturn only the dialog in annotated format. '
    print(prompt_misc)
    response_misc = chatbot.ask(prompt_misc)
    print(response_misc, file=print_to)
    print('response_misc done')
    chatbot = Chatbot(api_key=api_key)
    prompt_decl = joint_classes['decl'] + \
        '\n\nSTEP 4. Annotate all DECLARATIVE utterances as REFUTE, EXTEND, CONTRADICT, ELABORATE, ENHANCE, AGREE, AFFIRM, DISAVOW, ACKNOWLEDGE, DISAGREE, RESOLVE. Leave all other sentences as they are. All DECLARATIVE labels must be replaced with REFUTE, EXTEND, ELABORATE, ENHANCE, AGREE, AFFIRM, DISAVOW, ACKNOWLEDGE, DISAGREE, RESOLVE. \n' + response_misc + '\nReturn only the dialog in annotated format. '
    response_fin = chatbot.ask(prompt_decl)
    print(response_fin, file=print_to)
    response_fin = [x for x in response_fin.split('\n') if x]
    print('response ready')
    return response_fin


def write_annotations(sf_file: str, dialogs_file: str, output_file_name: str, print_all: bool = False) -> None:
    """Creates enumerated txt files with final annotation for each dialog. Also creates one tsv file with gold annotation + ChatGPT labels.

    txt files are created in folder dialog_responses/ and named according to their number during processing.

    Args:
        sf_file: Path to json file with sf prompts.
        dialogs_file: Path to tsv file with dialogs.
        output_file_name: Output tsv file name.
    """

    sep_classes, joint_classes = get_sf_classes(sf_file)
    dialogs_label, dialog_list = get_dialogs(dialogs_file)
    df_dummy = pd.DataFrame({'dialog_id': pd.Series(dtype='int'),
                            'utt_id': pd.Series(dtype='int'),
                             'gen_label': pd.Series(dtype='str')})
    i = 0
    for id, dialog in tqdm(list(dialog_list.items())[1:2]):  # set up to which dialog to annotate
        # NB: if the file response is already in dialog_responses folder, you have to delete it to reannotate
        if os.path.isfile('./dialog_responses/' + str(i)):
            with open('./dialog_responses/' + str(i)) as f:
                response = list(map(lambda x: x[:-1], f.readlines()))
        else:
            response = get_annotation(joint_classes, dialog, print_all=print_all)
            # response = get_annotation_step1(joint_classes, dialog, masks_to_labels)
            assert len(response) == len(dialog.split('\n')
                                        ), f'lens do not match for {str(dialog)} and ChatGPT {str(response)}.\n SOMETHING IS MISSING.'
            with open('./dialog_responses/' + str(i), 'w') as f:
                for line in response:
                    f.write(line + '\n')
        i += 1
        utt_ids = [int(x.split('. speaker')[0]) - 1 for x in response]
        dialog_ids = [int(id)] * len(response)
        labels = [x.split(' $$$ ')[1] for x in response]
        df_to_merge = pd.DataFrame(
            {'dialog_id': dialog_ids,
             'utt_id': utt_ids,
             'gen_label': labels
             })
        df_dummy = pd.concat([df_dummy, df_to_merge])
    df_final = df_dummy.merge(dialogs_label, on=['dialog_id', 'utt_id'], how="outer")
    df_final.to_csv(output_file_name, sep='\t')


write_annotations('sf_classes.json', 'dialogs_test.tsv', 'test.tsv', print_all=True)


# FOR NOW IGNORE THIS
# def get_annotation_step1(joint_classes: typing.Dict[str, str], dialog: str, masks_to_labels: typing.Dict[str, str]) -> str:
#     """Preprocesses open goals by leaving the first word and renaming some of them.

#     Used for preprocessing goals from open goal annotation datasets.
#     Simplified for now, more preprocessing tbd later.

#     Args:
#         goal: A goal.

#     Returns:
#       A preprocessed goal.
#     """
#     with open('sf_classes_masked.json') as f:
#         filetext = json.load(f)
#     misc = [x.split(' -')[0] for x in filetext['masked_prompts']['misc'].values()]
#     decl = [x.split(' -')[0] for x in filetext['masked_prompts']['decl'].values()]
#     questions = [x.split(' -')[0] for x in filetext['masked_prompts']['questions'].values()]
#     prompt = joint_classes['upper_level'] + \
#         '\n\nAnnotate this dialog according to the instruction. Only give utterances and labels. Use $$$ to separate utterances and labels.\n' + dialog
#     chatbot = Chatbot(api_key=api_key)
#     response_fin = []
#     response_upper = chatbot.ask(prompt)
#     print(response_upper)
#     print('response_upper done')
#     response_upper = '1.' + re.split(r'\b1\.', response_upper, maxsplit=1)[1]
#     for sent in response_upper.split('\n'):
#         if 'CLASS_4' in sent:
#             response_fin.append(sent)
#     ann_quest = response_upper.replace(' $$$ CLASS_1', ' $$$ DO NOT ANNOTATE THIS SENTENCE').replace(
#         ' $$$ CLASS_2', ' $$$ DO NOT ANNOTATE THIS SENTENCE').replace(' $$$ CLASS_4', ' $$$ DO NOT ANNOTATE THIS SENTENCE').replace(' $$$ CLASS_3', ' $$$ ANNOTATE_THIS')
#     ann_decl = response_upper.replace(' $$$ CLASS_2', ' $$$ DO NOT ANNOTATE THIS SENTENCE').replace(
#         ' $$$ CLASS_3', ' $$$ DO NOT ANNOTATE THIS SENTENCE').replace(' $$$ CLASS_4', ' $$$ DO NOT ANNOTATE THIS SENTENCE').replace(' $$$ CLASS_1', ' $$$ ANNOTATE_THIS')
#     ann_misc = response_upper.replace(' $$$ CLASS_1', ' $$$ DO NOT ANNOTATE THIS SENTENCE').replace(
#         ' $$$ CLASS_3', ' $$$ DO NOT ANNOTATE THIS SENTENCE').replace(' $$$ CLASS_4', ' $$$ DO NOT ANNOTATE THIS SENTENCE').replace(' $$$ CLASS_2', ' $$$ ANNOTATE_THIS')
#     qu_joint = ', '.join(questions)
#     prompt_questions = joint_classes['questions'] + \
#         f'\nYou have to annotate this dialog.\n' + \
#         ann_quest + \
#         f'\nAnnotate ONLY sentences ending with $$$ ANNOTATE_THIS with suitable label from {qu_joint}. Leave sentences with $$$ DO NOT ANNOTATE THIS SENTENCE as they are.\n'
#     chatbot = Chatbot(api_key=api_key)
#     response_questions = chatbot.ask(prompt_questions)
#     for sent in response_questions.split('\n'):
#         if any(sf in sent for sf in questions):
#             response_fin.append(sent)
#     print(ann_quest)
#     print(response_questions)
#     print('response_questions done')
#     misc_joint = ', '.join(misc)
#     prompt_misc = joint_classes['misc'] + \
#         f'\nYou have to annotate this dialog.\n' + \
#         ann_misc + \
#         f'\nAnnotate ONLY sentences ending with $$$ ANNOTATE_THIS with suitable label from {misc_joint}. Leave sentences with $$$ DO NOT ANNOTATE THIS SENTENCE as they are.\n'
#     chatbot = Chatbot(api_key=api_key)
#     response_misc = chatbot.ask(prompt_misc)
#     for sent in response_questions.split('\n'):
#         if any(sf in sent for sf in misc):
#             response_fin.append(sent)
#     print(ann_misc)
#     print(response_misc)
#     print('response_misc done')
#     decl_joint = ', '.join(decl)
#     prompt_decl = joint_classes['decl'] + \
#         f'\nYou have to annotate this dialog.\n' + \
#         ann_decl + \
#         f'\nAnnotate ONLY sentences ending with $$$ ANNOTATE_THIS with suitable label from {decl_joint}. Leave sentences with $$$ DO NOT ANNOTATE THIS SENTENCE as they are.\n'
#     chatbot = Chatbot(api_key=api_key)
#     response_decl = chatbot.ask(prompt_decl)
#     print(ann_decl)
#     print(response_decl)
#     for sent in response_decl.split('\n'):
#         if any(sf in sent for sf in decl):
#             response_fin.append(sent)
#     print(response_fin)
#     for key in reversed(masks_to_labels.keys()):
#         response_fin = set([res.replace(f'{key}', f'{masks_to_labels[key]}') for res in response_fin])
#     # response_fin = [x for x in response_fin.split('\n') if x]
#     print(response_fin)
#     print('response ready done')
#     return response_fin
# masks_to_labels, sep_classes, joint_classes = get_sf_classes('sf_classes_masked.json')
