# spaCy fishing

![Python Version](https://img.shields.io/badge/Python-%3E%3D%203.7-%2313aab7) [![PyPI version](https://badge.fury.io/py/spacyfishing.svg)](https://badge.fury.io/py/spacyfishing) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Tests](https://github.com/Lucaterre/spacyfishing/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Lucaterre/spacyfishing/actions/workflows/tests.yml) [![Built with spaCy](https://img.shields.io/badge/built%20with-spaCy-09a3d5.svg)](https://spacy.io)

<!-- add pip badge -->

A spaCy wrapper of [Entity-Fishing](https://nerd.readthedocs.io/en/latest/overview.html), a tool for named entity disambiguation and linking on Wikidata.

This extension allows using Entity-Fishing tool as a spaCy pipeline component to disambiguate and link named entities (with custom or pretrained NER spaCy models) to Wikidata knowledge base.

## Table of contents

 * [Installation](#Installation)
   * [normal](#normal)
   * [development](#development)
 * [Usage (examples)](#Usage)
    - [Simple example](#Simple-example)
    - [Get extra information from Wikidata](#Get-extra-information-from-Wikidata)
    - [Use other language](#Use-other-language)
    - [Get information about Entity fishing API response](#Get-information-about-Entity-fishing-API-response)
 * [Configuration parameters](#Configuration-parameters)
 * [Attributes](#Attributes)
 * [Recommendations](#Recommendations)
 * [Visualise results](#Visualise-results) 
 * [External ressources](#External-ressources)
 * [Details](#Details)


## Installation

### normal

```bash
pip install spacyfishing
```

### development

```bash
git clone https://github.com/Lucaterre/spacyfishing.git
virtualenv --python=/usr/bin/python3.8 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage


First, install a [pre-trained spaCy language model](https://spacy.io/models) for the NER task:

```bash
python -m spacy download en_core_web_sm
```

Note that it is possible to use custom NER model.

### Simple example

```Python
import spacy 

text_en = "Victor Hugo and Honoré de Balzac are French writers who lived in Paris."

nlp_model_en = spacy.load("en_core_web_sm")

nlp_model_en.add_pipe("entityfishing")

doc_en = nlp_model_en(text_en)

for ent in doc_en.ents:
        print((ent.text, ent.label_, ent._.kb_qid, ent._.url_wikidata, ent._.nerd_score))
```
```
('Victor Hugo', 'PERSON', 'Q535', 'https://www.wikidata.org/wiki/Q535', 0.972)
('Honoré de Balzac', 'PERSON', 'Q9711', 'https://www.wikidata.org/wiki/Q9711', 0.9724)
('French', 'NORP', 'Q121842', 'https://www.wikidata.org/wiki/Q121842', 0.3739)
('Paris', 'GPE', 'Q90', 'https://www.wikidata.org/wiki/Q90', 0.5652)
```

### Get extra information from Wikidata
By default, the component, as seen previously, attaches to the span only the QID, the Wikidata url and the score. 
However, it is possible to retrieve other information such as a short description of the entity, a standardized term, 
or other identifiers from knowledge bases related to Wikidata concept, for example Geonames id, VIAF id, etc.

To access to extra informations about wikidata entity, specify `True` in the `extra_info` parameter in the component configuration:

```Python

import spacy 

text_en = "Victor Hugo and Honoré de Balzac are French writers who lived in Paris."

nlp_model_en = spacy.load("en_core_web_sm")

# specify configuration:
nlp_model_en.add_pipe("entityfishing", config={"extra_info": True})

doc_en = nlp_model_en(text_en)

# Access to description with ent._.description:
for ent in doc_en.ents:
        print((ent.text, ent.label_, ent._.kb_qid, ent._.normal_term, ent._.description, ent._.src_description, ent._.other_ids))
```
```
('Victor Hugo', 'PERSON', 'Q535', 'Victor Hugo', "'''''' (; 26 February 1802 – 22 May 1885) was a French poet, novelist, and dramatist of the [[Romanticism|Romantic movement]]. Hugo is considered to be one of the greatest and best-known French writers. Outside of France, his most famous works are the novels '''', 1862, and ''[[The Hunchback of Notre-Dame]]'', 1831. In France, Hugo is known primarily for his poetry collections, such as '''' (''The Contemplations'') and '''' (''The Legend of the Ages'').", 'wikipedia-en', [{'propertyName': 'Sycomore ID', 'propertyId': 'P1045', 'value': '8795'}, {'propertyName': 'image', 'propertyId': 'P18', 'value': 'Victor Hugo.jpg'}, {'propertyName': 'signature', 'propertyId': 'P109', 'value': 'Victor Hugo Signature.svg'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q82955'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q214917'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q6625963'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q15296811'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q8178443'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q11774202'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q11774156'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q36180'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q644687'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q3579035'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q49757'}, {'propertyName': 'country of citizenship', 'propertyId': 'P27', 'value': 'Q142'}, {'propertyName': 'child', 'propertyId': 'P40', 'value': 'Q3271923'}, {'propertyName': 'child', 'propertyId': 'P40', 'value': 'Q2082427'}, {'propertyName': 'child', 'propertyId': 'P40', 'value': 'Q663856'}, {'propertyName': 'child', 'propertyId': 'P40', 'value': 'Q3083678'}, {'propertyName': 'father', 'propertyId': 'P22', 'value': 'Q2299673'}, {'propertyName': 'mother', 'propertyId': 'P25', 'value': 'Q3491058'}, {'propertyName': 'spouse', 'propertyId': 'P26', 'value': 'Q2825429'}, {'propertyName': 'place of birth', 'propertyId': 'P19', 'value': 'Q37776'}, {'propertyName': 'place of interment', 'propertyId': 'P119', 'value': 'Q188856'}, {'propertyName': 'sex or gender', 'propertyId': 'P21', 'value': 'Q6581097'}, {'propertyName': 'VIAF ID', 'propertyId': 'P214', 'value': '9847974'}, {'propertyName': 'BnF ID', 'propertyId': 'P268', 'value': '11907966z'}, {'propertyName': 'GND ID', 'propertyId': 'P227', 'value': '118554654'}, {'propertyName': 'Commons category', 'propertyId': 'P373', 'value': 'Victor Hugo'}, {'propertyName': 'Library of Congress authority ID', 'propertyId': 'P244', 'value': 'n79091479'}, {'propertyName': 'place of death', 'propertyId': 'P20', 'value': 'Q90'}, {'propertyName': 'MusicBrainz artist ID', 'propertyId': 'P434', 'value': 'c0c99c8f-4779-4c35-9497-67d60a73310a'}, {'propertyName': 'unmarried partner', 'propertyId': 'P451', 'value': 'Q440119'}, {'propertyName': 'unmarried partner', 'propertyId': 'P451', 'value': 'Q3271708'}, {'propertyName': 'member of', 'propertyId': 'P463', 'value': 'Q161806'}, {'propertyName': 'member of', 'propertyId': 'P463', 'value': 'Q12759592'}, {'propertyName': 'member of', 'propertyId': 'P463', 'value': 'Q2822385'}, {'propertyName': 'NDL Auth ID', 'propertyId': 'P349', 'value': '00443985'}, {'propertyName': 'SUDOC authorities', 'propertyId': 'P269', 'value': '026927608'}, {'propertyName': 'date of death', 'propertyId': 'P570', 'value': {'time': '+1885-05-22T00:00:00Z', 'timezone': 0, 'before': 0, 'after': 0, 'precision': 11, 'calendarmodel': 'http://www.wikidata.org/entity/Q1985727'}}, {'propertyName': 'date of birth', 'propertyId': 'P569', 'value': {'time': '+1802-02-26T00:00:00Z', 'timezone': 0, 'before': 0, 'after': 0, 'precision': 11, 'calendarmodel': 'http://www.wikidata.org/entity/Q1985727'}}, {'propertyName': 'NKCR AUT ID', 'propertyId': 'P691', 'value': 'jn19990003739'}, {'propertyName': 'given name', 'propertyId': 'P735', 'value': 'Q539581'}, {'propertyName': 'given name', 'propertyId': 'P735', 'value': 'Q632104'}, {'propertyName': "topic's main category", 'propertyId': 'P910', 'value': 'Q7367470'}, {'propertyName': 'educated at', 'propertyId': 'P69', 'value': 'Q209842'}, {'propertyName': 'educated at', 'propertyId': 'P69', 'value': 'Q1059546'}, {'propertyName': 'ISNI', 'propertyId': 'P213', 'value': '0000 0001 2120 0982'}, {'propertyName': 'ULAN ID', 'propertyId': 'P245', 'value': '500032572'}, {'propertyName': 'instance of', 'propertyId': 'P31', 'value': 'Q5'}, {'propertyName': 'SELIBR', 'propertyId': 'P906', 'value': '206651'}, {'propertyName': 'NLA (Australia) ID', 'propertyId': 'P409', 'value': '35212404'}, {'propertyName': 'BNE ID', 'propertyId': 'P950', 'value': 'XX874892'}, {'propertyName': 'BAV ID', 'propertyId': 'P1017', 'value': 'ADV10201285'}, {'propertyName': 'National Thesaurus for Author Names ID', 'propertyId': 'P1006', 'value': '068472390'}, {'propertyName': 'PTBNP ID', 'propertyId': 'P1005', 'value': '23526'}, {'propertyName': 'Freebase ID', 'propertyId': 'P646', 'value': '/m/01vh096'}, {'propertyName': 'Commons gallery', 'propertyId': 'P935', 'value': 'Victor Hugo'}, {'propertyName': 'SBN ID', 'propertyId': 'P396', 'value': 'IT\\ICCU\\CFIV\\000163'}, {'propertyName': 'position held', 'propertyId': 'P39', 'value': 'Q3044918'}, {'propertyName': 'position held', 'propertyId': 'P39', 'value': 'Q21032547'}, {'propertyName': 'position held', 'propertyId': 'P39', 'value': 'Q21032625'}, {'propertyName': 'CANTIC-ID', 'propertyId': 'P1273', 'value': 'a10409609'}, {'propertyName': 'NUKAT (WarsawU) authorities', 'propertyId': 'P1207', 'value': 'n93090024'}, {'propertyName': 'EGAXA ID', 'propertyId': 'P1309', 'value': '000805125'}, {'propertyName': 'OpenPlaques subject ID', 'propertyId': 'P1430', 'value': '3864'}, {'propertyName': 'native language', 'propertyId': 'P103', 'value': 'Q150'}, {'propertyName': 'Commons Creator page', 'propertyId': 'P1472', 'value': 'Victor Hugo'}, {'propertyName': 'IMDb ID', 'propertyId': 'P345', 'value': 'nm0401076'}, {'propertyName': 'languages spoken, written or signed', 'propertyId': 'P1412', 'value': 'Q150'}, {'propertyName': 'Perlentaucher ID', 'propertyId': 'P866', 'value': 'victor-hugo'}, {'propertyName': 'RSL ID (person)', 'propertyId': 'P947', 'value': '000081185'}, {'propertyName': 'RSL ID (person)', 'propertyId': 'P947', 'value': '000081185'}, {'propertyName': 'LAC ID', 'propertyId': 'P1670', 'value': '0009A1129'}, {'propertyName': 'LNB ID', 'propertyId': 'P1368', 'value': '000010603'}, {'propertyName': 'NLP ID', 'propertyId': 'P1695', 'value': 'A11372163'}, {'propertyName': 'NSK ID', 'propertyId': 'P1375', 'value': '000006120'}, {'propertyName': 'BIBSYS ID', 'propertyId': 'P1015', 'value': '90054094'}, {'propertyName': 'DBNL author ID', 'propertyId': 'P723', 'value': 'hugo020'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q4173137'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q19180675'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q602358'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q2657718'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q867541'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q4532135'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q17329836'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q3639582'}, {'propertyName': 'NNDB people ID', 'propertyId': 'P1263', 'value': '665/000026587'}, {'propertyName': 'National Portrait Gallery (London) person ID', 'propertyId': 'P1816', 'value': 'mp57489'}, {'propertyName': 'genealogics.org person ID', 'propertyId': 'P1819', 'value': 'I00434079'}, {'propertyName': 'birth name', 'propertyId': 'P1477', 'value': {'text': 'Victor Marie Hugo', 'language': 'fr'}}, {'propertyName': 'senat.fr ID', 'propertyId': 'P1808', 'value': 'senateur-3eme-republique/hugo_victor1354r3'}, {'propertyName': 'Project Gutenberg author ID', 'propertyId': 'P1938', 'value': '85'}, {'propertyName': 'conflict', 'propertyId': 'P607', 'value': 'Q46083'}, {'propertyName': 'AlloCiné person ID', 'propertyId': 'P1266', 'value': '36981'}, {'propertyName': 'Discogs artist ID', 'propertyId': 'P1953', 'value': '271274'}, {'propertyName': 'AllMusic artist ID', 'propertyId': 'P1728', 'value': 'mn0000115922'}, {'propertyName': 'National Library of Ireland authority', 'propertyId': 'P1946', 'value': 'vtls000374912'}, {'propertyName': 'noble title', 'propertyId': 'P97', 'value': 'Q185902'}, {'propertyName': 'Open Library ID', 'propertyId': 'P648', 'value': 'OL107571A'}, {'propertyName': 'NILF author id', 'propertyId': 'P2191', 'value': 'NILF21570'}, {'propertyName': 'National Gallery of Art artist ID', 'propertyId': 'P2252', 'value': '4398'}, {'propertyName': 'BiblioNet author ID', 'propertyId': 'P2188', 'value': '647'}, {'propertyName': 'RKDartists ID', 'propertyId': 'P650', 'value': '40381'}, {'propertyName': "Musée d'Orsay artist ID", 'propertyId': 'P2268', 'value': '15047'}, {'propertyName': 'Dictionary of Art Historians ID', 'propertyId': 'P2332', 'value': 'hugov'}, {'propertyName': 'HDS ID', 'propertyId': 'P902', 'value': '11461'}, {'propertyName': 'People Australia ID', 'propertyId': 'P1315', 'value': '867505'}, {'propertyName': 'AGORHA person/institution ID', 'propertyId': 'P2342', 'value': '113304'}, {'propertyName': 'SFDb person ID', 'propertyId': 'P2168', 'value': '133084'}, {'propertyName': 'AllMovie artist ID', 'propertyId': 'P2019', 'value': 'p310601'}, {'propertyName': 'PORT person ID', 'propertyId': 'P2435', 'value': '13863'}, {'propertyName': 'CERL ID', 'propertyId': 'P1871', 'value': 'cnp01259566'}, {'propertyName': 'FAST ID', 'propertyId': 'P2163', 'value': '40981'}, {'propertyName': 'FAST ID', 'propertyId': 'P2163', 'value': '40981'}, {'propertyName': 'WomenWriters ID', 'propertyId': 'P2533', 'value': '728b782f-e333-494e-86e6-11d487e1fe0a'}, {'propertyName': 'CTHS person ID', 'propertyId': 'P2383', 'value': '63'}, {'propertyName': 'Scope.dk person ID', 'propertyId': 'P2519', 'value': '57742'}, {'propertyName': 'KMDb person ID', 'propertyId': 'P1649', 'value': '00122258'}, {'propertyName': 'KulturNav-id', 'propertyId': 'P1248', 'value': '46270dea-cf15-43f2-adb1-ef2626b0eb63'}, {'propertyName': 'Nationalmuseum Sweden artist ID', 'propertyId': 'P2538', 'value': '11997'}, {'propertyName': 'ČSFD person ID', 'propertyId': 'P2605', 'value': '90694'}, {'propertyName': 'Filmportal ID', 'propertyId': 'P2639', 'value': '523cc573be0744f6a8492851cb8fa73d'}, {'propertyName': 'family name', 'propertyId': 'P734', 'value': 'Q14626498'}, {'propertyName': 'Léonore ID', 'propertyId': 'P640', 'value': 'LH/1320/26'}, {'propertyName': 'Kinopoisk person ID', 'propertyId': 'P2604', 'value': '64589'}, {'propertyName': 'BVMC person ID', 'propertyId': 'P2799', 'value': '1700'}, {'propertyName': 'Benezit ID', 'propertyId': 'P2843', 'value': 'B00090836'}, {'propertyName': 'Encyclopædia Britannica Online ID', 'propertyId': 'P1417', 'value': 'biography/Victor-Hugo'}, {'propertyName': 'Les Archives du Spectacle ID', 'propertyId': 'P1977', 'value': '10155'}, {'propertyName': 'LibriVox author ID', 'propertyId': 'P1899', 'value': '706'}, {'propertyName': 'NLR (Romania) ID', 'propertyId': 'P1003', 'value': 'RUNLRAUTH7721605'}, {'propertyName': 'NLR (Romania) ID', 'propertyId': 'P1003', 'value': 'RUNLRAUTH7721605'}, {'propertyName': 'permanent duplicated item', 'propertyId': 'P2959', 'value': 'Q23059782'}, {'propertyName': 'elCinema person ID', 'propertyId': 'P3136', 'value': '2006287'}, {'propertyName': 'WikiTree ID', 'propertyId': 'P2949', 'value': 'Hugo-215'}, {'propertyName': 'Great Russian Encyclopedia Online ID', 'propertyId': 'P2924', 'value': '1937300'}, {'propertyName': 'award received', 'propertyId': 'P166', 'value': 'Q10855195'}, {'propertyName': 'Theatricalia person ID', 'propertyId': 'P2469', 'value': '5q1'}, {'propertyName': 'National Library of Greece ID', 'propertyId': 'P3348', 'value': '60548'}, {'propertyName': 'Internet Broadway Database person ID', 'propertyId': 'P1220', 'value': '8950'}, {'propertyName': 'sibling', 'propertyId': 'P3373', 'value': 'Q318448'}, {'propertyName': 'sibling', 'propertyId': 'P3373', 'value': 'Q3059936'}, {'propertyName': 'work location', 'propertyId': 'P937', 'value': 'Q90'}, {'propertyName': 'Gran Enciclopèdia Catalana ID', 'propertyId': 'P1296', 'value': '0033170'}, {'propertyName': 'name in native language', 'propertyId': 'P1559', 'value': {'text': 'Victor Hugo', 'language': 'fr'}}, {'propertyName': 'Quora topic ID', 'propertyId': 'P3417', 'value': 'Victor-Hugo-36'}, {'propertyName': 'British Museum person-institution', 'propertyId': 'P1711', 'value': '32296'}, {'propertyName': 'SNAC ID', 'propertyId': 'P3430', 'value': 'w6wm1csb'}, {'propertyName': 'archives at', 'propertyId': 'P485', 'value': 'Q814779'}, {'propertyName': 'SANU member ID', 'propertyId': 'P3475', 'value': '196'}, {'propertyName': 'openMLOL author ID', 'propertyId': 'P3762', 'value': '830'}, {'propertyName': 'Cultureel Woordenboek identifier', 'propertyId': 'P3569', 'value': 'literatuur-internationaal/victor-hugo'}, {'propertyName': 'notable work', 'propertyId': 'P800', 'value': 'Q180736'}, {'propertyName': 'notable work', 'propertyId': 'P800', 'value': 'Q191380'}, {'propertyName': 'Babelio author ID', 'propertyId': 'P3630', 'value': '2250'}, {'propertyName': 'noble family', 'propertyId': 'P53', 'value': 'Q24929958'}, {'propertyName': 'catalog', 'propertyId': 'P972', 'value': 'Q5460604'}, {'propertyName': 'Bridgeman artist ID', 'propertyId': 'P3965', 'value': '8154'}, {'propertyName': 'significant event', 'propertyId': 'P793', 'value': 'Q201676'}, {'propertyName': 'significant event', 'propertyId': 'P793', 'value': 'Q3927614'}, {'propertyName': 'image of grave', 'propertyId': 'P1442', 'value': 'Panthéon Victor Hugo.JPG'}, {'propertyName': 'CiNii author ID', 'propertyId': 'P271', 'value': 'DA00460099'}, {'propertyName': 'NE.se ID', 'propertyId': 'P3222', 'value': 'victor-hugo'}, {'propertyName': 'BNA authority ID', 'propertyId': 'P3788', 'value': '000023421'}, {'propertyName': 'Artnet artist ID', 'propertyId': 'P3782', 'value': 'victor-marie-hugo'}, {'propertyName': 'lifestyle', 'propertyId': 'P1576', 'value': 'Q45996'}])
('Honoré de Balzac', 'PERSON', 'Q9711', 'Honoré de Balzac', "'''Honoré de Balzac''' (;, born '''Honoré Balzac''', 20 May 1799 \xa0 – 18 August 1850) was a French novelist and playwright. The [[novel sequence]] ''[[La Comédie Humaine]]'', which presents a panorama of [[Napoleonic Era|post-Napoleonic]] French life, is generally viewed as his ''[[Masterpiece|magnum opus]]''.", 'wikipedia-en', [{'propertyName': 'father', 'propertyId': 'P22', 'value': 'Q19111956'}, {'propertyName': 'IMDb ID', 'propertyId': 'P345', 'value': 'nm0051304'}, {'propertyName': 'Find a Grave grave ID', 'propertyId': 'P535', 'value': '51'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q214917'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q1930187'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q4263842'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q6625963'}, {'propertyName': 'occupation', 'propertyId': 'P106', 'value': 'Q175151'}, {'propertyName': 'country of citizenship', 'propertyId': 'P27', 'value': 'Q142'}, {'propertyName': 'place of death', 'propertyId': 'P20', 'value': 'Q90'}, {'propertyName': 'sex or gender', 'propertyId': 'P21', 'value': 'Q6581097'}, {'propertyName': 'native language', 'propertyId': 'P103', 'value': 'Q150'}, {'propertyName': 'BnF ID', 'propertyId': 'P268', 'value': '118900414'}, {'propertyName': 'VIAF ID', 'propertyId': 'P214', 'value': '29529595'}, {'propertyName': 'GND ID', 'propertyId': 'P227', 'value': '118506358'}, {'propertyName': 'SUDOC authorities', 'propertyId': 'P269', 'value': '02670305X'}, {'propertyName': 'Library of Congress authority ID', 'propertyId': 'P244', 'value': 'n79071094'}, {'propertyName': 'ISNI', 'propertyId': 'P213', 'value': '0000 0001 2347 8072'}, {'propertyName': 'MusicBrainz artist ID', 'propertyId': 'P434', 'value': 'a0412c28-426e-409c-a7ed-363a3ffc481a'}, {'propertyName': 'place of birth', 'propertyId': 'P19', 'value': 'Q288'}, {'propertyName': 'Commons category', 'propertyId': 'P373', 'value': 'Honoré de Balzac'}, {'propertyName': 'educated at', 'propertyId': 'P69', 'value': 'Q748307'}, {'propertyName': 'educated at', 'propertyId': 'P69', 'value': 'Q3064259'}, {'propertyName': 'educated at', 'propertyId': 'P69', 'value': 'Q209842'}, {'propertyName': 'place of interment', 'propertyId': 'P119', 'value': 'Q311'}, {'propertyName': 'unmarried partner', 'propertyId': 'P451', 'value': 'Q1986469'}, {'propertyName': 'unmarried partner', 'propertyId': 'P451', 'value': 'Q16089871'}, {'propertyName': 'unmarried partner', 'propertyId': 'P451', 'value': 'Q2940028'}, {'propertyName': 'unmarried partner', 'propertyId': 'P451', 'value': 'Q3218803'}, {'propertyName': 'spouse', 'propertyId': 'P26', 'value': 'Q263997'}, {'propertyName': 'date of birth', 'propertyId': 'P569', 'value': {'time': '+1799-05-20T00:00:00Z', 'timezone': 0, 'before': 0, 'after': 0, 'precision': 11, 'calendarmodel': 'http://www.wikidata.org/entity/Q1985727'}}, {'propertyName': 'date of death', 'propertyId': 'P570', 'value': {'time': '+1850-08-18T00:00:00Z', 'timezone': 0, 'before': 0, 'after': 0, 'precision': 11, 'calendarmodel': 'http://www.wikidata.org/entity/Q1985727'}}, {'propertyName': 'date of death', 'propertyId': 'P570', 'value': {'time': '+1850-08-18T00:00:00Z', 'timezone': 0, 'before': 0, 'after': 0, 'precision': 11, 'calendarmodel': 'http://www.wikidata.org/entity/Q1985727'}}, {'propertyName': 'NKCR AUT ID', 'propertyId': 'P691', 'value': 'jn19990000418'}, {'propertyName': 'instance of', 'propertyId': 'P31', 'value': 'Q5'}, {'propertyName': "topic's main category", 'propertyId': 'P910', 'value': 'Q7846093'}, {'propertyName': 'NDL Auth ID', 'propertyId': 'P349', 'value': '00432210'}, {'propertyName': 'Commons gallery', 'propertyId': 'P935', 'value': 'Honoré de Balzac'}, {'propertyName': 'Freebase ID', 'propertyId': 'P646', 'value': '/m/0bmjw'}, {'propertyName': 'ULAN ID', 'propertyId': 'P245', 'value': '500277159'}, {'propertyName': 'SELIBR', 'propertyId': 'P906', 'value': '38510'}, {'propertyName': 'NLA (Australia) ID', 'propertyId': 'P409', 'value': '35012972'}, {'propertyName': 'CANTIC-ID', 'propertyId': 'P1273', 'value': 'a10472241'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q17378135'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q4239850'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q2627728'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q4263804'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q19180675'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q602358'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q4532135'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q867541'}, {'propertyName': 'OpenPlaques subject ID', 'propertyId': 'P1430', 'value': '7037'}, {'propertyName': 'Commons Creator page', 'propertyId': 'P1472', 'value': 'Honoré de Balzac'}, {'propertyName': 'National Thesaurus for Author Names ID', 'propertyId': 'P1006', 'value': '068405944'}, {'propertyName': 'Perlentaucher ID', 'propertyId': 'P866', 'value': 'honore-de-balzac'}, {'propertyName': 'mother', 'propertyId': 'P25', 'value': 'Q19112644'}, {'propertyName': 'SBN ID', 'propertyId': 'P396', 'value': 'IT\\ICCU\\CFIV\\000620'}, {'propertyName': 'NNDB people ID', 'propertyId': 'P1263', 'value': '460/000022394'}, {'propertyName': 'ISFDB author ID', 'propertyId': 'P1233', 'value': '1596'}, {'propertyName': 'genealogics.org person ID', 'propertyId': 'P1819', 'value': 'I00309364'}, {'propertyName': 'signature', 'propertyId': 'P109', 'value': 'Honoré de Balzac signature c1842-43.svg'}, {'propertyName': 'RSL ID (person)', 'propertyId': 'P947', 'value': '000080865'}, {'propertyName': 'RSL ID (person)', 'propertyId': 'P947', 'value': '000080865'}, {'propertyName': 'given name', 'propertyId': 'P735', 'value': 'Q19819785'}, {'propertyName': 'Project Gutenberg author ID', 'propertyId': 'P1938', 'value': '251'}, {'propertyName': 'AlloCiné person ID', 'propertyId': 'P1266', 'value': '37056'}, {'propertyName': 'Open Library ID', 'propertyId': 'P648', 'value': 'OL29097A'}, {'propertyName': 'languages spoken, written or signed', 'propertyId': 'P1412', 'value': 'Q150'}, {'propertyName': 'religion', 'propertyId': 'P140', 'value': 'Q15934597'}, {'propertyName': 'DBNL author ID', 'propertyId': 'P723', 'value': 'balz001'}, {'propertyName': 'National Gallery of Art artist ID', 'propertyId': 'P2252', 'value': '38326'}, {'propertyName': 'AGORHA person/institution ID', 'propertyId': 'P2342', 'value': '147399'}, {'propertyName': 'child', 'propertyId': 'P40', 'value': 'Q17350135'}, {'propertyName': 'movement', 'propertyId': 'P135', 'value': 'Q667661'}, {'propertyName': 'British Museum person-institution', 'propertyId': 'P1711', 'value': '18293'}, {'propertyName': 'NILF author id', 'propertyId': 'P2191', 'value': 'NILF11433'}, {'propertyName': 'SFDb person ID', 'propertyId': 'P2168', 'value': '144872'}, {'propertyName': 'PORT person ID', 'propertyId': 'P2435', 'value': '249736'}, {'propertyName': 'AllMovie artist ID', 'propertyId': 'P2019', 'value': 'p315607'}, {'propertyName': 'FAST ID', 'propertyId': 'P2163', 'value': '38270'}, {'propertyName': 'National Portrait Gallery (London) person ID', 'propertyId': 'P1816', 'value': 'mp121282'}, {'propertyName': 'WomenWriters ID', 'propertyId': 'P2533', 'value': '9cbb103f-961b-4085-a071-856a3f825680'}, {'propertyName': 'BNE ID', 'propertyId': 'P950', 'value': 'XX1721276'}, {'propertyName': 'image', 'propertyId': 'P18', 'value': 'Honoré de Balzac (1842) Detail.jpg'}, {'propertyName': 'Scope.dk person ID', 'propertyId': 'P2519', 'value': '30857'}, {'propertyName': 'pseudonym', 'propertyId': 'P742', 'value': 'Horace de Saint-Aubin'}, {'propertyName': 'pseudonym', 'propertyId': 'P742', 'value': 'Horace de Saint-Aubin'}, {'propertyName': 'pseudonym', 'propertyId': 'P742', 'value': 'Horace de Saint-Aubin'}, {'propertyName': 'ČSFD person ID', 'propertyId': 'P2605', 'value': '110957'}, {'propertyName': 'Filmportal ID', 'propertyId': 'P2639', 'value': '11976ed04eeb4302b269b9c280a5bca7'}, {'propertyName': 'Kinopoisk person ID', 'propertyId': 'P2604', 'value': '72197'}, {'propertyName': 'BVMC person ID', 'propertyId': 'P2799', 'value': '382'}, {'propertyName': 'BiblioNet author ID', 'propertyId': 'P2188', 'value': '3183'}, {'propertyName': 'LibriVox author ID', 'propertyId': 'P1899', 'value': '86'}, {'propertyName': 'Les Archives du Spectacle ID', 'propertyId': 'P1977', 'value': '13315'}, {'propertyName': 'BAV ID', 'propertyId': 'P1017', 'value': 'ADV11284673'}, {'propertyName': 'BAV ID', 'propertyId': 'P1017', 'value': 'ADV11284673'}, {'propertyName': 'BAV ID', 'propertyId': 'P1017', 'value': 'ADV11284673'}, {'propertyName': 'BAV ID', 'propertyId': 'P1017', 'value': 'ADV11284673'}, {'propertyName': 'EGAXA ID', 'propertyId': 'P1309', 'value': '000903048'}, {'propertyName': 'NUKAT (WarsawU) authorities', 'propertyId': 'P1207', 'value': 'n93080159'}, {'propertyName': 'Gran Enciclopèdia Catalana ID', 'propertyId': 'P1296', 'value': '0007162'}, {'propertyName': 'employer', 'propertyId': 'P108', 'value': 'Q216047'}, {'propertyName': 'name in native language', 'propertyId': 'P1559', 'value': {'text': 'Honoré de Balzac', 'language': 'fr'}}, {'propertyName': 'Internet Broadway Database person ID', 'propertyId': 'P1220', 'value': '4418'}, {'propertyName': 'Internet Broadway Database person ID', 'propertyId': 'P1220', 'value': '4418'}, {'propertyName': 'National Library of Greece ID', 'propertyId': 'P3348', 'value': '61052'}, {'propertyName': 'sibling', 'propertyId': 'P3373', 'value': 'Q3218795'}, {'propertyName': 'Quora topic ID', 'propertyId': 'P3417', 'value': 'Honoré-De-Balzac'}, {'propertyName': 'manner of death', 'propertyId': 'P1196', 'value': 'Q3739104'}, {'propertyName': 'SNAC ID', 'propertyId': 'P3430', 'value': 'w6qr534v'}, {'propertyName': 'award received', 'propertyId': 'P166', 'value': 'Q163700'}, {'propertyName': 'openMLOL author ID', 'propertyId': 'P3762', 'value': '4244'}, {'propertyName': 'Great Russian Encyclopedia Online ID', 'propertyId': 'P2924', 'value': '1848201'}, {'propertyName': 'Babelio author ID', 'propertyId': 'P3630', 'value': '344660'}, {'propertyName': 'Babelio author ID', 'propertyId': 'P3630', 'value': '344660'}, {'propertyName': 'Bridgeman artist ID', 'propertyId': 'P3965', 'value': '20170'}, {'propertyName': 'notable work', 'propertyId': 'P800', 'value': 'Q240617'}, {'propertyName': 'notable work', 'propertyId': 'P800', 'value': 'Q50188'}, {'propertyName': 'notable work', 'propertyId': 'P800', 'value': 'Q2092894'}, {'propertyName': 'notable work', 'propertyId': 'P800', 'value': 'Q1373644'}, {'propertyName': 'notable work', 'propertyId': 'P800', 'value': 'Q1529231'}, {'propertyName': 'notable work', 'propertyId': 'P800', 'value': 'Q1142149'}, {'propertyName': 'notable work', 'propertyId': 'P800', 'value': 'Q2631465'}, {'propertyName': 'BNA authority ID', 'propertyId': 'P3788', 'value': '000035613'}, {'propertyName': 'student of', 'propertyId': 'P1066', 'value': 'Q157324'}, {'propertyName': 'student of', 'propertyId': 'P1066', 'value': 'Q318337'}, {'propertyName': 'student of', 'propertyId': 'P1066', 'value': 'Q434346'}, {'propertyName': 'academic degree', 'propertyId': 'P512', 'value': 'Q798137'}, {'propertyName': 'member of', 'propertyId': 'P463', 'value': 'Q3488144'}, {'propertyName': 'Artnet artist ID', 'propertyId': 'P3782', 'value': 'honore-de-balzac'}, {'propertyName': 'influenced by', 'propertyId': 'P737', 'value': 'Q79025'}, {'propertyName': 'Encyclopædia Britannica Online ID', 'propertyId': 'P1417', 'value': 'biography/Honore-de-Balzac'}])
('French', 'NORP', 'Q121842', 'French people', "The '''French''' are an [[ethnic group]] and [[nation]] who are identified with the country of [[France]]. This connection may be legal, historical, or cultural.", 'wikipedia-en', [{'propertyName': 'NDL Auth ID', 'propertyId': 'P349', 'value': '00563748'}, {'propertyName': 'GND ID', 'propertyId': 'P227', 'value': '4018199-6'}, {'propertyName': "topic's main category", 'propertyId': 'P910', 'value': 'Q3919837'}, {'propertyName': 'Freebase ID', 'propertyId': 'P646', 'value': '/m/03ts0c'}, {'propertyName': 'instance of', 'propertyId': 'P31', 'value': 'Q33829'}, {'propertyName': 'instance of', 'propertyId': 'P31', 'value': 'Q231002'}, {'propertyName': 'instance of', 'propertyId': 'P31', 'value': 'Q41710'}, {'propertyName': 'image', 'propertyId': 'P18', 'value': 'French people - mosaic.PNG'}, {'propertyName': 'Commons category', 'propertyId': 'P373', 'value': 'People of France'}, {'propertyName': 'demonym', 'propertyId': 'P1549', 'value': {'text': 'francez', 'language': 'ro'}}, {'propertyName': 'demonym', 'propertyId': 'P1549', 'value': {'text': 'francez', 'language': 'ro'}}, {'propertyName': 'Library of Congress authority ID', 'propertyId': 'P244', 'value': 'sh85051757'}, {'propertyName': 'Quora topic ID', 'propertyId': 'P3417', 'value': 'French-Ethnicity-and-People'}])
('Paris', 'GPE', 'Q90', 'Paris', "'''Paris''' is the [[Capital city|capital]] and most populous [[city]] of [[France]], with an administrative-limits area of and a 2015 population of 2,229,621. The city is a [[Communes of France|commune]] and [[Departments of France|department]], and the capital-heart of the [[Île-de-France]] ''[[Region in France|region]]'' (colloquially known as the 'Paris Region'), whose 12,142,802 2016 population represents roughly 18 percent of the population of France. By the 17th century, Paris had become one of Europe's major centres of finance, commerce, fashion, science, and the arts, a position that it retains still today. The Paris Region had a [[GDP]] of €649.6 billion (US $763.4 billion) in 2014, accounting for 30.4 percent of the GDP of France. According to official estimates, in 2013-14 the Paris Region had [[List of cities by GDP|the third-highest GDP in the world and the largest regional GDP in the EU]].", 'wikipedia-en', [{'propertyName': 'coat of arms', 'propertyId': 'P237', 'value': 'Q1925366'}, {'propertyName': "topic's main Wikimedia portal", 'propertyId': 'P1151', 'value': 'Q8253667'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q161741'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q209549'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q223140'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q230127'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q238723'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q245546'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q259463'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q270230'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q275118'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q163948'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q169293'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q171689'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q175129'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q187153'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q191066'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q194420'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q197297'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q200126'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q204622'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q210720'}, {'propertyName': 'contains administrative territorial entity', 'propertyId': 'P150', 'value': 'Q3278478'}, {'propertyName': 'motto text', 'propertyId': 'P1451', 'value': {'text': 'Fluctuat nec mergitur', 'language': 'la'}}, {'propertyName': 'category for people born here', 'propertyId': 'P1464', 'value': 'Q9226347'}, {'propertyName': 'Dewey Decimal Classification', 'propertyId': 'P1036', 'value': '2--44361'}, {'propertyName': 'country', 'propertyId': 'P17', 'value': 'Q142'}, {'propertyName': 'instance of', 'propertyId': 'P31', 'value': 'Q5119'}, {'propertyName': 'instance of', 'propertyId': 'P31', 'value': 'Q22927616'}, {'propertyName': 'instance of', 'propertyId': 'P31', 'value': 'Q6465'}, {'propertyName': 'instance of', 'propertyId': 'P31', 'value': 'Q866196'}, {'propertyName': 'instance of', 'propertyId': 'P31', 'value': 'Q1549591'}, {'propertyName': 'instance of', 'propertyId': 'P31', 'value': 'Q515'}, {'propertyName': 'located in the administrative territorial entity', 'propertyId': 'P131', 'value': 'Q13917'}, {'propertyName': 'located in the administrative territorial entity', 'propertyId': 'P131', 'value': 'Q1142326'}, {'propertyName': 'located in the administrative territorial entity', 'propertyId': 'P131', 'value': 'Q70972'}, {'propertyName': 'image', 'propertyId': 'P18', 'value': 'Airplane view Paris 01.jpg'}, {'propertyName': 'coat of arms image', 'propertyId': 'P94', 'value': 'Grandes Armes de Paris.svg'}, {'propertyName': 'locator map image', 'propertyId': 'P242', 'value': 'Paris-Position.svg'}, {'propertyName': 'locator map image', 'propertyId': 'P242', 'value': 'Paris-Position.svg'}, {'propertyName': 'legislative body', 'propertyId': 'P194', 'value': 'Q775994'}, {'propertyName': 'BnF ID', 'propertyId': 'P268', 'value': '152821567'}, {'propertyName': 'Library of Congress authority ID', 'propertyId': 'P244', 'value': 'n79058874'}, {'propertyName': 'SUDOC authorities', 'propertyId': 'P269', 'value': '080467008'}, {'propertyName': 'VIAF ID', 'propertyId': 'P214', 'value': '158822968'}, {'propertyName': 'INSEE municipality code', 'propertyId': 'P374', 'value': '75056'}, {'propertyName': 'GND ID', 'propertyId': 'P227', 'value': '4044660-8'}, {'propertyName': 'NDL Auth ID', 'propertyId': 'P349', 'value': '00629026'}, {'propertyName': 'flag', 'propertyId': 'P163', 'value': 'Q659058'}, {'propertyName': 'Commons category', 'propertyId': 'P373', 'value': 'Paris'}, {'propertyName': 'OpenStreetMap Relation identifier', 'propertyId': 'P402', 'value': '71525'}, {'propertyName': 'ISO 3166-2 code', 'propertyId': 'P300', 'value': 'FR-75'}, {'propertyName': 'located in time zone', 'propertyId': 'P421', 'value': 'Q6655'}, {'propertyName': 'located in time zone', 'propertyId': 'P421', 'value': 'Q6723'}, {'propertyName': 'ISNI', 'propertyId': 'P213', 'value': '0000 0001 2114 268X'}, {'propertyName': 'coordinate location', 'propertyId': 'P625', 'value': {'latitude': 48.856577777778, 'longitude': 2.3518277777778, 'altitude': None, 'precision': 2.7777777777778e-06, 'globe': 'http://www.wikidata.org/entity/Q2'}}, {'propertyName': 'inception', 'propertyId': 'P571', 'value': {'time': '-0300-00-00T00:00:00Z', 'timezone': 0, 'before': 0, 'after': 0, 'precision': 9, 'calendarmodel': 'http://www.wikidata.org/entity/Q1985786'}}, {'propertyName': 'award received', 'propertyId': 'P166', 'value': 'Q2727598'}, {'propertyName': 'award received', 'propertyId': 'P166', 'value': 'Q2990283'}, {'propertyName': 'award received', 'propertyId': 'P166', 'value': 'Q163700'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q12543'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q12761'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q12788'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q241021'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q253721'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q234728'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q135265'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q172455'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q189153'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q193929'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q234743'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q48958'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q166640'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q201982'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q208889'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q160506'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q205632'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q209086'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q175999'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q256004'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q208943'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q193370'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q18102'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q193819'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q193899'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q212274'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q609134'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q274327'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q212793'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q193877'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q135104'}, {'propertyName': 'shares border with', 'propertyId': 'P47', 'value': 'Q640102'}, {'propertyName': 'official website', 'propertyId': 'P856', 'value': 'http://www.paris.fr/'}, {'propertyName': "topic's main category", 'propertyId': 'P910', 'value': 'Q5626403'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q2851133'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q256294'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q1685859'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q2105'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q959708'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q289303'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q677730'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q601266'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q1684642'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q1685102'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q1986521'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q3131449'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q2596877'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q656015'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q947901'}, {'propertyName': 'head of government', 'propertyId': 'P6', 'value': 'Q1685301'}, {'propertyName': 'named after', 'propertyId': 'P138', 'value': 'Q656902'}, {'propertyName': 'sister city', 'propertyId': 'P190', 'value': 'Q220'}, {'propertyName': 'page banner', 'propertyId': 'P948', 'value': 'Paris banner.jpg'}, {'propertyName': 'DMOZ ID', 'propertyId': 'P998', 'value': 'Regional/Europe/France/Regions/Ile-de-France/Paris/'}, {'propertyName': 'DMOZ ID', 'propertyId': 'P998', 'value': 'Regional/Europe/France/Regions/Ile-de-France/Paris/'}, {'propertyName': 'DMOZ ID', 'propertyId': 'P998', 'value': 'Regional/Europe/France/Regions/Ile-de-France/Paris/'}, {'propertyName': 'DMOZ ID', 'propertyId': 'P998', 'value': 'Regional/Europe/France/Regions/Ile-de-France/Paris/'}, {'propertyName': 'DMOZ ID', 'propertyId': 'P998', 'value': 'Regional/Europe/France/Regions/Ile-de-France/Paris/'}, {'propertyName': 'DMOZ ID', 'propertyId': 'P998', 'value': 'Regional/Europe/France/Regions/Ile-de-France/Paris/'}, {'propertyName': 'DMOZ ID', 'propertyId': 'P998', 'value': 'Regional/Europe/France/Regions/Ile-de-France/Paris/'}, {'propertyName': 'DMOZ ID', 'propertyId': 'P998', 'value': 'Regional/Europe/France/Regions/Ile-de-France/Paris/'}, {'propertyName': 'MusicBrainz area ID', 'propertyId': 'P982', 'value': 'dc10c22b-e510-4006-8b7f-fecb4f36436e'}, {'propertyName': 'Freebase ID', 'propertyId': 'P646', 'value': '/m/05qtj'}, {'propertyName': 'coordinate of northernmost point', 'propertyId': 'P1332', 'value': {'latitude': 48.902156, 'longitude': 2.3844292, 'altitude': None, 'precision': 0.0001, 'globe': 'http://www.wikidata.org/entity/Q2'}}, {'propertyName': 'coordinate of southernmost point', 'propertyId': 'P1333', 'value': {'latitude': 48.8155755, 'longitude': 2.3444967, 'altitude': None, 'precision': 0.0001, 'globe': 'http://www.wikidata.org/entity/Q2'}}, {'propertyName': 'coordinate of westernmost point', 'propertyId': 'P1335', 'value': {'latitude': 48.854199, 'longitude': 2.224122, 'altitude': None, 'precision': 0.0001, 'globe': 'http://www.wikidata.org/entity/Q2'}}, {'propertyName': 'coordinate of easternmost point', 'propertyId': 'P1334', 'value': {'latitude': 48.8363848, 'longitude': 2.4697602, 'altitude': None, 'precision': 0.0001, 'globe': 'http://www.wikidata.org/entity/Q2'}}, {'propertyName': 'Gran Enciclopèdia Catalana ID', 'propertyId': 'P1296', 'value': '0049060'}, {'propertyName': 'category for people who died here', 'propertyId': 'P1465', 'value': 'Q9846779'}, {'propertyName': 'GeoNames ID', 'propertyId': 'P1566', 'value': '2968815'}, {'propertyName': 'GeoNames ID', 'propertyId': 'P1566', 'value': '2968815'}, {'propertyName': 'category for films shot at this location', 'propertyId': 'P1740', 'value': 'Q8458184'}, {'propertyName': 'place name sign', 'propertyId': 'P1766', 'value': 'Paris (town sign).jpg'}, {'propertyName': 'category of associated people', 'propertyId': 'P1792', 'value': 'Q8964470'}, {'propertyName': 'official name', 'propertyId': 'P1448', 'value': {'text': 'Paris', 'language': 'fr'}}, {'propertyName': 'population', 'propertyId': 'P1082', 'value': {'amount': '+2240621', 'unit': '1', 'upperBound': '+2285434', 'lowerBound': '+2195808'}}, {'propertyName': 'population', 'propertyId': 'P1082', 'value': {'amount': '+2240621', 'unit': '1', 'upperBound': '+2285434', 'lowerBound': '+2195808'}}, {'propertyName': 'population', 'propertyId': 'P1082', 'value': {'amount': '+2240621', 'unit': '1', 'upperBound': '+2285434', 'lowerBound': '+2195808'}}, {'propertyName': 'population', 'propertyId': 'P1082', 'value': {'amount': '+2240621', 'unit': '1', 'upperBound': '+2285434', 'lowerBound': '+2195808'}}, {'propertyName': 'population', 'propertyId': 'P1082', 'value': {'amount': '+2240621', 'unit': '1', 'upperBound': '+2285434', 'lowerBound': '+2195808'}}, {'propertyName': 'population', 'propertyId': 'P1082', 'value': {'amount': '+2240621', 'unit': '1', 'upperBound': '+2285434', 'lowerBound': '+2195808'}}, {'propertyName': 'postal code', 'propertyId': 'P281', 'value': '75001–75020'}, {'propertyName': 'postal code', 'propertyId': 'P281', 'value': '75001–75020'}, {'propertyName': 'capital of', 'propertyId': 'P1376', 'value': 'Q142'}, {'propertyName': 'capital of', 'propertyId': 'P1376', 'value': 'Q1110'}, {'propertyName': 'capital of', 'propertyId': 'P1376', 'value': 'Q13917'}, {'propertyName': 'capital of', 'propertyId': 'P1376', 'value': 'Q70972'}, {'propertyName': 'capital of', 'propertyId': 'P1376', 'value': 'Q71092'}, {'propertyName': 'capital of', 'propertyId': 'P1376', 'value': 'Q106577'}, {'propertyName': 'capital of', 'propertyId': 'P1376', 'value': 'Q207162'}, {'propertyName': 'capital of', 'propertyId': 'P1376', 'value': 'Q212429'}, {'propertyName': 'capital of', 'propertyId': 'P1376', 'value': 'Q1142326'}, {'propertyName': 'capital of', 'propertyId': 'P1376', 'value': 'Q16665915'}, {'propertyName': 'NUTS code', 'propertyId': 'P605', 'value': 'FR101'}, {'propertyName': 'replaces', 'propertyId': 'P1365', 'value': 'Q270273'}, {'propertyName': 'replaces', 'propertyId': 'P1365', 'value': 'Q1142326'}, {'propertyName': 'Twitter username', 'propertyId': 'P2002', 'value': 'Paris'}, {'propertyName': 'Facebook profile ID', 'propertyId': 'P2013', 'value': 'paris'}, {'propertyName': 'area', 'propertyId': 'P2046', 'value': {'amount': '+105.4', 'unit': 'http://www.wikidata.org/entity/Q712226'}}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q4173137'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q19180675'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q602358'}, {'propertyName': 'described by source', 'propertyId': 'P1343', 'value': 'Q2041543'}, {'propertyName': 'FAST ID', 'propertyId': 'P2163', 'value': '1205283'}, {'propertyName': 'GNS Unique Feature ID', 'propertyId': 'P2326', 'value': '-1456928'}, {'propertyName': 'list of monuments', 'propertyId': 'P1456', 'value': 'Q1403319'}, {'propertyName': 'list of monuments', 'propertyId': 'P1456', 'value': 'Q3252156'}, {'propertyName': 'Commons gallery', 'propertyId': 'P935', 'value': 'Paris'}, {'propertyName': 'Facebook Places ID', 'propertyId': 'P1997', 'value': '110774245616525'}, {'propertyName': 'diocese', 'propertyId': 'P708', 'value': 'Q1242250'}, {'propertyName': 'Encyclopædia Britannica Online ID', 'propertyId': 'P1417', 'value': 'place/Paris'}, {'propertyName': 'currency', 'propertyId': 'P38', 'value': 'Q4916'}, {'propertyName': 'patron saint', 'propertyId': 'P417', 'value': 'Q235863'}, {'propertyName': 'continent', 'propertyId': 'P30', 'value': 'Q46'}, {'propertyName': 'highest point', 'propertyId': 'P610', 'value': 'Q1440664'}, {'propertyName': 'foods traditionally associated', 'propertyId': 'P868', 'value': 'Q21129738'}, {'propertyName': 'demonym', 'propertyId': 'P1549', 'value': {'text': 'Parisien', 'language': 'fr'}}, {'propertyName': 'demonym', 'propertyId': 'P1549', 'value': {'text': 'Parisien', 'language': 'fr'}}, {'propertyName': 'demonym', 'propertyId': 'P1549', 'value': {'text': 'Parisien', 'language': 'fr'}}, {'propertyName': 'INSEE department code', 'propertyId': 'P2586', 'value': '75'}, {'propertyName': 'located next to body of water', 'propertyId': 'P206', 'value': 'Q1471'}, {'propertyName': 'elevation above sea level', 'propertyId': 'P2044', 'value': {'amount': '+28', 'unit': 'http://www.wikidata.org/entity/Q11573', 'upperBound': '+29', 'lowerBound': '+27'}}, {'propertyName': 'permanent duplicated item', 'propertyId': 'P2959', 'value': 'Q20514743'}, {'propertyName': "topic's main template", 'propertyId': 'P1424', 'value': 'Q18220037'}, {'propertyName': 'local dialing code', 'propertyId': 'P473', 'value': '1'}, {'propertyName': 'part of', 'propertyId': 'P361', 'value': 'Q16665915'}, {'propertyName': 'nickname', 'propertyId': 'P1449', 'value': {'text': 'Ville-Lumière', 'language': 'fr'}}, {'propertyName': 'nickname', 'propertyId': 'P1449', 'value': {'text': 'Ville-Lumière', 'language': 'fr'}}, {'propertyName': 'Encyclopædia Universalis Online ID', 'propertyId': 'P3219', 'value': 'paris'}, {'propertyName': 'Guardian topic ID', 'propertyId': 'P3106', 'value': 'world/paris'}, {'propertyName': 'IATA airport code', 'propertyId': 'P238', 'value': 'PAR'}, {'propertyName': 'NE.se ID', 'propertyId': 'P3222', 'value': 'paris'}, {'propertyName': 'NE.se ID', 'propertyId': 'P3222', 'value': 'paris'}, {'propertyName': 'Quora topic ID', 'propertyId': 'P3417', 'value': 'Paris'}, {'propertyName': 'MeSH ID', 'propertyId': 'P486', 'value': 'D010297'}, {'propertyName': 'Ringgold ID', 'propertyId': 'P3500', 'value': '55653'}, {'propertyName': 'Nomisma ID', 'propertyId': 'P2950', 'value': 'paris'}, {'propertyName': 'nighttime view', 'propertyId': 'P3451', 'value': 'Eiffel Tower from the Tour Montparnasse, 1 May 2012 N2.jpg'}, {'propertyName': 'catalog', 'propertyId': 'P972', 'value': 'Q5460604'}, {'propertyName': 'subreddit', 'propertyId': 'P3984', 'value': 'paris'}, {'propertyName': 'YSO ID', 'propertyId': 'P2347', 'value': '104996'}, {'propertyName': 'Instagram location ID', 'propertyId': 'P4173', 'value': '6889842'}, {'propertyName': 'history of topic', 'propertyId': 'P2184', 'value': 'Q845625'}, {'propertyName': 'pronunciation audio', 'propertyId': 'P443', 'value': 'Fr-Paris.ogg'}, {'propertyName': 'flag image', 'propertyId': 'P41', 'value': 'Flag of Paris with coat of arms.svg'}, {'propertyName': 'National Archives Identifier', 'propertyId': 'P1225', 'value': '10045153'}])
```

It is possible to filter other identifiers to get a more readable output, for example, 
if you only searched for identifiers from the Library of Congress (P244) and VIAF (P214)
specify `True` in the `extra_info` parameter and define a list that contains properties 
in the `filter_statements` parameter in the component configuration:

```Python

import spacy 

text_en = "Victor Hugo and Honoré de Balzac are French writers who lived in Paris."

nlp_model_en = spacy.load("en_core_web_sm")

# specify configuration:
nlp_model_en.add_pipe("entityfishing", config={"extra_info": True, "filter_statements":['P214', 'P244']})

doc_en = nlp_model_en(text_en)

# Access to description with ent._.description:
for ent in doc_en.ents:
        print((ent.text, ent.label_, ent._.kb_qid, ent._.other_ids))
```
```
('Victor Hugo', 'PERSON', 'Q535', [{'propertyName': 'VIAF ID', 'propertyId': 'P214', 'value': '9847974'}, {'propertyName': 'Library of Congress authority ID', 'propertyId': 'P244', 'value': 'n79091479'}])
('Honoré de Balzac', 'PERSON', 'Q9711', [{'propertyName': 'VIAF ID', 'propertyId': 'P214', 'value': '29529595'}, {'propertyName': 'Library of Congress authority ID', 'propertyId': 'P244', 'value': 'n79071094'}])
('French', 'NORP', 'Q121842', [{'propertyName': 'Library of Congress authority ID', 'propertyId': 'P244', 'value': 'sh85051757'}])
('Paris', 'GPE', 'Q90', [{'propertyName': 'Library of Congress authority ID', 'propertyId': 'P244', 'value': 'n79058874'}, {'propertyName': 'VIAF ID', 'propertyId': 'P214', 'value': '158822968'}])
```

### Use other language

By default, disambiguation model resources are set to English, to use an other language, specify the language code in the `language` parameter in the component configuration:

```Python
import spacy 

text_fr = "La bataille d'El-Alamein en Égypte oppose la 8e armée britannique dirigée par Bernard Montgomery aux divisions d'Erwin Rommel."

nlp_model_fr = spacy.load("fr_core_news_sm")

nlp_model_fr.add_pipe("entityfishing", config={"language": "fr"})

doc_fr = nlp_model_fr(text_fr)

for ent in doc_fr.ents:
        print((ent.text, ent.label_, ent._.kb_qid, ent._.url_wikidata))
```
```
("bataille d'El-Alamein", 'MISC', 'Q153376', 'https://www.wikidata.org/wiki/Q153376')
('Égypte', 'LOC', 'Q79', 'https://www.wikidata.org/wiki/Q79')
('Bernard Montgomery', 'PER', 'Q152025', 'https://www.wikidata.org/wiki/Q152025')
('Erwin Rommel', 'PER', 'Q14060', 'https://www.wikidata.org/wiki/Q14060')
```

To consult the languages available in Entity-Fishing follow this [link](https://nerd.readthedocs.io/en/latest/restAPI.html#supported-languages).

### Get information about Entity fishing API response

The raw response of the Entity-fishing API can be accessed in the doc object:

```
doc._.annotations
```
```
{'runtime': 18, 
 'nbest': False, 
 'text': "La bataille d'El-Alamein en Égypte oppose la 8e armée britannique dirigée par Bernard Montgomery aux divisions d'Erwin Rommel.", 
 'language': {'lang': 'fr', 'conf': 0.0}, 
 'global_categories': [
  {'weight': 0.01960784313725492, 'source': 'wikipedia-fr', 'category': 'Général allemand', 'page_id': 94081}, 
  {'weight': 0.01960784313725492, 'source': 'wikipedia-fr', 'category': "Chevalier grand-croix de l'ordre du Bain", 'page_id': 3399090}, 
  {'weight': 0.01960784313725492, 'source': 'wikipedia-fr', 'category': 'Naissance à Heidenheim an der Brenz', 'page_id': 8396804}
  ], 
  'entities': [
  {'rawName': "bataille d'El-Alamein", 'offsetStart': 1, 'offsetEnd': 6, 'nerd_score': 1, 'nerd_selection_score': 0.9198, 'wikipediaExternalRef': 261761, 'wikidataId': 'Q153376', 'domains': ['Military']},
  {'rawName': 'Égypte', 'offsetStart': 7, 'offsetEnd': 8, 'nerd_score': 1, 'nerd_selection_score': 0.6437, 'wikipediaExternalRef': 4011, 'wikidataId': 'Q79', 'domains': ['Geology']}, 
  {'rawName': 'Bernard Montgomery', 'offsetStart': 15, 'offsetEnd': 17, 'nerd_score': 1, 'nerd_selection_score': 0.9965, 'wikipediaExternalRef': 46225, 'wikidataId': 'Q152025', 'domains': ['Biology', 'Military']}, 
  {'rawName': 'Erwin Rommel', 'offsetStart': 20, 'offsetEnd': 22, 'nerd_score': 1, 'nerd_selection_score': 0.9955, 'wikipediaExternalRef': 46221, 'wikidataId': 'Q14060', 'domains': ['Military']}
  ]
 }
```

To access to query metadata for the response by Entity-Fishing API:

```
doc._.metadata
```
```
{'status_code': 200, 'reason': 'OK', 'ok': True, 'encoding': 'utf-8'}
```

## Configuration parameters

```
- api_ef_base          : URL of the Entity-Fishing API endpoint. Defaults to Huma-Num server.
- language             : Specify language of KB ressources for Entity-Fishing API. Defaults to "en".
- extra_info           : Get extra Wikidata informations about entity from service "concept look-up" 
                         of Entity-Fishing API as a short Wikipedia description, a normalised term, others KB ids. Defaults to false.
- filter_statements    : If `extra_info` set to True, filter other KB ids in output eg. ['P214', 'P244' ...] .Defaults to empty list.  
```

## Attributes

* **Doc** extensions:

    ```
   doc._.annotations :  Raw response from Entity-Fishing API.
   doc._.metadata    :  Raw information about request and response from Entity-Fishing API.
   ```

* **Span** extensions:

   ```
   default extensions 
   ------------------
  
   span._.kb_qid             : Wikidata identifier (QID).
   span._.url_wikidata       : URL to Wikidata ressource.
   span._.wikipedia_page_ref : Identifier of the concept in Wikipedia.
   span._.nerd_score         : Selection confidence score for the disambiguated entity.
  
   extra extensions (if `extra_info` set to True)
   ----------------------------------------------
   
   span._.description     : Short Wikipedia definition of the concept.
   span._.src_description : The name of Wikipedia KB from which the definition comes from (eg. wikipedia-en).
   span._.normal_term     : The normalised term name.
   span._.other_ids       : Others statements in KB relates to Wikipedia concept.
   ```

For details on Entity-Fishing response, follow this [link](https://nerd.readthedocs.io/en/latest/restAPI.html#response)

## Recommendations

If Entity-fishing is deployed locally or on specific server, specify the URL of the new Entity-fishing API endpoint in the config:

```
nlp.add_pipe("entityfishing", config={"api_ef_base": "<api-endpoint>"})
```

This can be useful, if you work with more recent dumps of Wikidata knowledge base or increase speed in the pipeline.

To install your own instance of Entity-Fishing, follow this [link](https://nerd.readthedocs.io/en/latest/build.html).

## Visualise results

To visualise the named entities and their wikidata links, use the manual option of displaCy:

```Python
import spacy 

text_fr = "La bataille d'El-Alamein en Égypte oppose la 8e armée britannique dirigée par Bernard Montgomery aux divisions d'Erwin Rommel."
nlp_model_fr = spacy.load("fr_core_news_sm")
nlp_model_fr.add_pipe("entityfishing", config={"language": "fr"})
doc_fr = nlp_model_fr(text_fr)

options = {
    "ents": ["MISC", "LOC", "PER"],
    "colors": {"LOC": "#82e0aa", "PER": "#85c1e9", "MISC": "#f0b27a"}
}

params = {"text": doc_fr.text,
          "ents": [{"start": ent.start_char,
                    "end": ent.end_char,
                    "label": ent.label_,
                    "kb_id": ent._.kb_qid,
                    "kb_url": ent._.url_wikidata}
                     for ent in doc_fr.ents],
          "title": None}

spacy.displacy.serve(params, style="ent", manual=True, options=options)
```

<img src="./docs/vizualizer.png" alt="vizualizer" width="1050" height="80"/>

The visualizer is serving on http://0.0.0.0:5000

## External ressources

- [spaCy homepage](https://spacy.io/)
- [spaCy GitHub](https://github.com/explosion/spaCy)


- [Entity-Fishing GitHub](https://github.com/kermitt2/entity-fishing)
- [Entity-Fishing web client](http://nerd.huma-num.fr/nerd/)
- [Entity-Fishing documentation](https://nerd.readthedocs.io/en/latest/)

## Details

This component is experimental, it may be used for research, and it may evolve in the future.

Entity-Fishing is tool created by Patrice Lopez (SCIENCE-MINER), with contributions of Inria Paris, and distributed under Apache 2.0 license. 
