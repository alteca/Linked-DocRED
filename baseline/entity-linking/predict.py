"""Entity-Linking using Wikidata or Wikipedia
"""
import json
import argparse
import time
import urllib
import requests
import numpy as np
from tqdm.auto import tqdm

SLEEP_SECS = 2

def read_docred(path):
    with open(path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
        
        # Remove NUM/TIME
        out_entities = []
        for instance in dataset:
            for entity in instance['entities']:
                if not entity['type'] in ['NUM', 'TIME']:
                    out_entities.append(entity)
                    
        
        for entity in out_entities:
            for mention in entity['mentions']:
                mention['key'] = mention['name'].lower().strip()

    return out_entities

def disambiguate_wikidata(surface_forms: list) -> dict:
    out = {}
    for i, surface_form in enumerate(tqdm(surface_forms)):
        search_encoded = surface_form.replace("&", "%26")
        response = requests.get(f'https://www.wikidata.org/w/api.php?action=wbsearchentities&search={search_encoded}&format=json&language=en&uselang=en&type=item')
        if response.status_code == 200:
            try:
                content = json.loads(response.content)
                results = [res['id'] for res in content['search']]
            except:
                print(surface_form, content)
                results = []
        else:
            print(f'Error: {response.status_code}')
            results = []
        out[surface_form] = results
    
        if i % 50 == 0:
            time.sleep(2)
    return out

def process_wikipedia_link(url):
    if 'https://en.wikipedia.org/wiki/' in url:
        url = url[30:]
        return urllib.parse.unquote(url)
    else:
        raise Exception(url)
    
def disambiguate_wikipedia(surface_forms: list) -> dict:
    out = {}
    for i, surface_form in enumerate(tqdm(surface_forms)):
        search_encoded = surface_form.replace("&", "%26")
        response = requests.get(f'https://en.wikipedia.org/w/api.php?action=opensearch&format=json&formatversion=2&search={search_encoded}&namespace=0&limit=10')
        if response.status_code == 200:
            content = json.loads(response.content)
            results = [process_wikipedia_link(res) for res in content[3]]
        else:
            print(f'Error: {response.status_code}')
            results = []
        out[surface_form] = results
    
        if i % 50 == 0:
            time.sleep(2)
    return out

def main(linked_docred_file: str, method: str, output_file: str):
    """Main entrypoint

    Args:
        linked_docred_file (str): path to Linked-DocRED file to disambiguate
        method (str): method to disambiguate
        output_file (str): output file to write candidates
    """
    docred_dev = read_docred(linked_docred_file)
    
    # Disambiguate every surface form
    unique_surface_forms = set()
    for entity in docred_dev:
        for mention in entity['mentions']:
            if mention['key'] not in unique_surface_forms:
                unique_surface_forms.add(mention['key'])
    unique_surface_forms = list(unique_surface_forms)
    
    disambiguated_surface_forms = {}
    if method == 'wikipedia':
        disambiguated_surface_forms = disambiguate_wikipedia(unique_surface_forms)
    elif method == 'wikidata':
        disambiguated_surface_forms = disambiguate_wikipedia(unique_surface_forms)
    else:
        raise Exception(method)
    
    # Make predictions
    for instance in tqdm(docred_dev):
        for entity in instance['entities']:
            wiki_resources = {}
            
            # Compute score for each candidate (lowest score = best)
            for mention in entity['mentions']:
                marked_cands = {k:False for k in wiki_resources}
                
                surface_form_candidates = disambiguated_surface_forms[mention['key']]
                num_candidates = len(surface_form_candidates)
            
                for i, cand in enumerate(surface_form_candidates):
                    if cand in wiki_resources:
                        wiki_resources[cand] = wiki_resources[cand] + i
                        marked_cands[cand] = True
                    else:
                        wiki_resources[cand] = + i
                        
                for k,marked in marked_cands.items():
                    if not marked:
                        wiki_resources[k] += num_candidates

            # Compute ranking
            wiki_scores = [v for k, v in wiki_resources.items()]
            wiki_resources = [k for k, v in wiki_resources.items()]

            indexes = np.argsort(wiki_scores)
            wiki_resources = [wiki_resources[i] for i in indexes]

            entity['predicted_entity_linking'] = wiki_resources
        
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(docred_dev, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Entity-Linking with Wikipedia/Wikidata')
    parser.add_argument('--input_file', help='Path to Linked-DocRED file to disambiguate',
                        type=str, required=True)
    parser.add_argument('--method', help='Method to use to disambiguate', choices=['wikipedia', 'wikidata'],
                        type=str, required=True)
    parser.add_argument('--output_file', help='Path to store entity-linking candidates',
                        type=str, required=True)
    args = parser.parse_args()
    
    main(args.input_file, args.method, args.output_file)