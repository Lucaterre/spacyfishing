# -*- coding: UTF-8 -*-

"""entity_fishing_linker.py

SpaCy wrapper to call Entity-fishing API
as disambiguation and entity linking component.
"""

import logging
from typing import Tuple
import json

import requests

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
    def generic_client(method: str,
                       url: str,
                       verbose: bool,
                       params: dict = None,
                       files: dict = None) -> requests.Response:
        """Client to interact with a generic Rest API.

        Parameters:
            method (str): service HTTP methods (get, post etc.)
            url (str): the base URL to the service being used.
            verbose (bool): display log messages.
            params (dict): requests parameters.
            files (dict): requests files.

        Returns:
            response (requests.Response): query response.
        """

        if params is None:
            params = {}
        if files is None:
            files = {}

        def make_requests(type_method: str,
                          type_url: str,
                          type_params: dict,
                          type_files: dict) -> requests.Response:
            res = requests.request(method=type_method,
                                   url=type_url,
                                   headers={
                                       "Accept": "application/json"
                                   },
                                   files=type_files,
                                   params=type_params)
            return res

        def client_log(msg: str) -> None:
            if verbose:
                logging.warning(msg)

        response = make_requests(method, url, params, files)

        # Manage response status code :
        # cf. https://nerd.readthedocs.io/en/latest/restAPI.html#response-status-codes
        if response.status_code == 400:
            client_log("Wrong request, missing parameters, "
                       "missing header, text too short (<= 5 characters). (400)")
        elif response.status_code == 500:
            client_log("Entity-Fishing API service seems broken. (500)")
        elif response.status_code == 404:
            client_log("Property was not found in request body. (404)")
        elif response.status_code == 406:
            client_log("Language is not supported by Entity-Fishing. (406)")

        return response

    @staticmethod
    def process_response(response: requests.models.Response) -> Tuple[dict, dict]:
        """decode response in JSON format and
        retrieve metadata information.

        Parameters:
            response (requests.models.Response): response from Entity-Fishing
            service.

        Returns:
            res_json (dict): response format in JSON.
            metadata (dict): HTTP information about request.
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
        """Preprocess data before call Entity-Fishing service.

        Parameters:
            text (str): Text to disambiguate.
            terms (str): Sequence of terms to disambiguate
            e.g. "ONU Barack Obama president ...".
            entities (list): Specific entities to disambiguate.
            language (dict): Type of language.
            full (bool): Retrieve extra information or not on entity. Defaults to `False`.

        Returns:
            dict (dict): data ready to send.
        """

        return {
            "query": json.dumps({
                "text": text,
                "shortText": terms,
                "language": language,
                "entities": [
                    {
                        "rawName": ent.text,
                        "offsetStart": ent.start,
                        "offsetEnd": ent.end,
                    } for ent in entities
                ],
                "mentions": [],
                "customisation": "generic",
                "full": "true" if full else "false"
            }, ensure_ascii=False)
        }

    def updated_entities(self, doc: Doc, response: list) -> None:
        """Attach to span default information: wikidata QID,
           wikidata url and ranking disambiguation score.
           Also, Attach to span extra information if flag is set
           to `True`.

        Parameters:
            doc (Doc): spaCy doc object.
            response (list): List that contains disambiguated entities in dict.
        """
        for entity in response:
            span = doc[entity['offsetStart']:entity['offsetEnd']]
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

    # ~ Entity-fishing call service methods ~:

    def concept_look_up(self, wiki_id: str) -> requests.Response:
        """Service returns the knowledge base concept information from QID
        or Wikipedia page id.

        Parameters:
            wiki_id (str): Wikidata identifier (QID) or Wikipedia page external reference
        Returns:
            response (requests.Response): query response from concept look-up service.
        """
        url_concept_lookup = self.api_ef_base + "kb/concept/" + wiki_id
        return self.generic_client(method="GET",
                                   url=url_concept_lookup,
                                   params=self.language,
                                   verbose=self.verbose)

    def disambiguate_text(self, files: dict) -> requests.Response:
        """Service returns disambiguate entities.

        Parameters:
            files (dict): JSON format for the query.
            See also https://nerd.readthedocs.io/en/latest/restAPI.html#generic-format
        Returns:
            response (requests.Response): query response from concept look-up service.
        """
        url_disambiguate = self.api_ef_base + "disambiguate"
        return self.generic_client(method='POST',
                                   url=url_disambiguate,
                                   files=files,
                                   verbose=self.verbose)

    def look_extra_informations_on_entity(self, span: Span, res_desc: dict) -> None:
        """Attach to span extra information:
        normalised term name, description, description source,
        others identifiers (statements attach to QID).

        Parameters:
            span (Span): spaCy span object where attach extra information.
            res_desc (dict): dict that contains extra information on entity.
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

    def main_disambiguation_process(self,
                                    text: str,
                                    terms: str,
                                    entities: list) -> Tuple[dict, dict, list]:
        """Generic routine that describe the call
        process of disambiguation service.
        1. prepare query for disambiguation service
        2. post query
        3. process response

        Parameters:
            text (str): Text to disambiguate.
            terms (str): Sequence of terms to disambiguate
            e.g. "ONU Barack Obama president ...".
            entities (list): Specific entities to disambiguate.

        Returns:
            res (dict): response from Entity-Fishing service.
            metadata (dict): information about HTTP request on
            Entity-Fishing service.
            entities_enhanced (list): list of entities disambiguated by
            Entity-Fishing.
        """

        data_to_post = self.prepare_data(text=text,
                                         terms=terms,
                                         entities=entities,
                                         language=self.language,
                                         full=self.flag_extra)

        req = self.disambiguate_text(files=data_to_post)
        res, metadata = self.process_response(response=req)
        try:
            entities_enhanced = res['entities']
        except KeyError:
            entities_enhanced = []

        return res, metadata, entities_enhanced

    def __call__(self, doc: Doc) -> Doc:
        """Attaches entities to spans (and doc)."""
        # 1. Disambiguate and linking named entities in Doc object with Entity-Fishing
        result_from_ef_text = self.main_disambiguation_process(text=doc.text,
                                                               terms="",
                                                               entities=doc.ents)
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
                    doc[ent[1]:ent[2]] for ent in [
                        (
                            ent.text, ent.start, ent.end
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
            result_from_ef_terms = self.main_disambiguation_process(text="",
                                                                    terms=terms,
                                                                    entities=nil_clustering)

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
