#!/usr/bin/env python3
"""generate a file of links from a Wikipedia XML dump"""

import sys
import re
import itertools
import json
from lxml import etree as et

nsmap = {'x': 'http://www.mediawiki.org/xml/export-0.10/'}
ns = "{http://www.mediawiki.org/xml/export-0.10/}"


def process_article_text(title, article_text):
    results = []
    matches = re.findall(r'\[\[[^\]]*\]\]', article_text)
    for match in matches:
        stripped = match.strip('[]')
        if "|" in stripped:
            stripped = stripped.split("|")[0]
        results.append((title, stripped))
    return results
    
    
filename_base = "wiki-latest-pages-articles-multistream.xml"    
    
if len(sys.argv) > 0:
    lang = sys.argv[1]
else:
    lang = "en"
    
filename = lang + filename_base

context = iter(et.iterparse(sys.stdin.buffer, events=("start", "end")))

# get the root element
event, root = next(context)
assert event == "start"

article_count = 0

with open(lang + 'wikilinks.txt', 'w') as outfile:
	for event, elem in context:
		if event == "end" and elem.tag == ns + "page":
		    redirect = elem.find(ns + "redirect") is not None
		    if elem.find(ns + "ns") is not None:
		        is_article = elem.find(ns + "ns").text == "0"
		    else:
		        is_article = False
		    if is_article and not redirect:
		        title = elem.find(ns + "title").text
		        try:
		            raw_text = elem.find(ns + "revision").find(ns + "text").text
		        except AttributeError:
		            try:
		                raw_text = elem.find("revision").find("text").text
		            except AttributeError:
		                raw_text = elem.find(ns + "revision").find("text").text

		        try:
		            no_templates = re.sub(r'\{\{[^\}]*\}\}', '', raw_text)
		            processed = process_article_text(title, no_templates)
		            outfile.writelines([link[0] + ' | ' + link[1] + '\n' for link in processed])
		            article_count += 1
		            if article_count % 100000 == 0:
		                print(article_count, "articles done at", title)
		        except TypeError:
		            print("***regex substitution error on unexpected",
		                  type(raw_text))
		            print("currently not attempting to add this to raw_articles")

		    root.clear()

