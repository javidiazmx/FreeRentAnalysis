import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = os.environ.get("RENTCAST_API_KEY") or "YOUR_API_KEY_HERE"

@app.route("/")
def home():
    return jsonify({"message": "Free Rent Analysis API is running"})

@app.route("/lookup", methods=["POST"])
def lookup():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.get_json()
    address = data.get("address", "").strip()
    if not address:
        return jsonify({"error": "Address is required"}), 400

    url = "https://api.rentcast.io/v1/properties/address"
    headers = {"accept": "application/json", "X-Api-Key": API_KEY}
    params = {"address": address}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        property_data = response.json()

        building = property_data.get("building", {})
        rooms = building.get("rooms", {})
        interior = building.get("interior", {})
        parking = building.get("parking", {})
        summary = building.get("summary", {})
        size = building.get("size", {})
        vintage = property_data.get("vintage", {})

        result = {
            "architecture": summary.get("archStyle", "N/A"),
            "basement_size": interior.get("bsmtsize", "N/A"),
            "basement_type": interior.get("bsmttype", "N/A"),
            "baths": rooms.get("bathstotal", "N/A"),
            "beds": rooms.get("beds", "N/A"),
            "cooling": summary.get("cooling", "N/A"),
            "garage_type": parking.get("garagetype", "N/A"),
            "heating": summary.get("heating", "N/A"),
            "parking_spaces": parking.get("prkgSpaces", "N/A"),
            "property_class": summary.get("bldgType", "N/A"),
            "sqft": size.get("livingsize", "N/A"),
            "year_built": summary.get("yearbuilt", "N/A")
        }

        print("✅ Processed Data:", result)  # Log to Render logs
        return jsonify(result)

    except requests.exceptions.RequestException as e:
        print("❌ API Request failed:", e)
        return jsonify({"error": "API request failed", "details": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
