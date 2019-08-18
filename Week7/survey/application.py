import cs50
import csv
import re
import passlib.hash
from pprint import pprint

from flask import Flask, jsonify, redirect, render_template, request

hashing_algorithms = {
    "argon2": passlib.hash.argon2,
    "bcrypt": passlib.hash.bcrypt_sha256,
    "pbkdf2_sha512": passlib.hash.pbkdf2_sha512,
    "sha256_crypt": passlib.hash.sha256_crypt,
    "sha512_crypt": passlib.hash.sha512_crypt,
    "md5_crypt": passlib.hash.md5_crypt,
    "sha1_crypt": passlib.hash.sha1_crypt,
    "des_crypt": passlib.hash.des_crypt
}

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


@app.route("/form", methods=["POST"])
def post_form():
    error_message = ""
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", 
                    request.form.get('email')):
        error_message = "Invalid email. "
    else:
        email = request.form.get('email')
    if not request.form.get("password"):
        error_message += "Invalid password. "
    else: 
        password = request.form.get("password")
    if request.form.get("use_hash"):
        if request.form.get("algorithm") not in hashing_algorithms.keys():
            error_message += "Invalid hashing algorithm."
        else:
            use_hash = True
            algorithm = request.form.get("algorithm")
    else:
        use_hash = False
        algorithm = "plaintext"

    if error_message:
        return render_template("error.html", message=error_message)
        
    if use_hash:
        password = hashing_algorithms[algorithm].encrypt(password)

    with open("survey.csv", "a") as file:
        writer = csv.DictWriter(file, fieldnames=["email", "password", "algorithm"])
        writer.writerow({"email": email, "password": password, "algorithm": algorithm})

    return redirect("/sheet")


@app.route("/sheet", methods=["GET"])
def get_sheet():
    with open("survey.csv", "r") as file:
        reader = csv.DictReader(file)
        users = list(reader)
    return render_template("sheet.html", users=users)
