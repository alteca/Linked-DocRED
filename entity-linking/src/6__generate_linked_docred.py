"""Generate Linked-DocRED from previous steps
Input: 5_docred_disambiguated.json
Output: Linked-DocRED
"""
import copy
import os
import json
import re
import urllib
import pandas as pd
from dotenv import load_dotenv
from .utils import read_docred

load_dotenv()

DOCRED_PATH = os.getenv('DOCRED_PATH')
EL_DATA_PATH = os.getenv('EL_DATA_PATH')
LINKED_DOCRED_PATH = os.getenv('LINKED_DOCRED_PATH')

docred = read_docred(DOCRED_PATH)

WIKIDATA_REGEX = re.compile(r'^Q[0-9]+$')


def correct_url(resource: str) -> str:
    """Correct url
    Args:
        resource (str): wikipedia url
    Returns:
        str: corrected url
    """
    if resource is None:
        return resource
    if resource.startswith('---'):
        return resource
    if WIKIDATA_REGEX.fullmatch(resource):
        return f'https://www.wikidata.org/wiki/{resource}'
    if not resource.startswith('https://en.wikipedia.org/'):
        return f'https://en.wikipedia.org/wiki/{resource}'
    return resource


def correct_wiki_resource(wiki_resource: str) -> str:
    """Format wikipedia resource
    Args:
        wiki_resource (str): wikipedia resource

    Returns:
        str: formatted resource
    """
    if wiki_resource is None or wiki_resource.startswith('---'):
        return wiki_resource

    parse_results = urllib.parse.urlparse(wiki_resource)

    sp = parse_results.path.split('/wiki/')
    if len(sp) > 1:
        return sp[-1]

    headers = urllib.parse.parse_qs(parse_results.query)
    if 'title' in headers:
        return headers['title'][0]

    print(wiki_resource)


def handle_entity_linking(entity_linking: dict):
    """Handle entity-linking to add confidence
    Args:
        entity_linking (dict): entity-linking
    """
    # Confidence score
    confidence = None
    if entity_linking['wikipedia_resource'].startswith('#DocRED'):
        confidence = 'C'
    elif entity_linking['method'] in ['links-in-page', 'common-knowledge']:
        confidence = 'B'
    elif entity_linking['method'] in ['manual', 'num/time', 'hyperlinks-alignment']:
        confidence = 'A'
    entity_linking['confidence'] = confidence


def handle_mention(mention: dict) -> dict:
    """Handle mention
    Args:
        mention (dict): mention
    Returns:
        dict: corrected mention
    """
    return {
        'name': mention['name'],
        'sent_id': mention['sent_id'],
        'pos': mention['pos'],
    }


def handle_instance(instance: dict, docred_instance: dict, dataset_name: str, instance_id: int):
    """Handle instance

    Args:
        instance (dict): processed instance
        docred_instance (dict): docred instance
        dataset_name (str): dataset name
        instance_id (int): id
    """
    # New entity format
    entities = []
    for id, entity in enumerate(instance['entities']):
        entities.append({
            'type': entity[0]['type'],
            'entity_linking': entity[0]['entity_linking'],
            'mentions': [handle_mention(m) for m in entity]
        })
    del instance['entities']

    relations = None
    if 'labels' in instance:
        relations = instance['labels']
        del instance['labels']

    del instance['text']
    del instance['text_clean']

    # Handle confidence
    for entity in entities:
        handle_entity_linking(entity['entity_linking'])
    instance['entities'] = entities

    # For test set only
    if relations is None:
        instance['old-entities'] = copy.deepcopy(instance['entities'])
    else:
        instance['relations'] = relations

    # Handle coreferences
    for i, entity in enumerate(instance['entities']):
        resource = entity['entity_linking']['wikipedia_resource']
        mentions = entity['mentions']

        if not resource.startswith('#ignored#') and len(mentions) > 0:
            for j in range(i+1, len(instance['entities'])):
                other_entity = instance['entities'][j]

                if other_entity['entity_linking']['wikipedia_resource'] == resource:
                    mentions.extend(other_entity['mentions'])
                    other_entity['mentions'] = []

                    # Update confidence
                    if other_entity['entity_linking']['confidence'] < entity['entity_linking']['confidence']:
                        entity['entity_linking'] = other_entity['entity_linking']

                    # Update relations
                    if 'relations' in instance:
                        for rel in instance['relations']:
                            if rel['h'] == j:
                                rel['h'] = i
                            if rel['t'] == j:
                                rel['t'] = i

    # Update relations
    if 'relations' in instance:
        for i in range(len(instance['entities']), 0, -1):
            entity = instance['entities'][i-1]
            if len(entity['mentions']) == 0:
                for rel in instance['relations']:
                    if rel['h'] >= i:
                        rel['h'] = rel['h'] - 1
                    if rel['t'] >= i:
                        rel['t'] = rel['t'] - 1

    # Remove empty entities
    instance['entities'] = [entity for entity in instance['entities']
                            if len(entity['mentions']) > 0]
    for i, entity in enumerate(instance['entities']):
        entity['id'] = i

    # Remove redundant relations
    if 'relations' in instance:
        instance['relations'] = [
            rel for rel in instance['relations'] if rel['h'] != rel['t']]

    instance['text'] = docred_instance['text']
    instance['title'] = docred_instance['title']


