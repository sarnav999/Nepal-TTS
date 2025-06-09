from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/triage', methods=['POST'])
def triage():
    data = request.get_json()
    symptoms = data.get('symptoms', '')
    medications = data.get('medications', [])
    # Hardcoded logic: just echo the symptoms and medications
    answer = f"Diagnosis based on symptoms: {symptoms}. Medications: {', '.join(medications) if medications else 'None'}."
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True) 