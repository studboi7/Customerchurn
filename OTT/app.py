from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import os

app = Flask(__name__)

# File paths
model_path = "random_forest_model.pkl"
encoder_path = "label_encoder.pkl"
scaler_path = "scaler.pkl"

# Ensure model files exist
if not os.path.exists(model_path) or not os.path.exists(encoder_path) or not os.path.exists(scaler_path):
    raise FileNotFoundError("Trained model, scaler, or label encoder not found! Run train_model.py first.")

# Load model, encoder, and scaler
model = joblib.load(model_path)
label_encoder = joblib.load(encoder_path)
scaler = joblib.load(scaler_path)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Extract form input
        gender = request.form["gender"]
        gender_encoded = int(label_encoder.transform([gender])[0])

        # Convert all inputs to numerical format
        data = np.array([
            int(request.form["year"]),
            gender_encoded,
            int(request.form["age"]),
            int(request.form["no_of_days_subscribed"]),
            int(request.form["multi_screen"]),
            int(request.form["mail_subscribed"]),
            int(request.form["weekly_mins_watched"]),
            int(request.form["minimum_daily_mins"]),
            int(request.form["maximum_daily_mins"]),
            int(request.form["videos_watched"]),
            int(request.form["maximum_days_inactive"]),
            int(request.form["customer_support_calls"]),
            float(request.form["avg_daily_mins"])
        ]).reshape(1, -1)

        # Scale the data
        data_scaled = scaler.transform(data)

        # Predict churn
        prediction = int(model.predict(data_scaled)[0])
        probability = model.predict_proba(data_scaled)[0][1] * 100

        # Apply custom threshold (25%) for churn decision
        result = {
            "churn": "Yes" if probability > 25 else "No",
            "probability": f"{probability:.2f}%"
        }

        # Optional: print for debug
        print("[DEBUG] Prediction:", prediction)
        print("[DEBUG] Probability:", probability)

        return jsonify(result)

    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Make the app accessible on the local network
    app.run(debug=True, host="0.0.0.0", port=5001)
