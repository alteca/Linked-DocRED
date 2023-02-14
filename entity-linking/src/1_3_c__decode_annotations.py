"""Decode manual annotation produced using Label Studio
Inputs: manual annotations file
Output: 1_not_matched_docred_elasticsearch_label_studio_annotated.json
"""
import os
import json
import argparse
import pandas as pd
from dotenv import load_dotenv
from .utils import read_docred

load_dotenv()

EL_DATA_PATH = os.getenv('EL_DATA_PATH')
DOCRED_PATH = os.getenv('DOCRED_PATH')

docred = read_docred(DOCRED_PATH)


def main(annotation_file: str):
    with open(annotation_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    manual_annotations = []
    for row in data:
        annotation = row['annotations'][0]['result'][0]
        if annotation['type'] == 'choices':
            choice = annotation['value']['choices'][0]
            if choice == "True":
                resource = row['data']['resource']
                method = 'elastic-verified'
            else:
                resource = row['data'][choice[1:]]
                method = 'google-verified'
        elif annotation['type'] == 'textarea':
            resource = annotation['value']['text'][0]
            method = 'manual'
            if resource.startswith('-'):
                resource = None
                method = None

        manual_annotations.append({
            'dataset': row['data']['dataset'],
            'id': row['data']['id'],
            'resource': resource,
            'method': method
        })
    manual_annotations = pd.DataFrame(manual_annotations)
    manual_annotations['text'] = manual_annotations.apply(
        lambda r: docred[r['dataset']][r['id']]['text'], axis='columns')
    manual_annotations['resource'] = manual_annotations['resource'].apply(
        lambda r: r.split("wiki/")[1] if r is not None and "wiki/" in r else r)
    manual_annotations.to_json(
        f"{EL_DATA_PATH}/1_not_matched_docred_elasticsearch_label_studio_annotated.json", 
        force_ascii=False, orient="records")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='1-3-c decode annotations')
    parser.add_argument('--file', help='File containing Label Studio annotations',
                        type=str, required=True)
    args = parser.parse_args()

    main(args.file)
