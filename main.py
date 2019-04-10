from price_fetcher import PriceFetcher 

data_history_start_date = '2010-07-17'

price_fetcher = PriceFetcher()

csv_path = input("Bitcoin block CSV file name....")

print('got csv path', csv_path)

price_fetcher.do_csv(csv_path)