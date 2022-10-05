# -*- coding: UTF-8 -*-

"""entity_fishing_linker.py

SpaCy wrapper to call Entity-fishing API
as disambiguation and entity linking component.
"""

import requests
import concurrent.futures
import json
import logging

from email import iterators
from typing import List, Tuple

from spacy import util
from spacy.language import Language
from spacy.tokens import Doc, Span


@Language.factory("entityfishing", default_config={
    "api_ef_base": "https://cloud.science-miner.com/nerd/service",
    "language": "en",
    "extra_info": False,
    "filter_statements": [],
    "verbose": False
})
class EntityFishing:
    """EntityFishing component for spaCy pipeline."""

    def __init__(self,
                 nlp: Language,
                 name: str,
                 api_ef_base: str,
                 language: str,
                 extra_info: bool,
                 filter_statements: list,
                 verbose: bool):
        """
        `EntityFishing` main class component.

        Note:
            Show default config for default attributes values.

        Parameters:
            api_ef_base (str): describes url of the entity-fishing API used.
            language (str): matches the language of the resources to
            be disambiguated (matches the language model for the NER task).
            extra_info (bool): attach extra information to spans as normalised term,
            description, others knowledge base ids.
            filter_statements (list): filter others KB ids
            that relies on QID  eg. ['P214', 'P244'].
            verbose (bool): display logging messages.

        Attributes:
            api_ef_base (str): cf. `api_ef_base` in parameters section.
            language (dict): cf. `language` in parameters section.
            prepare the language argument for the query.
            wikidata_url_base (str): wikidata base url (to concatenate QID identifiers).
            flag_extra (bool): cf. `extra_info` in parameters section.
            filter_statements (list): cf. `filter_statements` in parameters section.
            verbose (bool): cf. `verbose` in parameters section.
        """
        if not api_ef_base.endswith("/"):
            api_ef_base += "/"
        self.api_ef_base = api_ef_base
        self.language = dict(lang=language)
        self.wikidata_url_base = "https://www.wikidata.org/wiki/"

        self.flag_extra = extra_info
        self.filter_statements = filter_statements
        self.verbose = verbose

        # Set doc extensions to attaches raw response from Entity-Fishing API to doc
        Doc.set_extension("annotations", default={}, force=True)
        Doc.set_extension("metadata", default={}, force=True)

        # Set spans extensions to enhance spans with new information
        # come from Wikidata knowledge base.
        # default spans :
        Span.set_extension("kb_qid", default=None, force=True)
        Span.set_extension("wikipedia_page_ref", default=None, force=True)
        Span.set_extension("url_wikidata", default=None, force=True)
        Span.set_extension("nerd_score", default=None, force=True)

        # spans if extra_info set to True
        Span.set_extension("normal_term", default=None, force=True)
        Span.set_extension("description", default=None, force=True)
        Span.set_extension("src_description", default=None, force=True)
        Span.set_extension("other_ids", default=None, force=True)

    @staticmethod
    def generic_client_batch(method: str,
                             url_batch: List[str],
                             verbose: bool,
                             params: dict = None,
                             files_batch: List[dict] = None) -> List[requests.Response]:
        """
        It takes a list of urls and a list of files, and it sends a request to each url with the
        corresponding file

        :param method: str,
        :type method: str
        :param url_batch: a list of urls to send requests to
        :type url_batch: List[str]
        :param verbose: if True, the client will print out the status of each request
        :type verbose: bool
        :param params: dict = None,
        :type params: dict
        :param files_batch: a list of dictionaries, each dictionary containing the file to be annotated
        :type files_batch: List[dict]
        :return: A list of responses.
        """
        if params is None:
            params = {}
        if files_batch is None:
            files_batch = [{} for url in url_batch]

        def load_url(type_url, type_files):
            if method == "POST":
                return requests.post(
                    url=type_url,
                    headers={
                        "Accept": "application/json"
                    },
                    files=type_files,
                    params=params)
            else:
                return requests.get(
                    url=type_url,
                    headers={
                        "Accept": "application/json"
                    },
                    files=type_files,
                    params=params)

        response_batch = []
        resp_err, resp_ok = 0, 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_url = {executor.submit(
                load_url, type_url, type_files): (type_url, type_files) for type_url, type_files in zip(url_batch, files_batch)}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    response_batch.append(future.result())
                except Exception as exc:
                    resp_err = resp_err + 1
                else:
                    resp_ok = resp_ok + 1

        def client_log(msg: str) -> None:
            if verbose:
                logging.warning(msg)

        # Manage response status code :
        # cf. https://nerd.readthedocs.io/en/latest/restAPI.html#response-status-codes
        for idx, response in enumerate(response_batch):
            if response.status_code == 400:
                client_log(f"Request {idx}. Wrong request, missing parameters, "
                           "missing header, text too short (<= 5 characters). (400)")
            elif response.status_code == 500:
                client_log(
                    f"Request {idx}. Entity-Fishing API service seems broken. (500)")
            elif response.status_code == 404:
                client_log(
                    f"Request {idx}. Property was not found in request body. (404)")
            elif response.status_code == 406:
                client_log(
                    f"Request {idx}. Language is not supported by Entity-Fishing. (406)")

        return response_batch

    @staticmethod
    def process_response(response: requests.models.Response) -> Tuple[dict, dict]:
        """
        It takes a response object from the `requests` library and returns a tuple of two dictionaries.
        The first dictionary is the JSON response from the API, and the second dictionary contains
        metadata about the response

        :param response: The response object returned by the requests library
        :type response: requests.models.Response
        :return: A tuple of two dictionaries.
        """
        try:
            res_json = response.json()
        except requests.exceptions.JSONDecodeError:
            res_json = {}

        metadata = {
            "status_code": response.status_code,
            "reason": response.reason,
            "ok": response.ok,
            "encoding": response.encoding
        }

        return res_json, metadata

    @staticmethod
    def prepare_data(text: str, terms: str, entities: list, language: dict, full: bool = False) -> dict:
        """
        > The function takes in a text, a list of entities, a language dictionary and a boolean value.
        It then returns a dictionary with a key called "query" and a value that is a JSON object

        :param text: The text to be analyzed
        :type text: str
        :param terms: the terms to be searched for
        :type terms: str
        :param entities: list of entities in the text
        :type entities: list
        :param language: the language of the text
        :type language: dict
        :param full: if True, the response will contain the full text of the article, defaults to False
        :type full: bool (optional)
        :return: A dictionary with a key of "query" and a value of a json object.
        """
        return {
            "query": json.dumps({
                "text": text,
                "shortText": terms,
                "language": language,
                "entities": [
                    {
                        "rawName": ent.text,
                        "offsetStart": ent.start_char,
                        "offsetEnd": ent.end_char,
                    } for ent in entities
                ],
                "mentions": [],
                "customisation": "generic",
                "full": "true" if full else "false"
            }, ensure_ascii=False)
        }

    def updated_entities(self, doc: Doc, response: list) -> None:
        """
        > The function `updated_entities` takes a `Doc` object and a list of entities as input. It then
        iterates over the list of entities and updates the `Doc` object with the information contained
        in the list of entities

        :param doc: the document to be processed
        :type doc: Doc
        :param response: the response from the NERD API
        :type response: list
        """
        for entity in response:
            try:
                span = doc.char_span(start_idx=entity['offsetStart'],
                                     end_idx=entity['offsetEnd'])
                try:
                    span._.kb_qid = str(entity['wikidataId'])
                    span._.url_wikidata = self.wikidata_url_base + span._.kb_qid
                except KeyError:
                    pass
                try:
                    span._.wikipedia_page_ref = str(entity["wikipediaExternalRef"])
                    # if flag_extra : search other info on entity
                    # => attach extra entity info to span
                    if self.flag_extra:
                        self.look_extra_informations_on_entity(span, entity)
                except KeyError:
                    pass
                try:
                    span._.nerd_score = entity['confidence_score']
                except KeyError:
                    pass
            except AttributeError:
                pass

    # ~ Entity-fishing call service methods ~:
    def concept_look_up_batch(self, wiki_id_batch: str) -> List[requests.Response]:
        """
        > This function takes a list of wikipedia ids and returns a list of responses from the API

        :param wiki_id_batch: a list of wikipedia ids
        :type wiki_id_batch: str
        :return: A list of requests.Response objects.
        """
        url_concept_lookup_batch = [
            self.api_ef_base + "kb/concept/" + wiki_id for wiki_id in wiki_id_batch]
        return self.generic_client_batch(method="GET",
                                         url_batch=url_concept_lookup_batch,
                                         params=self.language,
                                         verbose=self.verbose)

    def disambiguate_text_batch(self, files_batch: List[dict]) -> List[requests.Response]:
        """
        > The function `disambiguate_text_batch` takes a list of dictionaries as input, where each
        dictionary contains the text to be disambiguated and the corresponding language. The function
        returns a list of responses, where each response contains the disambiguated text

        :param files_batch: a list of dictionaries, each dictionary containing the following keys:
        :type files_batch: List[dict]
        :return: A list of responses.
        """
        url_disambiguate = self.api_ef_base + "disambiguate"
        url_disambiguate_batch = [url_disambiguate for file in files_batch]
        return self.generic_client_batch(method='POST',
                                         url_batch=url_disambiguate_batch,
                                         files_batch=files_batch,
                                         verbose=self.verbose)

    def look_extra_informations_on_entity(self, span: Span, res_desc: dict) -> None:
        """
        It takes a span and a dictionary of information about the entity, and adds the information to
        the span

        :param span: The Span object that the extension is being applied to
        :type span: Span
        :param res_desc: the result of the query to Wikidata
        :type res_desc: dict
        """
        # normalised term name
        try:
            span._.normal_term = res_desc['preferredTerm']
        except KeyError:
            pass
        # description and source description (filter by language)
        try:
            span._.description = res_desc['definitions'][0]["definition"]
            span._.src_description = res_desc['definitions'][0]["source"]
        except KeyError:
            pass
        except IndexError:
            pass
        # others identifiers attach to QID
        # in Wikidata KB with filter properties or not
        try:
            ids = []
            for content in res_desc['statements']:
                new_id = {
                    k: content[k] for k in ['propertyName',
                                            'propertyId',
                                            'value']
                }
                if len(self.filter_statements) != 0:
                    if content['propertyId'] in self.filter_statements:
                        ids.append(new_id)
                else:
                    ids.append(new_id)

            span._.other_ids = ids
        except KeyError:
            pass
        except requests.exceptions.JSONDecodeError:
            pass

    def main_disambiguation_process_batch(self,
                                          text_batch: List[str],
                                          terms_batch: List[str],
                                          entities_batch: List[list]) -> List[Tuple[dict, dict, list]]:
        """
        It takes a batch of text, terms and entities, and returns a batch of disambiguated entities

        :param text_batch: a list of strings, each string is a text to be disambiguated
        :type text_batch: List[str]
        :param terms_batch: a list of strings, each string is a list of terms separated by a space
        :type terms_batch: List[str]
        :param entities_batch: a list of lists of entities, where each entity is a dictionary with the
        following keys:
        :type entities_batch: List[list]
        :return: A list of tuples, each tuple containing the response, metadata, and entities_enhanced.
        """
        data_to_post_batch = [self.prepare_data(text=text,
                                                terms=terms,
                                                entities=entities,
                                                language=self.language,
                                                full=self.flag_extra) for text, terms, entities in zip(text_batch, terms_batch, entities_batch)]
        reqs = self.disambiguate_text_batch(files_batch=data_to_post_batch)

        response_tuples = []
        for req in reqs:
            res, metadata = self.process_response(response=req)
            try:
                entities_enhanced = res['entities']
            except KeyError:
                entities_enhanced = []
            response_tuples.append((res, metadata, entities_enhanced))
        return response_tuples

    def process_single_doc_after_call(self, doc: Doc, result_from_ef_text) -> Doc:
        """
        - The function takes a document and a list of entities from the Entity-Fishing service.
        - It then checks if there are any entities in the document that were not disambiguated by the
        Entity-Fishing service.
        - If there are, it passes the text of these entities to the Entity-Fishing service again, but
        this time without the text of the document.
        - It then merges the results of the two calls to the Entity-Fishing service and attaches the
        information from the Entity-Fishing service to the entities in the document

        :param doc: The document to be processed
        :type doc: Doc
        :param result_from_ef_text: a list of three elements:
        :return: A list of dictionaries, each dictionary contains the information of a single entity.
        """
        entities_from_text = result_from_ef_text[2]

        # 1a. Attach raw response (with text method in Entity-Fishing service) to doc
        if len(result_from_ef_text[0]) > 0:
            doc._.annotations["disambiguation_text_service"] = result_from_ef_text[0]

        doc._.metadata["disambiguation_text_service"] = result_from_ef_text[1]

        # 2 .Because some named entities have not been disambiguated,
        # create a list with these unrelated entities ("nil clustering").
        # Pass them back in Entity-fishing without the text but with all
        # the named entities surrounding these entities, to create a context
        # of neighboring terms.
        # nil_clustering = named entities in doc - actual disambiguated entities by EF
        nil_clustering = []
        if len(result_from_ef_text[0]) > 0:
            try:
                nil_clustering = [
                    doc.char_span(start_idx=ent[1],
                                  end_idx=ent[2]) for ent in [
                        (
                            ent.text, ent.start_char, ent.end_char
                        ) for ent in doc.ents
                    ] if ent not in [
                        (
                            ent_ef['rawName'], ent_ef['offsetStart'], ent_ef['offsetEnd']
                        ) for ent_ef in result_from_ef_text[0]['entities']
                    ]
                ]
            except KeyError:
                pass
        entities_from_terms = []
        if len(nil_clustering) != 0:
            # prepare query for Entity-Fishing terms disambiguation
            terms = " ".join([ent.text for ent in doc.ents])
            result_from_ef_terms = self.main_disambiguation_process_batch(
                text_batch=[""],
                terms_batch=[terms],
                entities_batch=[nil_clustering]
            )[0]

            entities_from_terms = result_from_ef_terms[2]

            # 2b. Attach raw response (with terms method in Entity-Fishing service) to doc
            if len(result_from_ef_terms[0]) > 0:
                doc._.annotations["disambiguation_terms_service"] = result_from_ef_terms[0]
            doc._.metadata["disambiguation_terms_service"] = result_from_ef_terms[1]

        # 3. Merge two list of entities (first and second pass in EF service)
        # and attach information from Entity-Fishing to spans
        result = entities_from_text + [
            entity_term for entity_term in entities_from_terms
            if entity_term not in entities_from_text
        ] if len(entities_from_terms) > 0 else entities_from_text

        if len(result) > 0:
            try:
                self.updated_entities(doc, result)
            except KeyError:
                pass

        return doc

    def __call__(self, doc: Doc) -> Doc:
        """
        > The function takes a spaCy Doc object, and returns a Doc object with the entities
        disambiguated and linked

        :param doc: Doc
        :type doc: Doc
        :return: A Doc object with the entities linked to the corresponding Wikipedia page.
        """
        # 1. Disambiguate and linking named entities in Doc object with Entity-Fishing
        result_from_ef_text = self.main_disambiguation_process_batch(
            text_batch=[doc.text],
            terms_batch=[""],
            entities_batch=[doc.ents]
        )[0]
        return self.process_single_doc_after_call(doc, result_from_ef_text)

    def pipe(self, stream: iterators, batch_size: int = 128) -> Doc:
        """
        For each batch of documents, we disambiguate the named entities in the documents, and then yield
        the results

        :param stream: a generator that yields Doc objects
        :type stream: iterator
        :param batch_size: The number of documents to process at a time, defaults to 128 (optional)
        :type batch_size: int
        """
        for docs in util.minibatch(stream, size=batch_size):
            text_batch = [doc.text for doc in docs]
            entities_batch = [doc.ents for doc in docs]
            terms_batch = ["" for _ in text_batch]

            # 1. Disambiguate and linking named entities in Doc object with Entity-Fishing
            result_from_ef_text_batch = self.main_disambiguation_process_batch(
                text_batch=text_batch, terms_batch=terms_batch, entities_batch=entities_batch)

            for doc, result_from_ef_text in zip(docs, result_from_ef_text_batch):
                yield self.process_single_doc_after_call(doc, result_from_ef_text)
