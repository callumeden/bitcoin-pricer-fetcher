from price_fetcher import PriceFetcher 
import glob 

data_history_start_date = '2010-07-17'

price_fetcher = PriceFetcher()

csv_path = input("Bitcoin block CSV file name or regex....")

files = glob.glob(csv_path)
print('******************* found files matching regex to be {} **************************'.format(files))

for file in files:
	print('============================== starting price fetching for file {} ================================='.format(file))
	price_fetcher.write_csv_with_price_data(file)
	print('============================== completed price fetching for file {} ================================'.format(file))
