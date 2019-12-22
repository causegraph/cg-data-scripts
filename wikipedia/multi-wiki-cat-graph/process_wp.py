import sys
import re
import itertools
import json
from lxml import etree as et

nsmap = {'x': 'http://www.mediawiki.org/xml/export-0.10/'}
ns = "{http://www.mediawiki.org/xml/export-0.10/}"


def process_article_text(article, cat_prefix):
    results = []
    title, article_text = article[0], article[1]
    # idea here was to process sentences with links in them,
    # maybe grabbing other things too (nearby words, references)
    # TODO: get section names and words here, at least common ones
    # splitup = article[1].split(". ")
    # filtered = [item for item in splitup if ("[[" in item and "]]" in item)]
    # for item in filtered:
    matches = re.findall(r'\[\[[^\]]*\]\]', article_text)
    for match in matches:
        stripped = match.strip('[]')
        if "|" in stripped:
            stripped = stripped.split("|")[0]
        if stripped.startswith(cat_prefix):
            # print("stripped startswith cat_prefix")
            results.append((title, stripped))
    return results


chunk_size = 100000

raw_articles = []
titles = set()
collected_results = []

filename_base = "wiki-latest-pages-articles-multistream.xml"

if len(sys.argv) > 0:
    lang = sys.argv[1]
else:
    lang = "en"

filename = lang + filename_base
cat_prefix = json.loads(open('category_dict.json').read())[lang]
print("cat_prefix is", cat_prefix)
qid_dict = json.loads(open('wd_labels.json').read())[lang]

# get an iterable and turn it into an iterator
context = iter(et.iterparse(filename, events=("start", "end")))

# get the root element
event, root = next(context)
assert event == "start"

chunk_count = 0
for event, elem in context:
    if event == "end" and elem.tag == ns + "page":
        redirect = elem.find(ns + "redirect") is not None
        if elem.find(ns + "ns") is not None:
            is_article = elem.find(ns + "ns").text == "0"
            is_category = elem.find(ns + "ns").text == "14"
        else:
            is_article = False
            is_category = False
        if (is_article or is_category) and not redirect:
            title = elem.find(ns + "title").text
            titles.add(title)
            # TODO figure out why TF this try block is needed :P
            try:
                raw_text = elem.find(ns + "revision").find(ns + "text").text
            except AttributeError:
                try:
                    raw_text = elem.find("revision").find("text").text
                except AttributeError:
                    raw_text = elem.find(ns + "revision").find("text").text

            try:
                no_templates = re.sub(r'\{\{[^\}]*\}\}', '', raw_text)
                raw_articles.append((title, no_templates))
            except TypeError:
                print("***regex substitution error on unexpected",
                      type(raw_text), "in", title)
                print("currently not attempting to add this to raw_articles")

        root.clear()

        if len(raw_articles) >= chunk_size:
            results = map(process_article_text, raw_articles,
                          itertools.repeat(cat_prefix, len(raw_articles)))
            collected_results.extend(list(
                itertools.chain.from_iterable(results)))
            chunk_count += 1
            print(chunk_count * chunk_size, "articles done at", title)
            raw_articles = []


results = map(process_article_text, raw_articles,
              itertools.repeat(cat_prefix, len(raw_articles)))
print('results are type', type(results))
# print(list(results)[0])
collected_results.extend(list(itertools.chain.from_iterable(results)))
print('collected results are type', type(collected_results))
# print(collected_results[0])
print('collected results count:', len(collected_results))
final_results = {r for r in collected_results if r[1] in titles}
print('final results count before QID conversion:', len(final_results))

# TODO check difference between titles and qid_dict; does presence in one
# guarantee presence in the other


def get_qid_pair(r):
    if r[0] in qid_dict and r[1] in qid_dict:
        qid0, qid1 = qid_dict[r[0]], qid_dict[r[1]]
        if int(qid0[1:]) <= int(qid1[1:]):
            return (qid0, qid1)
        else:
            return (qid1, qid0)


final_results = {get_qid_pair(r) for r in final_results
                 if r[0] in qid_dict and r[1] in qid_dict}
print('final results count:', len(final_results))

with open(lang + 'wikilinks.txt', 'w') as outfile:
    outfile.writelines(
        [item[0] + ' | ' + item[1] + '\n' for item in final_results])

# with open(outfilelang + 'titles.txt', 'w') as titlefile:
#     titlefile.writelines([title + '\n' for title in sorted(list(titles))])
