# ATLOP (Relation Extraction)

Please refer to <https://github.com/wzhouad/ATLOP> for more details on ATLOP.

## Requirements

PURE and NeuralCoref have been trained, and the predictions have been made for the `dev` split (file `dev_pred_entities.json`).

## Installation

We have tested the installation with Python 3.7.12.

Install the packages listed in `requirements.txt`:

```bash
python3 -m pip install -r requirements.tx
```

To install `apex`, please follow the instructions listed in <https://github.com/NVIDIA/apex>.

## Training

To train ATLOP, use the following command

```bash
python3 train.py --data_dir "$LINKED_DOCRED_PATH" --save_path "$SAVE_PATH" --transformer_type bert --model_name_or_path bert-base-cased --train_file train_annotated.json --dev_file dev.json --test_file test.json --train_batch_size 4 --test_batch_size 8 --gradient_accumulation_steps 1 --num_labels 4 --learning_rate 5e-5 --max_grad_norm 1.0 --warmup_ratio 0.06 --num_train_epochs 30.0 --seed 66 --num_class $NUM_CLASSES
```

where
* `$LINKED_DOCRED_PATH`: path to Linked-DocRED dataset,
* `$SAVE_PATH`: path to save the trained model,
* `$NUM_CLASSES`: number of relations, `97` in the case of Linked-DocRED (96 relations + no relation).

## Prediction

To predict relations with ATLOP, use the following command

```bash
python3 train.py --data_dir "$LINKED_DOCRED_PATH" --load_path "$SAVE_PATH" --transformer_type bert --model_name_or_path bert-base-cased --train_file dev_pred_entities.json --dev_file dev_pred_entities.json --test_file dev_pred_entities.json --seed 66 --num_class $NUM_CLASSES
```

where
* `$LINKED_DOCRED_PATH`: path to Linked-DocRED dataset. Remember to add the predicted entities for the `dev` split file (file `dev_pred_entities.json`, produced by the NeuralCoref module),
* `$SAVE_PATH`: path to load the trained model,
* `$NUM_CLASSES`: number of relations, `97` in the case of Linked-DocRED (96 relations + no relation).