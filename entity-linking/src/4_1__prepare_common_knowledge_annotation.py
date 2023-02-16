"""Prepare common knowledge annotation
Input: 3_hyperlinks_alignment_links_in_page.jsonl
Output: 4_common_knowledge_label_studio.json
"""
import os
import json
from dotenv import load_dotenv
import pandas as pd
from tqdm.auto import tqdm
from .utils import preprocess_entity
from .search_wikipedia import WikipediaSearch

load_dotenv()

DOCRED_PATH = os.getenv('DOCRED_PATH')
EL_DATA_PATH = os.getenv('EL_DATA_PATH')
SEARCH_ENGINE_URL = os.getenv('SEARCH_ENGINE_URL')
NUM_CANDIDATES = 5
MIN_ENTITY_APPEARANCE = 3


def main():
    """Main Entrypoint
    """
    docred = []
    with open(f'{EL_DATA_PATH}/3_hyperlinks_alignment_links_in_page.jsonl', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            docred.append(json.loads(line))

    rows = []
    for i, instance in enumerate(docred):
        for entity_id, entity in enumerate(instance['entities']):
            if entity['entity_linking']['wikipedia_resource'] is None:
                rows.append({
                    'dataset': instance['dataset'],
                    'id': i,
                    'entity_id': entity_id,
                    'entity_type': entity['mentions'][0]['type'],
                    'entity_text': entity['mentions'][0]['name'],
                    'entity_texts': [mention['name'] for mention in entity['mentions']],
                })

    not_labeled = pd.DataFrame(rows)
    not_labeled = not_labeled[~not_labeled['entity_type'].isin([
                                                               'TIME', 'NUM'])]
    not_labeled = not_labeled.copy()
    not_labeled['entity_texts'] = not_labeled['entity_texts'].apply(
        lambda l: list(set(l)))
    not_labeled['text'] = not_labeled.apply(
        lambda r: docred[r['dataset']][r['id']]['text'], axis='columns')

    rows = []
    for _, r in not_labeled.iterrows():
        entity_type = r['entity_type']
        for text in r['entity_texts']:
            rows.append({
                'text': text,
                'entity_type': entity_type,
                'simplified_text': preprocess_entity(text)
            })
    not_labeled = pd.DataFrame(rows)

    most_common_entities = not_labeled[not_labeled['simplified_text'] != ''].groupby(
        ['simplified_text', 'entity_type']).size().reset_index(name='count')
    most_common_entities = most_common_entities[most_common_entities['count'] > MIN_ENTITY_APPEARANCE].copy(
    )

    wikipedia_search = WikipediaSearch(SEARCH_ENGINE_URL)
    most_common_entities['examples'] = None
    most_common_entities['candidates'] = None
    for i, r in tqdm(most_common_entities.iterrows(), total=len(most_common_entities)):
        entities = not_labeled[(not_labeled['entity_type'] == r['entity_type']) & (
            not_labeled['entity_texts_simplified'].str.contains(f"${r['simplified_text']}$", regex=False))]
        # Examples
        sampled_entities = entities.sample(n=min(5, len(entities)))
        examples = []
        for _, rs in sampled_entities.iterrows():
            text = rs['text']
            for e in rs['entity_texts']:
                text = text.replace(e, f"<mark>{e}</mark>")
            examples.append({
                'text': text
            })
        most_common_entities.at[i, 'examples'] = examples

        # Candidates
        entity_text = entities['entity_text'].apply(
            lambda t: t.lower()).value_counts().reset_index().iloc[0]['index']
        keywords = entity_text.split(" ")
        candidates = wikipedia_search.get_search_results(
            keywords, NUM_CANDIDATES)
        o_candidates = []
        for cand in candidates:
            o_candidates.append({
                "text": f"{cand['title']} - {cand['summary'][0:100]} ({cand['url']})",
                "resource": cand['url']
            })
        most_common_entities.at[i, 'candidates'] = o_candidates

    with open(f"{EL_DATA_PATH}/4_common_knowledge_label_studio.json", 'w', encoding='utf-8') \
        as file:
        most_common_entities.to_json(file, orient="records", force_ascii=False)


if __name__ == '__main__':
    main()
