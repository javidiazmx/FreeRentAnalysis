import os
import logging
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__, template_folder="templates")

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/lookup', methods=['POST'])
def lookup():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.get_json()
    address = data.get("address", "")
    logging.info(f"📍 Received address: {address}")

    if not address:
        return jsonify({"error": "No address provided"}), 400

    try:
        # Replace this with your actual API key and endpoint
        api_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail"
        headers = {
            "apikey": os.environ.get("ATTOM_API_KEY", "ada28deedfc084dcea40ac71125d3a6e")
        }
        params = {"address": address}

        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        property_data = response.json()
        logging.info("✅ Property data fetched")

        # Drill into response safely
        result = property_data.get("property", [{}])[0]

        building = result.get("building", {})
        size = building.get("size", {})
        rooms = building.get("rooms", {})
        interior = building.get("interior", {})
        construction = building.get("construction", {})
        parking = building.get("parking", {})
        summary = building.get("summary", {})
        vintage = result.get("vintage", {})

        data_out = {
            "architecture": summary.get("archStyle", "N/A"),
            "basement_size": interior.get("bsmtsize", "N/A"),
            "basement_type": interior.get("bsmttype", "N/A"),
            "baths": rooms.get("bathstotal", "N/A"),
            "beds": rooms.get("beds", "N/A"),
            "cooling": building.get("interior", {}).get("cooling", "N/A"),
            "garage_type": parking.get("garagetype", "N/A"),
            "heating": building.get("interior", {}).get("heating", "N/A"),
            "parking_spaces": parking.get("prkgSpaces", "N/A"),
            "property_class": result.get("summary", {}).get("propclass", "N/A"),
            "sqft": size.get("livingsize", "N/A"),
            "year_built": result.get("summary", {}).get("yearbuilt", "N/A")
        }

        logging.info(f"✅ Extracted data: {data_out}")
        return jsonify(data_out)

    except Exception as e:
        logging.exception("❌ Error during lookup")
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
