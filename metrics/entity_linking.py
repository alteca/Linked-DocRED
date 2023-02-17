"""Entity-centry Entity-Linking metrics

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
import argparse
import json
import numpy as np
import pandas as pd


def compare_entity_mentions(m1, m1_type, m2, m2_type):
    return m1_type == m2_type and m1['sent_id'] == m2['sent_id'] and m1['pos'][0] == m2['pos'][0] and m1['pos'][1] == m2['pos'][1]


def main(truth_file: str, pred_file: str):
    """Main entrypoint
    Args:
        truth_file (str): path to ground truth data
        pred_file (str): path to predicted data
    """
    with open(truth_file, 'r', encoding='utf-8') as f:
        ref_linked_docred = json.load(f)

    with open(pred_file, 'r', encoding='utf-8') as f:
        pred_linked_docred = json.load(f)
    pred_linked_docred_mentions = []
    for instance in pred_linked_docred:
        out_mentions = []
        for entity in instance['entities']:
            candidates = entity['predicted_entity_linking']
            for mention in entity['mentions']:
                out_mentions.append({
                    'sent_id': mention['sent_id'],
                    'pos': mention['pos'],
                    'candidates': candidates,
                    'type': entity['type']
                })
        pred_linked_docred_mentions.append(out_mentions)

    results = []
    for instance, mentions_pred in zip(ref_linked_docred, pred_linked_docred_mentions):
        for entity in instance['entities']:
            wiki_resources = {}

            # Merge candidates using all mentions
            entity_type = entity['type']

            if entity_type in ['NUM', 'TIME']:
                continue

            for mention in entity['mentions']:
                marked_cands = {k: False for k in wiki_resources}

                for mention_pred in mentions_pred:
                    if compare_entity_mentions(mention, entity_type, mention_pred, mention_pred['type']):
                        num_candidates = len(mention_pred['candidates'])

                        for i, cand in enumerate(mention_pred['candidates']):
                            if cand in wiki_resources:
                                wiki_resources[cand] = wiki_resources[cand] + i
                                marked_cands[cand] = True
                            else:
                                wiki_resources[cand] = + i

                        for k, marked in marked_cands.items():
                            if not marked:
                                wiki_resources[k] += num_candidates

            # Compute ranking
            wiki_scores = [v for k, v in wiki_resources.items()]
            wiki_resources = [k for k, v in wiki_resources.items()]

            indexes = np.argsort(wiki_scores)
            wiki_resources = [wiki_resources[i] for i in indexes]

            results.append({
                'entity': entity,
                'candidates': wiki_resources
            })

    out = []
    for res in results:
        try:
            rank = res['candidates'].index(
                res['entity']['entity_linking']['wikipedia_resource']) + 1
        except ValueError:
            rank = -1
        out.append({
            'rank': rank,
            'confidence': res['entity']['entity_linking']['confidence']
        })
    out = pd.DataFrame(out)

    hit_at_1 = len(out[out['rank'] == 1]) / len(out)
    hit_at_5 = len(out[(out['rank'] <= 5) & (out['rank'] > -1)]) / len(out)
    mean_rank = out.loc[out['rank'] != -1, 'rank'].mean()
    not_found = len(out[out['rank'] == -1]) / len(out)
    print(
        f"Hit@1={hit_at_1}, Hit@5={hit_at_5}, Mean Rank={mean_rank}, Not Found={not_found}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Entity F1')
    parser.add_argument('--truth_file', help='Path to ground truth entities (in Linked-DocRED format)',
                        type=str, required=True)
    parser.add_argument('--pred_file', help='Path to predicted entities (in Linked-DocRED format)',
                        type=str, required=True)
    args = parser.parse_args()

    main(args.truth_file, args.pred_file)
