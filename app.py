import os
import io
import json
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from bs4 import BeautifulSoup
import pandas as pd
import requests
from google.cloud import vision
from google.cloud.vision import types
from google.oauth2 import service_account

# Constant inputs
# Note to run this alpha, you need to have Google Cloud API and Zillow API keys. 
# Modify the folder path 
UPLOAD_FOLDER = 'static/photos/'
API_KEY = pd.read_csv('/Users/kaizhao/Documents/project_API/google_api.csv', header=None).loc[0,0]
ZWSID = pd.read_csv('/Users/kaizhao/Documents/project_API/zillow_api.csv', header=None).loc[0,0]
PANOSRC = "https://maps.googleapis.com/maps/api/js?key=" + API_KEY + "&callback=initPano"
GOOGLE_SERVICE_KEY = '/Users/kaizhao/Documents/project_API/GA Student Project-f9c80f2c5b6c.json'
N_ADDRESS = 4

# Initiate Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Open Image
def get_exif(img):
    exif = Image.open(img)._getexif()

    if exif is not None:
        for key, value in exif.items():
            name = TAGS.get(key, key)
            exif[name] = exif.pop(key)

        if 'GPSInfo' in exif:
            for key in exif['GPSInfo'].keys():
                name = GPSTAGS.get(key, key)
                exif['GPSInfo'][name] = exif['GPSInfo'].pop(key)

    return exif or {}

#Extract Lat Lng and Convert to Decimals
def get_decimal_coordinates(info):
    for key in {'GPSLatitude', 'GPSLongitude'}:
        if key in info and key + 'Ref' in info:
            new_key = 'lat' if key == 'GPSLatitude' else 'long'
            e = info[key]
            ref = info[key + 'Ref']
            info[new_key] = ( e[0][0]/e[0][1] +
                          e[1][0]/e[1][1] / 60 +
                          e[2][0]/e[2][1] / 3600
                        ) * (-1 if ref in {'S','W'} else 1)

    if 'lat' in info and 'long' in info:
        return info['lat'], info['long']
    return None, None


def get_lat_long(img):
    return get_decimal_coordinates(get_exif(img).get('GPSInfo') or {})


# # ------------------------------ Google Reverse Geocoding API ---------------------------------

def get_url_geocode(lat, long):
    '''
        Generate Google API url
        Input: lat_long_raw & api_key (see above section 1.1 for instruction)
        Output: Google API url
    '''
    latlng = str(lat)+','+str(long)
    url_geocode = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latlng}&key={API_KEY}'
    return url_geocode

def get_address(lat, long):
    '''
        Generate Google API url
        Input: lat_long_raw & api_key
        Output: list of dictionary of addresses
    '''
    
    url = get_url_geocode(lat, long)

    res = requests.get(url)
    if res.status_code == 200:
        #print(f'Status code: {res.status_code}')
        res_jas = res.json()
    
        address_list = []
        for i in range(N_ADDRESS):
            address={}
            address['full_address'] = res_jas['results'][i]['formatted_address']
            address['street_number'] = address['full_address'].split(', ')[0]
            address['city'] = address['full_address'].split(', ')[1]
            address['state'] = address['full_address'].split(', ')[2].split(' ')[0]
            address['zip_code'] = address['full_address'].split(', ')[2].split(' ')[1]
            address['lat'] = res_jas['results'][i]['geometry']['location']['lat']
            address['lng'] = res_jas['results'][i]['geometry']['location']['lng']
            address['place_id'] = res_jas['results'][i]['place_id']
            address_list.append(address)
    else:
        print('Unexpected error: Check latitude, longitude format and Api Key')
    
    return address_list


# --------------------------------- GOOGLE VISION AI ----------------------------------------


def get_damage_type(file_name):
	'''
	    Instantiates a client
		Input: image file by file_name: str
		Output: damage type: str
	'''
	credentials = service_account.Credentials.from_service_account_file(GOOGLE_SERVICE_KEY)
	client = vision.ImageAnnotatorClient(credentials=credentials)

	# Loads the image into memory
	with io.open(file_name, 'rb') as image_file:
	    content = image_file.read()
	image = types.Image(content=content)

	# Obtain the ML annotation
	response = client.web_detection(image = image)
	annotations = response.web_detection

	# damage_type
	damage = set(annotations.best_guess_labels[0].label.split(' '))
	set_fire = {'fire', 'burn', 'smoke','soot'}
	set_flood = {'flood', 'water', 'sink', 'mold','storm','rain'}
	set_earthquake = {'earthquake', 'crack', 'shake','seismic','richter','mercalli'} 

	if bool(set_fire.intersection(damage)):
		damage_type = 'Fire'
	elif bool(set_flood.intersection(damage)):
		damage_type = 'Flood'
	elif bool(set_earthquake.intersection(damage)):
		damage_type = 'Earthquake'
	else:
		damage_type = 'Fail to Classify'

	return damage_type

# -------------------------------------- Zillow API ---------------------------------------------
 
def get_zillow_info(street_address, zip_code):
	'''
		function for obtaining zillow data
		input:
		     street_address: str
		     zip_code: str
		output:
		     property_info: dict  
	'''
	street_address = street_address.replace(' ', '+')

	# Generate api url based on the street address and zip code above
	z_info_url = f'http://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id={ZWSID}&address={street_address}&citystatezip={zip_code}'

	print(z_info_url)

	# Get property information
	res_z_info = requests.get(z_info_url)
	soup = BeautifulSoup(res_z_info.content, ['lxml-xml'])
	property_info = {}
	property_info['zpid'] = soup.find('zpid').text
	property_info['current_value'] = int(soup.find('amount').text)
	property_info['last_sold'] = int(soup.find('lastSoldPrice').text)
	property_info['last_sold_date'] = soup.find('lastSoldDate').text
	property_info['property_type'] = soup.find('useCode').text
	property_info['year_built'] = int(soup.find('yearBuilt').text)
	property_info['bedrooms'] = int(soup.find('bedrooms').text)
	property_info['bathrooms'] = float(soup.find('bathrooms').text)
	property_info['sqft'] = int(soup.find('finishedSqFt').text)
	property_info['lot_size'] = int(soup.find('lotSizeSqFt').text)

	# ZillowChart API parameters
	unit = 'dollar' # 'percent' or 'dollar'
	duration = '1year' # '1year', '5year', or '10year'. default = '1year'
	zpid = property_info['zpid'] # from section 3.2

	# ZillowChart ZPI
	z_chart_url = f'http://www.zillow.com/webservice/GetChart.htm?zws-id={ZWSID}&unit-type={unit}&zpid={zpid}&width=600&height=300&chartDuratoin={duration}'

	# obtain url to embed in the web-app
	res_z_chart = requests.get(z_chart_url)
	soup = BeautifulSoup(res_z_chart.content, ['lxml-xml'])

	# url for the historical zestimate chart
	chart_url = soup.find('url').text
	return property_info, chart_url

# ------------------------------------------------------------------------------------------------------------------------------
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
        lat, long = get_lat_long(f)
        addresses = get_address(lat, long)
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

	damage_type = get_damage_type(img_file)

	address_str = request.form.get('address')
	address = None
	if address_str and address_str != 'none':
		address = json.loads(address_str.replace('\'', '\"'))
		lat, long = address['lat'], address['lng']
		property_info, chart_url = get_zillow_info(address['street_number'], address['zip_code'])
	else:
		street_address = request.form.get('street_address')
		zip_code = request.form.get('zipcode')
		if not street_address or not zip_code :
			return 'yo you need to type in the street_address and zipcode'

		property_info, chart_url = get_zillow_info(street_address, zip_code)

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
