#!/usr/bin/env python3
"""check a year sequence to find gaps and anomalies and propose fixes"""

import sys
import time
import json
import urllib.request
import urllib.parse
import zlib

from wd_constants import lang_order

def get_label(obj):
    """get appropriate label, using language fallback chain"""
    has_sitelinks = 'sitelinks' in obj
    for lang in lang_order:
        site = lang + 'wiki'
        if has_sitelinks and site in obj['sitelinks']:
            return obj['sitelinks'][site]['title']
        elif lang in obj['labels']:
            return obj['labels'][lang]['value']
    return None

current_year = 2023

year_seqs = {
    'health_medicine': {
        'start_id': 'Q25389697',
        'end_id': 'Q115950283',
        'start_year': 1097,  # earliest "[year] in health and medicine"
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' en santé et médecine', 'lang': 'fr'},  # label query for when sequence fails
    },
    'pol_gov': {
        'start_id': 'Q97214391',
        'end_id': 'Q110903595',
        'start_year': 996,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in politics', 'lang': 'en'},
    },
    'literature': {
        'start_id': 'Q56342913',
        'end_id': 'Q111207022',
        'start_year': 1400,
        'end_year': current_year,
        # 'search_query': {'prefix': '', 'suffix': ' en littérature', 'lang': 'fr'},
        'search_query': {'prefix': '', 'suffix': ' w literaturze', 'lang': 'pl'}
    },
    'film': {
        'start_id': 'Q11968847',
        'end_id': 'Q113367507',
        'start_year': 1881,
        'end_year': 2024,
        'search_query': {'prefix': '', 'suffix': ' in film', 'lang': 'en'},
    },
    'art': {
        'start_id': 'Q21487890',
        'end_id': 'Q115986977',
        'start_year': 1486,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in art', 'lang': 'en'},
    },
    'art2': {
        'start_id': 'Q11982536',
        'end_id': 'Q3408074',
        'start_year': 1491,
        'end_year': 1500,
        'search_query': {'prefix': 'Kunståret ', 'suffix': '', 'lang': 'nb'},
    },
    'science': {
        'start_id': 'Q838114',
        'end_id': 'Q113574527',
        'start_year': 1500,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in science', 'lang': 'en'},
    },
    'science2': {
        'start_id': 'Q65141297',
        'end_id': 'Q80719630',
        'start_year': 1439,
        'end_year': 2022,
        'search_query': {'prefix': 'Vitenskapsåret ', 'suffix': '', 'lang': 'en'},
    },
    'united_states': {
        'start_id': 'Q2809402',
        'end_id': 'Q115805162',
        'start_year': 1776,
        'end_year': 2024,
        'search_query': {'prefix': '', 'suffix': ' in the United States', 'lang': 'en'},
    },
    'architecture': {
        'start_id': 'Q11958905',
        'end_id': 'Q115942407',
        'start_year': 1480,
        'end_year': current_year,
        'search_query': {'prefix': 'Arkitekturåret ', 'suffix': '', 'lang': 'nb'},
    },
    'architecture2': {
        'start_id': 'Q11958913',
        'end_id': 'Q110263957',
        'start_year': 1500,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' во архитектурата', 'lang': 'mk'},
    },
    'architecture3': {
        'start_id': 'Q65145859',
        'end_id': 'Q21484944',
        'start_year': 1400,
        'end_year': 1429,
        'search_query': {'prefix': 'Arkitekturåret ', 'suffix': '', 'lang': 'nb'},
    },
    'television': {
        'start_id': 'Q9547165',
        'end_id': 'Q113632768',
        'start_year': 1900,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in television', 'lang': 'en'},
    },
    'rail_transport': {
        'start_id': 'Q2809695',
        'end_id': 'Q108920929',
        'start_year': 1800,
        'end_year': 2030,
        'search_query': {'prefix': '', 'suffix': ' dans les chemins de fer', 'lang': 'fr'},
    },
    'law': {
        'start_id': 'Q16024737',
        'end_id': 'Q115951250',
        'start_year': 1682,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in law', 'lang': 'en'},
    },
    'theatre': {
        'start_id': 'Q2808403',
        'end_id': 'Q109968683',
        'start_year': 1601,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' au théâtre', 'lang': 'fr'},
    },
    'chess': {
        'start_id': 'Q28135570',
        'end_id': 'Q115951399',
        'start_year': 1782,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' aux échecs', 'lang': 'fr'},
    },
    'japan': {
        'start_id': 'Q25544402',
        'end_id': 'Q114875570',
        'start_year': 1867,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Japan', 'lang': 'en'},
    },
    'france': {
        'start_id': 'Q21187072',
        'end_id': 'Q114860352',
        'start_year': 1535,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in France', 'lang': 'en'},
    },
    'sweden': {
        'start_id': 'Q20706723',
        'end_id': 'Q114784090',
        'start_year': 1520,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Sweden', 'lang': 'en'},
    },
    'denmark': {
        'start_id': 'Q4551883',
        'end_id': 'Q115120440',
        'start_year': 1689,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Denmark', 'lang': 'en'},
    },
    'denmark2': {
        'start_id': 'Q4551883',
        'end_id': 'Q48852360',
        'start_year': 1689,
        'end_year': 1698,
        'search_query': {'prefix': '', 'suffix': ' in Denmark', 'lang': 'en'},
    },
    'denmark3': {
        'start_id': 'Q4551490',
        'end_id': 'Q4551835',
        'start_year': 1648,
        'end_year': 1683,
        'search_query': {'prefix': '', 'suffix': ' in Denmark', 'lang': 'en'},
    },
    'canada': {
        'start_id': 'Q109426261',
        'end_id': 'Q114798438',
        'start_year': 1690,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' au Canada', 'lang': 'fr'},
    },
    'norway': {
        'start_id': 'Q23661322',
        'end_id': 'Q114962661',
        'start_year': 1435,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Norway', 'lang': 'en'},
    },
    'classical_music': {
        'start_id': 'Q2809312',
        'end_id': 'Q111207024',
        'start_year': 1760,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in classical music', 'lang': 'en'},
    },
    'classical_music2': {
        'start_id': 'Q2807673',
        'end_id': 'Q2807858',
        'start_year': 1400,
        'end_year': 1499,
        'search_query': {'prefix': '', 'suffix': ' in classical music', 'lang': 'en'},
    },
    'classical_music3': {
        'start_id': 'Q2807954',
        'end_id': 'Q2808516',
        'start_year': 1501,
        'end_year': 1628,
        'search_query': {'prefix': '', 'suffix': ' in classical music', 'lang': 'en'},
    },
    'philosophy': {
        'start_id': 'Q97364151',
        'end_id': 'Q115951811',
        'start_year': 1004,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in philosophy', 'lang': 'en'},  #TODO revisit this one
    },
    'philosophy2': {
        'start_id': 'Q97364151',
        'end_id': 'Q110263958',
        'start_year': 1004,
        'end_year': 2022,
        'search_query': {'prefix': 'philosophy in ', 'suffix': '', 'lang': 'en'},
    },
    'philosophy3': {
        'start_id': 'Q97364151',
        'end_id': 'Q110263958',
        'start_year': 1004,
        'end_year': 2022,
        'search_query': {'prefix': 'Filosofiåret ', 'suffix': '', 'lang': 'no'},
    },
    'philosophy4': {
        'start_id': 'Q97364151',
        'end_id': 'Q110263958',
        'start_year': 1004,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' en philosophie', 'lang': 'fr'},
    },
    'philosophy5': {
        'start_id': 'Q97364151',
        'end_id': 'Q110263958',
        'start_year': 1004,
        'end_year': 2022,
        'search_query': {'prefix': 'filosofía en ', 'suffix': '', 'lang': 'es'},
    },
    'ukraine': {
        'start_id': 'Q52186225',
        'end_id': 'Q115057686',
        'start_year': 1990,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Ukraine', 'lang': 'en'},
    },
    'ireland': {
        'start_id': 'Q28224775',
        'end_id': 'Q114746760',
        'start_year': 1509,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Ireland', 'lang': 'en'},
    },
    'poetry': {
        'start_id': 'Q4548067',
        'end_id': 'Q112737520',
        'start_year': 1200,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in poetry', 'lang': 'en'},
    },
    'great_britain': {
        'start_id': 'Q4553764',
        'end_id': 'Q114784698',
        'start_year': 1801,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in the United Kingdom', 'lang': 'en'},
    },
    'wales': {
        'start_id': 'Q85719791',
        'end_id': 'Q116004961',
        'start_year': 1700,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Wales', 'lang': 'en'},
    },
    'computer_science': {
        'start_id': 'Q9129727',
        'end_id': 'Q116620495',
        'start_year': 1930,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in computer science', 'lang': 'en'},
    },
    'spaceflight': {
        'start_id': 'Q1004304',
        'end_id': 'Q111955402',
        'start_year': 1951,
        'end_year': 2027,
        'search_query': {'prefix': '', 'suffix': ' in spaceflight', 'lang': 'en'},
    },
    'sports': {
        'start_id': 'Q4553165',
        'end_id': 'Q39049009',
        'start_year': 1776,
        'end_year': 2028,
        'search_query': {'prefix': '', 'suffix': ' in sports', 'lang': 'en'},
    },
    'germany': {
        'start_id': 'Q110064665',
        'end_id': 'Q115120427',
        'start_year': 1799,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Germany', 'lang': 'en'},
    },
    'brazil': {
        'start_id': 'Q110653047',
        'end_id': 'Q115247679',
        'start_year': 1807,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' no Brasil', 'lang': 'pt'},
    },
    'aviation': {
        'start_id': 'Q16938783',
        'end_id': 'Q115942948',
        'start_year': 1891,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in aviation', 'lang': 'en'},
    },
    'scotland': {
        'start_id': 'Q80356970',
        'end_id': 'Q115973552',
        'start_year': 1680,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Scotland', 'lang': 'en'},
    },
    'mexico': {
        'start_id': 'Q26185314',
        'end_id': 'Q114798442',
        'start_year': 1899,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Mexico', 'lang': 'en'},
    },
    'chile': {
        'start_id': 'Q19869396',
        'end_id': 'Q114973730',
        'start_year': 1800,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Chile', 'lang': 'en'},
    },
    'australia': {
        'start_id': 'Q4553319',
        'end_id': 'Q114875512',
        'start_year': 1788,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Australia', 'lang': 'en'},
    },
    'paleontology': {
        'start_id': 'Q4554905',
        'end_id': 'Q115978793',
        'start_year': 1854,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in paleontology', 'lang': 'en'},
    },
    'switzerland': {
        'start_id': 'Q65089827',
        'end_id': 'Q86674589',
        'start_year': 1848,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' en Suisse', 'lang': 'fr'},
    },
    'new_zealand': {
        'start_id': 'Q4553732',
        'end_id': 'Q114875505',
        'start_year': 1800,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in New Zealand', 'lang': 'en'},
    },
    'archaeology': {
        'start_id': 'Q4553739',
        'end_id': 'Q116793529',
        'start_year': 1800,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in archaeology', 'lang': 'en'},
    },
    'archaeology2': {
        'start_id': 'Q112075457',
        'end_id': 'Q116793529',
        'start_year': 1678,
        'end_year': current_year,
        'search_query': {'prefix': 'Arkeologiåret ', 'suffix': '', 'lang': 'no'},
    },
    'portugal': {
        'start_id': 'Q4554970',
        'end_id': 'Q114784652',
        'start_year': 1857,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Portugal', 'lang': 'en'},
    },
    'argentina': {
        'start_id': 'Q4553728',
        'end_id': 'Q114784642',
        'start_year': 1800,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Argentina', 'lang': 'en'},
    },
    'belgium': {
        'start_id': 'Q15974499',
        'end_id': 'Q115801343',
        'start_year': 1830,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Belgium', 'lang': 'en'},
    },
    'afghanistan': {
        'start_id': 'Q4557084',
        'end_id': 'Q115917504',
        'start_year': 1896,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Afghanistan', 'lang': 'en'},
    },
    'spain': {
        'start_id': 'Q25544817',
        'end_id': 'Q115162318',
        'start_year': 1891,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Spain', 'lang': 'en'},
    },
    'association_football': {
        'start_id': 'Q1415774',
        'end_id': 'Q114724327',
        'start_year': 1870,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in association football', 'lang': 'en'},
    },
    'china': {
        'start_id': 'Q96359694',
        'end_id': 'Q114875519',
        'start_year': 1839,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in China', 'lang': 'en'},
    },
    'romania': {
        'start_id': 'Q25545113',
        'end_id': 'Q115944502',
        'start_year': 1914,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Romania', 'lang': 'en'},
    },
    'south_africa': {
        'start_id': 'Q4553736',
        'end_id': 'Q115784114',
        'start_year': 1800,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in South Africa', 'lang': 'en'},
    },
    'british_columbia': {
        'start_id': 'Q17619606',
        'end_id': 'Q115957916',
        'start_year': 1871,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' en Colombie-Britannique', 'lang': 'fr'},
    },
    'baseball': {
        'start_id': 'Q2810430',
        'end_id': 'Q114396013',
        'start_year': 1869,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in baseball', 'lang': 'en'},
    },
    'norwegian_football': {
        'start_id': 'Q4558035',
        'end_id': 'Q112056345',
        'start_year': 1902,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in Norwegian football', 'lang': 'en'},
    },
    'nova_scotia': {
        'start_id': 'Q18287051',
        'end_id': 'Q115958009',
        'start_year': 1867,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Nova Scotia', 'lang': 'en'},
    },
    'iceland': {
        'start_id': 'Q115959647',
        'end_id': 'Q115801051',
        'start_year': 1864,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Iceland', 'lang': 'en'},
    },
    'brazilian_football': {
        'start_id': 'Q11962114',
        'end_id': 'Q110130710',
        'start_year': 1902,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in Brazilian football', 'lang': 'en'},
    },
    'radio': {
        'start_id': 'Q16141387',
        'end_id': 'Q116076515',
        'start_year': 1900,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in radio', 'lang': 'en'},
    },
    'brittany': {
        'start_id': 'Q57628967',
        'end_id': 'Q116169460',
        'start_year': 1802,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Brittany', 'lang': 'en'},
    },
    'australian_literature': {
        'start_id': 'Q28224371',
        'end_id': 'Q116961074',
        'start_year': 1860,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Australian literature', 'lang': 'en'}
    },
    'quebec': {
        'start_id': 'Q21658663',
        'end_id': 'Q115958506',
        'start_year': 1763,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Quebec', 'lang': 'en'},
    },
    'bas-canada': {
        'start_id': 'Q24935201',
        'end_id': 'Q2810392',
        'start_year': 1793,
        'end_year': 1866,
        'search_query': {'prefix': '', 'suffix': ' au Bas-Canada', 'lang': 'fr'},
    },
    'organized_crime': {
        'start_id': 'Q4555722',
        'end_id': 'Q4619118',
        'start_year': 1879,
        'end_year': 2010,
        'search_query': {'prefix': '', 'suffix': ' in organized crime', 'lang': 'en'},
    },
    'albania': {
        'start_id': 'Q21467495',
        'end_id': 'Q115801300',
        'start_year': 1900,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Albania', 'lang': 'en'},
    },
    'albania2': {
        'start_id': 'Q21467495',
        'end_id': 'Q23019678',
        'start_year': 1900,
        'end_year': 2016,
        'search_query': {'prefix': '', 'suffix': ' në Shqipëri', 'lang': 'sq'},
    },
    'greece': {
        'start_id': 'Q107503401',
        'end_id': 'Q113956982',
        'start_year': 1830,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Greece', 'lang': 'en'},
    },
    'greece2': {
        'start_id': 'Q107503401',
        'end_id': 'Q113956982',
        'start_year': 1830,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' en Grèce', 'lang': 'fr'},
    },
    'finland': {
        'start_id': 'Q25545895',
        'end_id': 'Q114912618',
        'start_year': 1917,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Finland', 'lang': 'en'},
    },
    'finland2': {
        'start_id': 'Q25545895',
        'end_id': 'Q114912618',
        'start_year': 1917,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' en Finlande', 'lang': 'fr'},
    },
    'finnish_sport': {
        'start_id': 'Q92721384',
        'end_id': 'Q115943537',
        'start_year': 1920,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Finnish sport', 'lang': 'en'},
    },
    'india': {
        'start_id': 'Q24905979',
        'end_id': 'Q114878248',
        'start_year': 1500,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in India', 'lang': 'en'},
    },
    'ontario': {
        'start_id': 'Q16509913',
        'end_id': 'Q115958653',
        'start_year': 1867,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Ontario', 'lang': 'en'},
    },
    'latvia': {
        'start_id': 'Q13098776',
        'end_id': 'Q115058260',
        'start_year': 1887,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Latvia', 'lang': 'en'},
    },
    'venezuela': {
        'start_id': 'Q6366280',
        'end_id': 'Q116152557',
        'start_year': 1830,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Venezuela', 'lang': 'en'},
    },
    'science_fiction': {
        'start_id': 'Q17591916',
        'end_id': 'Q111207025',
        'start_year': 1880,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in science fiction', 'lang': 'en'},
    },
    'hong_kong': {
        'start_id': 'Q55698104',
        'end_id': 'Q115654957',
        'start_year': 1891,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Hong Kong', 'lang': 'en'},
    },
    'yukon': {
        'start_id': 'Q18331336',
        'end_id': 'Q115958679',
        'start_year': 1898,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Yukon', 'lang': 'en'},
    },
    'belgian_congo': {
        'start_id': 'Q106645369',
        'end_id': 'Q106670408',
        'start_year': 1908,
        'end_year': 1960,
        'search_query': {'prefix': '', 'suffix': ' in the Belgian Congo', 'lang': 'en'},
    },
    'dr_congo': {
        'start_id': 'Q52195848',
        'end_id': 'Q116259582',
        'start_year': 1997,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in the Democratic Republic of the Congo', 'lang': 'en'},
    },
    'animation': {
        'start_id': 'Q111181580',
        'end_id': 'Q116214074',
        'start_year': 1915,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in animation', 'lang': 'en'},
    },
    'norwegian_music': {
        'start_id': 'Q30681366',
        'end_id': 'Q60773327',
        'start_year': 1879,
        'end_year': 2019,
        'search_query': {'prefix': '', 'suffix': ' in Norwegian music', 'lang': 'en'},
    },
    'jazz': {
        'start_id': 'Q48812737',
        'end_id': 'Q116971788',
        'start_year': 1900,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in jazz', 'lang': 'en'},
    },
    'georgia': {
        'start_id': 'Q46611487',
        'end_id': 'Q115958796',
        'start_year': 1917,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Georgia', 'lang': 'en'},
    },
    'british_music': {
        'start_id': 'Q108366049',
        'end_id': 'Q116084556',
        'start_year': 1900,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in British music', 'lang': 'en'},
    },
    'anime': {
        'start_id': 'Q16948943',
        'end_id': 'Q110548344',
        'start_year': 1917,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in anime', 'lang': 'en'},
    },
    'bulgaria': {
        'start_id': 'Q104849360',
        'end_id': 'Q115806031',
        'start_year': 1890,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Bulgaria', 'lang': 'en'},
    },
    'manitoba': {
        'start_id': 'Q18287056',
        'end_id': 'Q115958763',
        'start_year': 1870,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Manitoba', 'lang': 'en'},
    },
    'sumo': {
        'start_id': 'Q48745342',
        'end_id': 'Q110263875',
        'start_year': 1746,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in sumo', 'lang': 'en'},
    },
    'broadcasting': {
        'start_id': 'Q346668',
        'end_id': 'Q115950715',
        'start_year': 1919,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in broadcasting', 'lang': 'en'},
    },
    'alberta': {
        'start_id': 'Q17332790',
        'end_id': 'Q116297725',
        'start_year': 1905,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Alberta', 'lang': 'en'},
    },
    'badminton': {
        'start_id': 'Q14160204',
        'end_id': 'Q110901777',
        'start_year': 1898,
        'end_year': 2026,
        'search_query': {'prefix': '', 'suffix': ' in badminton', 'lang': 'en'},
    },
    'public_domain': {
        'start_id': 'Q110555136',
        'end_id': 'Q110244952',
        'start_year': 2008,
        'end_year': 2026,
        'search_query': {'prefix': '', 'suffix': ' in public domain', 'lang': 'en'},
    },
    'dada': {
        'start_id': 'Q2811204',
        'end_id': 'Q2812491',
        'start_year': 1916,
        'end_year': 1969,
        'search_query': {'prefix': '', 'suffix': ' in dadaism and surrealism', 'lang': 'en'},
    },
    'new_brunswick': {
        'start_id': 'Q2809458',
        'end_id': 'Q115958809',
        'start_year': 1784,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in New Brunswick', 'lang': 'en'},
    },
    'algeria': {
        'start_id': 'Q106449927',
        'end_id': 'Q115018603',
        'start_year': 1886,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Algeria', 'lang': 'en'},
    },
    'algeria2': {
        'start_id': 'Q106449927',
        'end_id': 'Q56376810',
        'start_year': 1886,
        'end_year': 1953,
        'search_query': {'prefix': 'Argelia en ', 'suffix': '', 'lang': 'es'},
    },
    'astronomy': {
        'start_id': 'Q111738615',
        'end_id': 'Q60964015',
        'start_year': 1984,
        'end_year': 2025,
        'search_query': {'prefix': '', 'suffix': ' in astronomy', 'lang': 'en'},
    },
    'nwt': {
        'start_id': 'Q19543502',
        'end_id': 'Q116169492',
        'start_year': 1870,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': '  in the Northwest Territories', 'lang': 'en'},
    },
    'nordic_combined': {
        'start_id': 'Q19606015',
        'end_id': 'Q111207018',
        'start_year': 1899,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': '  in Nordic Combined', 'lang': 'en'},
    },
    'saskatchewan': {
        'start_id': 'Q18287330',
        'end_id': 'Q116447029',
        'start_year': 1905,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': '  in Saskatchewan', 'lang': 'en'},
    },
    'cycling': {
        'start_id': 'Q28145119',
        'end_id': 'Q110263940',
        'start_year': 1900,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': '  in cycling', 'lang': 'en'},
    },
    'journalism': {
        'start_id': 'Q53127730',
        'end_id': 'Q9549330',
        'start_year': 1805,
        'end_year': 1999,
        'search_query': {'prefix': '', 'suffix': ' no jornalismo', 'lang': 'pt'},
    },
    'estonia': {
        'start_id': 'Q104834800',
        'end_id': 'Q114912007',
        'start_year': 1918,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Estonia', 'lang': 'en'},
    },
    'british_radio': {
        'start_id': 'Q104872791',
        'end_id': 'Q115796219',
        'start_year': 1920,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in British radio', 'lang': 'en'},
    },
    'iraq': {
        'start_id': 'Q52199010',
        'end_id': 'Q116173821',
        'start_year': 1920,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Iraq', 'lang': 'en'},
    },
    'soviet_union': {
        'start_id': 'Q19869906',
        'end_id': 'Q4587294',
        'start_year': 1922,
        'end_year': 1991,
        'search_query': {'prefix': '', 'suffix': ' in the Soviet Union', 'lang': 'en'},
    },
    'russia': {
        'start_id': 'Q4588077',
        'end_id': 'Q111046812',
        'start_year': 1992,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Russia', 'lang': 'en'},
    },
    'russia2': {
        'start_id': 'Q26210421',
        'end_id': 'Q4027712',
        'start_year': 1874,
        'end_year': 1921,
        'search_query': {'prefix': '', 'suffix': ' in Russia', 'lang': 'en'},
    },
    'turkey': {
        'start_id': 'Q52175344',
        'end_id': 'Q115145952',
        'start_year': 1920,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Turkey', 'lang': 'en'},
    },
    'yemen': {
        'start_id': 'Q22935595',
        'end_id': 'Q116052011',
        'start_year': 2006,
        'end_year': 2023,
        'search_query': {'prefix': '', 'suffix': ' in Yemen', 'lang': 'en'},
    },
    'womens_road_cycling': {
        'start_id': 'Q97776121',
        'end_id': 'Q115517229',
        'start_year': 2001,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': " in women's road cycling", 'lang': 'en'},
    },
    'mens_road_cycling': {
        'start_id': 'Q3469282',
        'end_id': 'Q112317612',
        'start_year': 2004,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': " in men's road cycling", 'lang': 'en'},
    },
    'video_gaming': {
        'start_id': 'Q12061831',
        'end_id': 'Q114008549',
        'start_year': 1966,
        'end_year': 2025,
        'search_query': {'prefix': '', 'suffix': ' in video gaming', 'lang': 'en'},
    },
    'volleyball': {
        'start_id': 'Q11185572',
        'end_id': 'Q116205295',
        'start_year': 1950,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in volleyball', 'lang': 'en'},
    },
    'volleyball2': {
        'start_id': 'Q11185572',
        'end_id': 'Q110490237',
        'start_year': 1950,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': '年のバレーボール', 'lang': 'ja'},
    },
    'philippines': {
        'start_id': 'Q19599817',
        'end_id': 'Q113827481',
        'start_year': 1967,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in the Philippines', 'lang': 'en'},
    },
    'europe': {
        'start_id': 'Q2812772',
        'end_id': 'Q114896580',
        'start_year': 1980,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Europe', 'lang': 'en'},
    },
    'pakistan': {
        'start_id': 'Q16056618',
        'end_id': 'Q116035942',
        'start_year': 1947,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Pakistan', 'lang': 'en'},
    },
    'lgbt_rights': {
        'start_id': 'Q4574240',
        'end_id': 'Q116205191',
        'start_year': 1970,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in LGBT rights', 'lang': 'en'},
    },
    'japanese_music': {
        'start_id': 'Q28154186',
        'end_id': 'Q116442805',
        'start_year': 2007,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Japanese music', 'lang': 'en'},
    },
    # 'japanese_football': {
    #     'start_id': 'Q55638693',
    #     'end_id': 'Q110223541',
    #     'start_year': 1921,
    #     'end_year': 2022,
    #     'search_query': {'prefix': '', 'suffix': ' in Japanese football', 'lang': 'en'},
    # },
    'japanese_television': {
        'start_id': 'Q18159981',
        'end_id': 'Q114656760',
        'start_year': 1963,
        'end_year': 2024,
        'search_query': {'prefix': '', 'suffix': ' in Japanese television', 'lang': 'en'},
    },
    'japanese_television2': {
        'start_id': 'Q11185591',
        'end_id': 'Q114656760',
        'start_year': 1953,
        'end_year': 2024,
        'search_query': {'prefix': '', 'suffix': '年のテレビ (日本)', 'lang': 'ja'},
    },
    'indonesia': {
        'start_id': 'Q31338381',
        'end_id': 'Q116039546',
        'start_year': 1995,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Indonesia', 'lang': 'en'},
    },
    'azerbaijan': {
        'start_id': 'Q4609716',
        'end_id': 'Q115801690',
        'start_year': 2007,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Azerbaijan', 'lang': 'en'},
    },
    'armenia': {
        'start_id': 'Q20311977',
        'end_id': 'Q115800698',
        'start_year': 2012,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Armenia', 'lang': 'en'},
    },
    'artistic_gymnastics': {
        'start_id': 'Q16000938',
        'end_id': 'Q109973906',
        'start_year': 2014,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in artistic gymnastics', 'lang': 'en'},
    },
    'archosaur_paleontology': {
        'start_id': 'Q20311996',
        'end_id': 'Q115959672',
        'start_year': 2009,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in archosaur paleontology', 'lang': 'en'},
    },
    'arthropod_paleontology': {
        'start_id': 'Q20312012',
        'end_id': 'Q116177874',
        'start_year': 2009,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in arthropod paleontology', 'lang': 'en'},
    },
    'mammal_paleontology': {
        'start_id': 'Q20312021',
        'end_id': 'Q116085742',
        'start_year': 2009,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in mammal paleontology', 'lang': 'en'},
    },
    'reptile_paleontology': {
        'start_id': 'Q96369498',
        'end_id': 'Q116085509',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in reptile paleontology', 'lang': 'en'},
    },
    'paleoichthyology': {
        'start_id': 'Q28128325',
        'end_id': 'Q116177953',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in paleoichthyology', 'lang': 'en'},
    },
    'american_music': {
        'start_id': 'Q4619025',
        'end_id': 'Q114153028',
        'start_year': 2010,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in American music', 'lang': 'en'},
    },
    'australian_television': {
        'start_id': 'Q27961607',
        'end_id': 'Q116005127',
        'start_year': 1974,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Australian television', 'lang': 'en'},
    },
    'american_television': {
        'start_id': 'Q108378024',
        'end_id': 'Q113625062',
        'start_year': 1972,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in American television', 'lang': 'en'},
    },
    'american_soccer': {
        'start_id': 'Q13604936',
        'end_id': 'Q115821956',
        'start_year': 1996,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in American soccer', 'lang': 'en'},
    },
    'comics': {
        'start_id': 'Q3300535',
        'end_id': 'Q116029225',
        'start_year': 1895,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in comics', 'lang': 'en'},
    },
    'basketball': {
        'start_id': 'Q17619860',
        'end_id': 'Q110610857',
        'start_year': 1929,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in basketball', 'lang': 'en'},
    },
    'bangladesh': {
        'start_id': 'Q4574732',
        'end_id': 'Q116084713',
        'start_year': 1971,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Bangladesh', 'lang': 'en'},
    },
    'egypt': {
        'start_id': 'Q52178029',
        'end_id': 'Q115783931',
        'start_year': 1923,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Egypt', 'lang': 'en'},
    },
    'fantasy': {
        'start_id': 'Q50581632',
        'end_id': 'Q116505325',
        'start_year': 1930,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in fantasy', 'lang': 'en'},
    },
    'israel': {
        'start_id': 'Q3885502',
        'end_id': 'Q110517454',
        'start_year': 1948,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Israel', 'lang': 'en'},
    },
    'irish_television': {
        'start_id': 'Q96362495',
        'end_id': 'Q116264914',
        'start_year': 1960,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Irish television', 'lang': 'en'},
    },
    'kazakhstan': {
        'start_id': 'Q60651191',
        'end_id': 'Q116052615',
        'start_year': 1991,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Kazakhstan', 'lang': 'en'},
    },
    'libya': {
        'start_id': 'Q23019969',
        'end_id': 'Q116811608',
        'start_year': 1951,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Libya', 'lang': 'en'},
    },
    'nigeria': {
        'start_id': 'Q4605207',
        'end_id': 'Q114852090',
        'start_year': 2005,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Nigeria', 'lang': 'en'},
    },
    'thailand': {
        'start_id': 'Q24927068',
        'end_id': 'Q115158149',
        'start_year': 1939,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Thailand', 'lang': 'en'},
    },
    'siam': {
        'start_id': 'Q24932218',
        'end_id': 'Q24930115',
        'start_year': 1900,
        'end_year': 1938,
        'search_query': {'prefix': '', 'suffix': ' in Siam', 'lang': 'en'},
    },
    'ufc': {
        'start_id': 'Q16828127',
        'end_id': 'Q113614190',
        'start_year': 1993,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in UFC', 'lang': 'en'},
    },
    'zambia': {
        'start_id': 'Q65553284',
        'end_id': 'Q116175112',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Zambia', 'lang': 'en'},
    },
    'zimbabwe': {
        'start_id': 'Q4579526',
        'end_id': 'Q116003247',
        'start_year': 1980,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Zimbabwe', 'lang': 'en'},
    },
    'uruguay': {
        'start_id': 'Q60650551',
        'end_id': 'Q116505528',
        'start_year': 2010,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Uruguay', 'lang': 'en'},
    },
    'austria': {
        'start_id': 'Q31345279',
        'end_id': 'Q115801707',
        'start_year': 2004,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Austria', 'lang': 'en'},
    },
    'morocco': {
        'start_id': 'Q31344784',
        'end_id': 'Q115957413',
        'start_year': 1960,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Morocco', 'lang': 'en'},
    },
    'lorraine': {
        'start_id': 'Q28144971',
        'end_id': 'Q116680837',
        'start_year': 1789,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Lorraine', 'lang': 'en'},
    },
    'lorraine2': {
        'start_id': 'Q28144971',
        'end_id': 'Q116680837',
        'start_year': 1789,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' en Lorraine', 'lang': 'fr'},
    },
    'nepal': {
        'start_id': 'Q109534020',
        'end_id': 'Q116204889',
        'start_year': 1997,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Nepal', 'lang': 'en'},
    },
    'nunavut': {
        'start_id': 'Q18199134',
        'end_id': 'Q116695757',
        'start_year': 1999,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Nunavut', 'lang': 'en'},
    },
    'peru': {
        'start_id': 'Q31347210',
        'end_id': 'Q115555211',
        'start_year': 1977,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Peru', 'lang': 'en'},
    },
    'pro_wrestling': {
        'start_id': 'Q85722147',
        'end_id': 'Q109409708',
        'start_year': 1933,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in professional wrestling', 'lang': 'en'},
    },
    'philippine_television': {
        'start_id': 'Q85724996',
        'end_id': 'Q116695772',
        'start_year': 1979,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Philippine television', 'lang': 'en'},
    },
    'northern_ireland': {
        'start_id': 'Q4561079',
        'end_id': 'Q115801050',
        'start_year': 1921,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Northern Ireland', 'lang': 'en'},
    },
    'singapore': {
        'start_id': 'Q31339254',
        'end_id': 'Q114877607',
        'start_year': 1954,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Singapore', 'lang': 'en'},
    },
    'malaysia': {
        'start_id': 'Q4571284',
        'end_id': 'Q114875523',
        'start_year': 1963,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Malaysia', 'lang': 'en'},
    },
    'malaya': {
        'start_id': 'Q39047573',
        'end_id': 'Q4570906',
        'start_year': 1925,
        'end_year': 1962,
        'search_query': {'prefix': '', 'suffix': ' in Malaya', 'lang': 'en'},
    },
    'iran': {
        'start_id': 'Q52182345',
        'end_id': 'Q116167533',
        'start_year': 1950,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Iran', 'lang': 'en'},
    },
    'birding': {
        'start_id': 'Q4553738',
        'end_id': 'Q105730126',
        'start_year': 1800,
        'end_year': 2021,
        'search_query': {'prefix': '', 'suffix': ' in birding and ornithology', 'lang': 'en'},
    },
    'military_history': {
        'start_id': 'Q10548727',
        'end_id': 'Q21934492',
        'start_year': 1700,
        'end_year': 2016,
        'search_query': {'prefix': 'Krigsåret ', 'suffix': '', 'lang': 'sv'},
    },
    'south_korea': {
        'start_id': 'Q85722713',
        'end_id': 'Q114875872',
        'start_year': 1947,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in South Korea', 'lang': 'en'},
    },
    'south_korean_music': {
        'start_id': 'Q55601484',
        'end_id': 'Q115151645',
        'start_year': 1995,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in South Korean music', 'lang': 'en'},
    },
    'uganda': {
        'start_id': 'Q28868302',
        'end_id': 'Q115018094',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Uganda', 'lang': 'en'},
    },
    'uzbekistan': {
        'start_id': 'Q21016887',
        'end_id': 'Q115954762',
        'start_year': 2012,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Uzbekistan', 'lang': 'en'},
    },
    'palestine': {
        'start_id': 'Q12177532',
        'end_id': 'Q115892300',
        'start_year': 1999,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in the State of Palestine', 'lang': 'en'},
    },
    'taiwan': {
        'start_id': 'Q15908566',
        'end_id': 'Q115925806',
        'start_year': 1895,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Taiwan', 'lang': 'en'},
    },
    'tanzania': {
        'start_id': 'Q18758230',
        'end_id': 'Q115784821',
        'start_year': 2015,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Tanzania', 'lang': 'en'},
    },
    'bvi': {
        'start_id': 'Q43082320',
        'end_id': 'Q116177949',
        'start_year': 2014,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in the British Virgin Islands', 'lang': 'en'},
    },
    'tonga': {
        'start_id': 'Q21018631',
        'end_id': 'Q116481263',
        'start_year': 2014,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Tonga', 'lang': 'en'},
    },
    'tajikistan': {
        'start_id': 'Q30638864',
        'end_id': 'Q116820708',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Tajikistan', 'lang': 'en'},
    },
    'trinidad': {
        'start_id': 'Q111513620',
        'end_id': 'Q116155867',
        'start_year': 2015,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Trinidad and Tobago', 'lang': 'en'},
    },
    'syria': {
        'start_id': 'Q52180696',
        'end_id': 'Q116621529',
        'start_year': 1966,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Syria', 'lang': 'en'},
    },
    'senegal': {
        'start_id': 'Q65553003',
        'end_id': 'Q116264936',
        'start_year': 2015,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Senegal', 'lang': 'en'},
    },
    'sudan': {
        'start_id': 'Q21018739',
        'end_id': 'Q115012896',
        'start_year': 2014,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Sudan', 'lang': 'en'},
    },
    'serbia': {
        'start_id': 'Q4029969',
        'end_id': 'Q114746241',
        'start_year': 2005,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Serbia', 'lang': 'en'},
    },
    'scottish_television': {
        'start_id': 'Q4567609',
        'end_id': 'Q115978628',
        'start_year': 1952,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Scottish television', 'lang': 'en'},
    },
    'slovenia': {
        'start_id': 'Q17149695',
        'end_id': 'Q115120452',
        'start_year': 2014,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Slovenia', 'lang': 'en'},
    },
    'slovakia': {
        'start_id': 'Q31337990',
        'end_id': 'Q116039538',
        'start_year': 1992,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Slovakia', 'lang': 'en'},
    },
    'sri_lanka': {
        'start_id': 'Q23014921',
        'end_id': 'Q110419185',
        'start_year': 1979,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in Sri Lanka', 'lang': 'en'},
    },
    'rock_music': {
        'start_id': 'Q106959512',
        'end_id': 'Q114197366',
        'start_year': 2008,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in rock music', 'lang': 'en'},
    },
    'moldova': {
        'start_id': 'Q4623175',
        'end_id': 'Q115800784',
        'start_year': 2011,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Moldova', 'lang': 'en'},
    },
    'mongolia': {
        'start_id': 'Q21016592',
        'end_id': 'Q114877615',
        'start_year': 2014,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Mongolia', 'lang': 'en'},
    },
    'madagascar': {
        'start_id': 'Q20312569',
        'end_id': 'Q111237021',
        'start_year': 2014,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in Madagascar', 'lang': 'en'},
    },
    'mozambique': {
        'start_id': 'Q28868334',
        'end_id': 'Q110309417',
        'start_year': 2017,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in Mozambique', 'lang': 'en'},
    },
    'malta': {
        'start_id': 'Q17507550',
        'end_id': 'Q116023073',
        'start_year': 2012,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Malta', 'lang': 'en'},
    },
    'laos': {
        'start_id': 'Q19637854',
        'end_id': 'Q110321298',
        'start_year': 1949,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in Laos', 'lang': 'en'},
    },
    'lithuania': {
        'start_id': 'Q85729016',
        'end_id': 'Q116004886',
        'start_year': 2009,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Lithuania', 'lang': 'en'},
    },
    'kuwait': {
        'start_id': 'Q18704670',
        'end_id': 'Q116004810',
        'start_year': 1961,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Kuwait', 'lang': 'en'},
    },
    'kiribati': {
        'start_id': 'Q104856368',
        'end_id': 'Q116621367',
        'start_year': 2020,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Kiribati', 'lang': 'en'},
    },
    'kerala': {
        'start_id': 'Q110713117',
        'end_id': 'Q116004978',
        'start_year': 2003,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Kerala', 'lang': 'en'},
    },
    'kyrgyzstan': {
        'start_id': 'Q18702308',
        'end_id': 'Q110537130',
        'start_year': 2015,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in Kyrgyzstan', 'lang': 'en'},
    },
    'kenya': {
        'start_id': 'Q21020140',
        'end_id': 'Q114973509',
        'start_year': 2006,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Kenya', 'lang': 'en'},
    },
    'latin_music': {
        'start_id': 'Q65043939',
        'end_id': 'Q116265783',
        'start_year': 1986,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Latin music', 'lang': 'en'},
    },
    'boxing': {
        'start_id': 'Q4029702',
        'end_id': 'Q116996487',
        'start_year': 1996,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in boxing', 'lang': 'en'},
    },
    'climate_change': {
        'start_id': 'Q104880851',
        'end_id': 'Q115943210',
        'start_year': 2019,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in climate change', 'lang': 'en'},
    },
    'chinese_football': {
        'start_id': 'Q4612347',
        'end_id': 'Q110281478',
        'start_year': 2008,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in Chinese football', 'lang': 'en'},
    },
    'country_music': {
        'start_id': 'Q16242901',
        'end_id': 'Q115803856',
        'start_year': 1920,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in country music', 'lang': 'en'},
    },
    'canadian_television': {
        'start_id': 'Q4567595',
        'end_id': 'Q113560721',
        'start_year': 1952,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Canadian television', 'lang': 'en'},
    },
    'costa_rica': {
        'start_id': 'Q16820840',
        'end_id': 'Q116264932',
        'start_year': 2013,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Costa Rica', 'lang': 'en'},
    },
    'cambodia': {
        'start_id': 'Q21018736',
        'end_id': 'Q116157461',
        'start_year': 2006,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Cambodia', 'lang': 'en'},
    },
    'colombia': {
        'start_id': 'Q31341384',
        'end_id': 'Q114816729',
        'start_year': 1984,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Colombia', 'lang': 'en'},
    },
    'croatia': {
        'start_id': 'Q4584818',
        'end_id': 'Q114911211',
        'start_year': 1988,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Croatia', 'lang': 'en'},
    },
    'croatian_television': {
        'start_id': 'Q28228153',
        'end_id': 'Q24909004',
        'start_year': 1989,
        'end_year': 2016,
        'search_query': {'prefix': '', 'suffix': ' in Croatian television', 'lang': 'en'},
    },
    'cuba': {
        'start_id': 'Q30635426',
        'end_id': 'Q115790989',
        'start_year': 2013,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Cuba', 'lang': 'en'},
    },
    'cameroon': {
        'start_id': 'Q20312558',
        'end_id': 'Q115047829',
        'start_year': 2014,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Cameroon', 'lang': 'en'},
    },
    'benin': {
        'start_id': 'Q65552976',
        'end_id': 'Q115048638',
        'start_year': 2014,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Benin', 'lang': 'en'},
    },
    'tennis': {
        'start_id': 'Q4589897',
        'end_id': 'Q115766701',
        'start_year': 1994,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in tennis', 'lang': 'en'},
    },
    'macau': {
        'start_id': 'Q28035207',
        'end_id': 'Q116204887',
        'start_year': 1990,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Macau', 'lang': 'en'},
    },
    'amusement_parks': {
        'start_id': 'Q2810432',
        'end_id': 'Q113833096',
        'start_year': 1870,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' dans les parcs de loisirs', 'lang': 'fr'},
    },
    'webcomics': {
        'start_id': 'Q22905987',
        'end_id': 'Q116609845',
        'start_year': 2000,
        'end_year': 2021,
        'search_query': {'prefix': '', 'suffix': ' in webcomics', 'lang': 'en'},
    },
    'belarus': {
        'start_id': 'Q4609718',
        'end_id': 'Q115471131',
        'start_year': 2007,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Belarus', 'lang': 'en'},
    },
    'netherlands': {
        'start_id': 'Q19568559',
        'end_id': 'Q115806449',
        'start_year': 1987,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in the Netherlands', 'lang': 'en'},
    },
    'cape_verde': {
        'start_id': 'Q39057720',
        'end_id': 'Q116264917',
        'start_year': 1957,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Cape Verde', 'lang': 'en'},
    },
    'chad': {
        'start_id': 'Q48850490',
        'end_id': 'Q116177866',
        'start_year': 2005,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Chad', 'lang': 'en'},
    },
    'cyprus': {
        'start_id': 'Q31334612',
        'end_id': 'Q115801531',
        'start_year': 1960,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Cyprus', 'lang': 'en'},
    },
    'eu': {
        'start_id': 'Q21187468',
        'end_id': 'Q115162303',
        'start_year': 1993,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in the European Union', 'lang': 'en'},
    },
    'un': {
        'start_id': 'Q2814112',
        'end_id': 'Q105883245',
        'start_year': 2006,
        'end_year': 2021,
        'search_query': {'prefix': '', 'suffix': ' in the United Nations', 'lang': 'en'},
    },
    'canadian_soccer': {
        'start_id': 'Q4623131',
        'end_id': 'Q115816682',
        'start_year': 2011,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Canadian soccer', 'lang': 'en'},
    },
    'central_african_republic': {
        'start_id': 'Q31345661',
        'end_id': 'Q113985029',
        'start_year': 2012,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in the Central African Republic', 'lang': 'en'},
    },
    'dominican_republic': {
        'start_id': 'Q28868300',
        'end_id': 'Q116481445',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in the Dominican Republic', 'lang': 'en'},
    },
    'uae': {
        'start_id': 'Q19568386',
        'end_id': 'Q116039978',
        'start_year': 1971,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in the United Arab Emirates', 'lang': 'en'},
    },
    'north_korea': {
        'start_id': 'Q19568199',
        'end_id': 'Q116309958',
        'start_year': 1948,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in North Korea', 'lang': 'en'},
    },
    'england': {
        'start_id': 'Q63391584',
        'end_id': 'Q116177946',
        'start_year': 1983,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in England', 'lang': 'en'},
    },
    'england2': {
        'start_id': 'Q65088960',
        'end_id': 'Q16146835',
        'start_year': 1631,
        'end_year': 1707,
        'search_query': {'prefix': '', 'suffix': ' in England', 'lang': 'en'},
    },
    'economics': {
        'start_id': 'Q31843314',
        'end_id': 'Q111525152',
        'start_year': 1895,
        'end_year': 2022,
        'search_query': {'prefix': 'Ekonomiåret ', 'suffix': '', 'lang': 'sv'},
    },
    'economics2': {
        'start_id': 'Q31843314',
        'end_id': 'Q116699285',
        'start_year': 1895,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in economics', 'lang': 'en'},
    },
    'esports': {
        'start_id': 'Q4029980',
        'end_id': 'Q112641756',
        'start_year': 2006,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in esports', 'lang': 'en'},
    },
    'ethiopia': {
        'start_id': 'Q20982401',
        'end_id': 'Q115017650',
        'start_year': 2012,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Ethiopia', 'lang': 'en'},
    },
    'eritrea': {
        'start_id': 'Q107472484',
        'end_id': 'Q116311667',
        'start_year': 1991,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Eritrea', 'lang': 'en'},
    },
    'european_music': {
        'start_id': 'Q16244009',
        'end_id': 'Q105616253',
        'start_year': 2010,
        'end_year': 2021,
        'search_query': {'prefix': '', 'suffix': ' in European music', 'lang': 'en'},
    },
    'ghana': {
        'start_id': 'Q4586419',
        'end_id': 'Q114863206',
        'start_year': 1990,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Ghana', 'lang': 'en'},
    },
    'fiji': {
        'start_id': 'Q28868323',
        'end_id': 'Q116481258',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Fiji', 'lang': 'en'},
    },
    'hip_hop': {
        'start_id': 'Q23020753',
        'end_id': 'Q115867224',
        'start_year': 1979,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in hip hop music', 'lang': 'en'},
    },
    'hungary': {
        'start_id': 'Q31346370',
        'end_id': 'Q114746282',
        'start_year': 2010,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Hungary', 'lang': 'en'},
    },
    'heavy_metal': {
        'start_id': 'Q113685776',
        'end_id': 'Q111949942',
        'start_year': 1968,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in heavy metal music', 'lang': 'en'},
    },
    'handball': {
        'start_id': 'Q108920906',
        'end_id': 'Q110573913',
        'start_year': 1991,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in handball', 'lang': 'en'},
    },
    'italian_television': {
        'start_id': 'Q60539084',
        'end_id': 'Q106726535',
        'start_year': 1951,
        'end_year': 2017,
        'search_query': {'prefix': '', 'suffix': ' in Italian television', 'lang': 'en'},
    },
    'lebanon': {
        'start_id': 'Q31343449',
        'end_id': 'Q116177948',
        'start_year': 1952,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Lebanon', 'lang': 'en'},
    },
    'luxembourg': {
        'start_id': 'Q4565844',
        'end_id': 'Q115800948',
        'start_year': 1946,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Luxembourg', 'lang': 'en'},
    },
    'mauritania': {
        'start_id': 'Q30638876',
        'end_id': 'Q116757094',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Mauritania', 'lang': 'en'},
    },
    'newfoundland_labrador': {
        'start_id': 'Q18287764',
        'end_id': 'Q116254747',
        'start_year': 1949,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Newfoundland and Labrador', 'lang': 'en'},
    },
    'numismatics': {
        'start_id': 'Q15974617',
        'end_id': 'Q115410106',
        'start_year': 1990,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in numismatics', 'lang': 'en'},
    },
    'philippine_sports': {
        'start_id': 'Q55602003',
        'end_id': 'Q116233305',
        'start_year': 2013,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Philippine sports', 'lang': 'en'},
    },
    'philippine_music': {
        'start_id': 'Q17080849',
        'end_id': 'Q116214443',
        'start_year': 2013,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Philippine music', 'lang': 'en'},
    },
    'qatar': {
        'start_id': 'Q42530885',
        'end_id': 'Q116141719',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Qatar', 'lang': 'en'},
    },
    'rwanda': {
        'start_id': 'Q20311122',
        'end_id': 'Q115785695',
        'start_year': 1993,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Rwanda', 'lang': 'en'},
    },
    'saudi_arabia': {
        'start_id': 'Q23020019',
        'end_id': 'Q116060185',
        'start_year': 1932,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Saudi Arabia', 'lang': 'en'},
    },
    'standup_comedy': {
        'start_id': 'Q28447635',
        'end_id': 'Q115973218',
        'start_year': 2015,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in stand-up comedy', 'lang': 'en'},
    },
    'south_sudan': {
        'start_id': 'Q21020545',
        'end_id': 'Q114315476',
        'start_year': 2011,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in South Sudan', 'lang': 'en'},
    },
    'somaliland': {
        'start_id': 'Q96369417',
        'end_id': 'Q115991914',
        'start_year': 2015,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Somaliland', 'lang': 'en'},
    },
    'somalia': {
        'start_id': 'Q23019625',
        'end_id': 'Q116039602',
        'start_year': 2004,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Somalia', 'lang': 'en'},
    },
    'suriname': {
        'start_id': 'Q30592872',
        'end_id': 'Q116213300',
        'start_year': 2016,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Suriname', 'lang': 'en'},
    },
    'triathlon': {
        'start_id': 'Q28456219',
        'end_id': 'Q111992982',
        'start_year': 2013,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in triathlon', 'lang': 'en'},
    },
    'history_of_the_metro': {
        'start_id': 'Q3920027',
        'end_id': 'Q105972068',
        'start_year': 1863,
        'end_year': 2024,
        'search_query': {'prefix': '', 'suffix': ' in the history of the metro', 'lang': 'en'},
    },
    'vatican_city': {
        'start_id': 'Q110818958',
        'end_id': 'Q114746514',
        'start_year': 2005,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' au Vatican', 'lang': 'fr'},
    },
    'uk_pol_gov': {
        'start_id': 'Q105082053',
        'end_id': 'Q116021615',
        'start_year': 2016,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in United Kingdom politics and government', 'lang': 'en'},
    },
    'us_pol_gov': {
        'start_id': 'Q60539132',
        'end_id': 'Q85737979',
        'start_year': 2018,
        'end_year': 2021,
        'search_query': {'prefix': '', 'suffix': ' in United States politics and government', 'lang': 'en'},
    },
    'photography': {
        'start_id': 'Q16524635',
        'end_id': 'Q115726074',
        'start_year': 1800,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' en photographie', 'lang': 'fr'},
    },
    'meteorology': {
        'start_id': 'Q97194151',
        'end_id': 'Q56641505',
        'start_year': 1803,
        'end_year': 2018,
        'search_query': {'prefix': 'Meteorologiåret ', 'suffix': '', 'lang': 'no'},
    },
    'aquatic_sports': {
        'start_id': 'Q28232264',
        'end_id': 'Q85737695',
        'start_year': 2013,
        'end_year': 2020,
        'search_query': {'prefix': '', 'suffix': ' in aquatic sports', 'lang': 'en'},
    },
    'athletics': {
        'start_id': 'Q4578979',
        'end_id': 'Q116943944',
        'start_year': 1979,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in athletics', 'lang': 'en'},
    },
    'swedish_football': {
        'start_id': 'Q4570918',
        'end_id': 'Q107077569',
        'start_year': 1962,
        'end_year': 2021,
        'search_query': {'prefix': '', 'suffix': ' in Swedish football', 'lang': 'en'},
    },
    'swedish_music': {
        'start_id': 'Q4619100',
        'end_id': 'Q60773504',
        'start_year': 2010,
        'end_year': 2019,
        'search_query': {'prefix': '', 'suffix': ' in Swedish music', 'lang': 'en'},
    },
    'swedish_television': {
        'start_id': 'Q19570441',
        'end_id': 'Q24909281',
        'start_year': 2002,
        'end_year': 2016,
        'search_query': {'prefix': '', 'suffix': ' in Swedish television', 'lang': 'en'},
    },
    'weightlifting': {
        'start_id': 'Q65119849',
        'end_id': 'Q85737789',
        'start_year': 2009,
        'end_year': 2020,
        'search_query': {'prefix': '', 'suffix': ' in weightlifting', 'lang': 'en'},
    },
    'danish_music': {
        'start_id': 'Q24075024',
        'end_id': 'Q60773529',
        'start_year': 2015,
        'end_year': 2019,
        'search_query': {'prefix': '', 'suffix': ' in Danish music', 'lang': 'en'},
    },
    'education': {
        'start_id': 'Q11186475',
        'end_id': 'Q116237548',
        'start_year': 2002,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': '年の教育', 'lang': 'ja'},
    },
    'guatemala': {
        'start_id': 'Q18702205',
        'end_id': 'Q114862717',
        'start_year': 2015,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Guatemala', 'lang': 'en'},
    },
    'golf': {
        'start_id': 'Q4603553',
        'end_id': 'Q115157820',
        'start_year': 2004,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in golf', 'lang': 'en'},
    },
    'indonesian_football': {
        'start_id': 'Q30636060',
        'end_id': 'Q116114914',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Indonesian football', 'lang': 'en'},
    },
    'jordan': {
        'start_id': 'Q19568586',
        'end_id': 'Q116005084',
        'start_year': 1990,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Jordan', 'lang': 'en'},
    },
    'jamaica': {
        'start_id': 'Q31341519',
        'end_id': 'Q116177855',
        'start_year': 2016,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Jamaica', 'lang': 'en'},
    },
    'myanmar': {
        'start_id': 'Q23019656',
        'end_id': 'Q116004943',
        'start_year': 2013,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Myanmar', 'lang': 'en'},
    },
    'michigan_older': {
        'start_id': 'Q96361203',
        'end_id': 'Q60539102',
        'start_year': 1922,
        'end_year': 1994,
        'search_query': {'prefix': '', 'suffix': ' in Michigan', 'lang': 'en'},
    },
    'michigan_newer': {
        'start_id': 'Q96369337',
        'end_id': 'Q114044333',
        'start_year': 2012,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in Michigan', 'lang': 'en'},
    },
    'paraguay': {
        'start_id': 'Q30069130',
        'end_id': 'Q114784685',
        'start_year': 2016,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Paraguay', 'lang': 'en'},
    },
    'water_transport': {
        'start_id': 'Q10008569',
        'end_id': 'Q116271927',
        'start_year': 1885,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' v loďstvech', 'lang': 'cs'},
    },
    'water_transport2': {
        'start_id': 'Q11752938',
        'end_id': 'Q10008048',
        'start_year': 1873,
        'end_year': 1883,
        'search_query': {'prefix': '', 'suffix': ' v loďstvech', 'lang': 'cs'},
    },
    'water_transport3': {
        'start_id': 'Q9999401',
        'end_id': 'Q11752900',
        'start_year': 1856,
        'end_year': 1869,
        'search_query': {'prefix': '', 'suffix': ' v loďstvech', 'lang': 'cs'},
    },
    'el_salvador': {
        'start_id': 'Q97738274',
        'end_id': 'Q97738304',
        'start_year': 1900,
        'end_year': 1945,
        'search_query': {'prefix': '', 'suffix': ' in El Salvador', 'lang': 'en'},
    },
    'el_salvador2': {
        'start_id': 'Q30635473',
        'end_id': 'Q116156159',
        'start_year': 2013,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in El Salvador', 'lang': 'en'},
    },
    'el_salvador3': {
        'start_id': 'Q97738308',
        'end_id': 'Q97738310',
        'start_year': 1947,
        'end_year': 1949,
        'search_query': {'prefix': '', 'suffix': ' in El Salvador', 'lang': 'en'},
    },
    'transport': {
        'start_id': 'Q109075659',
        'end_id': 'Q97310576',
        'start_year': 1895,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' v dopravě', 'lang': 'cs'},
    },
    'south_african_television': {
        'start_id': 'Q19570504',
        'end_id': 'Q48806248',
        'start_year': 2005,
        'end_year': 2018,
        'search_query': {'prefix': '', 'suffix': ' in South African television', 'lang': 'en'},
    },
    'south_african_sport': {
        'start_id': 'Q4588081',
        'end_id': 'Q4607271',
        'start_year': 1992,
        'end_year': 2006,
        'search_query': {'prefix': '', 'suffix': ' in South African sport', 'lang': 'en'},
    },
    'equestrian_sports': {
        'start_id': 'Q25391515',
        'end_id': 'Q116786681',
        'start_year': 1971,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in equestrian sports', 'lang': 'en'},
    },
    'equestrian_sports2': {
        'start_id': 'Q25391481',
        'end_id': 'Q25391512',
        'start_year': 1951,
        'end_year': 1969,
        'search_query': {'prefix': '', 'suffix': ' in equestrian sports', 'lang': 'en'},
    },
    'poland': {
        'start_id': 'Q31343979',
        'end_id': 'Q115057666',
        'start_year': 2004,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Poland', 'lang': 'en'},
    },
    'bosnia_herzegovina': {
        'start_id': 'Q18712674',
        'end_id': 'Q115120470',
        'start_year': 1992,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Bosnia and Herzegovina', 'lang': 'en'},
    },
    'guinea': {
        'start_id': 'Q28868313',
        'end_id': 'Q115047893',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Guinea', 'lang': 'en'},
    },
    'angola': {
        'start_id': 'Q30593222',
        'end_id': 'Q115018307',
        'start_year': 2016,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Angola', 'lang': 'en'},
    },
    'bhutan': {
        'start_id': 'Q65552980',
        'end_id': 'Q116204883',
        'start_year': 2014,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Bhutan', 'lang': 'en'},
    },
    'rugby_union': {
        'start_id': 'Q2810455',
        'end_id': 'Q116629548',
        'start_year': 1871,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in rugby union', 'lang': 'en'},
    },
    'rugby_league': {
        'start_id': 'Q4603562',
        'end_id': 'Q114344870',
        'start_year': 2004,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in rugby league', 'lang': 'en'},
    },
    'andorra': {
        'start_id': 'Q31345207',
        'end_id': 'Q115800786',
        'start_year': 2018,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Andorra', 'lang': 'en'},
    },
    'liberia': {
        'start_id': 'Q113987896',
        'end_id': 'Q115801350',
        'start_year': 2010,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Liberia', 'lang': 'en'},
    },
    'antarctica': {
        'start_id': 'Q30635218',
        'end_id': 'Q116005020',
        'start_year': 2013,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Antarctica', 'lang': 'en'},
    },
    'vietnam': {
        'start_id': 'Q24959016',
        'end_id': 'Q116022761',
        'start_year': 2010,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Vietnam', 'lang': 'en'},
    },
    'tunisia': {
        'start_id': 'Q52194131',
        'end_id': 'Q115957044',
        'start_year': 1924,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Tunisia', 'lang': 'en'},
    },
    'czech_republic': {
        'start_id': 'Q60649884',
        'end_id': 'Q115801136',
        'start_year': 2012,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in the Czech Republic', 'lang': 'en'},
    },
    'namibia': {
        'start_id': 'Q24981972',
        'end_id': 'Q115784695',
        'start_year': 1990,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Namibia', 'lang': 'en'},
    },
    'italy': {
        'start_id': 'Q105402493',
        'end_id': 'Q115211211',
        'start_year': 1787,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Italy', 'lang': 'en'},
    },
    'africa': {
        'start_id': 'Q19952536',
        'end_id': 'Q115819851',
        'start_year': 2015,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' en Afrique', 'lang': 'fr'},
    },
    'ivory_coast': {
        'start_id': 'Q28868341',
        'end_id': 'Q111819075',
        'start_year': 2017,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in Ivory Coast', 'lang': 'en'},
    },
    'niger': {
        'start_id': 'Q23019664',
        'end_id': 'Q116817519',
        'start_year': 2014,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Niger', 'lang': 'en'},
    },
    'mali': {
        'start_id': 'Q28868321',
        'end_id': 'Q116177873',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Mali', 'lang': 'en'},
    },
    'burkina_faso': {
        'start_id': 'Q107394539',
        'end_id': 'Q116039576',
        'start_year': 1990,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Burkina Faso', 'lang': 'en'},
    },
    'malawi': {
        'start_id': 'Q65554898',
        'end_id': 'Q116005104',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Malawi', 'lang': 'en'},
    },
    'ecuador': {
        'start_id': 'Q23019672',
        'end_id': 'Q116155496',
        'start_year': 2015,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Ecuador', 'lang': 'en'},
    },
    'bolivia': {
        'start_id': 'Q26185043',
        'end_id': 'Q116030203',
        'start_year': 2016,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Bolivia', 'lang': 'en'},
    },
    'honduras': {
        'start_id': 'Q48850669',
        'end_id': 'Q116760948',
        'start_year': 2018,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Honduras', 'lang': 'en'},
    },
    'sierra_leone': {
        'start_id': 'Q31346642',
        'end_id': 'Q113624728',
        'start_year': 2020,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in Sierra Leone', 'lang': 'en'},
    },
    'togo': {
        'start_id': 'Q97356961',
        'end_id': 'Q116618852',
        'start_year': 2020,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Togo', 'lang': 'en'},
    },
    'haiti': {
        'start_id': 'Q31346223',
        'end_id': 'Q116735101',
        'start_year': 2020,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Haiti', 'lang': 'en'},
    },
    'nicaragua': {
        'start_id': 'Q48851108',
        'end_id': 'Q116741388',
        'start_year': 2014,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Nicaragua', 'lang': 'en'},
    },
    'oman': {
        'start_id': 'Q28868314',
        'end_id': 'Q116052065',
        'start_year': 2017,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Oman', 'lang': 'en'},
    },
    'turkmenistan': {
        'start_id': 'Q96370676',
        'end_id': 'Q116052614',
        'start_year': 2020,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Turkmenistan', 'lang': 'en'},
    },
    'eswatini': {
        'start_id': 'Q104860446',
        'end_id': 'Q116167441',
        'start_year': 2020,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Eswatini', 'lang': 'en'},
    },
    'comoros': {
        'start_id': 'Q104855841',
        'end_id': 'Q113982766',
        'start_year': 2020,
        'end_year': 2022,
        'search_query': {'prefix': '', 'suffix': ' in the Comoros', 'lang': 'en'},
    },
    'solomon_islands': {
        'start_id': 'Q104856319',
        'end_id': 'Q116735118',
        'start_year': 2020,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in the Solomon Islands', 'lang': 'en'},
    },
    'guyana': {
        'start_id': 'Q30632477',
        'end_id': 'Q116621384',
        'start_year': 2016,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Guyana', 'lang': 'en'},
    },
    'djibouti': {
        'start_id': 'Q114458244',
        'end_id': 'Q116167629',
        'start_year': 2020,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Djibouti', 'lang': 'en'},
    },
    'brunei': {
        'start_id': 'Q114458240',
        'end_id': 'Q114877611',
        'start_year': 2020,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Brunei', 'lang': 'en'},
    },
    'panama': {
        'start_id': 'Q31347681',
        'end_id': 'Q116732410',
        'start_year': 2019,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Panama', 'lang': 'en'},
    },
    'burundi': {
        'start_id': 'Q65555828',
        'end_id': 'Q116888444',
        'start_year': 2019,
        'end_year': current_year,
        'search_query': {'prefix': '', 'suffix': ' in Burundi', 'lang': 'en'},
    },
}

