task_ner_labels = {
    'ace04': ['FAC', 'WEA', 'LOC', 'VEH', 'GPE', 'ORG', 'PER'],
    'ace05': ['FAC', 'WEA', 'LOC', 'VEH', 'GPE', 'ORG', 'PER'],
    'scierc': ['Method', 'OtherScientificTerm', 'Task', 'Generic', 'Material', 'Metric'],
    'docred': ['LOC', 'NUM', 'ORG', 'PER', 'MISC', 'TIME']
}

task_rel_labels = {
    'ace04': ['PER-SOC', 'OTHER-AFF', 'ART', 'GPE-AFF', 'EMP-ORG', 'PHYS'],
    'ace05': ['ART', 'ORG-AFF', 'GEN-AFF', 'PHYS', 'PER-SOC', 'PART-WHOLE'],
    'scierc': ['PART-OF', 'USED-FOR', 'FEATURE-OF', 'CONJUNCTION', 'EVALUATE-FOR', 'HYPONYM-OF', 'COMPARE'],
    'docred': ['COREF', 'P6', 'P17', 'P19', 'P20', 'P22', 'P25', 'P26', 'P27', 'P30', 'P31', 'P35', 'P36', 'P37', 'P39', 'P40', 'P50', 'P54', 'P57', 'P58', 'P69', 'P86', 'P102', 'P108', 'P112', 'P118', 'P123', 'P127', 'P131', 'P136', 'P137', 'P140', 'P150', 'P155', 'P156', 'P159', 'P161', 'P162', 'P166', 'P170', 'P171', 'P172', 'P175', 'P176', 'P178', 'P179', 'P190', 'P194', 'P205', 'P206', 'P241', 'P264', 'P272', 'P276', 'P279', 'P355', 'P361', 'P364', 'P400', 'P403', 'P449', 'P463', 'P488', 'P495', 'P527', 'P551', 'P569', 'P570', 'P571', 'P576', 'P577', 'P580', 'P582', 'P585', 'P607', 'P674', 'P676', 'P706', 'P710', 'P737', 'P740', 'P749', 'P800', 'P807', 'P840', 'P937', 'P1001', 'P1056', 'P1198', 'P1336', 'P1344', 'P1365', 'P1366', 'P1376', 'P1412', 'P1441', 'P3373']
}

def get_labelmap(label_list):
    label2id = {}
    id2label = {}
    for i, label in enumerate(label_list):
        label2id[label] = i + 1
        id2label[i + 1] = label
    return label2id, id2label
