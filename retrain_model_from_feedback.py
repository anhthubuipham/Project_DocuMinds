import os
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

# === Configuration ===
FEEDBACK_FILE = "feedback_log.json"
MODEL_OUTPUT_PATH = "retrained_document_classifier.joblib"

# === Step 1: Load feedback data ===
if not os.path.exists(FEEDBACK_FILE):
    print("❌ No feedback_log.json found. Please run the sorter and collect feedback first.")
    exit()

with open(FEEDBACK_FILE, "r") as f:
    feedback_data = json.load(f)

df = pd.DataFrame(feedback_data)
df = df[["text_excerpt", "correct_category"]].dropna()

if df.empty or len(df) < 3:
    print("⚠️ Not enough feedback entries to train a model (need at least 3).")
    exit()

# === Step 2: Train model ===
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", LogisticRegression(max_iter=1000))
])

pipeline.fit(df["text_excerpt"], df["correct_category"])

# === Step 3: Save new model ===
joblib.dump(pipeline, MODEL_OUTPUT_PATH)
print(f"✅ Model retrained and saved as: {MODEL_OUTPUT_PATH}")

