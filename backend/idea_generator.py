from flask import Flask, request, jsonify
from transformers import pipeline
import torch
import re

app = Flask(__name__)

# Use GPU if available
device = 0 if torch.cuda.is_available() else -1
generator = pipeline("text-generation", model="distilgpt2", device=device)

@app.route('/generate-ideas', methods=['POST'])
def generate_ideas():
    data = request.get_json()
    topic = data.get('prompt', '').strip().lower()

    if not topic:
        return jsonify({'error': 'No prompt provided'}), 400

    prompt = (
        f"Generate 10 short, relevant, and meaningful project ideas related to '{topic}'. "
        "Each idea should be under 30 words and should be listed like:\n"
        "1. Idea one\n2. Idea two\n"
    )

    try:
        idea_set = set()
        max_attempts = 10
        attempts = 0
        idea_pattern = re.compile(r'^\d+\.\s*(.+)')

        while len(idea_set) < 10 and attempts < max_attempts:
            responses = generator(
                prompt,
                max_length=120,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.8,
                top_k=40,
                top_p=0.9,
                no_repeat_ngram_size=2,
                early_stopping=True
            )
            attempts += 1

            for response in responses:
                lines = response['generated_text'].split('\n')
                for line in lines:
                    match = idea_pattern.match(line.strip())
                    if match:
                        idea = match.group(1).strip()
                        # Basic trimming at punctuation
                        idea = re.split(r'[.!?]', idea)[0].strip()
                        word_count = len(idea.split())

                        # Ensure it's not too short, contains the topic or a related term
                        if 5 <= word_count <= 30 and (
                            topic in idea.lower() or any(word in idea.lower() for word in topic.split())
                        ):
                            idea_set.add(idea)

                    if len(idea_set) == 10:
                        break

        if len(idea_set) < 10:
            return jsonify({'error': 'Could not generate 10 relevant ideas.'}), 500

        return jsonify({'ideas': list(idea_set)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=6000) 
