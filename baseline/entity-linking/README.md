# Entity-Linking

Entity-Linking using Wikidata and Wikipedia.

## Requirements

PURE and NeuralCoref have been trained and have made predictions on the `dev` split of Linked-DocRED.

## Installation

We have tested the installation with Python 3.9.15.

Install the packages listed in `requirements.txt`:

```bash
python3 -m pip install -r requirements.txt
```

## Prediction

To predict entity-linking, run the following command:

```bash
python3 predict.py --input_file "$LINKED_DOCRED_FILE" --output_file "$SAVE_PATH" --method "$METHOD"
```

where
* `$LINKED_DOCRED_FILE`: file in the format of Linked-DocRED to predict,
* `$SAVE_PATH`: path to save predictions,
* `$METHOD`: method to use (`wikipedia` or `wikidata`)