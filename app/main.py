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


@app.route("/analyze")
def analyze():
    url = request.args.get("url")
    token = request.args.get("token")

    if url == None:
        return Spy.output("No URL provided.", error=True, errorCode=1)

    if token == None:
        return Spy.output("No token provided.", error=True, errorCode=2)
    elif token != os.environ["privacyspy_token"]:
        return Spy.output("Invalid token.", error=True, errorCode=3)

    try:
        article = spy.extract_policy_from_url(url=url)
    except:
        return Spy.output("Failed to extract a privacy policy from URL.", error=True, errorCode=4)

    if spy.is_english(article):
        analysis = spy.privacy_policy_summary(article)
        return Spy.output(analysis)
    else:
        return Spy.output("The Privacy Policy is not English.", error=True, errorCode=5)


app.run(host="0.0.0.0", port=5000)
