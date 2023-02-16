import argparse
import os
import json
import numpy as np

def process_dataset(input_file, output_file, name):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    out_data = []
    for doc_key, instance in enumerate(data):
        if doc_key >= 10:
            break
        sents_start_pos = np.insert(np.cumsum([len(sent) for sent in instance['sents']]), 0, 0).tolist()
        
        sentences = [[word for sent in instance['sents'] for word in sent]]

        entities = instance['entities']
        ner = []
        for entity in entities:
            entity_type = entity['type']
            for mention in entity['mentions']:
                sent_offset = sents_start_pos[mention['sent_id']]
                pos = mention['pos']
                mention['doc_pos'] = (sent_offset + pos[0], sent_offset + pos[1] - 1)
                
                ner.append([mention['doc_pos'][0], mention['doc_pos'][1], entity_type])
        
        relations = []

        # Coref
        for entity in entities:
            mentions = entity['mentions']
            for i in range(len(mentions)):
                for j in range(i+1, len(mentions)):
                    mention1 = mentions[i]
                    mention2 = mentions[j]
                    
                    relations.append([*mention1['doc_pos'], *mention2['doc_pos'], 'COREF'])

        # Other relations
        for relation in instance['relations']:
            entity1 = entities[relation['h']]
            entity2 = entities[relation['t']]
            
            mention1 = entity1['mentions'][0]
            mention2 = entity2['mentions'][0]
            
            relations.append([*mention1['doc_pos'], *mention2['doc_pos'], relation['r']])
        
        out_data.append({
            'doc_key': f'key-{name}-{doc_key}',
            'sentences': sentences,
            'ner': [ner],
            'relations': [relations]
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for instance in out_data:
            json.dump(instance, f)
            f.write('\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_dir', type=str, default=None, required=True, 
                        help="path to the input dataset")
    parser.add_argument('--output_dir', type=str, default='entity_output', 
                        help="output directory of the dataset")
    
    args = parser.parse_args()
    
    # Paths
    args.input_train_data = os.path.join(args.input_dir, 'train_annotated.json')
    args.input_dev_data = os.path.join(args.input_dir, 'dev.json')
    args.input_test_data = os.path.join(args.input_dir, 'dev.json') # Change to test
    args.output_train_data = os.path.join(args.output_dir, 'train.json')
    args.output_dev_data = os.path.join(args.output_dir, 'dev.json')
    args.output_test_data = os.path.join(args.output_dir, 'test.json')
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Process dataset
    process_dataset(args.input_train_data, args.output_train_data, 'train')
    process_dataset(args.input_dev_data, args.output_dev_data, 'dev')
    process_dataset(args.input_test_data, args.output_test_data, 'test')