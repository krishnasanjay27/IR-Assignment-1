# run_query.py
from searcher import search

def main():
    
    print("Type a query and press Enter (type 'exit' to quit)\n")

    while True:
        query = input("Query > ").strip()
        if query.lower() in ["exit", "quit", "q"]:
            print("Bye! 👋")
            break

        results = search(query, top_k=10)

        if not results:
            print("No matching documents found.\n")
        else:
            print("\nTop results:")
            for rank, (doc_name, score) in enumerate(results, start=1):
                print(f"{rank}. {doc_name}  (score = {score:.4f})")
            print()

if __name__ == "__main__":
    main()
