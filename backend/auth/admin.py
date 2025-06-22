from flask import Blueprint, render_template, request, redirect, session, flash, url_for
import os, json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

admin_data_file = "backend/data/admin.json"

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")  # In real apps, hash & verify passwords

        if not all([username, password]):
            flash("❌ All fields required", "error")
            return render_template("admin_login.html")

        if not os.path.exists(admin_data_file):
            with open(admin_data_file, "w") as f:
                json.dump([], f)

        with open(admin_data_file, "r") as f:
            data = json.load(f)
        data.append({"username": username, "password": password})
        with open(admin_data_file, "w") as f:
            json.dump(data, f, indent=2)

        session["admin"] = {"username": username}
        flash(f"👨‍💼 Welcome, {username}!", "success")
        return redirect("/admin/dashboard")

    return render_template("admin_login.html")


@admin_bp.route('/dashboard')
def dashboard():
    if "admin" not in session:
        return redirect("/admin/login")
    return render_template("admin_dashboard.html", user=session["admin"])


@admin_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if "admin" not in session:
        return redirect("/admin/login")

    upload_folder = "backend/uploads"
    os.makedirs(upload_folder, exist_ok=True)

    if request.method == 'POST':
        branch = request.form.get("branch")
        subject = request.form.get("subject")
        semester = request.form.get("semester")
        file = request.files.get("file")

        if not all([branch, subject, semester, file]):
            flash("All fields and file are required.", "error")
            return redirect("/admin/upload")

        filename = file.filename
        file.save(os.path.join(upload_folder, filename))
        flash("✅ File uploaded successfully!", "success")
        return redirect(url_for("home"))

    return render_template("admin_upload.html")
