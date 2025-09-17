from utils import load_corpus

if __name__ == "__main__":
    corpus_dir = "../corpus"  # adjust if needed
    corpus = load_corpus(corpus_dir)

    # Print summary
    print(f"Loaded {len(corpus)} documents.\n")

    # Show sample output for first 2 docs
    for doc_id in list(corpus.keys())[:2]:
        term_freqs = corpus[doc_id]

        total_tokens = sum(term_freqs.values())
        unique_terms = len(term_freqs)

        print(f"\nDocID: {doc_id}")
        print(f"Total tokens: {total_tokens}")
        print(f"Unique terms: {unique_terms}")

        # Show top 10 most frequent terms
        top_terms = sorted(term_freqs.items(), key=lambda x: x[1], reverse=True)[:10]
        print("Top 10 terms:", top_terms)
