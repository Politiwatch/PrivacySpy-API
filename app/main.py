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
    if request.method == "GET":
        url = request.args.get("url")
        token = request.args.get("token")

        if url == None:
            return Spy.output("No URL provided.", error=True, errorCode=1)

        try:
            article = spy.extract_policy_from_url(url=url)
        except:
            return Spy.output("Failed to extract a privacy policy from URL.", error=True, errorCode=4)

    if request.method == "POST":
        if "plain_text" in request.form:
            article = request.form["plain_text"]
        else:
            article = spy.extract_policy_from_html(
                html=request.form["raw_html"])
        token = request.form["token"]
        raw = request.form["raw_html"]

    if token == None:
        return Spy.output("No token provided.", error=True, errorCode=2)
    elif token != os.environ["privacyspy_token"]:
        return Spy.output("Invalid token.", error=True, errorCode=3)

    if spy.is_english(article):
        analysis = spy.privacy_policy_summary(article)
        return Spy.output(analysis)
    else:
        return Spy.output("The Privacy Policy is not English.", error=True, errorCode=5)


app.run(host="0.0.0.0", port=5000)
