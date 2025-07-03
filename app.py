from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)
ATTOM_KEY = 'ada28deedfc084dcea40ac71125d3a6e'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])
def lookup():
    addr = request.json.get('address')
    res = requests.get(
        'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail',
        params={'address1': addr},
        headers={
            'Accept': 'application/json',
            'APIKey': ATTOM_KEY
        }
    )
    if res.status_code == 200:
        prop = res.json().get('property', [{}])[0]
        s = prop.get('property', {}).get('structure', {})
        return jsonify({
            'beds': s.get('bedrooms'),
            'baths': s.get('bathrooms'),
            'sqft': s.get('finishedAreaTotal'),
            'year_built': s.get('yearBuilt')
        })
    return jsonify({'error': 'No data found'}), 404

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