seq_to_check = 'latin_music'
start_id = year_seqs[seq_to_check]['start_id']
end_id = year_seqs[seq_to_check]['end_id']
start_year = year_seqs[seq_to_check]['start_year']
end_year = year_seqs[seq_to_check]['end_year']
search_query = year_seqs[seq_to_check]['search_query']


wd_url = 'https://wikidata.org/wiki/'
skipchars = len(wd_url)
# the API URL to get detailed info on multiple items from Wikidata
url_base = 'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids='
search_url_base = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&search='
# the documented limit on how many items can be queried at once
query_limit = 50

def get_entities(query_ids):
    ids_joined = '|'.join(query_ids)
    req = urllib.request.Request(url_base + ids_joined)
    req.add_header('User-Agent', 'YearSequenceChecker/0.1 (https://www.wikidata.org/wiki/User:Jamie7687)')
    # req.add_header('Accept-Encoding', 'gzip')
    time.sleep(0.1)
    result = urllib.request.urlopen(req)
    result_json = json.loads(result.read())
    if result_json['success'] == 1:
        return result_json['entities']
    else:
        raise Exception('wbgetentities call failed')

def search_year_item(year, label_query):
    url = search_url_base + urllib.parse.quote(label_query['prefix']) + \
        str(year) + urllib.parse.quote(label_query['suffix']) + \
        "&language=" + label_query['lang']
    print(url)
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'YearSequenceChecker/0.1 (https://www.wikidata.org/wiki/User:Jamie7687)')
    time.sleep(0.1)
    result = urllib.request.urlopen(req)
    result_content = result.read()
    print(result_content)
    result_json = json.loads(result_content)
    print(result_json)
    return result_json

