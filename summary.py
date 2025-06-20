from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        return jsonify({"error": "Text is required"}), 400

    try:
        summary = summarizer(text, max_length=512, min_length=30, do_sample=False)[0]["summary_text"]
        return jsonify({"summary": summary.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return 'Flask Summarizer API running'

if __name__ == '__main__':
    app.run(port=8000, debug=True)
