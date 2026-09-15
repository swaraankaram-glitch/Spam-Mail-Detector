# SpamGuard

A local Flask dashboard for SMS spam classification using TF-IDF and Multinomial Naive Bayes.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python train_model.py
python app.py
```

Open http://127.0.0.1:5000. Training rebuilds both model artifacts and their matching evaluation report. Paths are resolved relative to the project, so the application can also be launched from another directory. The server binds to localhost with debug mode disabled.

## Dashboard

- Three KPIs: session scans, spam flagged, and held-out detection accuracy.
- Seven-day trend chart reflecting scans made during the current page session.
- Spam category donut: keyword-based Phishing, Scams, Marketing, and Other estimates. The classifier itself predicts only spam or clean.
- Interactive tester with probability gauge and highlighted words that provide positive model evidence toward spam. These probabilities are model estimates, not calibrated guarantees.
- Activity log with status filter and sortable message, status, confidence, and time columns.
- Confusion matrix, ROC curve, AUC, and real model information.

Messages are sent to your local Flask server for inference. History lives only in page memory and clears on reload; messages are not written to disk. This application flags messages for review; it does not block email delivery. No external frontend services or chart CDNs are required.

## Evaluation

Training removes duplicate message texts before a stratified 80/20 split (`random_state=42`). The vectorizer is fitted only on training data. Current results: **97.0% accuracy**, **0.9858 ROC AUC**, on **1,032 held-out messages**.

| Actual / predicted | Clean | Spam |
| --- | ---: | ---: |
| Clean | 904 | 0 |
| Spam | 31 | 97 |

The test set's spam recall is approximately 75.8%, despite high overall accuracy. The model is trained on English SMS data; email and newer phishing patterns have not been evaluated. It is not BERT. The dashboard does not use the illustrative 98.2% accuracy or 89% probability from the design brief.

## Project map

| Path | Purpose |
| --- | --- |
| `app.py` | Flask page, input validation, inference, word evidence, metrics endpoint |
| `train_model.py` | Deduplicated dataset split, model training, saved evaluation |
| `templates/index.html` | Responsive dashboard markup |
| `static/style.css`, `static/script.js` | Styling, tester, charts, session history |
| `model/` | Classifier, vectorizer, and `metrics.json` used by the application |
| `spam.csv` | Training input (`Category`, `Message`) |
| `SMSSpamCollection`, `sms.zip`, `readme` | Original corpus materials and dataset documentation |
| `model.pkl` | Legacy artifact; not used by the current application |
| `test_app.py` | API and evaluation regression checks |

## API

`POST /predict` accepts a JSON object with a nonempty `message` string (maximum 10,000 characters). It returns the classification, confidence, spam/clean probabilities, evidence keywords, and an estimated category. Invalid requests return JSON errors with HTTP 400; oversized request bodies return HTTP 413.

`GET /metrics` returns the saved held-out evaluation. If it is missing, run `python train_model.py` and restart the app after retraining.

## Verification

```powershell
python -m unittest -v
python -m compileall -q app.py train_model.py
node --check static/script.js
```

Node is only required for the optional JavaScript syntax check. API regression checks passed; browser visual and interaction checks could not be performed in the development session because no browser was available.

## Repairs made

Removed Markdown fences embedded in the HTML/JavaScript, replaced the broken tester script, validated JSON shape and message types, added input size limits, fixed working-directory-dependent paths, removed duplicate training imports, ensured the model directory exists, and replaced the incomplete Streamlit README with Flask instructions. Existing local page/script work was incorporated into the dashboard rewrite. Original dataset materials and the unused legacy model were retained.
