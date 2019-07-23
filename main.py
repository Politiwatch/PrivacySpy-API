from flask import Flask, jsonify, request
from privacyspy import Spy


app = Flask(__name__)
spy = Spy()


@app.route("/analyze")
def analyze():
    url = request.args.get("url")
    article = spy.extract_policy_from_url(url=url)

    if spy.is_english(article):
        analysis = spy.privacy_policy_summary(article)
        print(analysis)
        return jsonify(spy.output(analysis))
    else:
        return jsonify({
            "version": spy.__version__,
            "status": "error",
            "error": "The Privacy Policy is not English."
        })


app.run(debug=True, port=3000)
