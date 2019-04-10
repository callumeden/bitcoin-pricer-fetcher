from price_fetcher import PriceFetcher 
import glob 
import time


data_history_start_date = '2010-07-17'

price_fetcher = PriceFetcher()

csv_path = input("Bitcoin block CSV file name or regex....")

output_path = input("Please provide output path....")

files = glob.glob(csv_path)
print('******************* found files matching regex to be {} **************************'.format(files))

start = time.time()
for file in files:
	print('============================== starting price fetching for file {} ================================='.format(file))
	price_fetcher.write_csv_with_price_data(file, output_path)
	print('============================== completed price fetching for file {} ================================'.format(file))

end = time.time()

print('************** time elapsed = {} *********************'.format(end - start))