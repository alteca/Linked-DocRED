"""Automatic entity-linking (Hyperlinks Alignment + Links in Page)
Input: 1_matched_docred.jsonl, 1_articles_titles.jsonl
Output: 3_hyperlinks_alignment_links_in_page.jsonl
"""
import json
import os
import re
from dotenv import load_dotenv
import bs4
import numpy as np
import pandas as pd
from tqdm import tqdm
from .utils import preprocess_abstract, read_docred, text_similarity

load_dotenv()

DOCRED_PATH = os.getenv('DOCRED_PATH')
EL_DATA_PATH = os.getenv('EL_DATA_PATH')

docred = read_docred(DOCRED_PATH)

edit_regex = re.compile(r'.*wikipedia.org.*?title=(.*)&.*')

# Alignement hyperparameters
INDEL_SCORE = -10
SMALL_INDEL_SCORE = -1
MISMATCH_SCORE = -1
MATCH_SCORE = 1


def compute_word_positions(sents: list) -> list:
    """Returns char positions of words in list of sentences

    Args:
        sents (list): list of sentences

    Returns:
        list: sentences with token positions
    """
    pos = 0
    out = []
    for sent in sents:
        out_sent = []
        for tok in sent:
            out_sent.append({
                'text': tok,
                'start': pos,
                'end': pos + len(tok)
            })
            pos += len(tok) + 1
        out.append(out_sent)
    return out


def word_to_tokens_entities(vertexSet: list, sents_pos: int) -> list:
    """Convert words pos to char pos
    Args:
        vertexSet (list): vertexset with word positions
        sents_pos (int): current position
    Returns:
        list: vertexset with char positions
    """
    for vertex in vertexSet:
        for entity in vertex:
            start = sents_pos[entity['sent_id']][entity['pos'][0]]['start']
            end = sents_pos[entity['sent_id']][entity['pos'][1]-1]['end']

            entity['char_pos'] = [start, end]
    return vertexSet


def preprocess_instance(instance: dict) -> dict:
    """Preprocess instance

    Args:
        instance (dict): instance

    Returns:
        dict: instance
    """
    instance['text'] = ' '.join([' '.join(sent) for sent in instance['sents']])
    sents_pos = compute_word_positions(instance['sents'])
    instance['vertexSet'] = word_to_tokens_entities(
        instance['vertexSet'], sents_pos)

    txt = instance['text']
    txt = list(txt)
    for vertex in instance['vertexSet']:
        for entity in vertex:
            txt[entity['char_pos'][0]] = '<'
            txt[entity['char_pos'][1] - 1] = '>'

    return instance


def filter_url(url: str) -> str:
    """Filter url to keep wikipedia links
    Args:
        url (str): url

    Returns:
        str: cleaned url or None
    """
    if 'wikipedia.org' in url:
        if edit_regex.match(url):
            return edit_regex.search(url).group(1)
        return url
    if 'cite_note' in url:
        return None
    if url.startswith('./'):
        return url[2:]
    if url.startswith('http'):
        return None
    if url.startswith('//'):
        return None
    return None


def extract_links(pos: int, soup):
    """Extract and process links

    Args:
        pos (int): current pos
        soup (_type_): bs4 soup

    Returns:
        tuple: next pos, extracted links, extracted texts
    """
    links = []
    texts = []
    for tag in soup:
        if isinstance(tag, bs4.element.Tag):
            if tag.name == 'a':
                resource = filter_url(tag.attrs['href'])
                if resource is not None and len(tag.text) > 0:
                    links.append({
                        'text': tag.text,
                        'resource': resource,
                        'start': pos,
                        'end': pos + len(tag.text)
                    })
                texts.append(tag.text)
                pos += len(tag.text)
            else:
                pos, l, t = extract_links(pos, tag)
                texts.extend(t)
                links.extend(l)
        elif type(tag) == bs4.element.NavigableString:
            texts.append(str(tag))
            pos += len(str(tag))
    return pos, links, texts


def extract_links_wiki(paragraphs: list) -> tuple:
    """Extract and process links for the whole instance
    Args:
        paragraphs (list): list of sentences

    Returns:
        tuple: list of texts, list of links
    """
    pos = 0
    links = []
    text = ''
    for p in paragraphs:
        pos, l, t = extract_links(pos, p)
        links.extend(l)
        text += ''.join(t)
    return text, links


def get_wiki_page(resource: str) -> tuple:
    """Process wikipedia page
    Args:
        resource (str): id of wikipedia page
    Returns:
        tuple: wikipedia text, abstract links (for text alignment), all links in wikipedia page
    """
    wiki_file = f'{EL_DATA_PATH}/1_wikipedia_pages/{resource}.html'
    if os.path.exists(wiki_file):
        with open(wiki_file, 'r', encoding='utf-8') as f:
            wiki_html = bs4.BeautifulSoup(f, features="html.parser")
    else:
        return

    def process_link(a):
        a_text = preprocess_abstract(a.text)
        return {
            'text': a_text,
            'resource': filter_url(a.attrs['href'])
        }

    wiki_paragraphs = wiki_html.find_all(
        'section', {'data-mw-section-id': "0"})[0].find_all('p')
    wiki_abstract_text, wiki_abstract_links = extract_links_wiki(
        wiki_paragraphs)
    for link in wiki_abstract_links:
        assert wiki_abstract_text[link['start']:link['end']] == link['text']

    wiki_all_links = wiki_html.find_all('a')
    wiki_all_links = [process_link(a) for a in wiki_all_links]
    wiki_all_links = {a['text']: a['resource']
                      for a in wiki_all_links if a['text'] != '' and a['resource'] is not None}

    return wiki_abstract_text, wiki_abstract_links, wiki_all_links


