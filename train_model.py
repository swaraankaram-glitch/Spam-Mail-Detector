from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve, roc_auc_score

BASE = Path(__file__).resolve().parent

def train():
    data = pd.read_csv(BASE / 'spam.csv').loc[:, ['Category', 'Message']].dropna()
    data['Message'] = data['Message'].str.strip()
    data = data[data['Category'].isin(['ham', 'spam']) & data['Message'].ne('')]
    data = data.drop_duplicates(subset=['Message'])
    x_train, x_test, y_train, y_test = train_test_split(
        data['Message'], data['Category'].map({'ham': 0, 'spam': 1}),
        test_size=0.2, random_state=42, stratify=data['Category'])
    vectorizer = TfidfVectorizer(lowercase=True, stop_words='english', max_features=5000)
    train_vectors = vectorizer.fit_transform(x_train)
    test_vectors = vectorizer.transform(x_test)
    model = MultinomialNB().fit(train_vectors, y_train)
    prediction = model.predict(test_vectors)
    probability = model.predict_proba(test_vectors)[:, list(model.classes_).index(1)]
    fpr, tpr, _ = roc_curve(y_test, probability)
    metrics = {'algorithm': 'Multinomial Naive Bayes', 'features': 'TF-IDF · 5,000 max features',
               'accuracy': round(accuracy_score(y_test, prediction) * 100, 2),
               'auc': round(roc_auc_score(y_test, probability), 4),
               'confusion_matrix': confusion_matrix(y_test, prediction, labels=[0, 1]).tolist(),
               'roc': list(map(list, zip(fpr.tolist(), tpr.tolist()))),
               'train_size': len(x_train), 'test_size': len(x_test)}
    (BASE / 'model').mkdir(exist_ok=True)
    joblib.dump(model, BASE / 'model/spam_classifier.pkl')
    joblib.dump(vectorizer, BASE / 'model/vectorizer.pkl')
    (BASE / 'model/metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    print(f"Saved model. Held-out accuracy: {metrics['accuracy']}%; AUC: {metrics['auc']}")

if __name__ == '__main__':
    train()
