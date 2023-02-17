# Entity-Linking Process

This folder contains the necessary source code to run the disambiguation process implemented for Linked-DocRED. For more details, please refer to *Section 3* of the paper.

## Requirements

In order to run the disambiguation process, a working instance of *ElasticSearch* must have been setuped (see [ElasticSearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)). We have tested for ElasticSearch v8.6.

You also need to create a file named `.env`, that contains variables used by the Python scripts. You have to follow the template of `.env.example`.

## Installation

We have tested the installation with Python 3.8.16.

Install the packages listed in `requirements.txt`:

```bash
python3 -m pip install -r requirements.txt
```

## Running

You firstly need to download the DBpedia abstract dump (from <https://databus.dbpedia.org/dbpedia/text/long-abstracts>). *Warning: you need approximately 10GB of disk space in order to decompress the file and index it in ElasticSearch.*

Then, you need to run each script in ascending order (`1_1__index_articles.py`, `1_2__find_docred_instances.py`, ..., `6__generate_linked_docred.py`)

The recommended command is the following:

```bash
python3 -m src.1_1__index_articles <OPTIONS>
```