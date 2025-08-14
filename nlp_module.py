import json
import re

import joblib
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def ensure_nlp_resources():
    # Проверяем и скачиваем ресурсы NLTK
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    # Проверяем и скачиваем модель SpaCy
    try:
        nlp = spacy.load('ru_core_news_sm')
    except OSError:
        spacy.cli.download('ru_core_news_sm')
        nlp = spacy.load('ru_core_news_sm')

    return nlp

nlp = ensure_nlp_resources()
russian_stopwords = stopwords.words('russian')

# Деление текста на блоки в зависимости от страницы
def split_into_blocks(text, parts_num=9):
    pattern = r'(?=\d{2}/)'
    blocks = re.split(pattern, text)
    blocks = [block.strip() for block in blocks if block.strip()]

    if len(blocks) <= 1:
        text_len = len(text)
        approx_block_size = text_len // parts_num
        blocks = []
        for i in range(parts_num):
            start = i * approx_block_size
            end = (i + 1) * approx_block_size if i < parts_num - 1 else text_len
            block = text[start:end].strip()
            if block:
                blocks.append(block)
    return blocks

# Ключевой модуль очистки и фильтрации текста
def tokenize_and_clean(text):
    tokens = word_tokenize(text)
    doc = nlp(" ".join(tokens))
    lemmatized_tokens = [token.lemma_.lower() for token in doc]

    extra_stopwords = {"сделать", "связать", "это"}
    combined_stopwords = set(russian_stopwords).union(extra_stopwords)

    filtered_tokens = [lemma for lemma in lemmatized_tokens if lemma not in combined_stopwords]

    return " ".join(filtered_tokens)


def process_json(json_path="json_data.json", parts_num=9):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    processed_data = []
    for doc in data:
        blocks = split_into_blocks(doc['text'], parts_num=parts_num)
        block_pairs = []
        for block in blocks:
            cleaned_block = tokenize_and_clean(block)
            block_pairs.append({
                'orig': block,
                'clean': cleaned_block
            })

        processed_data.append({
            'id': doc['id'],
            'title': doc['title'],
            'url': doc['url'],
            'blocks': block_pairs
        })

    return processed_data


def create_tfidf_index(processed_data):
    corpus = []
    index_map = []

    for doc in processed_data:
        for i, block in enumerate(doc['blocks']):
            corpus.append(block['clean'])
            index_map.append((doc['id'], i))

    tfidf_vectorizer = TfidfVectorizer(lowercase=False)
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)

    joblib.dump(tfidf_vectorizer, 'tfidf_vectorizer.joblib')
    joblib.dump(tfidf_matrix, 'tfidf_matrix.joblib')
    joblib.dump(index_map, 'index_map.joblib')


def find_relevant_pages(query, tfidf_vectorizer, tfidf_matrix, processed_data, index_map, threshold=0.2):
    cleaned_query = tokenize_and_clean(query)
    query_tokens = word_tokenize(cleaned_query)
    query_token_set = set(query_tokens)

    query_vector = tfidf_vectorizer.transform([cleaned_query])
    sim_scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    top_block_indices = sim_scores.argsort()[::-1][:5]

    final_results = []

    doc_id_to_doc = {d['id']: d for d in processed_data}

    for idx in top_block_indices:
        if idx >= len(index_map):
            continue

        doc_id, block_idx = index_map[idx]

        doc = doc_id_to_doc.get(doc_id)
        if doc is None:
            continue

        orig_block = doc['blocks'][block_idx]['orig']

        cleaned_block = tokenize_and_clean(orig_block)
        block_tokens = word_tokenize(cleaned_block)
        block_token_set = set(block_tokens)

        if len(query_token_set) == 0:
            continue

        overlap = query_token_set.intersection(block_token_set)
        overlap_ratio = len(overlap) / len(query_token_set)

        if overlap_ratio >= threshold:
            final_results.append({
                'doc_id': doc_id,
                'url': doc.get('url', ''),
                'block_index': block_idx,
                'block_text': orig_block.strip()
            })

    return final_results


class TextSearchEngine:
    def __init__(self, json_path="json_data.json", parts_num=9):
        self.processed_data = process_json(json_path=json_path, parts_num=parts_num)
        self._create_or_load_tfidf_index()

    def _create_or_load_tfidf_index(self):
        try:
            self.tfidf_vectorizer = joblib.load('tfidf_vectorizer.joblib')
            self.tfidf_matrix = joblib.load('tfidf_matrix.joblib')
            self.index_map = joblib.load('index_map.joblib')
        except FileNotFoundError:
            create_tfidf_index(self.processed_data)
            self.tfidf_vectorizer = joblib.load('tfidf_vectorizer.joblib')
            self.tfidf_matrix = joblib.load('tfidf_matrix.joblib')
            self.index_map = joblib.load('index_map.joblib')

    def search(self, query, threshold=0.2, top_k=5):
        return find_relevant_pages(
            query=query,
            tfidf_vectorizer=self.tfidf_vectorizer,
            tfidf_matrix=self.tfidf_matrix,
            processed_data=self.processed_data,
            index_map=self.index_map,
            threshold=threshold,
        )
