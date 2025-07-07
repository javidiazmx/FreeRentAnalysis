from flask import Flask, request, jsonify, render_template
import requests
import os
import json

app = Flask(__name__)

# ATTOM API Key
ATTOM_KEY = os.environ.get('ATTOM_KEY', 'ada28deedfc084dcea40ac71125d3a6e')

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

        # Separate address1 and address2
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

        # Beds
        beds = struct.get('rooms', {}).get('beds') \
            or prop.get('summary', {}).get('beds_count') \
            or 'N/A'

        # Baths - now checking directly under root property first
        raw_baths = prop.get('bathstotal') \
            or struct.get('rooms', {}).get('baths') \
            or prop.get('summary', {}).get('baths_count')

        if raw_baths is not None:
            try:
                baths = int(raw_baths) if float(raw_baths).is_integer() else round(float(raw_baths), 1)
            except:
                baths = 'N/A'
        else:
            baths = 'N/A'

        # Sq Ft
        sqft = struct.get('size', {}).get('universalsize') \
            or struct.get('size', {}).get('grosssize') \
            or prop.get('summary', {}).get('building_area') \
            or 'N/A'

        # Year Built
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
