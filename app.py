from flask import Flask, render_template, request
import pandas as pd
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.utils.ml_utils.feature_extractor import extract_features
import sys

app = Flask(__name__)

# Load pre-trained objects
preprocessor = load_object("final_model/preprocessor.pkl")
final_model = load_object("final_model/model.pkl")
network_model = NetworkModel(preprocessor=preprocessor, model=final_model)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    url = ""
    if request.method == "POST":
        try:
            url = request.form.get("url")
            df = pd.DataFrame([extract_features(url)])
            y_pred = network_model.predict(df)[0]

            # Map 0/1 to Safe / Phishing
            if y_pred == 0:
                result = "Safe "
                status_class = "safe"
            else:
                result = "Phishing "
                status_class = "phishing"

            return render_template("index.html", result=result, status_class=status_class, url=url)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    return render_template("index.html", result=result, url=url, status_class="")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
