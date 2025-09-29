from flask import Flask, request, jsonify
import os, faiss, numpy as np, google.generativeai as genai
from pypdf import PdfReader

app = Flask(__name__)

# Gemini API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# PDF laden & chunken
pdf_path = "HB_officiële_spelregels_honkbal_2025_v1.2.pdf"
def load_pdf(pdf_path, chunk_size=500):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

chunks = load_pdf(pdf_path)

# Embeddings
embed_model = "models/embedding-gecko-001"
def embed_text(texts):
    embeddings = []
    for t in texts:
        r = genai.embed_content(model=embed_model, content=t)
        embeddings.append(r["embedding"])
    return np.array(embeddings, dtype="float32")

embeddings = embed_text(chunks)

# FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Search functie
def search(query, top_k=5):
    q_emb = embed_text([query])
    distances, indices = index.search(q_emb, top_k)
    return [chunks[i] for i in indices[0]]

# RAG functie
def ask_gemini(query):
    context_chunks = search(query)
    context_text = "\n\n".join(context_chunks)
    prompt = f"""Beantwoord de vraag volgens de officiële honkbalregels.
Als het niet in de regels staat, zeg dat duidelijk.

Regels:
{context_text}

Vraag: {query}
"""
    model = genai.GenerativeModel("models/gemini-2.5-pro")
    response = model.generate_content(prompt)
    return response.text

# API endpoint
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    question = data["question"]
    answer = ask_gemini(question)
    return jsonify({"answer": answer})

# Voor Cloud Run: host op 0.0.0.0
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
