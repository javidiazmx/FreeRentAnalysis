import os
import logging
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Enable detailed logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])
def lookup():
    data = request.get_json()
    address = data.get('address', '')
    app.logger.info(f"📍 Received address: {address}")

    url = "https://search.onboard-apis.com/propertyapi/v1.0.0/property/detail"
    headers = {
        "accept": "application/json",
        "apikey": os.getenv("ada28deedfc084dcea40ac71125d3a6e")  # Ensure this is set in Render environment
    }
    params = {
        "address1": address,
        "address2": "USA"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        property_data = response.json()
        app.logger.info("✅ Property data fetched")

        result = property_data.get("property", [{}])[0]
        building = result.get("building", {})
        summary = result.get("summary", {})
        interior = building.get("interior", {})
        rooms = building.get("rooms", {})
        parking = building.get("parking", {})

        # Log full building structure to find hidden fields like cooling/heating
        import json
        app.logger.info("🧱 Building JSON:\n" + json.dumps(building, indent=2))

        data = {
            "architecture": summary.get("archStyle", "N/A"),
            "basement_size": interior.get("bsmtsize", "N/A"),
            "basement_type": interior.get("bsmttype", "N/A"),
            "baths": rooms.get("bathstotal", "N/A"),
            "beds": rooms.get("beds", "N/A"),
            "cooling": building.get("cooling", "N/A"),  # Likely missing
            "heating": building.get("heating", "N/A"),  # Likely missing
            "garage_type": parking.get("garagetype", "N/A"),
            "parking_spaces": parking.get("prkgSpaces", "N/A"),
            "property_class": summary.get("propclass", "N/A"),
            "sqft": building.get("size", {}).get("livingsize", "N/A"),
            "year_built": summary.get("yearbuilt", "N/A")
        }

        app.logger.info(f"✅ Extracted data: {data}")
        return jsonify(data)

    except requests.RequestException as e:
        app.logger.error(f"❌ API request failed: {e}")
        return jsonify({"error": "Failed to retrieve property data"}), 500
    except Exception as e:
        app.logger.error(f"❌ Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
