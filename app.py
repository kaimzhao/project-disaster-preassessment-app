import json
import os
import pandas as pd
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import helper
from external_api import google_api, zillow_api

# Constant inputs
# Note to run this alpha, you need to have Google Cloud API and Zillow API keys. 
# Modify the folder path 
UPLOAD_FOLDER = 'static/photos/'
API_KEY = pd.read_csv('/Users/kaizhao/Documents/project_API/google_api.csv', header=None).loc[0,0]
PANOSRC = "https://maps.googleapis.com/maps/api/js?key=" + API_KEY + "&callback=initPano"

# Initiate Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#--------------------------------------
# uploader.html
@app.route('/')
def index():
    return render_template('uploader.html')

# address.html
@app.route('/uploader', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        f.save(filename)
        lat, long = helper.get_lat_long(f)
        addresses = google_api.get_address(lat, long)
        return  render_template(
            'addresses.html',
            img_file=filename,
            lat=lat,
            long=long,
            addresses=addresses)

# report.html
@app.route('/report', methods=['POST'])
def report():
	lat = request.form.get('lat')
	long = request.form.get('long')
	img_file = request.form.get('img_file')

	damage_type = google_api.get_damage_type(img_file)

	address_str = request.form.get('address')
	address = None
	if address_str and address_str != 'none':
		address = json.loads(address_str.replace('\'', '\"'))
		lat, long = address['lat'], address['lng']
		property_info, chart_url = zillow_api.get_zillow_info(address['street_number'], address['zip_code'])
	else:
		street_address = request.form.get('street_address')
		zip_code = request.form.get('zipcode')
		if not street_address or not zip_code :
			return 'yo you need to type in the street_address and zipcode'

		property_info, chart_url = zillow_api.get_zillow_info(street_address, zip_code)

	return render_template(
		'report.html', 
		property_info=property_info,
		damage_type=damage_type,
		img_file=img_file,
		chart_url=chart_url,
		lat=lat,
		long=long,
		full_address=(address or {}).get('full_address'),
		panoSRC = PANOSRC
	)

if __name__ == '__main__':
    app.run(debug=True)
