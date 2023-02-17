"""Entity-centric Relation F1 score

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
from tqdm.auto import tqdm
import math

def generate_relation_mentions_from_entity(h_entity, relation, t_entity):
    for h_mention in h_entity['mentions']:
            for t_mention in t_entity['mentions']:
                yield {
                    'h': h_mention,
                    'h_type': h_entity['type'],
                    'r': relation,
                    't': t_mention,
                    't_type': t_entity['type']
                }

def len_relation_mentions(h_entity, relation, t_entity):
    return len(h_entity['mentions']) * len(t_entity['mentions'])

def compare_entity_mentions(m1, m2):
    # Types are supposed equal (guaranteed by formula)
    return m1['sent_id'] == m2['sent_id'] and m1['pos'][0] == m2['pos'][0] and m1['pos'][1] == m2['pos'][1]

def compare_relation_mention(r1, r2):
    # Relation types are supposed equal (guaranteed by formula)
    h1, h1_type, r1, t1, t1_type = r1['h'], r1['h_type'], r1['r'], r1['t'], r1['t_type']
    h2, h2_type, r2, t2, t2_type = r2['h'], r2['h_type'], r2['r'], r2['t'], r2['t_type']
    return h1_type == h2_type and t1_type == t2_type and compare_entity_mentions(h1, h2) and compare_entity_mentions(t1, t2)

def tp_p_cluster(p_c, G_M_type, hard_aggregation):
    # tp_p for a cluster of an instance
    intersection = 0
    for c_mention in generate_relation_mentions_from_entity(p_c['h'], p_c['r'], p_c['t']):
        for g_mention in G_M_type:
            if compare_relation_mention(c_mention, g_mention):
                intersection += 1
                break
    len_pc = len_relation_mentions(p_c['h'], p_c['r'], p_c['t'])
    if len_pc > 0:
        res = intersection / len_pc
        if hard_aggregation:
            return math.floor(res)
        else:
            return res
    else:
        return None
    
def tp_g_cluster(g_c, P_M_type, hard_aggregation):
    # tp_g for a cluster of an instance
    intersection = 0
    for c_mention in generate_relation_mentions_from_entity(g_c['h'], g_c['r'], g_c['t']):
        for g_mention in P_M_type:
            if compare_relation_mention(c_mention, g_mention):
                intersection += 1
                break
    len_gc = len_relation_mentions(g_c['h'], g_c['r'], g_c['t'])
    if len_gc > 0:
        res = intersection / len_gc
        if hard_aggregation:
            return math.floor(res)
        else:
            return res
    else:
        return None

def main(truth_file: str, pred_file: str, hard_aggregation: bool):
    """Main entrypoint
    Args:
        truth_file (str): path to ground truth data
        pred_file (str): path to predicted data
        hard_aggregation (bool): wether to use soft or hard aggregation
    """
    with open(truth_file, 'r', encoding='utf-8') as f:
        ref_linked_docred = json.load(f)
        
    with open(pred_file, 'r', encoding='utf-8') as f:
        pred_linked_docred = json.load(f)
    
    tags = ["P6", "P17", "P19", "P20", "P22", "P25", "P26", "P27", "P30", "P31", "P35", "P36", "P37", 
        "P39", "P40", "P50", "P54", "P57", "P58", "P69", "P86", "P102", "P108", "P112", "P118", "P123", 
        "P127", "P131", "P136", "P137", "P140", "P150", "P155", "P156", "P159", "P161", "P162", "P166", 
        "P170", "P171", "P172", "P175", "P176", "P178", "P179", "P190", "P194", "P205", "P206", "P241", 
        "P264", "P272", "P276", "P279", "P355", "P361", "P364", "P400", "P403", "P449", "P463", "P488", 
        "P495", "P527", "P551", "P569", "P570", "P571", "P576", "P577", "P580", "P582", "P585", "P607", 
        "P674", "P676", "P706", "P710", "P737", "P740", "P749", "P800", "P807", "P840", "P937", "P1001", 
        "P1056", "P1198", "P1336", "P1344", "P1365", "P1366", "P1376", "P1412", "P1441", "P3373"]
    # Instance > Tag > Cluster > Mention
    P_C = []
    G_C = []
    # Instance > Tag > Mention
    P_M = []
    G_M = []

    for instance_pred in tqdm(pred_linked_docred):
        # Predicted relations
        P_C_inst = {t:[] for t in tags}
        P_M_inst = {t:[] for t in tags}
        entities = instance_pred['entities']
        for relation in instance_pred['relations']:
            h_entity = entities[relation['h']]
            t_entity = entities[relation['t']]
            
            P_C_type = P_C_inst[relation['r']]
            P_C_type.append({
                'h': h_entity,
                'r': relation,
                't': t_entity
            })
            
            P_M_type = P_M_inst[relation['r']]
            P_M_type.extend(generate_relation_mentions_from_entity(h_entity, relation, t_entity))
        P_C.append(P_C_inst)
        P_M.append(P_M_inst)
        
    for instance in tqdm(ref_linked_docred):
        # Ground truth
        G_C_inst = {t:[] for t in tags}
        G_M_inst = {t:[] for t in tags}
        entities = instance['entities']
        for relation in instance['relations']:
            h_entity = entities[relation['h']]
            t_entity = entities[relation['t']]
            
            G_C_type = G_C_inst[relation['r']]
            G_C_type.append({
                'h': h_entity,
                'r': relation,
                't': t_entity
            })
            
            G_M_type = G_M_inst[relation['r']]
            G_M_type.extend(generate_relation_mentions_from_entity(h_entity, relation, t_entity))
        G_C.append(G_C_inst)
        G_M.append(G_M_inst)
    
    TP_P = {t:0 for t in tags}
    P_C_count = {t:0 for t in tags}
    FP = {t:0 for t in tags}
    for p_c_inst, g_m_inst in tqdm(zip(P_C, G_M)):
        for type in p_c_inst:
            for p_cluster in p_c_inst[type]:
                tp_p = tp_p_cluster(p_cluster, g_m_inst[type], hard_aggregation)
                if tp_p is not None:
                    TP_P[type] += tp_p
            P_C_count[type] += len(p_c_inst[type])

    for type in FP:
        FP[type] = P_C_count[type] - TP_P[type]
        
    TP_G = {t:0 for t in tags}
    G_C_count = {t:0 for t in tags}
    FN = {t:0 for t in tags}
    for g_c_inst, p_m_inst in tqdm(zip(G_C, P_M)):
        for type in g_c_inst:
            for g_cluster in g_c_inst[type]:
                tp_g = tp_g_cluster(g_cluster, p_m_inst[type], hard_aggregation)
                if tp_g is not None:
                    TP_G[type] += tp_g
            G_C_count[type] += len(g_c_inst[type])

    for type in FN:
        FN[type] = G_C_count[type] - TP_G[type]
    
    P = sum(TP_P.values()) / (sum(TP_P.values()) + sum(FP.values()))
    R = sum(TP_G.values()) / (sum(TP_G.values()) + sum(FN.values()))
    F1 = 2 * (P * R) / (P + R)
    print(f"Prec={P}, Rec={R}, F1={F1}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Relation F1')
    parser.add_argument('--truth_file', help='Path to ground truth relations (in Linked-DocRED format)',
                        type=str, required=True)
    parser.add_argument('--pred_file', help='Path to predicted relations (in Linked-DocRED format)',
                        type=str, required=True)
    parser.add_argument('--hard', help='Wether to use soft or hard aggregation', action='store_true')
    parser.set_defaults(hard=False)
    args = parser.parse_args()

    main(args.truth_file, args.pred_file, args.hard)