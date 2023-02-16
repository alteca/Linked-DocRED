"""Prepare manual annotation
Inputs: 1_not_matched_docred_elasticsearch.jsonl
Output: 1_not_matched_docred_elasticsearch_label_studio.json

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
import json
from dotenv import load_dotenv
from tqdm.auto import tqdm
import pandas as pd
from .utils import read_docred
from .search_wikipedia import WikipediaSearch

load_dotenv()

DOCRED_PATH = os.getenv('DOCRED_PATH')
EL_DATA_PATH = os.getenv('EL_DATA_PATH')
SEARCH_ENGINE_URL = os.getenv('SEARCH_ENGINE_URL')
NUM_CANDIDATES = 5

docred = read_docred(DOCRED_PATH)


def main(num_candidates: int = NUM_CANDIDATES):
    """Generate instances that need to be manually annotated. For each of these
        instances search for potential candidates.

    Args:
        num_candidates (int, optional): number of candidates per instance.
                Defaults to NUM_CANDIDATES.
    """
    to_annotate = pd.read_json(
        f"{EL_DATA_PATH}/1_not_matched_docred_elasticsearch.jsonl", orient="records")
    to_annotate['text'] = to_annotate.apply(
        lambda r: docred[r['dataset']][r['id']]['text'], axis='columns')
    to_annotate['wiki_url'] = to_annotate['resource'].apply(
        lambda r: f'<a href="https://en.wikipedia.org/wiki/{r}">{r}</a>')

    # Write line by line to avoid in case of bug
    with open(f"{EL_DATA_PATH}/1_not_matched_docred_elasticsearch_label_studio.jsonl", "w",
              encoding="utf-8") as f:
        wikipedia_search = WikipediaSearch(SEARCH_ENGINE_URL)

        for _, r in tqdm(to_annotate.iterrows(), total=len(to_annotate)):
            keywords = r['text'].split(" ")[0:10]

            out = {
                "dataset": r["dataset"],
                "id": r["id"],
                "text": r["text"],
                "resource": r['resource'],
                "wiki_url": r["wiki_url"],
            }

            candidates = wikipedia_search.get_search_results(
                keywords, num_candidates)
            for i in range(num_candidates):
                if i >= len(candidates):
                    out[f'candidate_{i}'] = ""
                    out[f'candidate_{i}_alias'] = ""
                else:
                    candidate = candidates[i]
                    out[f'candidate_{i}'] = f"{candidate['title']} - {candidate['summary'][0:100]}\
({candidate['url']})"
                    out[f'candidate_{i}_alias'] = candidate['url']

            f.write(json.dumps(out, ensure_ascii=False))
            f.write("\n")

        wikipedia_search.close()

    # Write right format for Label Studio
    to_annotate = pd.read_json(
        f"{EL_DATA_PATH}/1_not_matched_docred_elasticsearch_label_studio.jsonl", lines=True)
    with open(f"{EL_DATA_PATH}/1_not_matched_docred_elasticsearch_label_studio.json", 'w',
              encoding='utf-8') as file:
        to_annotate.to_json(file, force_ascii=False, orient="records")


if __name__ == "__main__":
    main()
