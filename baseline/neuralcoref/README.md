# NeuralCoref (Coreference Resolution)

Please refer to <https://github.com/huggingface/neuralcoref> for more details on NeuralCoref.

## Requirements

PURE is trained and has predicted the entities (see subfolder `pure/`). In particular, the file `ent_pred_dev.json` must exist.

## Installation

We have tested the installation with Python 3.6.15.

It is **mandatory** to have Python <= 3.6, in order to install `spaCy` v2.1, which is required to install `neuralcoref`.

Install the packages listed in `requirements.txt`:

```bash
python3 -m pip install -r requirements.txt
```

Download spaCy model, using the following command

```bash
python3 -m spacy download en_core_web_sm
```

## Prediction

To predict coreferences, run the following command:

```bash
python3 predict.py --data_dir "$LINKED_DOCRED_PATH" --entity_path "$PURE_ENTITIES_PATH" --output_dir "$SAVE_DIR"
```

where
* `$LINKED_DOCRED_PATH`: path to Linked-DocRED dataset,
* `$PURE_ENTITIES_PATH`: path to `ent_dev_pred.json` file outputed by PURE.
* `$SAVE_DIR`: path to store predicted files. We are interested in the `dev_pred_entities.json` file.