def needleman_wunsch_alignment(docred_text: str, wikipedia_text: str) -> tuple:
    """Needleman Wunsch algorithm to align docred instance and wikipedia text

    Args:
        docred_text (str): docred instance
        wikipedia_text (str): wikipedia abstract

    Returns:
        tuple: dictionaries to translate docred position to wikipedia position
        (and conversely), text similarity
    """
    # See https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm
    # for Needleman-Wunsch implementation
    docred_text, wikipedia_text = list(docred_text), list(wikipedia_text)

    # Initialize matrix
    docred_len, wikipedia_len = len(docred_text), len(wikipedia_text)
    F = np.empty([docred_len + 1, wikipedia_len + 1])
    # 0: nothing, 1: ins text1 (i), 2 : ins text2 (j), 3 : match/mismatch
    arrows = np.empty([docred_len + 1, wikipedia_len + 1])

    F[0, 0] = 0
    arrows[0, 0] = 0
    for i in range(1, docred_len+1):
        F[i, 0] = F[i-1, 0] + INDEL_SCORE
        arrows[i, 0] = 1
    for j in range(1, wikipedia_len+1):
        F[0, j] = F[0, j-1] + SMALL_INDEL_SCORE
        arrows[0, j] = 2

    # Needlman-Wunsch algo
    for i in range(1, docred_len+1):
        for j in range(1, wikipedia_len+1):
            # Compute score
            if j == 0 or j == wikipedia_len:
                in_text1_score = F[i-1, j] + SMALL_INDEL_SCORE
            else:
                in_text1_score = F[i-1, j] + INDEL_SCORE
            in_text2_score = F[i, j-1] + INDEL_SCORE

            match_score = F[i-1, j-1]
            if docred_text[i-1] == wikipedia_text[j-1]:
                match_score += MATCH_SCORE
            else:
                match_score += MISMATCH_SCORE

            # Select path with best score
            F[i, j] = max(in_text1_score, in_text2_score, match_score)
            arrows[i, j] = np.argmax(
                [in_text1_score, in_text2_score, match_score]) + 1

    # Backtracking to find best path
    docred_to_wiki = {}
    wiki_to_docred = {}
    distance = 0
    i, j = docred_len, wikipedia_len
    while i > 0 and j > 0:
        if arrows[i, j] == 0:
            break
        elif arrows[i, j] == 1:
            # Ins in text1
            docred_to_wiki[i-1] = None
            distance += 1
            i -= 1
        elif arrows[i, j] == 2:
            # ins in text2
            wiki_to_docred[j-1] = None
            if j > 1 and j < wikipedia_len:
                distance += 1
            j -= 1
        else:  # arrows[i, j] == 3:
            # match/mismatch
            docred_to_wiki[i-1] = j-1
            wiki_to_docred[j-1] = i-1
            if docred_text[i-1] != wikipedia_text[j-1]:
                distance += 1
            i -= 1
            j -= 1

    while i > 0:
        docred_to_wiki[i-1] = None
        distance += 1
        i -= 1

    while j > 0:
        wiki_to_docred[j-1] = None
        j -= 1

    similarity = 1 - distance / len(docred_text)

    return docred_to_wiki, wiki_to_docred, similarity


