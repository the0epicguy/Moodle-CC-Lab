from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Demonstration data is kept in memory. It resets when the app process restarts.
students = [
    {"id": 1, "name": "Aarav Sharma", "course": "Computer Engineering"},
    {"id": 2, "name": "Mira Patel", "course": "Information Technology"},
]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        course = request.form.get("course", "").strip()

        if name and course:
            students.append({
                "id": max((student["id"] for student in students), default=0) + 1,
                "name": name,
                "course": course,
            })

        return redirect(url_for("index"))

    return render_template("index.html", students=students)


if __name__ == "__main__":
    # Local development runs on port 5000. On EC2, systemd/Gunicorn binds port 8000.
    app.run(host="0.0.0.0", port=5000, debug=False)
