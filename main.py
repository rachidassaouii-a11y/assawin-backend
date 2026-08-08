mport os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration de la clé API
api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "ASSAWIN API is running successfully!"})

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json(silent=True)
        if not data or "query" not in data:
            return jsonify({"error": "Format JSON invalide ou champ 'query' manquant"}), 400
        
        user_query = data.get("query", "")
        if not user_query:
            return jsonify({"error": "Aucune question fournise"}), 400
        
        response = model.generate_content(user_query)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
