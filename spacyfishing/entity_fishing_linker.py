# -*- coding: UTF-8 -*-

"""entity_fishing_linker.py

SpaCy wrapper to call Entity-fishing API
as disambiguation and entity linking component.
"""

import logging

import requests

from spacy.language import Language
from spacy.tokens import Doc, Span


@Language.factory("entityfishing", default_config={
    "api_ef_base": "http://nerd.huma-num.fr/nerd/service",
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
            extra_info (bool): attach extra informations to spans as normalised term,
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
        Doc.set_extension("annotations", default=None, force=True)
        Doc.set_extension("metadata", default=None, force=True)

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
                       "missing header, text too short (> 5 chars). (400)")
        elif response.status_code == 500:
            client_log("Entity-Fishing API service seems broken. (500)")
        elif response.status_code == 404:
            client_log("Property was not found in request body. (404)")
        elif response.status_code == 406:
            client_log("Language is not supported by Entity-Fishing. (406)")

        return response

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

        # Attach to span default information: wikidata QID,
        # wikidata url and ranking disambiguation score
        if res != {} and len(doc.ents) > 0 and req.status_code == 200:
            try:
                for entity in res['entities']:
                    try:
                        span = doc[entity['offsetStart']:entity['offsetEnd']]
                        span._.kb_qid = str(entity['wikidataId'])
                        try:
                            span._.wikipedia_page_ref = str(entity["wikipediaExternalRef"])
                        except KeyError:
                            pass
                        span._.url_wikidata = self.wikidata_url_base + span._.kb_qid
                        span._.nerd_score = entity['nerd_selection_score']
                        # Attach to span extra information:  normalised term name, description,
                        # description source, others identifiers (statements attach to QID)
                        if self.flag_extra and span._.wikipedia_page_ref is not None:
                            try:
                                req_desc = self.concept_look_up(span._.wikipedia_page_ref)
                                res_desc = req_desc.json()
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
                                # others identifiers attach to QID
                                # in Wikidata KB with filter properties or not
                                try:
                                    if len(self.filter_statements) != 0:
                                        ids = [
                                            {
                                                k: content[k] for k in ['propertyName',
                                                                        'propertyId',
                                                                        'value']
                                             } for content in res_desc['statements']
                                            if content['propertyId'] in self.filter_statements
                                        ]
                                    else:
                                        ids = [
                                            {
                                                k: content[k] for k in ['propertyName',
                                                                        'propertyId',
                                                                        'value']
                                             } for content in res_desc['statements']]
                                    span._.other_ids = ids
                                except KeyError:
                                    pass
                            except requests.exceptions.JSONDecodeError:
                                pass
                    except KeyError:
                        pass
            except KeyError:
                pass

        return doc
