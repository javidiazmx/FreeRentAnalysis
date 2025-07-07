from flask import Flask, request, jsonify, render_template
import requests
import os
import json

app = Flask(__name__)

# ATTOM API key (replace this in Render secrets)
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

        # Split address into parts
        address_parts = address.split(",", 1)
        address1 = address_parts[0].strip()
        address2 = address_parts[1].strip() if len(address_parts) > 1 else ''

        # Call ATTOM API
        res = requests.get(
            'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail',
            params={'address1': address1, 'address2': address2},
            headers={'Accept': 'application/json', 'apikey': ATTOM_KEY}
        )

        print(f"==> ATTOM Status Code: {res.status_code}")
        print(f"==> ATTOM Response: {res.text}")

        if res.status_code != 200:
            return jsonify({'error': f'ATTOM error: {res.status_code}'}), res.status_code

        results = res.json()
        props = results.get('property', [])
        if not props:
            print("==> No properties found in response.")
            return jsonify({'error': 'No property data found'}), 404

        prop = props[0]
        print("==> Raw Property JSON:")
        print(json.dumps(prop, indent=2))

        building = prop.get('building', {})
        summary = prop.get('summary', {})
        rooms = building.get('rooms', {})
        size = building.get('size', {})

        # LOG each possible value
        print(f"building.rooms.beds: {rooms.get('beds')}")
        print(f"summary.beds_count: {summary.get('beds_count')}")
        print(f"bathstotal: {prop.get('bathstotal')}")
        print(f"building.rooms.baths: {rooms.get('baths')}")
        print(f"summary.baths_count: {summary.get('baths_count')}")
        print(f"size.universalsize: {size.get('universalsize')}")
        print(f"size.grosssize: {size.get('grosssize')}")
        print(f"summary.building_area: {summary.get('building_area')}")
        print(f"prop.yearbuilt: {prop.get('yearbuilt')}")
        print(f"building.yearbuilt: {building.get('yearbuilt')}")
        print(f"summary.yearbuilt: {summary.get('yearbuilt')}")

        # Extract values using correct fallback logic
        beds = rooms.get('beds') or summary.get('beds_count') or 'N/A'

        # Try every path for baths — also cast float to int when needed
        raw_baths = prop.get('bathstotal') \
            or rooms.get('baths') \
            or summary.get('baths_count')

        if isinstance(raw_baths, (int, float)):
            baths = int(raw_baths) if float(raw_baths).is_integer() else round(float(raw_baths), 1)
        else:
            baths = 'N/A'

        sqft = size.get('universalsize') \
            or size.get('grosssize') \
            or summary.get('building_area') \
            or 'N/A'

        year_built = prop.get('yearbuilt') \
            or building.get('yearbuilt') \
            or summary.get('yearbuilt') \
            or 'N/A'

        return jsonify({
            'beds': beds,
            'baths': baths,
            'sqft': sqft,
            'year_built': year_built
        })

    except Exception as e:
        print(f"==> Exception occurred: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
