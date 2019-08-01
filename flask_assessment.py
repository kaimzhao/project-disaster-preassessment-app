from flask import Flask, render_template
from bs4 import BeautifulSoup
import pandas as pd
import requests

app = Flask(__name__)

# # ---------------------- Google Reverse Geocoding API ------------------------------------

# # ======= Input

# #  Lattitude and Longitude from extracted from picture
# #  Input format: turple or list 
# #  example: (37.79100833333333, -122.40064166666667) or
# #           [37.79100833333333, -122.40064166666667]

# lat_long_raw = (37.79100833333333, -122.40064166666667)

# # number of addresses to return
# n_address = 4

# # API Key
# # !!!SAVE YOUR API AS A CSV ON YOUR LOCAL DRIVE AND READ USING THE CODE BELOW, DO NOT EXPLICITLY USE
# #    API KEY IN THIS BOOK!!!
# api_key = pd.read_csv('/Users/kaizhao/Documents/project_API/google_api.csv', header=None).loc[0,0]

# # Generate Google API url
# # Input: lat_long_raw & api_key (see above section 1.1 for instruction)
# # Output: Google API url

# # ======== API

# def get_url_geocode(lat_long_raw, api_key):
#     lat, long = lat_long_raw
#     latlng = str(lat)+','+str(long)
#     url_geocode = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latlng}&key={api_key}'
#     return url_geocode

# # Generate Google API url
# # Input: lat_long_raw & api_key (see above section 1.1 for instruction)
# #        n_address: integer - number of addresses to return
# # Output: list of dictionary of addresses


# def get_address(lat_long_raw, api_key, n_address):
    
#     url = get_url_geocode(lat_long_raw, api_key)

#     res = requests.get(url)
#     if res.status_code == 200:
#         #print(f'Status code: {res.status_code}')
#         res_jas = res.json()
    
#         address_list = []
#         for i in range(n_address):
#             address={}
#             address['full_address'] = res_jas['results'][i]['formatted_address']
#             address['street_number'] = address['full_address'].split(', ')[0]
#             address['city'] = address['full_address'].split(', ')[1]
#             address['state'] = address['full_address'].split(', ')[2].split(' ')[0]
#             address['zip_code'] = address['full_address'].split(', ')[2].split(' ')[1]
#             address['lat'] = res_jas['results'][i]['geometry']['location']['lat']
#             address['lng'] = res_jas['results'][i]['geometry']['location']['lng']
#             address['place_id'] = res_jas['results'][i]['place_id']
#             address_list.append(address)
#     else:
#         print('Unexpected error: Check latitude, longitude format and Api Key')
    
#     return address_list

# # ======= USER SELECT and VALIDATE ADDRESS
# address_list = get_address(lat_long_raw, api_key, n_address)

# # allow the user to validate the 4 addresses output by the reverse geocoding: option in 0-3
# # if none of the addressed match (option == 4), user need to manually input address
# # input outside 0-4 will lead to an ERROR message

# def address_select():
#     n = None
#     while n not in range (5):
#         n = int(input('Selection: '))
#         if n in range(4):
#             address = address_list[n]['full_address']
#             print(address)
#             return address
#         elif n == 4:
#             street_number = input('Input Street Address: ')
#             city = input('Input city: ')
#             state = input('Input State: ')
#             zip_code = input('Input zip code: ')
#             address = street_number + ', ' + city + ', ' + state + ' ' + zip_code 
#             print(address)
#             return address
#         else:
#             print('Please input valide selection')

# address = address_select()

# # ------------------ End of Google Reverse Geocoding API ---------------------------------










address = '333 Fletcher Dr, Atherton, CA 94027, USA'



# -------------------------- START OF ZILLOW API -----------------------------------------
# zillow web service API
ZWSID = pd.read_csv('/Users/kaizhao/Documents/project_API/zillow_api.csv', header=None).loc[0,0]

# Generate street address and zip code input based on validated google reverse geocoding
street_address = address.split(', ')[0].replace(' ', '+')
zip_code = address.split(', ')[2].split(' ')[1]


# Generate api url based on the street address and zip code above
z_info_url = f'http://www.zillow.com/webservice/GetDeepSearchResults.htm?\
zws-id={ZWSID}&address={street_address}&citystatezip={zip_code}'

# collecting property information
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

# ------------------------- END of Zillow API -----------------------------------------------

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', property_info=property_info)

if __name__ == '__main__':
    app.run(debug=True)
