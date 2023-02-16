import json
import argparse
import spacy
import neuralcoref
import numpy as np
from tqdm.auto import tqdm


def pos_to_sent(pos, start_pos):
    for i in range(0, len(start_pos)):
        if start_pos[i] > pos:
            return i-1, pos - start_pos[i-1]


def read_docred(path):
    with open(path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    return dataset


def most_frequent(List):
    return max(set(List), key=List.count)


def main(linked_docred_path: str, entity_path: str, save_dir: str):
    """Main entrypoint
    Args:
        linked_docred_path (str): Path to Linked-DocRED dataset
        entity_path (str): Path to predicted entities
        save_dir (str): output directory
    """
    docred_dev = read_docred(f'{linked_docred_path}/dev.json')

    # Compute coreferences
    nlp = spacy.load('en_core_web_sm')
    nlp.tokenizer = nlp.tokenizer.tokens_from_list
    coref = neuralcoref.NeuralCoref(nlp.vocab)
    nlp.add_pipe(coref, name='neuralcoref')

    for instance in tqdm(docred_dev):
        doc = [tok for sent in instance['sents'] for tok in sent]
        cum_sent_pos = [len(sent) for sent in instance['sents']]
        cum_sent_pos = np.insert(np.cumsum(cum_sent_pos), 0, 0).tolist()
        nlp_doc = nlp(doc)

        coreferences = []
        if nlp_doc._.has_coref:
            for cluster in nlp_doc._.coref_clusters:
                cls = []
                for m in cluster.mentions:
                    sent_id, start_pos = pos_to_sent(m.start, cum_sent_pos)
                    end_pos = start_pos + m.end - m.start
                    cls.append({
                        'sent': sent_id,
                        'pos': [start_pos, end_pos]
                    })
                coreferences.append(cls)
        instance['coreferences'] = coreferences

    docred_pred_coreferences = []
    for instance in docred_dev:
        out_instance = []
        for coreference in instance['coreferences']:
            out_coref = []
            for mention in coreference:
                out_coref.append({
                    'sent_id': mention['sent'],
                    'pos': mention['pos'],
                })
            out_instance.append(out_coref)
        docred_pred_coreferences.append(out_instance)

    # Load predicted entities
    predictions = []
    with open(entity_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            predictions.append(json.loads(line))

    docred_pred_entities = []
    for i, instance in enumerate(predictions):
        out_instance = []
        instance_sent = docred_dev[i]['sents']
        cum_sent_pos = [len(sent) for sent in instance_sent]
        cum_sent_pos = np.insert(np.cumsum(cum_sent_pos), 0, 0).tolist()

        for mention in instance['predicted_ner'][0]:
            sent_id, start_pos = pos_to_sent(mention[0], cum_sent_pos)
            end_pos = min(
                start_pos + mention[1] - mention[0] + 1, len(instance_sent[sent_id]))
            out_instance.append({
                'sent_id': sent_id,
                'pos': [start_pos, end_pos],
                'type': mention[2]
            })
        docred_pred_entities.append(out_instance)

    # Merge coreferences and entities
    cluster_id = 0
    for coref_inst, ent_inst in zip(docred_pred_coreferences, docred_pred_entities):
        for ent in ent_inst:
            ent['cluster'] = None

        for cluster in coref_inst:
            for cl_mention in cluster:
                cl_sent = cl_mention['sent_id']
                cl_start = cl_mention['pos'][0]
                cl_end = cl_mention['pos'][1]

                for ent in ent_inst:
                    if ent['cluster'] is not None:
                        continue
                    if ent['sent_id'] != cl_sent:
                        continue
                    if ent['pos'][0] != cl_start or ent['pos'][1] != cl_end:
                        continue
                    ent['cluster'] = cluster_id
                    break
            cluster_id += 1

        for ent in ent_inst:
            if ent['cluster'] is None:
                ent['cluster'] = cluster_id
                cluster_id += 1

    output_entities = []
    for instance, pred_entities in tqdm(zip(docred_dev, docred_pred_entities)):
        out_entities = []
        min_cluster = min([ent['cluster'] for ent in pred_entities])
        max_cluster = max([ent['cluster'] for ent in pred_entities])
        for i in range(min_cluster, max_cluster+1):
            cluster = [{
                'sent_id': ent['sent_id'],
                'pos': ent['pos'],
                'name': ' '.join(instance['sents'][ent['sent_id']][ent['pos'][0]:ent['pos'][1]])} for ent in pred_entities if ent['cluster'] == i]
            if len(cluster) > 0:
                type = most_frequent(
                    [ent['type'] for ent in pred_entities if ent['cluster'] == i])
                out_entities.append({'mentions': cluster, 'type': type})

        output_entities.append({
            'title': instance['title'],
            'sents': instance['sents'],
            'entities': out_entities,
        })

    with open(f'{save_dir}/dev_pred_entities.json', 'w', encoding='utf-8') as f:
        json.dump(output_entities, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='NeuralCoref coreferences')
    parser.add_argument('--data_dir', help='Path do Linked-DocRED',
                        type=str, required=True)
    parser.add_argument('--entity_path', help='Path do PURE predicted entities',
                        type=str, required=True)
    parser.add_argument('--save_dir', help='Path to store coreferences',
                        type=str, required=True)
    args = parser.parse_args()

    main(args.data_dir, args.entity_path, args.save_dir)
