import io
import pandas as pd
import requests
from flask import Flask
from google.cloud import vision
from google.cloud.vision import types
from google.oauth2 import service_account

# Constant inputs
# Note to run this alpha, you need to have Google Cloud API and Zillow API keys. 
# Modify the folder path 
API_KEY = pd.read_csv('/Users/kaizhao/Documents/project_API/google_api.csv', header=None).loc[0,0]
GOOGLE_SERVICE_KEY = '/Users/kaizhao/Documents/project_API/GA Student Project-f9c80f2c5b6c.json'
N_ADDRESS = 4


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

