# -*- coding: UTF-8 -*-
#!/usr/bin/env python3


"""
process_long_text.py

This script is a customizable example that allows you to work on large texts.

Process:

    1. Create a custom preprocess text function
    (sentences tokenization and clean processes)
    2. Create a pipeline with two components:
    - custom_ner: an intermediate pipeline apply ner with batch
     method Language.pipe() and recompute entities offsets in context of all text;
    - spacy_fishing: apply disambiguation and linking on all preprocess text (to keep more context as possible);
    3. Apply complete pipeline on text and retrieve results.
"""

import spacy
from spacy import Language
from spacy.tokens import Doc


def open_file(file_name: str) -> str:
    with open(file_name, mode="r", encoding="utf-8") as f:
        return f.read()


def text_preprocessor(text: str) -> list:
    return [sentence.strip() for sentence in text.split("\n") if sentence != ""]


@Language.factory("custom_ner", default_config={
    "model_name": "",
    "sentences_to_process": []
})
class CustomNer:
    def __init__(self,
                 nlp: Language,
                 name: str,
                 model_name: str,
                 sentences_to_process: list):
        self.nlp = nlp
        self.pipeline_ner = spacy.load(model_name, disable=["tok2vec", "morphologizer", "parser", "senter", "attribute_ruler", "lemmatizer"])
        self.sentences = sentences_to_process

    def __call__(self, doc: Doc):
        start_sentence = 0
        spans = []
        for sent in self.pipeline_ner.pipe(self.sentences):
            # add 1 char that correspond to space added in
            # sentences concatenation (" ".join())
            end_sentence = start_sentence + len(sent.text) + 1
            # recompute named entities characters offsets
            for ent in sent.ents:
                start = start_sentence + ent.start_char
                end = start + len(ent.text)
                spans.append(doc.char_span(start, end, label=ent.label_))
            start_sentence = end_sentence

        doc.set_ents(spans)

        return doc


if __name__ == '__main__':
    # Set model, language, file that contains text to analyze
    model = "en_core_web_sm"
    language = "en"
    filename = "data/text_en.txt"

    # Apply preprocessing
    sentences = text_preprocessor(open_file(filename))
    huge_text = " ".join(sentences)

    # Create pipeline
    huge_pipeline_linking = spacy.blank(language)
    huge_pipeline_linking.add_pipe('custom_ner', config={"model_name": model, "sentences_to_process": sentences})
    huge_pipeline_linking.add_pipe('entityfishing', config={"language": language})

    # Apply pipeline
    doc_linked = huge_pipeline_linking(huge_text)

    # Test
    for ent in doc_linked.ents:
        print(ent.text, ent.label_, ent._.kb_qid)

