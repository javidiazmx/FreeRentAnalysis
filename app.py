from flask import Flask, request, jsonify, render_template
import requests
import os
import json

app = Flask(__name__)

# Read API key from environment variable or fallback
ATTOM_KEY = os.environ.get('ATTOM_KEY', 'YOUR_API_KEY_HERE')

# Serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Handle property lookup via ATTOM API
@app.route('/lookup', methods=['POST'])
def lookup():
    try:
        data = request.get_json()
        address = data.get('address')

        if not address:
            return jsonify({'error': 'Missing address'}), 400

        # Split address into street and city/state
        address_parts = address.split(",", 1)
        address1 = address_parts[0].strip()
        address2 = address_parts[1].strip() if len(address_parts) > 1 else ''

        # Send request to ATTOM
        res = requests.get(
            'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/address',
            params={'address1': address1, 'address2': address2},
            headers={'Accept': 'application/json', 'apikey': ATTOM_KEY}
        )

        print(f"Status Code: {res.status_code}")
        print(f"Response Text: {res.text}")

        if res.status_code != 200:
            return jsonify({'error': f'ATTOM error: {res.status_code}'}), res.status_code

        results = res.json()
        props = results.get('property', [])
        if not props:
            return jsonify({'error': 'No data found'}), 404

        prop = props[0]
        print(json.dumps(prop, indent=2))
        struct = prop.get('building', {})

        # Fallback field logic
        beds = struct.get('rooms', {}).get('beds') \
            or prop.get('summary', {}).get('beds_count') \
            or 'N/A'

        baths = struct.get('rooms', {}).get('baths') \
            or prop.get('summary', {}).get('baths_count') \
            or 'N/A'

        sqft = struct.get('size', {}).get('universalsize') \
            or struct.get('size', {}).get('grosssize') \
            or prop.get('summary', {}).get('building_area') \
            or 'N/A'

        year_built = struct.get('yearbuilt') \
            or prop.get('summary', {}).get('yearbuilt') \
            or 'N/A'

        return jsonify({
            'beds': beds,
            'baths': baths,
            'sqft': sqft,
            'year_built': year_built
        })

    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Run the Flask app with correct port binding for Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