def disambiguate_instance(docred_instance: dict, hit_instance: dict, articles_names: dict):
    """Main function to disambiguate instance

    Args:
        docred_instance (dict): docred instance
        hit_instance (dict): match information (which wikipedia page to get)
        articles_names (dict): title of the Wikipedia articles
    """
    try:
        wiki_abstract_text, wiki_abstract_links, wiki_all_links = get_wiki_page(
            hit_instance['resource'])
    except:
        return None

    _, wiki_to_docred, similarity = needleman_wunsch_alignment(
        docred_instance['text'], wiki_abstract_text)

    wiki_names = articles_names.loc[hit_instance['resource'], 'names']
    wiki_names = [preprocess_abstract(n) for n in wiki_names]

    for entity in docred_instance['vertexSet']:
        for mention in entity:
            mention_start = mention['char_pos'][0]
            mention_end = mention['char_pos'][1]
            mention['resource'] = None

    # Text-alignment : Needleman Wunsch match
    text_aligned_entities = {}
    text_aligned_entities_simplified = {}
    for entity_id, entity in enumerate(docred_instance['vertexSet']):
        for i, mention in enumerate(entity):
            mention_start = mention['char_pos'][0]
            mention_end = mention['char_pos'][1]-1

            for wiki_ent in wiki_abstract_links:
                wiki_start = wiki_to_docred[wiki_ent['start']]
                wiki_end = wiki_to_docred[wiki_ent['end']-1]
                if wiki_start is not None and wiki_start < mention_end and \
                        (wiki_end is None or wiki_end > mention_start):
                    docred_text = mention['name']
                    wiki_text = wiki_abstract_text[wiki_ent['start']:wiki_ent['end']]
                    text_sim = text_similarity(docred_text, wiki_text)

                    if text_sim > 0.75:
                        mention['resource'] = {
                            'url': wiki_ent['resource'],
                            'matcher': 'hyperlinks-alignment',
                            'matched-text': wiki_text
                        }

                        text_aligned_entities[mention['name']] = {
                            'url': wiki_ent['resource'],
                            'coref': f"{entity_id}-{i}"
                        }
                        simplified_ent = preprocess_abstract(mention['name'])
                        if len(simplified_ent) > 0:
                            text_aligned_entities_simplified[simplified_ent] = {
                                'url': wiki_ent['resource'],
                                'coref': f"{entity_id}-{i}"
                            }
                        break

    for entity in docred_instance['vertexSet']:
        for mention in entity:
            if mention['resource'] is not None:
                continue

            # Coreference of already matched entity
            if mention['name'] in text_aligned_entities:
                match = text_aligned_entities[mention['name']]
                mention['resource'] = {
                    'url': match['url'],
                    'coref': match['coref'],
                    'matcher': 'coreference'
                }
                continue

            docred_ent_text_simplified = preprocess_abstract(
                mention['name'])
            if docred_ent_text_simplified in text_aligned_entities_simplified:
                match = text_aligned_entities_simplified[docred_ent_text_simplified]
                mention['resource'] = {
                    'url': match['url'],
                    'coref': match['coref'],
                    'matcher': 'coreference-simplified'
                }
                continue

            # Other links in page
            if docred_ent_text_simplified in wiki_all_links:
                mention['resource'] = {
                    'url': wiki_all_links[docred_ent_text_simplified],
                    'matcher': 'link-in-page'
                }
                continue

            # Name of wikipedia article
            if docred_ent_text_simplified in wiki_names:
                mention['resource'] = {
                    'url': hit_instance['resource'],
                    'matcher': 'article-name'
                }

    # Merge mention-level alignement
    for entity in docred_instance['vertexSet']:
        resource = None
        matcher = None
        for i, mention in enumerate(entity):
            if mention['resource'] is not None:
                m_res = mention['resource']

                if m_res['matcher'] == 'text-alignment' and m_res['matcher'] != matcher:
                    resource = m_res['url']
                    matcher = m_res['matcher']

                elif m_res['matcher'] == 'coreference' and m_res['matcher'] != matcher:
                    pot_resource = int(m_res['coref'].split("-")[0])
                    if pot_resource is not None and pot_resource != i:
                        matcher = 'links-in-page'
                        resource = pot_resource
                elif m_res['matcher'] == 'simplified-coreference' and m_res['matcher'] != matcher:
                    pot_resource = int(m_res['coref'].split("-")[0])
                    if pot_resource is not None and pot_resource != i:
                        matcher = 'links-in-page'
                        resource = pot_resource
                elif m_res['matcher'] == 'link-in-page' and m_res['matcher'] != matcher:
                    resource = m_res['url']
                    matcher = m_res['matcher']
                elif m_res['matcher'] == 'article-title' and m_res['matcher'] != matcher:
                    resource = m_res['url']
                    matcher = m_res['matcher']

        entity = {
            'entity_linking':  {
                'wikipedia_resource': resource,
                'method': matcher
            },
            'mentions': entity,
            'type': entity[0]['type']
        }
        for mention in entity['mentions']:
            if 'resource' in mention:
                del mention['resource']
                
        if entity['type'] in ['NUM', 'TIME']:
            entity['entity_linking'] = {
                'wikipedia_resource': '#ignored#',
                'method': 'num/time'
            }

    output = {
        'dataset': hit_instance['dataset'],
        'id': hit_instance['id'],
        'entities': docred_instance['vertexSet']
    }
    return output


def main():
    """Main Entrypoint
    """
    hits = pd.read_json(
        f"{EL_DATA_PATH}/1_matched_docred.jsonl", lines=True, orient="records")

    articles_names = pd.read_json(
        f'{EL_DATA_PATH}/1_articles_titles.jsonl', lines=True, orient="records")
    articles_names = articles_names.set_index('resource')

    with open(f'{EL_DATA_PATH}/3_hyperlinks_alignment_links_in_page.jsonl', 'w', encoding='utf-8') \
        as f:
        for _, r in tqdm(hits.iterrows(), total=len(hits)):
            docred_instance = docred[r['dataset']][r['id']]
            instance = disambiguate_instance(
                docred_instance, r, articles_names)
            f.write(json.dumps(instance))
            f.write('\n')
            f.flush()


if __name__ == "__main__":
    main()
