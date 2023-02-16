"""Utils for docred disambiguation

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
import re
import math
import json
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import SnowballStemmer
from Levenshtein import distance as levenshtein_distance

stop_words = set(stopwords.words('english'))
stemmer = SnowballStemmer('english')
tokenizer = RegexpTokenizer(r'\w+')
NUMBER_REGEX = re.compile('[0-9]+')
CHAR_REGEX = re.compile(r'\\.')


def preprocess_abstract(abstract: str) -> str:
    """Clean abstract text

    Args:
        abstract (str): abstract text

    Returns:
        str: cleaned text
    """
    abstract = abstract.lower()
    abstract = abstract.replace('\\', '')

    # Remove punct
    words = tokenizer.tokenize(abstract)

    # Remove stop words
    words = [w for w in words if not w.lower() in stop_words]

    # Stemming
    words = [stemmer.stem(w) for w in words]

    return ' '.join(words)


def preprocess_entity(text: str) -> str:
    """Clean entity text

    Args:
        text (str): entity text

    Returns:
        str: cleaned text
    """
    text = text.lower()
    text = CHAR_REGEX.sub('', text)
    text = NUMBER_REGEX.sub('', text)

    # Remove punct
    words = tokenizer.tokenize(text)

    # Remove stop words
    words = [w for w in words if not w.lower() in stop_words]

    # Stemming
    words = [stemmer.stem(w) for w in words]

    return ' '.join(words)


def text_similarity(text1: str, text2: str) -> float:
    """Compute similarity between 2 texts

    Args:
        text1 (str): text
        text2 (str): text

    Returns:
        float: similarity [0, 1], 1=equal
    """
    return 1 - levenshtein_distance(text1, text2) / max(len(text1), len(text2))


def text_similarity_docred(docred_text: str, wikipedia_text: str) -> float:
    """Text similarity to compare docred instance to wikipedia instance
    Args:
        docred_text (str): docred text
        wikipedia_text (str): wikipedia text

    Returns:
        float: similarity [0, 1], 1=equal
    """
    wikipedia_text = wikipedia_text[0:len(
        docred_text)]  # Truncate wikipedia_text
    return 1 - levenshtein_distance(docred_text, wikipedia_text) / len(docred_text)


def read_docred_file(path) -> list:
    """Read docred file
    Args:
        path (str): path to file
    Returns:
        list: list of instances
    """
    with open(path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    for instance in dataset:
        instance['text'] = ' '.join([' '.join(sent)
                                    for sent in instance['sents']])
        instance['text_clean'] = preprocess_abstract(instance['text'])

    return dataset


def read_docred(path) -> dict:
    """Read entire dataset
    Args:
        path (str): root path of docred dataset
    Returns:
        dict: docred dataset
    """
    return {
        'dev': read_docred_file(f'{path}/dev.json'),
        'test': read_docred_file(f'{path}/test.json'),
        'train_annotated': read_docred_file(f'{path}/train_annotated.json')
    }


def sigmoid(x: float) -> float:
    """Sigmoid function
    Args:
        x (float): input
    Returns:
        float: sigmoid
    """
    return 1 / (1 + math.exp(-x))
