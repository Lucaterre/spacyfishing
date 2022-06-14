# -*- coding: UTF-8 -*-

"""
entity_fishing_linker.py

SpaCy wrapper to call Entity-fishing API
as disambiguation and entity linking component.
"""

import time

import requests

from spacy.language import Language
from spacy.tokens import Doc, Span


@Language.factory("entityfishing", default_config={
    "api_ef_base": "http://nerd.huma-num.fr/nerd/service",
    "language": "en",
    "description_required": False
})
class EntityFishing:
    """EntityFishing component for spaCy pipeline."""
    def __init__(self,
                 nlp: Language,
                 name: str,
                 api_ef_base: str,
                 language: str,
                 description_required: bool):
        """
        Show default config for default attributes values.

        Parameters:
            api_ef_base (str): describes url of the entity-fishing API used.
            language (str): matches the language of the resources to
            be disambiguated (matches the language model for the NER task).
            description_required (bool): flag to search or not the description
            associated with the Wikidata entity.

        Attributes:
            api_ef_base (str): cf. `api_ef_base` in parameters section.
            language (dict): cf. `language` in parameters section.
            prepare the language argument for the query.
            flag_desc (str): cf. `description_required` in parameters section.
            wikidata_url_base (str): wikidata base url (to concatenate QID identifiers).
        """
        if not api_ef_base.endswith("/"):
            api_ef_base += "/"
        self.api_ef_base = api_ef_base
        self.language = dict(lang=language)
        self.flag_desc = description_required
        self.wikidata_url_base = "https://www.wikidata.org/wiki/"

        # Set doc extensions to attaches raw response from Entity-Fishing API to doc
        Doc.set_extension("annotations", default=None, force=True)
        Doc.set_extension("metadata", default=None, force=True)

        # Set spans extensions to enhance spans with new information
        # come from Wikidata knowledge base.
        Span.set_extension("kb_qid", default=None, force=True)
        Span.set_extension("description", default=None, force=True)
        Span.set_extension("url_wikidata", default=None, force=True)
        Span.set_extension("nerd_score", default=None, force=True)

    @staticmethod
    def generic_client(method: str, url: str, params: dict = {}, files: dict = {}) -> requests.Response:
        """Client to interact with a generic Rest API.

        Parameters:
            method (str): service HTTP methods (get, post etc.)
            url (str): the base URL to the service being used.
            params (dict): requests parameters.
            files (dict): requests files.

        Returns:
            response (requests.Response): query response.
        """
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

        response = make_requests(method, url, params, files)

        # Retry request if too many requests
        if response.status_code == 429:
            time.sleep(int(response.headers["Retry-After"]))
            response = make_requests(method, url, params, files)

        return response

    def concept_look_up(self, kb_qid: str) -> requests.Response:
        """Service returns the knowledge base concept information from QID.

        Parameters:
            kb_qid (str): Wikidata identifier (QID)
        Returns:
            response (requests.Response): query response from concept look-up service.
        """
        url_concept_lookup = self.api_ef_base + "kb/concept/" + kb_qid
        return self.generic_client(method="GET",
                                   url=url_concept_lookup,
                                   params=self.language)

    def disambiguate_text(self, files: dict) -> requests.Response:
        """Service returns disambiguate entities.

        Parameters:
            files (dict): JSON format for the query.
            See also https://nerd.readthedocs.io/en/latest/restAPI.html#generic-format
        Returns:
            response (requests.Response): query response from concept look-up service.
        """
        url_disambiguate = self.api_ef_base + "disambiguate"
        return self.generic_client(method='POST', url=url_disambiguate, files=files)

    def __call__(self, doc: Doc) -> Doc:
        """Attaches entities to spans (and doc)."""

        # prepare query for Entity-Fishing disambiguation
        data = {"query": str({
            "text": doc.text,
            "language": self.language,
            "entities": [{
                "rawName": ent.text,
                "offsetStart": ent.start,
                "offsetEnd": ent.end,
            } for ent in doc.ents],
            "mentions": ["ner", "wikipedia"] if len(doc.ents) == 0 else [],
            "customisation": "generic"
        })}

        # Post query to Entity-Fishing disambiguation service
        req = self.disambiguate_text(files=data)

        #req.raise_for_status()
        try:
            res = req.json()
        except requests.exceptions.JSONDecodeError:
            res = {}

        # Attach raw response to doc
        doc._.annotations = res
        doc._.metadata = {
            "status_code": req.status_code,
            "reason": req.reason,
            "ok": req.ok,
            "encoding": req.encoding
        }

        # Attach wikidata QID, wikidata url, description (optional) and ranking disambiguation score
        if len(res['entities']) > 0 and len(doc.ents) > 0 and req.status_code == 200:
            for entity in res['entities']:
                try:
                    span = doc[entity['offsetStart']:entity['offsetEnd']]
                    span._.kb_qid = entity['wikidataId']
                    span._.url_wikidata = self.wikidata_url_base + span._.kb_qid
                    span._.nerd_score = entity['nerd_selection_score']
                    if self.flag_desc:
                        try:
                            req_desc = self.concept_look_up(span._.kb_qid)
                            req_desc.raise_for_status()
                            res_desc = req_desc.json()
                            span._.description = res_desc['definitions'][0]['definition']
                        except KeyError:
                            pass
                except KeyError:
                    pass

        return doc
