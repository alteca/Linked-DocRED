# Linked-Re-DocRED Dataset

## Introduction

DocRED follows a recommend-revise scheme for its annotations: entity and relation candidates were automatically generated thanks to heuristics and models, and they were curated by human annotators.
Therefore, DocRED is precise (entity and relation annotations are correct) but incomplete: some entities and relations were not detected by the heuristics and models.
This incompleteness has a negative impact during training and evaluation.

Re-DocRED [[1]](#cite-1) addresses this shortcoming, by complementing relation annotations. In practice, it doubles the number of relations of the dataset (from 57k to 121k).
The authors observed a positive impact on the performance of RE models when using Re-DocRED instead of DocRED.

Linked-Re-DocRED is the fusion between Re-DocRED and Linked-DocRED. It contains the complementary relation annotations of Re-DocRED with the entity-linking annotations of Linked-DocRED.

## Dataset Download

Please download the `dev_revised.json`, `test_revised.json` and `train_revised.json` files.

## Dataset format

The files are formatted as `json`. A file contains a list of instances (documents). An instance is a json object with the following keys:

* `title`. Title of the document.
* `sents`. List of the sentences of the document. Each sentence contains the list of tokens/words that composes it.
* `entities`. List of entities. Each entity is a json object with the following keys:
    * `id`. Id of the entity in the document.
    * `type`. Type of the entity (`NUM`, `TIME`, `PER`, `ORG`, `LOC`, `MISC`).
    * `mentions`. Mentions (coreferences) of the entity in the document. Each mention is a json object with the following keys:
        * `name`. Text of the mention.
        * `sent_id`. Index of the sentence where the mention is located.
        * `pos=[start_pos, end_pos[`. Interval to indicate the location of the mention in the sentence.
    * `entity_linking`. Entity-Linking annotation for the entity. It is a json object with the following keys:
        * `wikipedia_resource`. Wikipedia/DBpedia id. To go the the Wikipedia page, simply add the prefix `https://en.wikipedia.org/wiki/` to `wikipedia_resource`. *Special values: `#ignored#` if the entity is a numeral or temporal value, `#DocRED-<id>#` if the entity is not in Wikipedia.*
        * `wikipedia_not_resource`. Only if the `wikipedia_resource` not in Wikipedia. The list of Wikipedia candidates that were refused.
        * `wikidata_resource`. Wikidata id found with the entity-linking.
        * `method`. Method used to disambiguate the entity (`manual`, `hyperlinks-alignment`, `links-in-page`, `common-knowledge`, or `num/time`).
        * `confidence`. Confidence score (`A`, `B`, or `C`).
* `relations`. List of relations. Each relation is a json object with the following keys:
    * `r`. Type of the relation (Wikidata code).
    * `h`. Id of the *head/subject* entity (corresponds to the `id` key of each entity).
    * `t`. Id of the *tail/object* entity (corresponds to the `id` key of each entity).
    * `evidence`. List of sentences index that support the existence of the relation.

### Sample instance

```json
{
    "title": "Skai TV",
    "sents": [
        [ "Skai", "TV", "is", "a", "Greek", "free", "-", "to", "-", "air", "television", "network", "based", "in", "Piraeus", "."],
        [ "It", "is", "part", "of", "the", "Skai", "Group", ",", "one", "of", "the", "largest", "media", "groups", "in", "the", "country", "."],
        ...
    ],
    "entities": [
        {
            "id": 0,
            "type": "ORG",
            "entity_linking": {
                "wikipedia_resource": "Skai_TV",
                "wikidata_resource": "Q2334737",
                "wikipedia_not_resource": null,
                "method": "links-in-page",
                "confidence": "B"
            },
            "mentions": [
                {"name": "Skai TV", "sent_id": 4, "pos": [0, 2]},
                {"name": "Skai TV", "sent_id": 0, "pos": [0, 2]},
                {"name": "Skai TV", "sent_id": 5, "pos": [3, 5]}
            ]
        },
        {
            "id": 7,
            "type": "ORG",
            "entity_linking": {
                "wikipedia_resource": "Cosmote_TV",
                "wikidata_resource": "Q7073092",
                "wikipedia_not_resource": null,
                "method": "hyperlinks-alignment",
                "confidence": "A"
            },
            "mentions": [
                {"name": "Cosmote TV", "sent_id": 3, "pos": [18, 20]}
            ]
        },
        ...
    ],
    "relations": [
        {"r": "P17", "h": 2, "t": 1, "evidence": [0, 4]},
        {"r": "P17", "h": 3, "t": 1, "evidence": [0, 1, 4]},
        ...
    ]
}
```

## How to load Linked-Re-DocRED?

We provide a very simple code sample to load the Linked-Re-DocRED dataset:

```python
import json

def read_linked_re_docred_file(path: str) -> list:
    """Read Linked-Re-DocRED file
    Args:
        path (str): path to file
    Returns:
        list: list of instances
    """
    with open(path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    return dataset


def read_linked_re_docred(linked_re_docred_path: str) -> dict:
    """Read entire dataset
    Args:
        path (str): root path of Linked-Re-DocRED
    Returns:
        dict: Linked-Re-DocRED dataset
    """
    return {
        'dev': read_linked_re_docred_file(f'{linked_re_docred_path}/dev_revised.json'),
        'test': read_linked_re_docred_file(f'{linked_re_docred_path}/test_revised.json'),
        'train': read_linked_re_docred_file(f'{linked_re_docred_path}/train_revised.json')
    }

linked_re_docred = read_linked_re_docred("<path to Linked-Re-DocRED>")

# Iterate over each split and instances
for split, data in linked_re_docred.items():
    print(f'Current split: {split}')
    for instance_id, instance in enumerate(data):
        print(instance_id, instance)
```

## References

<div class="csl-entry"><a name="cite-1"></a><b>[1]</b> Tan, Qingyu, Lu Xu, Lidong Bing, Hwee Tou Ng, and Sharifah Mahani Aljunied. “Revisiting DocRED - Addressing the False Negative Problem in Relation Extraction.” In <i>Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing</i>, 8472–87. Abu Dhabi, United Arab Emirates: Association for Computational Linguistics, 2022. <a href="https://aclanthology.org/2022.emnlp-main.580">https://aclanthology.org/2022.emnlp-main.580</a>.</div>
