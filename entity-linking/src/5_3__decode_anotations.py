"""Decode Label Studio annotations for manual annotation, and disambiguate all entities.
Input: annotation file
       4_hyperlinks_alignment_links_in_page_common_knowledge.json
Output: 5_docred_disambiguated.json
"""
import os
import json
import argparse
from tqdm.auto import tqdm
from dotenv import load_dotenv
from .utils import read_docred

load_dotenv()

DOCRED_PATH = os.getenv('DOCRED_PATH')
EL_DATA_PATH = os.getenv('EL_DATA_PATH')

docred = read_docred(DOCRED_PATH)


def main(annotation_file: str):
    """Main entrypoint
    Args:
        annotation_file (str): path to file containing annotations
    """
    with open(annotation_file, 'r', encoding='utf-8') as file:
        annotations = json.load(file)

    with open(f'{EL_DATA_PATH}/4_hyperlinks_alignment_links_in_page_common_knowledge.json', 'r',
              encoding='utf-8') as f:
        processed_docred = json.load(f)

    for instance in tqdm(annotations):
        instance_data = instance['data']
        dataset_name = instance_data['dataset']
        instance_id = instance_data['id']
        annotations = instance['annotations']

        if len(annotations) > 1:
            print(dataset_name, instance_id)

        for annotation in annotations[0]['result']:
            # --- Disambiguation
            if annotation['to_name'].startswith('to_disambiguate_'):
                entity_index = int(annotation['to_name'][16:])
                entity = instance_data['to_disambiguate'][entity_index]
                entity_id = entity['entity_id']

                wiki_resource = None
                wiki_not_resource = []

                if annotation['type'] == 'choices':
                    values = annotation['value']['choices']
                    if len(values) > 1:
                        raise Exception(values)
                    value = values[0]

                    if value.startswith('to_disambiguate_'):    # Result from Google
                        choice = int(value.split('_')[-1])
                        wiki_resource = entity['candidates'][choice]['resource']
                    elif value == 'Does not exist':             # Entity to create
                        wiki_resource = '---new'
                        wiki_not_resource = [cand['resource']
                                             for cand in entity['candidates']]
                    elif value == 'Title':                      # Title
                        wiki_resource = '---title'
                    else:
                        raise Exception(value)

                elif annotation['type'] == 'textarea':
                    values = annotation['value']['text']
                    if len(values) > 1:
                        raise Exception(values)
                    value = values[0]

                    if value.isdigit():                         # Coreference
                        wiki_resource = f'---coref{value}'
                    else:                                       # Existing entity
                        wiki_resource = value
                else:
                    raise Exception(annotation)

                # Check entity text is same between manual annotation and docred
                docred_instance = docred[dataset_name][instance_id]['vertexSet'][entity_id]
                all_names = [mention['name'].strip().lower()
                             for mention in docred_instance]
                if entity['text'].lower() not in all_names:
                    raise Exception(
                        (dataset_name, instance_id, entity_id), entity, docred_instance, all_names)

                processed_docred[dataset_name][instance_id]['entities'][entity_id]['entity_linking'] = {
                    'wikipedia_resource': wiki_resource,
                    'method': 'manual',
                    'wikipedia_not_resource': wiki_not_resource
                }

            elif annotation['from_name'] == 'error':                      # --- Error
                pass
            else:
                raise Exception(annotation)

    with open(f'{EL_DATA_PATH}/5_docred_disambiguated.json', 'w', encoding='utf-8') as f:
        json.dump(processed_docred, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='5-3 decode annotations')
    parser.add_argument('--file', help='File containing Label Studio annotations',
                        type=str, required=True)
    args = parser.parse_args()

    main(args.file)
