from flask import Flask, request, jsonify, render_template
import requests
import os
import json

app = Flask(__name__)

# Use your ATTOM API key
ATTOM_KEY = os.environ.get('ATTOM_KEY', 'YOUR_ACTUAL_KEY_HERE')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])
def lookup():
    try:
        data = request.get_json()
        address = data.get('address')

        if not address:
            return jsonify({'error': 'Missing address'}), 400

        # Split into address1 and address2 for ATTOM API
        address_parts = address.split(",", 1)
        address1 = address_parts[0].strip()
        address2 = address_parts[1].strip() if len(address_parts) > 1 else ''

        res = requests.get(
            'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail',
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
        struct = prop.get('building', {})

        # Bedrooms
        beds = struct.get('rooms', {}).get('beds') \
            or prop.get('summary', {}).get('beds_count') \
            or 'N/A'

        # Bathrooms with rounding
        raw_baths = prop.get('bathstotal') \
            or struct.get('rooms', {}).get('baths') \
            or prop.get('summary', {}).get('baths_count')

        if raw_baths:
            baths = int(raw_baths) if float(raw_baths).is_integer() else round(float(raw_baths), 1)
        else:
            baths = 'N/A'

        # Square feet
        sqft = struct.get('size', {}).get('universalsize') \
            or struct.get('size', {}).get('grosssize') \
            or prop.get('summary', {}).get('building_area') \
            or 'N/A'

        # Year built
        year_built = struct.get('yearbuilt') \
            or prop.get('yearbuilt') \
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
