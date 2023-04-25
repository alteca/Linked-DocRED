# Dataset

## Dataset Download

Please download the `dev.json`, `test.json` and `train_annotated.json` files. `rel_info.json` contains information about the relations in Linked-DocRED.

If you are interested in distantly annotated data for entities and relations, please download the `train_distant.json` file of DocRED (see <https://github.com/thunlp/DocRED>).

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

### Differences with DocRED

Linked-DocRED follows a similar `json` format with DocRED. There are, however, some differences:

* In Linked-DocRED, `vertexSet` key has been replaced by `entities`.
* In Linked-DocRED, `labels` key has been replaced by `relations`.
* In DocRED, the `vertexSet` contained only the list of mentions, whereas in Linked-DocRED, we have more metadata (`id`, `type`, `entity_linking`), and the mentions are accessible using the key `mentions`.
* In Linked-DocRED, the `type` key has been removed from each mention.

### Test set

In DocRED, the annotation for relations has not been release for the `test` split. It allows the existence of a Codalab competition (see <https://github.com/thunlp/DocRED>).

Our entity-linking process elicited some errors and coreferences that were not identified in DocRED. These modifications makes our entity annotations incompatible with the Codalab competition. Therefore, only for the `test.json` file, we add a key `old-entities`, containing the initial DocRED entities (that are not modified), to allow a user to participate in the Codalab competition.

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

## How to load Linked-DocRED?

We provide a very simple code sample to load the Linked-DocRED dataset:

```python
import json

def read_linked_docred_file(path: str) -> list:
    """Read docred file
    Args:
        path (str): path to file
    Returns:
        list: list of instances
    """
    with open(path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    return dataset


def read_linked_docred(linked_docred_path: str) -> dict:
    """Read entire dataset
    Args:
        path (str): root path of linked docred dataset
    Returns:
        dict: linked docred dataset
    """
    return {
        'dev': read_docred_file(f'{linked_docred_path}/dev.json'),
        'test': read_docred_file(f'{linked_docred_path}/test.json'),
        'train_annotated': read_docred_file(f'{linked_docred_path}/train_annotated.json')
    }

linked_docred = read_linked_docred("<path to Linked-DocRED>")

# Iterate over each split and instances
for split, data in linked_docred.items():
    print(f'Current split: {split}')
    for instance_id, instance in enumerate(data):
        print(instance_id, instance)
```