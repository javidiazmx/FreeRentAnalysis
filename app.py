from flask import Flask, request, jsonify, render_template_string
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

API_KEY = "ada28deedfc084dcea40ac71125d3a6e"
API_URL = "https://search.onboard-apis.com/propertyapi/v1.0.0/property/detail"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Free Rent Analysis</title>
</head>
<body>
    <h2>Enter Address</h2>
    <input type="text" id="address" value="5565 Cambridge Way, Hanover Park, IL 60133, USA" style="width: 500px">
    <button onclick="lookup()">Lookup</button>
    <h2>Property Details</h2>
    <div id="results"></div>

    <script>
    async function lookup() {
        const address = document.getElementById("address").value;
        const response = await fetch("/lookup", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({address})
        });

        const resultDiv = document.getElementById("results");
        if (response.ok) {
            const data = await response.json();
            let html = "<ul>";
            for (const [key, value] of Object.entries(data)) {
                html += `<li><strong>${key.replace(/_/g, ' ')}:</strong> ${value}</li>`;
            }
            html += "</ul>";
            resultDiv.innerHTML = html;
        } else {
            alert("Lookup failed. Please check the address.");
        }
    }
    </script>
</body>
</html>
'''

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/lookup", methods=["POST"])
def lookup():
    data = request.get_json()
    address = data.get("address")
    logging.info(f"📍 Received address: {address}")

    params = {
        "address1": address.split(", USA")[0],
        "address2": "USA"
    }
    headers = {
        "accept": "application/json",
        "apikey": API_KEY
    }

    try:
        res = requests.get(API_URL, params=params, headers=headers)
        res.raise_for_status()
        json_data = res.json()
        property_info = json_data["property"][0]
        building = property_info.get("building", {})
        summary = property_info.get("summary", {})

        details = {
            "architecture": summary.get("archStyle", "N/A"),
            "basement_size": building.get("interior", {}).get("bsmtsize", "N/A"),
            "basement_type": building.get("interior", {}).get("bsmttype", "N/A"),
            "baths": building.get("rooms", {}).get("bathstotal", "N/A"),
            "beds": building.get("rooms", {}).get("beds", "N/A"),
            "cooling": building.get("interior", {}).get("cooling") or "N/A",
            "garage_type": building.get("parking", {}).get("garagetype", "N/A"),
            "heating": building.get("interior", {}).get("heating") or "N/A",
            "parking_spaces": building.get("parking", {}).get("prkgSpaces", "N/A"),
            "property_class": summary.get("propclass", "N/A"),
            "sqft": building.get("size", {}).get("livingsize", "N/A"),
            "year_built": summary.get("yearbuilt", "N/A")
        }

        logging.info(f"✅ Extracted data: {details}")
        return jsonify(details)

    except requests.RequestException as e:
        logging.error(f"❌ API request failed: {e}")
        return jsonify({"error": "Failed to fetch property data"}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
