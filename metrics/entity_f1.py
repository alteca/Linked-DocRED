"""Entity-centric Entity F1 score

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

def compare_entity_mentions(m1, m2):
    # Types are supposed equal (guaranteed by formula)
    return m1['sent_id'] == m2['sent_id'] and m1['pos'][0] == m2['pos'][0] and m1['pos'][1] == m2['pos'][1]

def tp_p_cluster(p_c, G_M_type, hard_aggregation):
    # tp_p for a cluster of an instance
    intersection = 0
    for c_mention in p_c['mentions']:
        for g_mention in G_M_type:
            if compare_entity_mentions(c_mention, g_mention):
                intersection += 1
                break
    if len(p_c['mentions']) > 0:
        res = intersection / len(p_c['mentions'])
        if hard_aggregation:
            return math.floor(res)
        else:
            return res
    else:
        return None
    
def tp_g_cluster(g_c, P_M_type, hard_aggregation):
    # tp_g for a cluster of an instance
    intersection = 0
    for c_mention in g_c['mentions']:
        for g_mention in P_M_type:
            if compare_entity_mentions(c_mention, g_mention):
                intersection += 1
                break
    if len(g_c['mentions']) > 0:
        res = intersection / len(g_c['mentions'])
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
    
    tags = ['NUM', 'TIME', 'ORG', 'LOC', 'PER', 'MISC']
    # Instance > Tag > Cluster > Mention
    P_C = []
    G_C = []
    # Instance > Tag > Mention
    P_M = []
    G_M = []

    for instance, instance_pred in zip(ref_linked_docred, pred_linked_docred):
        # Predicted
        P_C_inst = {t:[] for t in tags}
        P_M_inst = {t:[] for t in tags}
        for entity in instance_pred['entities']:
            P_C_type = P_C_inst[entity['type']]
            P_C_type.append(entity)
            
            P_M_type = P_M_inst[entity['type']]
            P_M_type.extend(entity['mentions'])
        P_C.append(P_C_inst)
        P_M.append(P_M_inst)
            
        # Ground truth
        G_C_inst = {t:[] for t in tags}
        G_M_inst = {t:[] for t in tags}
        for entity in instance['entities']:
            G_C_type = G_C_inst[entity['type']]
            G_C_type.append(entity)
            
            G_M_type = G_M_inst[entity['type']]
            G_M_type.extend(entity['mentions'])
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
            for p_cluster in g_c_inst[type]:
                tp_p = tp_g_cluster(p_cluster, p_m_inst[type], hard_aggregation)
                if tp_p is not None:
                    TP_G[type] += tp_p
            G_C_count[type] += len(g_c_inst[type])

    for type in FN:
        FN[type] = G_C_count[type] - TP_G[type]
        
    P = sum(TP_P.values()) / (sum(TP_P.values()) + sum(FP.values()))
    R = sum(TP_G.values()) / (sum(TP_G.values()) + sum(FN.values()))
    F1 = 2 * (P * R) / (P + R)
    print(f"Prec={P}, Rec={R}, F1={F1}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Entity F1')
    parser.add_argument('--truth_file', help='Path to ground truth entities (in Linked-DocRED format)',
                        type=str, required=True)
    parser.add_argument('--pred_file', help='Path to predicted entities (in Linked-DocRED format)',
                        type=str, required=True)
    parser.add_argument('--hard', help='Wether to use soft or hard aggregation', action='store_true')
    parser.set_defaults(hard=False)
    args = parser.parse_args()

    main(args.truth_file, args.pred_file, args.hard)