def main():
    """Main Entrypoint
    """
    with open(f'{EL_DATA_PATH}/5_docred_disambiguated.json', 'r',
              encoding='utf-8') as f:
        processed_docred = json.load(f)

    for instance in processed_docred:
        for entity in instance['entities']:
            resource = entity['entity_linking']['wikipedia_resource']
            resource = correct_url(resource)
            resource = correct_wiki_resource(resource)
            entity['entity_linking']['wikipedia_resource'] = resource

            if 'wikipedia_not_resource' not in entity['entity_linking']:
                entity['entity_linking']['wikipedia_not_resource'] = []

    articles_names = pd.read_json(
        f'{EL_DATA_PATH}/1_matched_docred.jsonl', lines=True, orient="records")
    articles_names = articles_names[['resource', 'id', 'dataset']]
    articles_names = articles_names.set_index(['dataset', 'id']).sort_index()

    # Handle coreferences
    docred_id = 0
    new_resources = {}
    for _ in range(0, 3):
        for instance in processed_docred:
            for entity in instance['entities']:
                wiki_resource = entity['entity_linking']['wikipedia_resource']
                if not wiki_resource.startswith('---'):
                    continue

                if wiki_resource == '---ignored':
                    wiki_resource = '#ignored#'
                    entity['entity_linking']['wikipedia_resource'] = wiki_resource
                elif wiki_resource == '---new':
                    docred_id += 1
                    wiki_resource = f'#DocRED-{docred_id}#'
                    entity['entity_linking']['wikipedia_resource'] = wiki_resource
                elif wiki_resource.startswith('---new'):
                    if wiki_resource not in new_resources:
                        docred_id += 1
                        new_resources[wiki_resource] = f'#DocRED-{docred_id}#'
                    entity['entity_linking']['wikipedia_resource'] = new_resources[wiki_resource]
                elif wiki_resource == '---title':
                    wiki_resource = articles_names.at[(
                        instance['dataset'], instance['id']), 'resource']
                    if wiki_resource is None:
                        docred_id += 1
                        wiki_resource = f'#DocRED-{docred_id}#'
                    entity['entity_linking']['wikipedia_resource'] = wiki_resource
                elif wiki_resource.startswith('---coref'):
                    entity_id = int(wiki_resource[8:])

                    coref = processed_docred[instance['dataset']
                                             ][instance['id']]['entities'][entity_id]['entity_linking']
                    if not coref['wiki_resource'].startswith('---'):
                        entity['entity_linking']['wikipedia_resource'] = coref['wikipedia_resource']
                        entity['entity_linking']['wikipedia_not_resource'] = coref['wikipedia_not_resource']

        # Add confidence + format dataset
        for dataset_name, dataset in docred.items():
            for instance_id, docred_instance in enumerate(dataset):
                processed_instance = processed_docred[dataset_name][instance_id]
                handle_instance(processed_instance,
                                docred_instance, dataset_name, instance_id)

        # Save files
        os.makedirs(f'{LINKED_DOCRED_PATH}', exist_ok=True)

        for dataset_name, dataset in docred.items():
            with open(f'{LINKED_DOCRED_PATH}/{dataset_name}.json', 'w', encoding='utf-8') as f:
                json.dump(dataset, f)


if __name__ == '__main__':
    main()
