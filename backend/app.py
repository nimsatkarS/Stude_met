from flask import Flask, request, jsonify, render_template, redirect, session
import joblib
import json
import os
import random

# 🔥 Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session

# 🔗 Register Blueprints
from auth.student import student_bp
from auth.faculty import faculty_bp
from auth.admin import admin_bp

app.register_blueprint(student_bp)
app.register_blueprint(faculty_bp)
app.register_blueprint(admin_bp)

# 📦 Load ML model & vectorizer
model_path = "backend/model_training"
model = joblib.load(os.path.join(model_path, "model.pkl"))
vectorizer = joblib.load(os.path.join(model_path, "vectorizer.pkl"))

# 📚 Load dataset
with open(os.path.join(model_path, "final_combined_dataset.json"), "r", encoding="utf-8") as f:
    dataset = json.load(f)

# 🔤 Normalize subject names
def normalize_subject(input_subject):
    subject_map = {
        "data structure": "data structures",
        "data structure ": "data structures",
        "dsa": "data structures",
        "daa": "design and analysis of algorithms",
        "design & analysis algorithm": "design and analysis of algorithms",
        "design and analysis algorithm": "design and analysis of algorithms",
        "oop": "object oriented programming",
        "object oriented": "object oriented programming",
        "object orented programming": "object oriented programming",
        "ai": "artificial intelligence",
        "artificial intelligence ()": "artificial intelligence",
        "artificial intelligence": "artificial intelligence"
    }
    return subject_map.get(input_subject.strip().lower(), input_subject.strip().lower())

# 🏠 Home route
@app.route('/')
def home():
    user = session.get("student") or session.get("faculty") or session.get("admin")
    return render_template('index.html', user=user)

# 🧪 Quiz page
@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

# 🎯 Fetch MCQs for a subject
@app.route('/get-mcq', methods=['POST'])
def get_mcq():
    content = request.get_json()
    print("🔍 Received:", content)

    branch = content.get('branch', '').strip().lower()
    semester = content.get('semester', '').strip().lower()
    subject = normalize_subject(content.get('subject', '').strip())

    with open("backend/model_training/mcq_dataset.json", "r", encoding="utf-8") as f:
        mcqs = json.load(f)

    filtered = [
        q for q in mcqs
        if q['branch'].strip().lower() == branch
        and q['semester'].strip().lower() == semester
        and normalize_subject(q['subject']) == subject
    ]

    random.shuffle(filtered)
    filtered = filtered[:30]

    print("✅ Filtered questions:", len(filtered))
    return jsonify(filtered)

# ✅ Quiz submission handler
@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    content = request.get_json()
    answers = content.get("answers", [])

    correct = 0
    incorrect = 0

    for q in answers:
        if q.get("selected") and q.get("selected").strip().lower() == q.get("answer", '').strip().lower():
            correct += 1
        else:
            incorrect += 1

    return jsonify({
        "total": len(answers),
        "correct": correct,
        "incorrect": incorrect
    })

# 📌 Dropdown options for UI
@app.route('/get-options')
def get_options():
    branches = sorted(set(item['branch'].strip() for item in dataset))
    semesters = sorted(set(item['semester'].strip() for item in dataset), key=lambda x: int(x))
    subjects = sorted(set(item['subject'].strip() for item in dataset))
    return jsonify({
        "branches": branches,
        "semesters": semesters,
        "subjects": subjects
    })

# 📌 Get subject list for a branch-semester
@app.route('/get-subjects')
def get_subjects():
    branch = request.args.get('branch', '').strip().lower()
    semester = request.args.get('semester', '').strip()
    subjects = sorted(set(
        item['subject']
        for item in dataset
        if item['branch'].strip().lower() == branch and item['semester'].strip() == semester
    ))
    return jsonify(subjects)

# 📈 Predict questions
@app.route('/predict', methods=['POST'])
def predict():
    content = request.get_json()
    branch = content.get('branch', '').strip().lower()
    semester = content.get('semester', '').strip()
    subject = normalize_subject(content.get('subject', '').strip())

    print("🔍 Predict Request:")
    print("   Branch  :", branch)
    print("   Semester:", semester)
    print("   Subject :", subject)

    filtered_questions = [
        item for item in dataset
        if branch in item['branch'].strip().lower()
        and semester == item['semester'].strip()
        and subject in normalize_subject(item['subject'])
    ]

    print(f"✅ Matched Questions: {len(filtered_questions)}")

    if not filtered_questions:
        return jsonify({"message": "No data found for given filters"}), 404

    texts = [item['question'] for item in filtered_questions]
    X = vectorizer.transform(texts)
    preds = model.predict(X)

    predicted_questions = {}
    for i, pred in enumerate(preds):
        cluster = predicted_questions.setdefault(str(pred), [])
        cluster.append(texts[i])

    return jsonify(predicted_questions)

# 🚀 Run server
if __name__ == '__main__':
    app.run(debug=True)
