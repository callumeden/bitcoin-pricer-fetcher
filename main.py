import requests
import datetime
import functools
import csv

coindesk_historic_endpoint = 'https://api.coindesk.com/v1/bpi/historical/close.json'
data_history_start_date = '2010-07-17'

price_data = {}
GBP_ISO = 'GBP'
USD_ISO = 'USD'
EUR_ISO = 'EUR'

def do_csv(file_path):
	with open(file_path, 'r') as in_file:
		with open('./output/' + file_path, 'w') as out_file:

			reader = csv.reader(in_file)
			writer = csv.writer(out_file)

			for block in reader:
				price = get_prices_for_block(block)
				block.append(price[GBP_ISO])
				block.append(price[USD_ISO])
				block.append(price[EUR_ISO])
				writer.writerow(block)
	

def get_prices_for_block(block):
	block_time = int(block[2])
	gbp_price = fetch_price_for_epoch_time(block_time, GBP_ISO)
	usd_price = fetch_price_for_epoch_time(block_time, USD_ISO)
	eur_price = fetch_price_for_epoch_time(block_time, EUR_ISO)

	return {GBP_ISO: gbp_price, USD_ISO: usd_price, EUR_ISO: eur_price}

def timestmap_to_date_string(date):
	return date.strftime('%Y-%m-%d')

def fetch_price_for_epoch_time(epoch_time, currency):
	block_date = datetime.datetime.fromtimestamp(epoch_time)
	block_date_day_only =  timestmap_to_date_string(block_date)
	
	if block_date_day_only not in price_data:
		populate_data(block_date)

	return get_price_in_currency(block_date_day_only, currency)

def get_price_in_currency(day, currency):
	if day not in price_data:
		print('ERROR: could not get data for day', day)
		return 0

	price_data_for_day = price_data[day]

	if currency not in price_data_for_day:
		print('ERROR: Could not get data in currency {} for day {}'.format(currency, day))
		return 0

	return price_data_for_day[currency]

def fetch_price_rate_for_dates(date_from, date_to, currency):

	date_from_str = timestmap_to_date_string(date_from)
	date_to_str = timestmap_to_date_string(date_to)

	request_with_props = coindesk_historic_endpoint + '?start={}&end={}&currency={}'.format(date_from_str, date_to_str, currency)

	response = requests.get(request_with_props)

	if response.status_code != 200:
		print('no price data for date', date_from)
		return {}


	return response.json()['bpi']

def populate_data(date):
	"""
	Fetches price data for all 3 currencies for current date + 5 days following
	"""
	prefetch_days = 5

	fetch_until = date + datetime.timedelta(days=prefetch_days)
	print('fetching data for date begining {} until {}'.format(date, fetch_until))

	gbp_prices = fetch_price_rate_for_dates(date, fetch_until, 'GBP')
	usd_prices = fetch_price_rate_for_dates(date, fetch_until, 'USD')
	eur_prices = fetch_price_rate_for_dates(date, fetch_until, 'EUR')

	print('GBP', gbp_prices)
	print('USD', usd_prices)
	print('EUR', eur_prices)

	for day in range(prefetch_days + 1):
		date_index = date + datetime.timedelta(days=day)
		date_index_str = timestmap_to_date_string(date_index)

		currency_values = {
			GBP_ISO : gbp_prices.get(date_index_str, 0),
			USD_ISO : usd_prices.get(date_index_str, 0),
			EUR_ISO : eur_prices.get(date_index_str, 0)
		}

		price_data[date_index_str] = currency_values

