"""Process wikipedia abstracts to insert them into ElasticSearch
Input: DBPedia dump
Output: data inserted in ElasticSearch

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
import os
import re
import argparse
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
from tqdm import tqdm
from .utils import preprocess_abstract

load_dotenv()

ES_INDEX = os.getenv('ES_INDEX')
ES_URL = os.getenv('ES_URL')
ES_USER = os.getenv('ES_USER')
ES_PASSWORD = os.getenv('ES_PASSWORD')

es = Elasticsearch(ES_URL, basic_auth=(ES_USER, ES_PASSWORD))

rdf_regex = re.compile(
    r'<http:\/\/dbpedia\.org\/resource\/([^\s]+)> <[^\s]+> "(.*)"@(\w+) \.')


def process_rdf_line(rdf_line: str):
    """Process line from rdf file

    Args:
        rdf_line (str): line

    Returns:
        dict: read wikipedia instance
    """
    result = rdf_regex.search(rdf_line)

    resource = result.group(1)
    language = result.group(3)

    abstract = result.group(2)
    abstract = abstract.replace('\\', '')
    abstract_clean = preprocess_abstract(abstract)

    return {
        'text': abstract,
        'text_clean': abstract_clean,
        'url': resource,
        'language': language
    }


def wikipedia_generator(file: str):
    """Generator to insert wikipedia instances into elasticsearch

    Args:
        file (str): DBPedia dump to load

    Yields:
        dict: instance
    """
    with open(file, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('#'):
                continue
            else:
                wiki_instance = process_rdf_line(line)
                if wiki_instance['language'] != 'en':
                    continue

                wiki_instance['_id'] = wiki_instance['url']
                yield wiki_instance


def main(file: str):
    """Main entrypoint
    Args:
        file (str): file containing DBPedia dump
    """

    # Recreate index
    if es.indices.exists(index=ES_INDEX):
        es.indices.delete(index=ES_INDEX)

    mappings = {
        "properties": {
            "text": {"type": "text"},
            "text_clean": {"type": "text"},
            "url": {"type": "keyword"},
            "language": {"type": "keyword"}
        }
    }
    es.indices.create(index=ES_INDEX, mappings=mappings)

    # Insert data
    with tqdm() as t:
        for _ in helpers.streaming_bulk(es, index=ES_INDEX, actions=wikipedia_generator(file)):
            t.update(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='1-1 index articles')
    parser.add_argument('--file', help='DBPedia dump file',
                        type=str, required=True)
    args = parser.parse_args()

    main(args.file)
