from flask import Blueprint, render_template, request, redirect, session
import json
import os

student_bp = Blueprint('student', __name__, url_prefix='/student')
students_file = "backend/data/students.json"

@student_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        branch = request.form.get("branch")

        if not all([name, email, branch]):
            return "All fields required", 400

        if not os.path.exists(students_file):
            with open(students_file, "w") as f:
                json.dump([], f)

        with open(students_file, "r") as f:
            data = json.load(f)

        data.append({"name": name, "email": email, "branch": branch})

        with open(students_file, "w") as f:
            json.dump(data, f, indent=2)

        session["student"] = {"name": name, "email": email, "branch": branch}
        return redirect("/")  # Redirect to homepage

    return render_template("student_login.html")

@student_bp.route('/dashboard')
def dashboard():
    user = session.get("student")
    if not user:
        return redirect("/student/login")
    return render_template("student_dashboard.html", user=user)
