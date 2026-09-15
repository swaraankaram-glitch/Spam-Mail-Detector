from pathlib import Path
import json
import re
import joblib
from flask import Flask, render_template, request, jsonify

BASE = Path(__file__).resolve().parent
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 65536
try:
    model = joblib.load(BASE / 'model/spam_classifier.pkl')
    vectorizer = joblib.load(BASE / 'model/vectorizer.pkl')
except FileNotFoundError as error:
    raise RuntimeError('Model files are missing. Run: python train_model.py') from error

@app.get('/')
def home():
    return render_template('index.html')

@app.get('/metrics')
def metrics():
    path = BASE / 'model/metrics.json'
    if not path.exists():
        return jsonify(error='Evaluation unavailable. Run python train_model.py.'), 503
    return jsonify(json.loads(path.read_text(encoding='utf-8')))

@app.errorhandler(413)
def too_large(error):
    return jsonify(error='Message is too large. Limit: 10,000 characters.'), 413

@app.post('/predict')
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('message'), str):
        return jsonify(error='Send a JSON object with a message string.'), 400
    message = data['message'].strip()
    if not message:
        return jsonify(error='Please enter a message.'), 400
    if len(message) > 10000:
        return jsonify(error='Message is too large. Limit: 10,000 characters.'), 400
    vector = vectorizer.transform([message])
    probabilities = model.predict_proba(vector)[0]
    spam_index = list(model.classes_).index(1)
    clean_index = list(model.classes_).index(0)
    spam = bool(model.predict(vector)[0] == 1)
    # Positive feature log-likelihood differences are evidence toward spam.
    names = vectorizer.get_feature_names_out()
    weights = model.feature_log_prob_[spam_index] - model.feature_log_prob_[clean_index]
    evidence = sorted(((str(names[i]), float(vector[0, i] * weights[i]))
                       for i in vector.indices if weights[i] > 0), key=lambda item: -item[1])[:10]
    category = None
    if spam:
        if re.search(r'\b(password|verify|account|login|bank)\b', message, re.I):
            category = 'Phishing'
        elif re.search(r'\b(win|won|prize|claim|cash|lottery)\b', message, re.I):
            category = 'Scams'
        elif re.search(r'\b(offer|sale|discount|buy|free|subscribe)\b', message, re.I):
            category = 'Marketing'
        else:
            category = 'Other'
    return jsonify(result='SPAM' if spam else 'NOT SPAM',
                   confidence=round(float(max(probabilities)) * 100, 2),
                   spam_probability=round(float(probabilities[spam_index]) * 100, 2),
                   not_spam_probability=round(float(probabilities[clean_index]) * 100, 2),
                   keywords=[word for word, _ in evidence], category=category)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
