# Metrics

This folder contains the definition of the metrics, proposed with Linked-DocRED, to evaluate Information Extraction Pipelines.

## Installation

We have tested the installation with Python 3.9.15.

Install the packages listed in `requirements.txt`:

```bash
python3 -m pip install -r requirements.txt
```

## Metrics
* NER F1: mention-level,
* Coref B3: to evaluate coreferences,
* Entity F1: entity-level evaluation of entity/coreference extraction,
* Relation F1: entity-level evaluation of relation extraction,
* Hit@1, Hit@5, Not Found, Mean Rank: entity-level metrics for entity-linking.

## Expected format

The tools to evaluate entity-linkings expect files (both ground truth and predictions) to be formatted in the same format as Linked-DocRED.