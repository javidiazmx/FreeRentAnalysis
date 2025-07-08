from flask import Flask, request, jsonify, render_template
import requests
import os
import json

app = Flask(__name__)

# Set your ATTOM API key here
ATTOM_KEY = os.environ.get('ATTOM_KEY', 'YOUR_API_KEY_HERE')

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

        address_parts = address.split(",", 1)
        address1 = address_parts[0].strip()
        address2 = address_parts[1].strip() if len(address_parts) > 1 else ''

        # Make API request
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

        # Extract values
        beds = struct.get('rooms', {}).get('beds') or 'N/A'
        baths = struct.get('rooms', {}).get('bathstotal') or 'N/A'
        sqft = struct.get('size', {}).get('universalsize') or struct.get('size', {}).get('grosssize') or 'N/A'
        year_built = struct.get('yearbuilt') or 'N/A'

        garage_type = struct.get('parking', {}).get('garagetype', 'N/A')
        parking_spaces = struct.get('parking', {}).get('prkgSpaces', 'N/A')
        basement_type = struct.get('interior', {}).get('bsmttype', 'N/A')
        basement_size = struct.get('interior', {}).get('bsmtsize', 'N/A')
        architecture = struct.get('summary', {}).get('archStyle', 'N/A')
        heating = struct.get('utilities', {}).get('heatsystem', 'N/A')
        cooling = struct.get('utilities', {}).get('coolsystem', 'N/A')
        property_class = prop.get('area', {}).get('countyuse1', 'N/A')

        # Log all extracted fields
        print("✅ Extracted Values:")
        print(f"Beds: {beds}")
        print(f"Baths: {baths}")
        print(f"SqFt: {sqft}")
        print(f"Year Built: {year_built}")
        print(f"Garage Type: {garage_type}")
        print(f"Parking Spaces: {parking_spaces}")
        print(f"Basement Type: {basement_type}")
        print(f"Basement Size: {basement_size}")
        print(f"Architecture: {architecture}")
        print(f"Heating: {heating}")
        print(f"Cooling: {cooling}")
        print(f"Property Class: {property_class}")

        return jsonify({
            'beds': beds,
            'baths': baths,
            'sqft': sqft,
            'year_built': year_built,
            'garage_type': garage_type,
            'parking_spaces': parking_spaces,
            'basement_type': basement_type,
            'basement_size': basement_size,
            'architecture': architecture,
            'heating': heating,
            'cooling': cooling,
            'property_class': property_class
        })

    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
