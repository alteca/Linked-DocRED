# PURE (Named Entity Recognition)

Please refer to https://github.com/princeton-nlp/PURE for more details on PURE.

## Installation

We have tested the installation with Python 3.7.12.

Install the packages listed in `requirements.txt`:

```bash
python3 -m pip install -r requirements.tx
```

## Preliminary step

We first need to transform Linked-DocRED in the right format for PURE. Run the following command:

```bash
python3 prepare_dataset.py --input_dir="$LINKED_DOCRED_PATH" --output_dir="$LINKED_DOCRED_PREPRO"
```

where
* `$LINKED_DOCRED_PATH`: path to Linked-DocRED dataset,
* `$LINKED_DOCRED_PREPRO`: output path to store preprocessed Linked-DocRED

## Training

To train the PURE NER, run the following command

```bash
python3 run_entity.py --do_train --do_eval --num_epoch=25 --learning_rate=1e-5 --task_learning_rate=5e-4 --train_batch_size=16 --context_window 300 --task docred --data_dir "$LINKED_DOCRED_PREPRO" --model "allenai/longformer-base-4096" --output_dir "$SAVE_DIR"
```

where
* `$LINKED_DOCRED_PREPRO`: path to preprocessed Linked-DocRED,
* `$SAVE_DIR`: path to store trained model.

## Predictions

To predict entities with PURE, run the following command

```bash
python3 run_entity.py --do_eval --context_window 300 --task docred --data_dir "$LINKED_DOCRED_PREPRO" --model "allenai/longformer-base-4096" --output_dir "$SAVE_DIR"
```

where
* `$LINKED_DOCRED_PREPRO`: path to preprocessed Linked-DocRED,
* `$SAVE_DIR`: path to store predicted files. We are interested in the `ent_pred_dev.json` file.