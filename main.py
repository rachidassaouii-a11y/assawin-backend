import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration de la clé API
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Initialisation du modèle
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "ASSAWIN API is running successfully!"})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_query = data.get("query", "")
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    response = model.generate_content(user_query)
    return jsonify({"response": response.text})
