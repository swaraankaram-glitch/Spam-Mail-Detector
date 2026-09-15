import pandas as pd
import joblib
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report


# ==================================================
# 1. LOAD DATASET
# ==================================================

print("Loading dataset...")

df = pd.read_csv(
    "spam.csv",
    encoding="latin-1"
)

print("Total messages:", len(df))

print("\nColumns found:")
print(df.columns.tolist())


# ==================================================
# 2. SELECT REQUIRED COLUMNS
# ==================================================

# Your dataset contains:
# Category = spam / ham
# Message  = actual SMS text

df = df[["Category", "Message"]]

df = df.rename(
    columns={
        "Category": "label",
        "Message": "message"
    }
)


# Remove missing values
df = df.dropna()


# ==================================================
# 3. CHECK DATA
# ==================================================

print("\nMessage distribution:")

print(
    df["label"].value_counts()
)


# ==================================================
# 4. CONVERT LABELS
# ==================================================

df["label"] = df["label"].map({
    "ham": 0,
    "spam": 1
})


# ==================================================
# 5. SPLIT DATA
# ==================================================

X = df["message"]

y = df["label"]


X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42,

    stratify=y
)


print("\nTraining messages:", len(X_train))

print("Testing messages:", len(X_test))


# ==================================================
# 6. TF-IDF VECTORIZATION
# ==================================================

print("\nCreating TF-IDF vectors...")

vectorizer = TfidfVectorizer(

    lowercase=True,

    stop_words="english",

    max_features=5000
)


X_train_tfidf = vectorizer.fit_transform(
    X_train
)

X_test_tfidf = vectorizer.transform(
    X_test
)


# ==================================================
# 7. TRAIN NAIVE BAYES MODEL
# ==================================================

print("Training Naive Bayes model...")

model = MultinomialNB()

model.fit(
    X_train_tfidf,
    y_train
)


# ==================================================
# 8. EVALUATE MODEL
# ==================================================

predictions = model.predict(
    X_test_tfidf
)


accuracy = accuracy_score(
    y_test,
    predictions
)


print("\n")
print("=" * 50)

print("MODEL RESULTS")

print("=" * 50)

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "Not Spam",
            "Spam"
        ]
    )
)


# ==================================================
# 9. SAVE MODEL
# ==================================================

joblib.dump(
    model,
    "model/spam_classifier.pkl"
)


joblib.dump(
    vectorizer,
    "model/vectorizer.pkl"
)


print("=" * 50)

print("MODEL SAVED SUCCESSFULLY")

print("=" * 50)

print(
    "✓ model/spam_classifier.pkl"
)

print(
    "✓ model/vectorizer.pkl"
)