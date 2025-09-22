# src/app.py
import json
import os
from flask import Flask, request, jsonify, render_template, send_from_directory, abort
from searcher import search  # uses your existing searcher.search(query)
# Note: searcher returns list of (filename, score)

app = Flask(__name__, template_folder="templates", static_folder="static")

# Root page
@app.route("/")
def index():
    return render_template("index.html")

# Search API - POST JSON { "query": "..." }
@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400

    try:
        results = search(query, top_k=10)  # returns list of (filename, score)
        # normalize structure to JSON-friendly format
        res_json = [{"filename": fname, "score": float(score)} for fname, score in results]
        return jsonify({"results": res_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Preview API - safe-serving small snippet of the file from corpus
@app.route("/api/preview")
def api_preview():
    filename = request.args.get("file", "")
    if not filename:
        return jsonify({"error": "Missing file parameter"}), 400

    # Validate filename exists in corpus and avoid directory traversal
    corpus_dir = os.path.join(os.path.dirname(__file__), "..", "corpus")
    corpus_dir = os.path.abspath(corpus_dir)
    file_path = os.path.join(corpus_dir, filename)
    file_path = os.path.abspath(file_path)
    if not file_path.startswith(corpus_dir) or not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read(2000)  # read first ~2000 characters
        # shrink to first 400 chars for preview
        snippet = text[:800].replace("\n", " ").strip()
        if len(text) > 800:
            snippet = snippet + "..."
        return jsonify({"filename": filename, "snippet": snippet})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Optional: serve static files (Flask does this automatically from static/)
# If you need to test fallback static route:
@app.route("/static/<path:path>")
def static_proxy(path):
    return send_from_directory(os.path.join(app.root_path, "static"), path)

if __name__ == "__main__":
    # Run in debug for development
    app.run(host="127.0.0.1", port=5000, debug=True)
