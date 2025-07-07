from flask import Flask, request, render_template
import requests
import os
import json

app = Flask(__name__)

ATTOM_KEY = os.environ.get('ATTOM_KEY', 'ada28deedfc084dcea40ac71125d3a6e')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])
def lookup():
    address = request.form.get('address')

    if not address:
        return render_template('index.html', error="Missing address")

    address_parts = address.split(",", 1)
    address1 = address_parts[0].strip()
    address2 = address_parts[1].strip() if len(address_parts) > 1 else ''

    res = requests.get(
        'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail',
        params={'address1': address1, 'address2': address2},
        headers={'Accept': 'application/json', 'apikey': ATTOM_KEY}
    )

    if res.status_code != 200:
        return render_template('index.html', error=f"ATTOM error: {res.status_code}")

    results = res.json()
    props = results.get('property', [])
    if not props:
        return render_template('index.html', error="No property data found")

    prop = props[0]
    building = prop.get('building', {})
    rooms = building.get('rooms', {})
    size = building.get('size', {})
    interior = building.get('interior', {})
    parking = building.get('parking', {})
    summary = building.get('summary', {})
    prop_summary = prop.get('summary', {})

    # Extract fields with fallbacks
    data = {
        'beds': rooms.get('beds') or prop_summary.get('beds_count') or 'N/A',
        'baths': rooms.get('bathstotal') or prop_summary.get('baths_count') or 'N/A',
        'sqft': size.get('universalsize') or size.get('grosssize') or prop_summary.get('building_area') or 'N/A',
        'year_built': building.get('yearbuilt') or prop_summary.get('yearbuilt') or 'N/A',
        'garage_type': parking.get('garagetype', 'N/A'),
        'parking_spaces': parking.get('prkgSpaces', 'N/A'),
        'arch_style': summary.get('archStyle', 'N/A'),
        'basement_type': interior.get('bsmttype', 'N/A'),
        'basement_size': interior.get('bsmtsize', 'N/A'),
        'cooling': interior.get('cooling', 'N/A'),
        'heating': interior.get('heating', 'N/A'),
        'property_class': summary.get('bldgType') or prop_summary.get('propclass') or 'N/A'
    }

    # Logging
    print("🔎 RAW JSON:\n", json.dumps(prop, indent=2))
    for k, v in data.items():
        print(f"✅ {k.replace('_', ' ').title()}: {v}")

    return render_template('index.html', address=address, **data)

if __name__ == '__main__':
    app.run(debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
