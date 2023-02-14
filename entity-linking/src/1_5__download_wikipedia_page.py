"""Download wikipedia pages and title
Input: 1_matched_docred.jsonl
Output: Folder 1_wikipedia_pages
        1_articles_title.jsonl
"""
import json
import os
import time
import requests
import pandas as pd
from tqdm import tqdm
from SPARQLWrapper import SPARQLWrapper2
from dotenv import load_dotenv

load_dotenv()

EL_DATA_PATH = os.getenv('EL_DATA_PATH')

TIMESTAMP = '2018-12-27T00:00:00Z'
SLEEP_SECS = 2
BATCH_SIZE = 100


def download_wikipedia_pages():
    """Download wikipedia pages
    """
    docred = pd.read_json(
        f"{EL_DATA_PATH}/1_matched_docred.jsonl", lines=True, orient="records")

    os.makedirs(f"{EL_DATA_PATH}/1_wikipedia_pages")

    for _, r in tqdm(docred.iterrows(), total=len(docred)):
        filename = r["resource"].replace('/', '_')
        file_path = f'{EL_DATA_PATH}/1_wikipedia_pages/{filename}.html'
        if not os.path.exists(file_path):
            instance_title = r["resource"]
            try:
                instance_title_encoded = instance_title.replace("&", "%26")
                response = requests.get(
                    f'https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&titles={instance_title_encoded}&prop=revisions&rvstart={TIMESTAMP}&rvprop=ids|timestamp&rvlimit=1')
                content = json.loads(response.content)
                instance_versionid = content['query']['pages'][0]['revisions'][0]['revid']
            except:
                try:
                    response = requests.get(
                        f'https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&titles={instance_title_encoded}&prop=revisions&rvprop=ids|timestamp&rvlimit=1&rvdir=newer')
                    content = json.loads(response.content)
                    instance_versionid = content['query']['pages'][0]['revisions'][0]['revid']
                except:
                    print({
                        'dataset': r['dataset'],
                        'id': r['id'],
                        'resource': r['resource']
                    })
                    continue

            response = requests.get(
                f'https://en.wikipedia.org/api/rest_v1/page/html/{instance_title}/{instance_versionid}', allow_redirects=True)
            with open(file_path, 'wb') as f:
                f.write(response.content)

            time.sleep(SLEEP_SECS)


def get_articles_names():
    """Query for articles names with SPARQL
    """
    docred = pd.read_json(
        f"{EL_DATA_PATH}/1_matched_docred.jsonl", lines=True, orient="records")
    resources = docred['resource'].to_list()
    names = {res: set() for res in resources}

    sparql = SPARQLWrapper2("http://dbpedia.org/sparql")
    nl = '\n'

    for i in tqdm(range(0, len(resources), BATCH_SIZE)):
        sparql.setQuery(f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?resource ?label WHERE {{
                VALUES ?resource {{
                    {nl.join(f'<http://dbpedia.org/resource/{res}>' for res in resources[i:i+BATCH_SIZE])}
                }}
                ?resource rdfs:label ?label.
                FILTER (lang(?label) = 'en')
            }}
        """)
        bindings = sparql.query().bindings
        for b in bindings:
            resource = b['resource'].value[28:]
            name = b['label'].value
            if resource in names:
                names[resource].add(name)
            else:
                names[resource] = set([name])

        time.sleep(SLEEP_SECS)

    docred['names'] = docred['resource'].apply(
        lambda r: list(names[r]) if r in names else [])
    docred[['resource', 'names']].to_json(
        f'{EL_DATA_PATH}/1_articles_title.jsonl', orient='records', lines=True)

    names = {res: list(n) for res, n in names.items()}
    with open(f'{EL_DATA_PATH}/1_articles_title.json', 'w', encoding='utf-8') as f:
        json.dump(names, f)


if __name__ == "__main__":
    print("--- Download Wikipedia pages")
    download_wikipedia_pages()

    print("--- Get Wikipedia pages name")
    get_articles_names()
