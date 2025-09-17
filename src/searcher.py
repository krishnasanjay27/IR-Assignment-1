import json
import math
from utils import tokenize, stem_tokens

# --------------------------
# Load inverted index and doc lengths
# --------------------------
with open("../output/dictionary.json", "r", encoding="utf-8") as f:
    dictionary = json.load(f)

with open("../output/doc_lengths.json", "r", encoding="utf-8") as f:
    doc_lengths = json.load(f)

with open("../output/doc_id_to_name.json", "r", encoding="utf-8") as f:
    doc_id_to_name = {int(k): v for k, v in json.load(f).items()}



# Total number of documents
N = len(doc_lengths)

# --------------------------
# Precompute normalized document weights (lnc)
# --------------------------
doc_vectors = {}  # docID -> {term: normalized weight}

for doc_id_str, length in doc_lengths.items():
    doc_id = int(doc_id_str)
    term_freqs = {}  # term -> frequency in this doc

    # gather term frequencies for this doc
    for term, postings in dictionary.items():
        for posting_doc_id, tf in postings:
            if posting_doc_id == doc_id:
                term_freqs[term] = tf

    # compute log tf weights
    weights = {term: 1 + math.log10(tf) for term, tf in term_freqs.items()}

    # normalize vector
    norm = math.sqrt(sum(w ** 2 for w in weights.values()))
    if norm > 0:
        for term in weights:
            weights[term] /= norm

    doc_vectors[doc_id] = weights

# --------------------------
# Query processing
# --------------------------
def preprocess_query(query):
    tokens = tokenize(query)
    stems = stem_tokens(tokens)
    tf = {}
    for t in stems:
        tf[t] = tf.get(t, 0) + 1
    return tf

def compute_query_weights(query_tf):
    weights = {}
    for term, freq in query_tf.items():
        if term in dictionary:
            df = len(dictionary[term])
            tf_weight = 1 + math.log10(freq)
            idf = math.log10(N / df)
            weights[term] = tf_weight * idf

    # normalize query vector
    norm = math.sqrt(sum(w ** 2 for w in weights.values()))
    if norm > 0:
        for t in weights:
            weights[t] /= norm

    return weights

# --------------------------
# Cosine similarity
# --------------------------
def cosine_similarity(doc_weights, query_weights):
    return sum(doc_weights.get(t, 0) * w for t, w in query_weights.items())

# --------------------------
# Search function
# --------------------------
def search(query, top_k=10):
    query_tf = preprocess_query(query)
    query_weights = compute_query_weights(query_tf)

    # compute similarity scores
    scores = []
    for doc_id, doc_w in doc_vectors.items():
        score = cosine_similarity(doc_w, query_weights)
        if score > 0:
            scores.append((doc_id, score))

    # sort by descending score, break ties by docID ascending
    scores.sort(key=lambda x: (-x[1], x[0]))

    # map doc_id to filename and return top_k
    results = [(doc_id_to_name[doc_id], score) for doc_id, score in scores[:top_k]]
    return results


# --------------------------
# Example usage
# --------------------------
if __name__ == "__main__":
    query = "Uber"
    top_docs = search(query)
    print("Top documents for query:", query)
    print(top_docs)
