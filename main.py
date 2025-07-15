import os
import shutil
import fitz  # PyMuPDF
import docx

SOURCE_FOLDER = "source_folder"
TARGET_BASE = "sorted"

CATEGORIES = {
    "Invoices": ["invoice", "amount", "payment"],
    "University": ["semester", "university", "course"],
    "Applications": ["application", "cv", "cover letter"],
    "Work": ["project", "meeting", "client"],
    "Private": ["insurance", "contract", "rent"]
}

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        with fitz.open(file_path) as doc:
            return " ".join(page.get_text() for page in doc)
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        return " ".join(paragraph.text for paragraph in doc.paragraphs)
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""

def classify_text(text):
    text = text.lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "Unsorted"

def move_file(file_path, category):
    target_folder = os.path.join(TARGET_BASE, category)
    os.makedirs(target_folder, exist_ok=True)
    shutil.move(file_path, os.path.join(target_folder, os.path.basename(file_path)))

def sort_documents():
    for filename in os.listdir(SOURCE_FOLDER):
        full_path = os.path.join(SOURCE_FOLDER, filename)
        if os.path.isfile(full_path) and filename.endswith((".pdf", ".docx", ".txt")):
            print(f"Processing: {filename}")
            text = extract_text(full_path)
            category = classify_text(text)
            move_file(full_path, category)
            print(f"Moved to: {category}")

if __name__ == "__main__":
    sort_documents()
