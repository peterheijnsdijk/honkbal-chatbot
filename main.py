from flask import Flask, request, jsonify
import os
import google.generativeai as genai
from pathlib import Path
from PyPDF2 import PdfReader

app = Flask(__name__)

# Configureer Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# PDF inlezen bij startup
pdf_path = Path("HB_officiele_spelregels_honkbal_2025_v1.2.pdf")
pdf_text = ""
if pdf_path.exists():
    reader = PdfReader(str(pdf_path))
    for page in reader.pages:
        pdf_text += page.extract_text() + "\n"

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    question = data.get("question", "")

    if not question:
        return jsonify({"answer": "Geen vraag ontvangen."})

    # Hier kan je RAG logica doen; nu dummy: hele PDF als context
    prompt = f"Beantwoord de volgende vraag over honkbalregels op basis van de tekst:\n\n{pdf_text}\n\nVraag: {question}\nAntwoord:"
    
    # Genereer antwoord via Gemini
    try:
        response = genai.generate(
            model="gemini-2.5-pro",
            prompt=prompt,
            temperature=0
        )
        answer = response.text
    except Exception as e:
        answer = f"Fout bij genereren: {str(e)}"

    return jsonify({"answer": answer})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
