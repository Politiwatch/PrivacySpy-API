import os
from flask import Flask, jsonify, request
from privacyspy import Spy


app = Flask(__name__)
spy = Spy()


@app.route("/")
def root():
    return jsonify({
        "error": "No API request received. See documentation for details."
    })


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    token = None
    if request.method == "GET":
        token = request.args.get("token")
    elif request.method == "POST":
        token = request.form["token"]

    if token == None:
        return Spy.output("No token provided.", error=True, errorCode=2)
    elif token != os.environ["privacyspy_token"]:
        return Spy.output("Invalid token.", error=True, errorCode=3)

    article = None

    if request.method == "GET":
        url = request.args.get("url")
        if url == None:
            return Spy.output("No URL provided.", error=True, errorCode=1)
        try:
            article = spy.extract_policy_from_url(url=url)
        except:
            return Spy.output("Failed to extract a privacy policy from URL.", error=True, errorCode=4)

    if request.method == "POST":
        article = request.form["text"]

    # Checking for English not necessary
    analysis = spy.privacy_policy_summary(article)
    return Spy.output(analysis)


app.run(host="0.0.0.0", port=5000, debug=os.environ.get("DEBUG", "False") == "True")
