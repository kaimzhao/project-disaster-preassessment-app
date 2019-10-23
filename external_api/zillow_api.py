import pandas as pd
import requests
from bs4 import BeautifulSoup

# Constant inputs
# Note to run this alpha, you need to have Zillow API keys. 
# Modify the folder path 
ZWSID = pd.read_csv('/Users/kaizhao/Documents/project_API/zillow_api.csv', header=None).loc[0,0]


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

