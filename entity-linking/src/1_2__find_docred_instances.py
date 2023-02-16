"""Finds the Wikipedia page that corresponds to each DocRED instance
Input: DocRED files, ElasticSearch
Output: 1_matched_docred_elasticsearch.jsonl, 1_not_matched_docred_elasticsearch.jsonl

---
Linked-DocRED
Copyright (C) 2023 Alteca.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import json
import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from tqdm import tqdm
from .utils import text_similarity_docred

load_dotenv()

WIKIPEDIA_TEXT_SIM_THRESHOLD = 0.5

ES_INDEX = os.getenv('ES_INDEX')
ES_URL = os.getenv('ES_URL')
ES_USER = os.getenv('ES_USER')
ES_PASSWORD = os.getenv('ES_PASSWORD')
DOCRED_PATH = os.getenv('DOCRED_PATH')
EL_DATA_PATH = os.getenv('EL_DATA_PATH')

es = Elasticsearch(ES_URL, basic_auth=(ES_USER, ES_PASSWORD))

MAX_CANDIDATES = 5


def find_candidate_elasticsearch(docred_text: str):
    """Find candidate in elasticsearch

    Args:
        docred_text (str): docred instance text

    Returns:
        dict: candidate
    """
    candidate = {
        'resource': None,
        'text_similarity': -1,
    }

    res = es.search(index=ES_INDEX, query={
        "match": {
            "text": {
                "query": docred_text
            }
        }
    })
    hits = res['hits']['hits']

    if len(hits) == 0:
        return candidate

    hits = hits[0:MAX_CANDIDATES]
    best_text_similarity = -1
    for hit in hits:
        candidate_text = hit['_source']['text']
        text_sim = text_similarity_docred(docred_text, candidate_text)

        if text_sim > best_text_similarity:
            candidate = {
                'resource': hit['_source']['url'],
                'text_similarity': text_sim,
            }
            best_text_similarity = text_sim
    return candidate, best_text_similarity


def process_dataset(dataset_path: str, dataset_name: str, matched_file, not_matched_file):
    """Process dataset to find candidates
    Args:
        dataset_path (str): path to docred dataset
        dataset_name (str): name of docred dataset (dev, test, train)
        matched_file (any): file to write found docred documents
        not_matched_file (any): file to write not found docred documents
    """
    with open(dataset_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for i, instance in enumerate(tqdm(data)):
        instance_text = ' '.join([' '.join(sent)
                                 for sent in instance['sents']])

        candidate, text_sim = find_candidate_elasticsearch(instance_text)
        candidate['id'] = i
        candidate['dataset'] = dataset_name

        if text_sim > WIKIPEDIA_TEXT_SIM_THRESHOLD:
            f = matched_file
        else:
            f = not_matched_file
            
        f.write(json.dumps(candidate))
        f.write('\n')
        f.flush()

def main():
    """Main entrypoint
    """
    with open(f'{EL_DATA_PATH}/1_matched_docred_elasticsearch.jsonl', 'w', encoding='utf-8') as matched_file:
        with open(f'{EL_DATA_PATH}/1_not_matched_docred_elasticsearch.jsonl', 'w', encoding='utf-8') as not_matched_file:
            print('--- Processing dev dataset')
            process_dataset(f'{DOCRED_PATH}/dev.json', 'dev', matched_file, not_matched_file)

            print('--- Processing test dataset')
            process_dataset(f'{DOCRED_PATH}/test.json', 'test', matched_file, not_matched_file)

            print('--- Processing train_annotated dataset')
            process_dataset(f'{DOCRED_PATH}/train_annotated.json', 'train_annotated', matched_file, not_matched_file)
    
if __name__ == '__main__':
    main()
