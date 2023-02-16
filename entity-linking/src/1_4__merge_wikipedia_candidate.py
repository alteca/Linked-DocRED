"""Merge manual annotation and automatically found Wikipedia articles
Input: 1_matched_docred_elasticsearch.jsonl
       1_not_matched_docred_elasticsearch_label_studio_annotated.json
Output: 1_matched_docred.jsonl

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
