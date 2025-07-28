from flask import Flask, render_template, request, jsonify
import requests
import random
import os
from dotenv import load_dotenv

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = Flask(__name__)


# ---------- HOOKS ----------
hooks = [
    "Unlock the secret to...",
    "Struggling with ___? Here's your fix.",
    "What if we told you ___ could change everything?",
    "Top 5 hacks to instantly boost ___",
    "Here's why most people fail at ___"
]

# ---------- ROUTES ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_content():
    data = request.json
    category = data.get('category')
    topic = data.get('topic')
    model = data.get('model')
    keywords = data.get('keywords', '')  # New: Keywords for customization
    word_count = data.get('word_count', 100)  # New: Word count for blog
    enhance = data.get('enhance', False)  # New: Enhance flag

    # Input validation
    if not topic or not category or not model:
        return jsonify({"error": "Missing input fields."}), 400

    prompt = generate_prompt(category, topic, keywords, word_count, enhance)
    response = call_ai_api(prompt, model)

    return jsonify({
        "content": response.strip(),
        "hook": random.choice(hooks)
    })

@app.route('/enhance', methods=['POST'])
def enhance_content():
    data = request.json
    original_content = data.get('original_content')
    category = data.get('category')
    topic = data.get('topic')
    model = data.get('model')
    keywords = data.get('keywords', '')
    word_count = data.get('word_count', 100)

    if not original_content or not topic or not category or not model:
        return jsonify({"error": "Missing input fields."}), 400

    prompt = f"Enhance the following content about {topic} to make it more engaging and detailed while keeping the tone consistent with {category}. "
    if keywords:
        prompt += f"Incorporate these keywords: {keywords}. "
    prompt += f"Target length: {word_count} words. Original content: {original_content}"
    response = call_ai_api(prompt, model)

    return jsonify({
        "content": response.strip(),
        "hook": random.choice(hooks)
    })

# ---------- PROMPT BUILDER ----------
def generate_prompt(category, topic, keywords, word_count, enhance):
    base_prompt = ""
    if category == "instagram":
        base_prompt = f"Write a catchy and engaging Instagram post about {topic}. Keep it under 100 words."
    elif category == "blog":
        base_prompt = f"Write a professional blog paragraph on {topic}. Include valuable insights, target {word_count} words, and keep the tone engaging."
    elif category == "about":
        base_prompt = f"Write a creative and professional About Us section for a company focused on {topic}."
    elif category == "faq":
        base_prompt = f"Write a list of 3 FAQs with answers related to {topic}."
    else:
        base_prompt = f"Write something creative on {topic}."

    if keywords:
        base_prompt += f" Incorporate the following keywords: {keywords}."
    if enhance:
        base_prompt = f"Enhance this prompt to make it more detailed and engaging: {base_prompt}"
    return base_prompt

# ---------- API CALLER ----------
def call_ai_api(prompt, model):
    if model == "huggingface":
        return call_huggingface(prompt)
    elif model == "cohere":
        return call_cohere(prompt)
    elif model == "groq":
        return call_groq(prompt)
    else:
        return "Invalid model selected."

# ---------- HUGGING FACE ----------
def call_huggingface(prompt):
    url = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": prompt}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code != 200:
            return "HuggingFace API error: " + response.text
        output = response.json()
        return output[0]['generated_text']
    except Exception as e:
        return "Error generating content using HuggingFace."

# ---------- COHERE ----------
def call_cohere(prompt):
    url = "https://api.cohere.ai/v1/generate"
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "command-r-plus",
        "prompt": prompt,
        "max_tokens": 150
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code != 200:
            return "Cohere API error: " + response.text
        output = response.json()
        return output['generations'][0]['text']
    except Exception as e:
        return "Error generating content using Cohere."

# ---------- GROQ ----------
def call_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code != 200:
            return "Groq API error: " + response.text
        output = response.json()
        return output['choices'][0]['message']['content']
    except Exception as e:
        return "Error generating content using Groq."

# ---------- MAIN ----------
if __name__ == '__main__':
    app.run(debug=True)