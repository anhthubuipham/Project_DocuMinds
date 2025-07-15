import os
import shutil
import fitz  # PyMuPDF
import docx
import json
from datetime import datetime

# Configuration
SOURCE_FOLDER = "source_folder"
TARGET_BASE = "sorted"
FEEDBACK_FILE = "feedback_log.json"

# Categories and associated keywords
CATEGORIES = {
    "Invoices": ["invoice", "amount", "payment"],
    "University": ["semester", "university", "course"],
    "Applications": ["application", "cv", "cover letter"],
    "Work": ["project", "meeting", "client"],
    "Private": ["insurance", "contract", "rent"]
}

# Load existing feedback if available
if os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, "r") as f:
        feedback_data = json.load(f)
else:
    feedback_data = []

# Function to extract text from supported files
def extract_text(file_path):
    try:
        if file_path.endswith(".pdf"):
            with fitz.open(file_path) as doc:
                return " ".join(page.get_text() for page in doc)
        elif file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            return " ".join(p.text for p in doc.paragraphs)
        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return ""

# Simple rule-based classification
def classify_text(text):
    text = text.lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "Unsorted"

# Move file into sorted folder
def move_file(file_path, category):
    target_folder = os.path.join(TARGET_BASE, category)
    os.makedirs(target_folder, exist_ok=True)
    shutil.move(file_path, os.path.join(target_folder, os.path.basename(file_path)))

# Main sorting logic
def sort_documents():
    decisions = []
    print(f"🔍 Scanning folder: {SOURCE_FOLDER}")
    for filename in os.listdir(SOURCE_FOLDER):
        full_path = os.path.join(SOURCE_FOLDER, filename)
        if os.path.isfile(full_path) and filename.endswith((".pdf", ".docx", ".txt")):
            text = extract_text(full_path)
            category = classify_text(text)
            move_file(full_path, category)
            print(f"✅ Moved: {filename} → {category}")
            decisions.append({
                "filename": filename,
                "predicted_category": category,
                "text_excerpt": text[:150] + "..." if len(text) > 150 else text
            })
        else:
            print(f"⚠️ Skipped: {filename} (unsupported or not a file)")
    return decisions

# Ask for user feedback after sorting
def ask_for_feedback(decisions):
    print("\n📋 Summary of this run:")
    for i, entry in enumerate(decisions):
        print(f" {i+1}. {entry['filename']} → {entry['predicted_category']}")

    all_correct = input("\n✅ Are all classifications correct? (y/n): ").strip().lower()
    if all_correct != "y":
        wrong_indices = input("Enter the numbers of incorrect files (comma-separated, e.g., 1,3): ")
        wrong_indices = [int(x.strip()) - 1 for x in wrong_indices.split(",") if x.strip().isdigit()]
        for idx in wrong_indices:
            correct_cat = input(f"Enter the correct category for '{decisions[idx]['filename']}': ").strip()
            feedback_entry = {
                "filename": decisions[idx]["filename"],
                "predicted_category": decisions[idx]["predicted_category"],
                "correct_category": correct_cat,
                "text_excerpt": decisions[idx]["text_excerpt"],
                "timestamp": datetime.now().isoformat()
            }
            feedback_data.append(feedback_entry)


    # Save feedback data
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback_data, f, indent=2)
    print("✅ Feedback saved.")

# Entry point
if __name__ == "__main__":
    results = sort_documents()
    ask_for_feedback(results)
