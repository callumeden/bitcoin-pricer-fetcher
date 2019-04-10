import requests
import datetime
import functools
import csv
import ntpath

class PriceFetcher:

	def __init__(self):
		self.price_data = {}
		self.gbp_iso = 'GBP'
		self.usd_iso = 'USD'
		self.eur_iso = 'EUR'
		self.coindesk_historic_endpoint = 'https://api.coindesk.com/v1/bpi/historical/close.json'


	def write_csv_with_price_data(self, file_path):
		file_name = ntpath.basename(file_path)

		print('do csv for file path', file_path)
		with open(file_path, 'r') as in_file:
			with open('./output/' + file_name +'-price-data', 'w') as out_file:

				reader = csv.reader(in_file)
				writer = csv.writer(out_file)

				for block in reader:
					price = self.get_prices_for_block(block)
					block.append(price[self.gbp_iso])
					block.append(price[self.usd_iso])
					block.append(price[self.eur_iso])
					writer.writerow(block)


	def get_prices_for_block(self, block):
		block_time = int(block[2])
		gbp_price = self.fetch_price_for_epoch_time(block_time, self.gbp_iso)
		usd_price = self.fetch_price_for_epoch_time(block_time, self.usd_iso)
		eur_price = self.fetch_price_for_epoch_time(block_time, self.eur_iso)

		return {self.gbp_iso: gbp_price, self.usd_iso: usd_price, self.eur_iso: eur_price}

	def timestmap_to_date_string(self, date):
		return date.strftime('%Y-%m-%d')

	def fetch_price_for_epoch_time(self, epoch_time, currency):
		block_date = datetime.datetime.fromtimestamp(epoch_time)
		block_date_day_only =  self.timestmap_to_date_string(block_date)
		
		if block_date_day_only not in self.price_data:
			self.populate_data(block_date)

		return self.get_price_in_currency(block_date_day_only, currency)

	def get_price_in_currency(self, day, currency):
		if day not in self.price_data:
			print('ERROR: could not get data for day', day)
			return 0

		price_data_for_day = self.price_data[day]

		if currency not in price_data_for_day:
			print('ERROR: Could not get data in currency {} for day {}'.format(currency, day))
			return 0

		return price_data_for_day[currency]

	def fetch_price_rate_for_dates(self, date_from, date_to, currency):

		date_from_str = self.timestmap_to_date_string(date_from)
		date_to_str = self.timestmap_to_date_string(date_to)

		request_with_props = self.coindesk_historic_endpoint + '?start={}&end={}&currency={}'.format(date_from_str, date_to_str, currency)

		response = requests.get(request_with_props)

		if response.status_code != 200:
			print('no price data for date', date_from)
			return {}


		return response.json()['bpi']

	def populate_data(self, date):
		"""
		Fetches price data for all 3 currencies for current date + 5 days following
		"""
		prefetch_days = 500

		fetch_until = date + datetime.timedelta(days=prefetch_days)
		print('fetching data for date begining {} until {}'.format(date, fetch_until))

		gbp_prices = self.fetch_price_rate_for_dates(date, fetch_until, 'GBP')
		usd_prices = self.fetch_price_rate_for_dates(date, fetch_until, 'USD')
		eur_prices = self.fetch_price_rate_for_dates(date, fetch_until, 'EUR')

		print('GBP', gbp_prices)
		print('USD', usd_prices)
		print('EUR', eur_prices)

		for day in range(prefetch_days + 1):
			date_index = date + datetime.timedelta(days=day)
			date_index_str = self.timestmap_to_date_string(date_index)

			currency_values = {
				self.gbp_iso : gbp_prices.get(date_index_str, 0),
				self.usd_iso : usd_prices.get(date_index_str, 0),
				self.eur_iso : eur_prices.get(date_index_str, 0)
			}

			self.price_data[date_index_str] = currency_values

