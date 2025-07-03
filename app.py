from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

# Replace this with your actual ATTOM API key or use Render env variable
ATTOM_KEY = os.environ.get('ATTOM_KEY', 'YOUR_API_KEY_HERE')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])
def lookup():
    data = request.get_json()
    address = data.get('address')

    if not address:
        return jsonify({'error': 'Missing address'}), 400

    res = requests.get(
        'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/address',
        params={'fulladdress': address},
        headers={
            'Accept': 'application/json',
            'apikey': ATTOM_KEY
        }
    )

    if res.status_code != 200:
        print(f"ATTOM ERROR: {res.status_code} - {res.text}")
        return jsonify({'error': 'Failed to retrieve data'}), 500

    results = res.json()
    props = results.get('property', [])
    if not props:
        return jsonify({'error': 'No data found'}), 404

    prop = props[0]
    struct = prop.get('building', {})

    return jsonify({
        'beds': struct.get('rooms', {}).get('beds'),
        'baths': struct.get('rooms', {}).get('baths'),
        'sqft': struct.get('size', {}).get('universalsize'),
        'year_built': struct.get('yearbuilt')
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
