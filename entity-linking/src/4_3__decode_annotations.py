"""Decode Label Studio annotations for common knowledge and annotate data
Input: annotated file
       3_hyperlinks_alignment_links_in_page.jsonl
Output: 4_hyperlinks_alignment_links_in_page_common_knowledge.json
"""
import os
import json
import argparse
import pandas as pd
from dotenv import load_dotenv
from .utils import preprocess_entity

load_dotenv()

EL_DATA_PATH = os.getenv('EL_DATA_PATH')


def main(annotation_file: str):
    """Main entrypoint
    Args:
        annotation_file (str): path to annotated file (exported from Label Studio)
    """
    with open(annotation_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    rows = []
    for row in data:
        if len(row['annotations'][0]['result']) == 0:
            print(row)
            continue
        annotation = row['annotations'][0]['result'][0]
        simplified_text = row['data']['simplified_text']
        entity_type = row['data']['entity_type']
        if annotation['type'] == 'choices':
            choice = annotation['value']['choices'][0]
            if choice == 'Other':
                resource = None
            else:
                num = int(choice[12])
                resource = row['data']['candidates'][num]['resource']
        elif annotation['type'] == 'textarea':
            resource = annotation['value']['text'][0]
            if resource.startswith('-'):
                resource = f"---{simplified_text}"

        rows.append({
            'simplified_text': simplified_text,
            'entity_type': entity_type,
            'resource': resource,
        })
    most_common_entities = pd.DataFrame(rows)

    docred = []
    with open(f'{EL_DATA_PATH}/3_hyperlinks_alignment_links_in_page.jsonl', 'r', encoding='utf-8') \
        as f:
        for line in f.readlines():
            docred.append(json.loads(line))

    for instance in docred:
        for entity in instance['entities']:
            if entity['entity_linking']['resource'] is not None \
                and entity['entity_linking']['method'] != 'common-knowledge':
                continue

            simplified_texts = [preprocess_entity(
                mention) for mention in entity['mentions']]
            for simplified_text in simplified_texts:
                search_tuple = (simplified_text, entity['type'])
                if search_tuple in most_common_entities:
                    entity['entity_linking'] = {
                        'wikipedia_resource': most_common_entities.at[search_tuple],
                        'method': 'common-knowledge'
                    }
                    break

    with open(f'{EL_DATA_PATH}/4_hyperlinks_alignment_links_in_page_common_knowledge.json', 'w',
              encoding='utf-8') as f:
        json.dump(docred, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='4-3 decode annotations')
    parser.add_argument('--file', help='File containing Label Studio annotations',
                        type=str, required=True)
    args = parser.parse_args()

    main(args.file)
