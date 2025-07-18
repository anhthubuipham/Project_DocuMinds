from flask import Flask, request, jsonify
import joblib
import os
import json
from datetime import datetime

# Load the trained model
MODEL_PATH = "mock_document_classifier.joblib"
model = joblib.load(MODEL_PATH)

# Feedback file
FEEDBACK_FILE = "feedback_log.json"
if os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, "r") as f:
        feedback_log = json.load(f)
else:
    feedback_log = []

# Create Flask app
app = Flask(__name__)

# Classify endpoint
@app.route('/classify', methods=['POST'])
def classify():
    data = request.json
    text = data.get("text", "")
    filename = data.get("filename", "unknown")
    if not text.strip():
        return jsonify({"error": "No text provided"}), 400
    prediction = model.predict([text])[0]
    return jsonify({"filename": filename, "predicted_category": prediction})

# Feedback endpoint
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    feedback_entry = {
        "filename": data.get("filename", "unknown"),
        "predicted_category": data.get("predicted_category", ""),
        "correct_category": data.get("correct_category", ""),
        "text_excerpt": data.get("text_excerpt", "")[:150],
        "timestamp": datetime.now().isoformat()
    }
    feedback_log.append(feedback_entry)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback_log, f, indent=2)
    return jsonify({"status": "Feedback saved"}), 200

# Run server
if __name__ == "__main__":
    app.run(port=5000)
