from flask import Blueprint, render_template, request, redirect, session, flash, url_for
import os, json

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

faculty_data_file = "backend/data/faculty.json"
upload_folder = "backend/uploads"

os.makedirs(upload_folder, exist_ok=True)

@faculty_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        branch = request.form.get("branch")

        if not all([name, email, branch]):
            return "All fields required", 400

        # Save faculty info
        if not os.path.exists(faculty_data_file):
            with open(faculty_data_file, "w") as f:
                json.dump([], f)

        with open(faculty_data_file, "r") as f:
            data = json.load(f)
        data.append({"name": name, "email": email, "branch": branch})
        with open(faculty_data_file, "w") as f:
            json.dump(data, f, indent=2)

        session["faculty"] = {"name": name, "email": email, "branch": branch}
        return redirect("/faculty/upload")

    return render_template("faculty_login.html")


@faculty_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    user = session.get("faculty")
    if not user:
        return redirect("/faculty/login")

    if request.method == 'POST':
        branch = request.form.get("branch")
        subject = request.form.get("subject")
        semester = request.form.get("semester")
        file = request.files.get("file")

        if file:
            filename = file.filename
            path = os.path.join(upload_folder, filename)
            file.save(path)
            print(f"📁 File uploaded to {path}")

            # ✅ Flash message and redirect
            flash("✅ File uploaded successfully!", "success")
            return redirect(url_for("home"))

    return render_template("faculty_upload.html")