def check_years(ys):
    search_results = []
    search_entities = {}

    for i in range(ys['start_year'], ys['end_year'] + 1):
        search_results.append(search_year_item(i, ys['search_query']))

    for result in search_results:
        if(len(result['search'])) == 1:
            cur_id = result['search'][0]['id']
            search_entities.update(get_entities([cur_id]))
        elif len(result['search']) > 1:
            print('!!!!danger on', result['search'])

    print('dates to add, if applicable:')
    print('qid,P585')

    for entity in search_entities:
        if 'P585' not in search_entities[entity]['claims']:
            if ys['search_query']['suffix'] != '':
                print(entity + ',+' + get_label(search_entities[entity]).split()[0] + '-01-01T00:00:00Z/9')
            elif ys['search_query']['prefix'] != '':
                print(entity + ',+' + get_label(search_entities[entity]).split()[-1] + '-01-01T00:00:00Z/9')

    print('"instance of"/types to add, if applicable:')
    print('qid,P31')

    for entity in search_entities:
        if 'P31' not in search_entities[entity]['claims']:
            print(entity + ',Q18340514')


entities_full = {}

entities_full.update(get_entities([start_id]))
count = 1
next_id = start_id

print('starting at the beginning of the chain')
while True:
    try:
        next_id = entities_full[next_id]['claims']['P156'][0]['mainsnak']['datavalue']['value']['id']
        entities_full.update(get_entities([next_id]))
        count += 1
        item_label = get_label(entities_full[next_id])
        print(count, next_id, item_label)
    except Exception as e:
        print(e)
        print('first gap starts at', next_id)
        gap_start = next_id
        if 'P585' in entities_full[next_id]['claims']:
            gap_start_year = int(entities_full[next_id]['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:5])
        else:
            gap_start_year = start_year
            check_years(year_seqs[seq_to_check])
        print(gap_start)
        break


entities_full.update(get_entities([end_id]))
count = 1
next_id = end_id

print('starting at the end of the chain')
while True:
    try:
        next_id = entities_full[next_id]['claims']['P155'][0]['mainsnak']['datavalue']['value']['id']
        entities_full.update(get_entities([next_id]))
        count += 1
        item_label = get_label(entities_full[next_id])
        print(count, next_id, item_label)
    except Exception as e:
        print(e)
        print('last gap ends at', next_id)
        gap_end = next_id
        if 'P585' in entities_full[next_id]['claims']:
            gap_end_year = int(entities_full[next_id]['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:5])
        else:
            gap_end_year = end_year
            check_years(year_seqs[seq_to_check])
        print(gap_end)
        break

with open('seq_entities_full.json', 'w') as efile:
    json.dump(entities_full, efile, indent=4)

search_results = []

print('checking the gaps')
if gap_start_year < gap_end_year:
    for y in range(gap_start_year - 1, gap_end_year + 1):
        search_results.append(search_year_item(y, search_query))
        time.sleep(0.2)

with open('gap_search_results.json', 'w') as gapfile:
    json.dump(search_results, gapfile, indent=4)

ids = []

for result in search_results:
    search = result['search']
    if len(search) == 1:
        result_id = search[0]['id']
        ids.append(result_id)
        if result_id not in entities_full:
            entities_full.update(get_entities([result_id]))
            time.sleep(0.1)
    elif len(search) == 0:
        print('no results for', result)
    elif len(search) > 1:
        print('multiple results for', result)
        for r in search:
            orig_query = result['searchinfo']['search']
            if r['display']['label']['value'] == orig_query:
                result_id = search[0]['id']
                ids.append(result_id)
                if result_id not in entities_full:
                    entities_full.update(get_entities([result_id]))
                    time.sleep(0.1)


def check_stmt(src, dst, typ):
    try:
        to_check = entities_full[src]['claims'][typ][0]['mainsnak']['datavalue']['value']['id']
    except KeyError as e:
        print('KeyError')
        return False
    if to_check == dst:
        print('TRUE TRUE')
        return True
    else:
        print('FALSE!!!!!!!')
        return False

def is_consecutive(src, dst, typ):
    try:
        src_item = entities_full[src]
        dst_item = entities_full[dst]
        src_year = int(src_item['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:5])
        dst_year = int(dst_item['claims']['P585'][0]['mainsnak']['datavalue']['value']['time'][1:5])
        if typ == 'P155' and dst_year == src_year - 1:
            return True
        elif typ == 'P156' and dst_year == src_year + 1:
            return True
        else:
            return False
    except KeyError:
        return False

prev_statements = ['qid,P155\n']
next_statements = ['qid,P156\n']

for i, id in enumerate(ids):
    if i !=0:
        prev_present = check_stmt(id, ids[i-1], 'P155')
        is_consec = is_consecutive(id, ids[i-1], 'P155')
        if not prev_present and is_consec:
            prev_statements.append(id + ',' + ids[i-1] + '\n')
        else:
            print('statement present:', id, ids[i-1], 'P155')

    if i != len(ids) - 1:
        next_present = check_stmt(id, ids[i+1], 'P156')
        is_consec = is_consecutive(id, ids[i+1], 'P156')
        if not next_present and is_consec:
            next_statements.append(id + ',' + ids[i+1] + '\n')
        else:
            print('statement present:', id, ids[i+1], 'P156')

print(''.join(prev_statements))
print(''.join(next_statements))

with open('seqpatch_' + seq_to_check + '.csv', 'w') as qsfile:
    qsfile.writelines(prev_statements)
    qsfile.writelines(next_statements)
