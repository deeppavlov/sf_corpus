# Speech Function Corpus
This repository contains all the scripts for pre- and post-processing the (annotated) dialogs & work with ChatGPT. Annotation pipeline for Toloka can be found [here](https://github.com/deeppavlov/toloka_tools). Everything for Toloka front-end (and the structure of instructions) can be found [here](https://github.com/deeppavlov/discourse_toloka/tree/feat/full).  Our notion with all the useful text info is [here](https://faithful-viburnum-b94.notion.site/Speech-Functions-906c01ea3d63424d8c754713fb43782f).

Use `make_jsons.py` to make json files `sf_classes.json` and `sf_classes_masked.json` from you hand-written prompts (if you make any changes to the initial prompts). You may also change the desired structure of classes (what upper level includes, what questions include, etc.) there. 

Use `chatgpt_annotation.py` to perform annotation. Note that you need an API token for that. Specify it in separate file `secret.txt` or in the beginning of `chatgpt_annotation.py` file manually.
