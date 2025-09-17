import os
import re
import nltk
from collections import Counter
    

# Make sure NLTK Porter stemmer is available
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

def tokenize(text: str):
    """
    Lowercase, remove non-alphanumeric chars, and tokenize text into words.
    """
    # Lowercase
    text = text.lower()
    # Replace punctuation with space
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    # Split into tokens
    tokens = text.split()
    return tokens

def stem_tokens(tokens):
    """
    Apply Porter stemming to a list of tokens.
    """
    return [stemmer.stem(token) for token in tokens]

def process_document(path: str):
    """
    Read a document, tokenize, stem, and return term frequency dict.
    """
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    tokens = tokenize(text)
    stems = stem_tokens(tokens)
    tf = Counter(stems)  # term frequencies
    return tf

def load_corpus(corpus_dir: str):
    """
    Load all txt documents in corpus_dir.
    Returns dict: {docID: term_freq_dict}
    docID = integer assigned in sorted order of filenames.
    """
    corpus = {}
    files = sorted(os.listdir(corpus_dir))
    for i, filename in enumerate(files, start=1):
        if filename.endswith(".txt"):
            path = os.path.join(corpus_dir, filename)
            tf = process_document(path)
            corpus[i] = tf
    return corpus
