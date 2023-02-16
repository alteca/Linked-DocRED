"""Mention Level NER metrics
"""
import argparse
import json
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score


def compare_instance(ref_mentions: list, pred_mentions: list) -> np.array:
    """Compare mentions of the reference and predicted Linked-DocRED instance
    Args:
        ref_mentions (list): true mentions
        pred_mentions (list): predicted mentions
    Returns:
        np.array: classifications
    """
    for mention in ref_mentions:
        mention['mark'] = False
    for mention in pred_mentions:
        mention['mark'] = False

    y_true = []
    y_pred = []
    for ref_mention in ref_mentions:
        ref_sent = ref_mention['sent_id']
        ref_start, ref_end = ref_mention['pos']

        for pred_mention in pred_mentions:
            if pred_mention['mark']:
                continue
            if pred_mention['sent_id'] != ref_sent:
                continue
            if pred_mention['pos'][0] != ref_start or pred_mention['pos'][1] != ref_end:
                continue

            pred_mention['mark'] = True
            ref_mention['mark'] = True
            y_true.append(ref_mention['type'])
            y_pred.append(pred_mention['type'])
            break

        if not ref_mention['mark']:
            ref_mention['mark'] = True
            y_true.append(ref_mention['type'])
            y_pred.append('na')

    for mention in pred_mentions:
        if not mention['mark']:
            mention['mark'] = True
            y_true.append('na')
            y_pred.append(mention['type'])

    return np.array(y_true), np.array(y_pred)


def main(truth_file: str, pred_file: str):
    """Main entrypoint
    Args:
        truth_file (str): path to ground truth data
        pred_file (str): path to predicted data
    """
    # Load mentions
    with open(truth_file, 'r', encoding='utf-8') as f:
        ref_linked_docred = json.load(f)
    ref_linked_docred_mentions = []
    for instance in ref_linked_docred:
        out_instance = []
        for entity in instance['entities']:
            for mention in entity['mentions']:
                out_instance.append({
                    'name': mention['name'],
                    'sent_id': mention['sent_id'],
                    'pos': mention['pos'],
                    'type': entity['type'],
                })
    ref_linked_docred_mentions.append(out_instance)

    with open(pred_file, 'r', encoding='utf-8') as f:
        pred_linked_docred = json.load(f)
    pred_linked_docred_mentions = []
    for instance in pred_linked_docred:
        out_instance = []
        for entity in instance['entities']:
            for mention in entity['mentions']:
                out_instance.append({
                    'name': mention['name'],
                    'sent_id': mention['sent_id'],
                    'pos': mention['pos'],
                    'type': entity['type'],
                })
    pred_linked_docred_mentions.append(out_instance)

    ys_true = []
    ys_pred = []
    for ref_instance, pred_instance in zip(ref_linked_docred_mentions, pred_linked_docred_mentions):
        y_true, y_pred = compare_instance(ref_instance, pred_instance)
        ys_true.append(y_true)
        ys_pred.append(y_pred)

    ys_true = np.concatenate(ys_true)
    ys_pred = np.concatenate(ys_pred)

    precision, recall, fscore, _ = precision_recall_fscore_support(
        ys_true, ys_pred, average='micro')
    accuracy = accuracy_score(ys_true, ys_pred)
    print(
        f"Prec={precision}, Rec={recall}, F1(micro)={fscore}, Accuracy={accuracy}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='NER F1')
    parser.add_argument('--truth_file', help='Path to ground truth entities (in Linked-DocRED format)',
                        type=str, required=True)
    parser.add_argument('--pred_file', help='Path to predicted entities (in Linked-DocRED format)',
                        type=str, required=True)
    args = parser.parse_args()

    main(args.truth_file, args.pred_file)
