import json
import math
from utils import tokenize, stem_tokens
from soundex import soundex

# --------------------------
# CONFIG
# --------------------------
SOUNDEX_ENABLED = True   # set False to disable Soundex fallback

# --------------------------
# Load inverted index and doc lengths
# --------------------------
# NOTE: we convert JSON string-keys to int-keys for convenience
with open("../output/dictionary.json", "r", encoding="utf-8") as f:
    dictionary = json.load(f)

with open("../output/doc_lengths.json", "r", encoding="utf-8") as f:
    raw_doc_lengths = json.load(f)
    # convert keys to int
    doc_lengths = {int(k): v for k, v in raw_doc_lengths.items()}

with open("../output/doc_id_to_name.json", "r", encoding="utf-8") as f:
    raw_id2name = json.load(f)
    doc_id_to_name = {int(k): v for k, v in raw_id2name.items()}

# Total number of documents
N = len(doc_lengths)

# --------------------------
# Basic derived maps
# --------------------------
# df_map: term -> document frequency
df_map = {term: len(postings) for term, postings in dictionary.items()}

# --------------------------
# Precompute normalized document weights (lnc) efficiently
# We iterate postings once and build per-doc vectors.
# --------------------------
# Step A: accumulate raw (1+log10(tf)) weights per doc
_doc_raw_weights = {}   # docID -> {term: raw_weight}
for term, postings in dictionary.items():
    # postings are lists; each posting is like [docID, tf] (JSON converts tuples->lists)
    for posting in postings:
        # tolerate both [docID, tf] and {"doc":..} shapes; assume list/tuple
        try:
            posting_doc_id = int(posting[0])
            tf = int(posting[1])
        except Exception:
            # if posting isn't list-like, skip defensively
            continue

        w = 1.0 + math.log10(tf) if tf > 0 else 0.0
        if posting_doc_id not in _doc_raw_weights:
            _doc_raw_weights[posting_doc_id] = {}
        _doc_raw_weights[posting_doc_id][term] = w

# Step B: normalize per-doc vectors
doc_vectors = {}
for doc_id, term_w_map in _doc_raw_weights.items():
    norm = math.sqrt(sum(w * w for w in term_w_map.values()))
    if norm > 0:
        doc_vectors[doc_id] = {t: (w / norm) for t, w in term_w_map.items()}
    else:
        doc_vectors[doc_id] = {t: 0.0 for t in term_w_map.keys()}

# Free memory for intermediate
_doc_raw_weights = None

# --------------------------
# Precompute soundex map (code -> [terms]) for fast lookup
# (if Soundex disabled we'll still have the map available)
# --------------------------
soundex_map = {}
if SOUNDEX_ENABLED:
    for term in dictionary.keys():
        code = soundex(term)
        soundex_map.setdefault(code, []).append(term)
    # Optionally sort lists by decreasing df so the first candidate is highest df
    for code, terms in soundex_map.items():
        terms.sort(key=lambda t: -df_map.get(t, 0))

# --------------------------
# Query processing (with Soundex fallback)
# --------------------------
def preprocess_query(query, use_soundex=SOUNDEX_ENABLED):
    """
    Returns a query term-frequency map (terms are stemmed, matching index keys).
    If a stem is not found, and soundex is enabled, we try to replace it
    with the highest-df candidate that shares the Soundex code.
    """
    tokens = tokenize(query)
    stems = stem_tokens(tokens)
    qtf = {}
    for t in stems:
        if t in dictionary:
            qtf[t] = qtf.get(t, 0) + 1
            continue

        if use_soundex:
            code = soundex(t)
            candidates = soundex_map.get(code, [])
            if candidates:
                # pick best candidate (soundex_map sorted by df)
                replacement = candidates[0]
                # debug printing - can be turned off or redirected to logger
                print(f"[Soundex] Replacing '{t}' with '{replacement}'")
                qtf[replacement] = qtf.get(replacement, 0) + 1
            # if no candidate, term is ignored (no entry in qtf)
    return qtf

def compute_query_weights(query_tf):
    """
    ltc: tf weight = 1 + log10(tf_q), idf = log10(N/df), weight = tf_weight * idf
    then cosine-normalize the query vector.
    """
    weights = {}
    for term, freq in query_tf.items():
        if term not in dictionary:
            continue
        df = df_map.get(term, 0)
        if df <= 0:
            continue
        tf_w = 1.0 + math.log10(freq) if freq > 0 else 0.0
        idf = math.log10(N / df) if df > 0 else 0.0
        weights[term] = tf_w * idf

    norm = math.sqrt(sum(w * w for w in weights.values()))
    if norm > 0:
        for t in list(weights.keys()):
            weights[t] /= norm
    return weights

# --------------------------
# Cosine similarity (dot product of normalized vectors)
# --------------------------
def cosine_similarity(doc_weights, query_weights):
    return sum(doc_weights.get(t, 0.0) * w for t, w in query_weights.items())

# --------------------------
# Public search function
# --------------------------
def search(query, top_k=10, use_soundex=SOUNDEX_ENABLED):
    """
    Returns list of (filename, score) up to top_k.
    """
    query_tf = preprocess_query(query, use_soundex)
    if not query_tf:
        return []

    query_weights = compute_query_weights(query_tf)
    if not query_weights:
        return []

    scores = []
    # iterate only over docs that contain at least one of the query terms:
    candidate_docs = set()
    for term in query_weights.keys():
        for posting in dictionary.get(term, []):
            try:
                pid = int(posting[0])
            except Exception:
                continue
            candidate_docs.add(pid)

    for doc_id in candidate_docs:
        doc_w = doc_vectors.get(doc_id, {})
        score = cosine_similarity(doc_w, query_weights)
        if score > 0:
            scores.append((doc_id, score))

    # Sort by score desc, tie-break by doc_id asc
    scores.sort(key=lambda x: (-x[1], x[0]))

    # Map to filename (doc_id_to_name uses int keys)
    results = []
    for doc_id, score in scores[:top_k]:
        fname = doc_id_to_name.get(doc_id, str(doc_id))
        results.append((fname, score))
    return results


if __name__ == "__main__":
    q = "zoomato"
    print("Searching for:", q)
    res = search(q, top_k=10)
    for fname, score in res:
        print(f"{fname}\t{score:.6f}")
