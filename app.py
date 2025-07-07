from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)
ATTOM_KEY = os.environ.get('ATTOM_KEY', 'ada28deedfc084dcea40ac71125d3a6e')

@app.route('/lookup', methods=['POST'])
def lookup():
    try:
        if not request.is_json:
            return jsonify({'error': "Unsupported Media Type: request must be JSON"}), 415

        data = request.get_json()
        address = data.get('address')

        if not address:
            return jsonify({'error': 'Missing address'}), 400

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
        print("✅ Full ATTOM JSON:", json.dumps(prop, indent=2))

        building = prop.get('building', {})
        rooms = building.get('rooms', {})
        size = building.get('size', {})
        parking = building.get('parking', {})
        summary = building.get('summary', {})
        interior = building.get('interior', {})
        construction = building.get('construction', {})

        # Basic Fields
        beds = rooms.get('beds') or 'N/A'
        baths = rooms.get('bathstotal') or 'N/A'
        sqft = size.get('universalsize') or size.get('grosssize') or size.get('livingsize') or 'N/A'
        year_built = building.get('yearbuilt') or prop.get('summary', {}).get('yearbuilt') or 'N/A'

        # Extra Fields
        garage_type = parking.get('garagetype') or 'N/A'
        parking_spaces = parking.get('prkgSpaces') or 'N/A'
        architecture_style = summary.get('archStyle') or 'N/A'
        basement_type = interior.get('bsmttype') or 'N/A'
        basement_size = interior.get('bsmtsize') or 'N/A'
        cooling_type = building.get('utilities', {}).get('coolingtype') or 'N/A'
        heating_type = building.get('utilities', {}).get('heatingtype') or 'N/A'
        property_class = summary.get('bldgType') or 'N/A'

        print("✅ Extracted Data:")
        print(f"Beds: {beds}, Baths: {baths}, SqFt: {sqft}, Year Built: {year_built}")
        print(f"Garage: {garage_type}, Parking Spaces: {parking_spaces}")
        print(f"Architecture: {architecture_style}, Basement: {basement_type} - {basement_size}")
        print(f"Cooling: {cooling_type}, Heating: {heating_type}, Class: {property_class}")

        return jsonify({
            'beds': beds,
            'baths': baths,
            'sqft': sqft,
            'year_built': year_built,
            'garage_type': garage_type,
            'parking_spaces': parking_spaces,
            'architecture_style': architecture_style,
            'basement_type': basement_type,
            'basement_size': basement_size,
            'cooling_type': cooling_type,
            'heating_type': heating_type,
            'property_class': property_class
        })

    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
