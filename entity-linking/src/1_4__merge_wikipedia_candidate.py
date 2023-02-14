"""Merge manual annotation and automatically found Wikipedia articles
Input: 1_matched_docred_elasticsearch.jsonl
       1_not_matched_docred_elasticsearch_label_studio_annotated.json
Output: 1_matched_docred.jsonl
"""
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

EL_DATA_PATH = os.getenv('EL_DATA_PATH')


def main():
    """Main entrypoint
    """
    # Get automatically matched data
    automatic_annotations = pd.read_json(
        f'{EL_DATA_PATH}/1_matched_docred_elasticsearch.jsonl', lines=True)
    automatic_annotations['method'] = 'elastic'
    automatic_annotations = automatic_annotations.drop(
        ["text_similarity", "text_clean"])

    # Get annotated data
    manual_annotations = pd.read_json(
        f"{EL_DATA_PATH}/1_not_matched_docred_elasticsearch_label_studio_annotated.json",
        orient="records")

    final_dataset = pd.concat(
        [automatic_annotations, manual_annotations], ignore_index=True, axis='rows')
    final_dataset = final_dataset.sort_values(
        ["dataset", "id"]).reset_index(drop=True)
    final_dataset.to_json(
        f"{EL_DATA_PATH}/1_matched_docred.jsonl", lines=True, orient="records")


if __name__ == "__main__":
    main()
