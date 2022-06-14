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
    "url_base": "http://nerd.huma-num.fr/nerd/service",
    "language": "en",
    "description_required": False
})
class EntityFishing:
    """
    szs
    """
    def __init__(self,
                 nlp: Language,
                 name: str,
                 url_base: str,
                 language: str,
                 description_required: bool):
        """

        :param url_base:
        :param language:
        :param description_required:
        """
        if not url_base.endswith("/"):
            url_base += "/"
        self.url_base = url_base
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
    def generic_client(method: str, url: str, params=None, files=None) -> requests.Response:
        """

        :param method:
        :param url:
        :param params:
        :param files:
        :return:
        """
        if files is None:
            files = {}
        if params is None:
            params = {}

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
        print(response)
        print(type(response))
        if response.status_code == 429:
            time.sleep(int(response.headers["Retry-After"]))
            response = make_requests(method, url, params, files)
        #elif response.status_code == 404:
        #    response =

        return response

    def concept_look_up(self, kb_qid: str) -> requests.Response:
        """service returns the knowledge base concept information from wikidata ID"""
        url_concept_lookup = self.url_base + "kb/concept/" + kb_qid
        return self.generic_client(method="GET",
                                   url=url_concept_lookup,
                                   params=self.language)

    def disambiguate_text(self, files: dict) -> requests.Response:
        """Method"""
        url_disambiguate = self.url_base + "disambiguate"
        return self.generic_client(method='POST', url=url_disambiguate, files=files)

    def __call__(self, doc: Doc) -> Doc:
        """This special class method requests Entity-Fishing API.
        Then, Attaches entities to spans (and doc)."""

        # Get entities from doc and prepare these for requests
        entities = [{
            "rawName": ent.text,
            "offsetStart": ent.start,
            "offsetEnd": ent.end,
        } for ent in doc.ents]

        # prepare query for Entity-Fishing Text
        data = {"query": str({
                "text": doc.text,
                "language": self.language,
                "entities": entities,
                "mentions": ["ner", "wikipedia"] if len(entities) == 0 else [],
                "customisation": "generic"
                })}

        # Post request to Entity-Fishing API
        req = self.disambiguate_text(files=data)
        req.raise_for_status()
        res = req.json()

        # Attach raw response to doc
        doc._.annotations = res
        doc._.metadata = {
            "status_code": req.status_code,
            "reason": req.reason,
            "ok": req.ok,
            "encoding": req.encoding
        }

        # Attach wikidata QID, wikidata url, description (optional) and ranking disambiguation score
        for entity in res.get('entities'):
            try:
                span = doc[entity['offsetStart']:entity['offsetEnd']]
                span._.kb_qid = entity['wikidataId']
                if self.flag_desc:
                    try:
                        req_desc = self.concept_look_up(span._.kb_qid)
                        req_desc.raise_for_status()
                        res_desc = req_desc.json()
                        span._.description = res_desc['definitions'][0]['definition']
                    except KeyError:
                        pass
                span._.url_wikidata = self.wikidata_url_base + span._.kb_qid
                span._.nerd_score = entity['nerd_selection_score']
            except KeyError:
                pass

        return doc
