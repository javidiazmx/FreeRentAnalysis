import os
import logging
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])
def lookup():
    data = request.get_json()
    address = data.get("address", "").strip()
    app.logger.info(f"📍 Received address: {address}")

    if not address:
        return jsonify({"error": "Address is required"}), 400

    url = "https://search.onboard-apis.com/propertyapi/v1.0.0/property/detail"
    params = {
        "address1": address,
        "address2": "USA"
    }

    headers = {
        "accept": "application/json",
        "apikey": os.environ.get("RENT_API_KEY")  # 🔑 Make sure this is set in your environment!
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        app.logger.info("✅ Property data fetched")

        # Parse details
        prop = data["property"][0]
        details = {
            "architecture": prop.get("building", {}).get("summary", {}).get("archStyle", "N/A"),
            "basement_size": prop.get("building", {}).get("interior", {}).get("bsmtsize", "N/A"),
            "basement_type": prop.get("building", {}).get("interior", {}).get("bsmttype", "N/A"),
            "baths": prop.get("building", {}).get("rooms", {}).get("bathstotal", "N/A"),
            "beds": prop.get("building", {}).get("rooms", {}).get("beds", "N/A"),
            "cooling": prop.get("building", {}).get("interior", {}).get("cooling", "N/A"),
            "garage_type": prop.get("building", {}).get("parking", {}).get("garagetype", "N/A"),
            "heating": prop.get("building", {}).get("interior", {}).get("heating", "N/A"),
            "parking_spaces": prop.get("building", {}).get("parking", {}).get("prkgSpaces", "N/A"),
            "property_class": prop.get("summary", {}).get("propclass", "N/A"),
            "sqft": prop.get("building", {}).get("size", {}).get("livingsize", "N/A"),
            "year_built": prop.get("summary", {}).get("yearbuilt", "N/A")
        }

        app.logger.info(f"✅ Extracted data: {details}")
        return jsonify(details)

    except requests.exceptions.RequestException as e:
        app.logger.error(f"❌ API request failed: {e}")
        return jsonify({"error": "Lookup failed. Please check the address or try again later."}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
