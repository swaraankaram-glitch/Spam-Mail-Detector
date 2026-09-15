from flask import Flask, render_template, request, jsonify
import joblib


# ==================================================
# CREATE FLASK APPLICATION
# ==================================================

app = Flask(__name__)


# ==================================================
# LOAD TRAINED MODEL
# ==================================================

model = joblib.load(
    "model/spam_classifier.pkl"
)

vectorizer = joblib.load(
    "model/vectorizer.pkl"
)


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def home():

    return render_template("index.html")


# ==================================================
# SPAM PREDICTION
# ==================================================

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    message = data.get(
        "message",
        ""
    ).strip()


    # Check if message is empty

    if not message:

        return jsonify({
            "error": "Please enter a message."
        }), 400


    # Convert message into TF-IDF

    message_vector = vectorizer.transform(
        [message]
    )


    # Make prediction

    prediction = model.predict(
        message_vector
    )[0]


    # Get probabilities

    probabilities = model.predict_proba(
        message_vector
    )[0]


    not_spam_probability = probabilities[0]

    spam_probability = probabilities[1]


    # Determine result

    if prediction == 1:

        result = "SPAM"

        confidence = spam_probability

    else:

        result = "NOT SPAM"

        confidence = not_spam_probability


    # Send result to frontend

    return jsonify({

        "result": result,

        "confidence": round(
            confidence * 100,
            2
        ),

        "spam_probability": round(
            spam_probability * 100,
            2
        ),

        "not_spam_probability": round(
            not_spam_probability * 100,
            2
        )

    })


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )