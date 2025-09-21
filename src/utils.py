import os
import re
from collections import Counter

# Make sure NLTK Porter stemmer is available
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()


def tokenize(text: str):
    """Lowercase, remove non-alphanumeric chars, and tokenize text into words."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = text.split()
    return tokens


def stem_tokens(tokens):
    """Apply Porter stemming to a list of tokens."""
    return [stemmer.stem(token) for token in tokens]


def process_document(path: str):
    """Read a document, tokenize, stem, and return both tokens and term frequency dict."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    tokens = tokenize(text)
    stems = stem_tokens(tokens)
    tf = Counter(stems)  # term frequencies
    return list(tf.keys()), tf  # return both tokens and term frequencies


def load_corpus(corpus_dir):
    corpus = {}           # docID -> term_freqs
    doc_id_to_name = {}   # docID -> filename

    for i, filename in enumerate(sorted(os.listdir(corpus_dir)), start=1):
        if filename.endswith(".txt"):
            tokens, term_freqs = process_document(os.path.join(corpus_dir, filename))
            corpus[i] = term_freqs
            doc_id_to_name[i] = filename

    return corpus, doc_id_to_name
