"""Prepare manual annotation
Input: 4_hyperlinks_alignment_links_in_page_common_knowledge.json
Output: 5_manual_annotation_candidates.json

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
import math
from dotenv import load_dotenv
import pandas as pd
from tqdm.auto import tqdm
import seaborn as sns
from .search_wikipedia import WikipediaSearch
from .utils import read_docred

load_dotenv()

DOCRED_PATH = os.getenv('DOCRED_PATH')
EL_DATA_PATH = os.getenv('EL_DATA_PATH')
SEARCH_ENGINE_URL = os.getenv('SEARCH_ENGINE_URL')
NUM_CANDIDATES = 5

docred = read_docred(DOCRED_PATH)


def rgb_to_str(rgb: tuple) -> str:
    """Convert rgb tuple to str code
    Args:
        rgb (tuple): rgb tuple
    Returns:
        tuple: color, text color
    """
    r, g, b = rgb
    luminance = (0.2126*r) + (0.7152*g) + (0.0722*b)
    text_color = 'black' if luminance > 0.36 else 'white'
    return f'rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})', text_color


def get_color(tag_type: str, index: int, n_colors: int, bias=2):
    """Generate color depending on type
    Args:
        tag_type (str): type
        index (int): n° of entity in the specific type
        n_colors (int): total nb of entities in the specific type
        bias (int, optional): bias. Defaults to 2.

    Returns:
        str: color, text color
    """
    if tag_type == 'LOC':
        return rgb_to_str(sns.color_palette("Greens", n_colors=n_colors+bias)[index+bias])
    elif tag_type == 'PER':
        return rgb_to_str(sns.color_palette("RdPu", n_colors=n_colors+bias)[index+bias])
    elif tag_type == 'ORG':
        return rgb_to_str(sns.color_palette("Blues", n_colors=n_colors+bias)[index+bias])
    elif tag_type == 'MISC':
        return rgb_to_str(sns.color_palette("YlOrBr", n_colors=n_colors+bias)[index+bias])


def handle_instance(instance: dict, instance_id: int, dataset_name: str, all_entities_indexed: dict) -> dict:
    """Handle instance to generate annotation task
    Args:
        instance (dict): instance
        instance_id (int): instance id
        dataset_name (str): dataset name
        all_entities_indexed (dict): every entity
    Returns:
        dict: annotation
    """
    title = instance['title']
    sentences = instance['sents'].copy()

    to_disambiguate = []
    disambiguated = []

    color_index = {'LOC': 0, 'ORG': 0, 'PER': 0, 'MISC': 0}
    total_colors = {'LOC': 0, 'ORG': 0, 'PER': 0, 'MISC': 0}
    for entity in instance['vertexSet']:
        entity_type = entity[0]['type']
        if entity_type in ['NUM', 'TIME']:
            continue
        else:
            total_colors[entity_type] += 1

    wikipedia_search = WikipediaSearch(SEARCH_ENGINE_URL)
    for entity_id, entity in enumerate(instance['vertexSet']):
        entity_type = entity[0]['type']
        if entity_type in ['NUM', 'TIME']:
            continue

        color, text_color = get_color(
            entity_type, color_index[entity_type], total_colors[entity_type])
        color_index[entity_type] += 1

        entity_linked_row = all_entities_indexed.loc[(
            dataset_name, instance_id, entity_id)]
        entity_text = entity_linked_row['entity_text']

        entity_resource = entity_linked_row['resource']
        is_disambiguated = entity_resource is not None and (
            isinstance(entity_resource, str) or not math.isnan(entity_resource))
        if not is_disambiguated:
            candidates = wikipedia_search.get_search_results(
                entity_text.split(" "), NUM_CANDIDATES)
            o_candidates = []
            for cand in candidates:
                o_candidates.append({
                    "text": f"{cand['title']} - {cand['summary'][0:100]} ({cand['url']})",
                    "resource": cand['url']
                })

            to_disambiguate.append({
                'entity_id': entity_id,
                'type': entity_type,
                'text': entity_text,
                'color': color,
                'text_color': text_color,
                'html': f'{entity_id} - ({entity_type}) <span style="background-color:{color};color:{text_color}">{entity_text}</span>',
                'candidates': o_candidates
            })
        else:
            disambiguated.append({
                'entity_id': entity_id,
                'type': entity_type,
                'text': entity_text,
                'resource': entity_resource,
                'html': f'<p>{entity_id} - ({entity_type}) <b><span style="color:{color}">{entity_text}</span></b> <a href="https://en.wikipedia.org/wiki/{entity_resource}">{entity_resource}</a></p>',
                'color': color
            })

        for mention in entity:
            sent_id = mention['sent_id']
            start_token = mention['pos'][0]
            end_token = mention['pos'][1] - 1
            if not is_disambiguated:
                opening_tag = f'<span style="background-color:{color};color:{text_color}">'
                closing_tag = '</span>'
            else:
                opening_tag = f'<b><span style="color:{color}">'
                closing_tag = '</span></b>'
            sentences[sent_id][start_token] = opening_tag + \
                sentences[sent_id][start_token]
            sentences[sent_id][end_token] = sentences[sent_id][end_token] + closing_tag

    text = '<p>' + ' '.join([' '.join([tok for tok in sent])
                            for sent in sentences]) + '</p>'
    return {
        'dataset': dataset_name,
        'id': instance_id,
        'title': title,
        'html_text': text,
        'disambiguated': disambiguated,
        'to_disambiguate': to_disambiguate,
        'legend': '<span style="background-color:#4BB061">LOC</span> - <span style="background-color:#F887AC">PER</span> - <span style="background-color:#6AADD5">ORG</span> - <span style="background-color:#FD9828;">MISC</span>'
    }


def handle_dataset(dataset: list, name: str, all_entities_indexed: dict) -> pd.DataFrame:
    """Handle dataset
    Args:
        dataset (list): dataset
        name (str): name of dataset
        all_entities_indexed (dict): every entity
    Returns:
        pd.DataFrame: processed dataset
    """
    rows = []
    for i, instance in tqdm(enumerate(dataset), total=len(dataset)):
        row = handle_instance(instance, i, name, all_entities_indexed)
        if len(row['to_disambiguate']) > 0:
            rows.append(row)
    return pd.DataFrame(rows)


def main():
    """Main entrypoint
    """
    with open(f'{EL_DATA_PATH}/4_hyperlinks_alignment_links_in_page_common_knowledge.json', 'r',
              encoding='utf-8') as f:
        processed_docred = json.load(f)

    rows = []
    for instance in processed_docred:
        for i, entity in enumerate(instance['entities']):
            rows.append({
                'dataset': instance['dataset'],
                'id': instance['id'],
                'entity_id': i,
                'entity_type': entity['type'],
                'entity_text': entity['mentions'][0]['name'],
                'wikipedia_resource': entity['entity_linking']['wikipedia_resource']
            })
    all_entities_indexed = pd.DataFrame(rows)
    all_entities_indexed = all_entities_indexed.set_index(
        ['dataset', 'id', 'entity_id']).sort_index()

    out_dataset = []
    for name, dataset in docred.items():
        out_dataset.append(handle_dataset(dataset, name, all_entities_indexed))
    out_dataset = pd.concat(out_dataset, ignore_index=True, axis='rows')

    with open(f"{EL_DATA_PATH}/5_manual_annotation_candidates.json", 'w', encoding='utf-8') as file:
        out_dataset.to_json(file, orient="records", force_ascii=False)


if __name__ == '__main__':
    main()
