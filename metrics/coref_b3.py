"""Coreference B3 metric

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
from sklearn.metrics.cluster import contingency_matrix


def bcubed(targets, predictions, beta: float = 1):
    """B3 metric (see Baldwin1998)
    Args:
        targets (torch.Tensor): true labels
        predictions (torch.Tensor): predicted labels
        beta (float, optional): beta for f_score. Defaults to 1.
    Returns:
        Tuple[float, float, float]: b3 f1, precision and recall
    """

    cont_mat = contingency_matrix(targets, predictions)
    cont_mat_norm = cont_mat / cont_mat.sum()

    precision = np.sum(cont_mat_norm * (cont_mat /
                       cont_mat.sum(axis=0))).item()
    recall = np.sum(cont_mat_norm * (cont_mat /
                    np.expand_dims(cont_mat.sum(axis=1), 1))).item()
    f1_score = (1 + beta) * precision * recall / (beta * (precision + recall))

    return f1_score, precision, recall


def compare_instance(ref_entities, pred_entities):
    for mention in ref_entities:
        mention['mark'] = False
    for mention in pred_entities:
        mention['mark'] = False

    y_true = []
    y_pred = []
    for ref_mention in ref_entities:
        ref_sent = ref_mention['sent_id']
        ref_start, ref_end = ref_mention['pos']

        for pred_mention in pred_entities:
            if pred_mention['mark']:
                continue
            if pred_mention['sent_id'] != ref_sent:
                continue
            if pred_mention['pos'][0] != ref_start or pred_mention['pos'][1] != ref_end:
                continue

            pred_mention['mark'] = True
            ref_mention['mark'] = True
            y_true.append(ref_mention['cluster'])
            y_pred.append(pred_mention['cluster'])
            break

        if not ref_mention['mark']:
            ref_mention['mark'] = True
            y_true.append(ref_mention['cluster'])
            y_pred.append(-1)

    for mention in pred_entities:
        if not mention['mark']:
            mention['mark'] = True
            y_true.append(-1)
            y_pred.append(mention['cluster'])

    return np.array(y_true), np.array(y_pred)


def main(truth_file: str, pred_file: str):
    """Main entrypoint
    Args:
        truth_file (str): path to ground truth data
        pred_file (str): path to predicted data
    """
    with open(truth_file, 'r', encoding='utf-8') as f:
        ref_linked_docred = json.load(f)
    ref_linked_docred_entities = []
    cluster_id = 0
    for instance in ref_linked_docred:
        out_instance = []
        for entity in instance['entities']:
            for mention in entity['mentions']:
                out_instance.append({
                    'name': mention['name'],
                    'sent_id': mention['sent_id'],
                    'pos': mention['pos'],
                    'type': entity['type'],
                    'cluster': cluster_id
                })
                cluster_id += 1
    ref_linked_docred_entities.append(out_instance)

    with open(pred_file, 'r', encoding='utf-8') as f:
        pred_linked_docred = json.load(f)
    pred_linked_docred_entities = []
    cluster_id = 0
    for instance in pred_linked_docred:
        out_instance = []
        for entity in instance['entities']:
            for mention in entity['mentions']:
                out_instance.append({
                    'name': mention['name'],
                    'sent_id': mention['sent_id'],
                    'pos': mention['pos'],
                    'type': entity['type'],
                    'cluster': cluster_id
                })
                cluster_id += 1
    pred_linked_docred_entities.append(out_instance)

    ys_true = []
    ys_pred = []
    for ref_instance, pred_instance in zip(ref_linked_docred_entities, pred_linked_docred_entities):
        y_true, y_pred = compare_instance(ref_instance, pred_instance)
        ys_true.append(y_true)
        ys_pred.append(y_pred)

    ys_true = np.concatenate(ys_true)
    ys_pred = np.concatenate(ys_pred)

    f1_score, precision, recall = bcubed(ys_true, ys_pred)
    print(f"B3 - Prec={precision}, Rec={recall}, F1={f1_score}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Coref B3')
    parser.add_argument('--truth_file', help='Path to ground truth entities (in Linked-DocRED format)',
                        type=str, required=True)
    parser.add_argument('--pred_file', help='Path to predicted entities (in Linked-DocRED format)',
                        type=str, required=True)
    args = parser.parse_args()

    main(args.truth_file, args.pred_file)
