import json
from utils import load_corpus

def build_inverted_index(corpus):
    dictionary = {}
    doc_lengths = {}

    for doc_id, term_freqs in corpus.items():
        total_tokens = sum(term_freqs.values())
        doc_lengths[doc_id] = total_tokens

        for term, freq in term_freqs.items():
            if term not in dictionary:
                dictionary[term] = []
            dictionary[term].append((doc_id, freq))

    return dictionary, doc_lengths


if __name__ == "__main__":
    corpus_dir = "../corpus"
    corpus, doc_id_to_name = load_corpus(corpus_dir)

    print(f"Loaded {len(corpus)} documents.\n")

    dictionary, doc_lengths = build_inverted_index(corpus)

    # Show sample output
    for term in list(dictionary.keys())[:5]:
        print(f"Term: '{term}' → Postings: {dictionary[term]}")
    for doc_id in list(doc_lengths.keys())[:5]:
        print(f"DocID {doc_id} → Length: {doc_lengths[doc_id]}")

    # 🔹 Save index to output/
    with open("../output/dictionary.json", "w", encoding="utf-8") as f:
        json.dump(dictionary, f, indent=2)
    with open("../output/doc_lengths.json", "w", encoding="utf-8") as f:
        json.dump(doc_lengths, f, indent=2)
    with open("../output/doc_id_to_name.json", "w", encoding="utf-8") as f:
        json.dump(doc_id_to_name, f, indent=2)

    print("\nIndex and doc_id_to_name saved in output/ folder.")
