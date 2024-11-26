import os
from enum import StrEnum
import requests
import pandas as pd


class FMPEndpoint(StrEnum):
    SEARCH = 'search?query=-TICKER-'
    TICKER_SEARCH = 'search-ticker?query=-TICKER-'
    NAME_SEARCH = 'search-name?query=-TICKER-'
    LIST_ALL_STOCKS = 'stock/list'
    LIST_ALL_ETFS = 'etf/list'
    LIST_BY_EXCHANGE = 'symbol/-EXCHANGE-'
    COMPANY_DATA = 'profile/-TICKER-'
    MARKET_CAP = 'market-capitalization/-TICKER-'
    COMPANY_LOGO = 'image-stock/-TICKER-'
    STOCK_QUOTE = 'quote/-TICKER-'
    STOCK_SHORT_QUOTE = 'quote-short/-TICKER-'
    HISTORICAL_QUOTE = 'stock-price-change/-TICKER-'
class FMPController:

    def __init__(self):
        self.basic_url = 'https://financialmodelingprep.com/api/v3/'
        self.api_key = os.environ.get('FMP_API_KEY')

    def get_final_url(self, url:str):
        return url + '?apikey=' + self.api_key

    def get_top_500_US_stocks(self) -> dict:
        url = self.basic_url + FMPEndpoint.LIST_BY_EXCHANGE
        url_nyse = url.replace('-EXCHANGE-', 'NYSE')
        url_nyse = self.get_final_url(url_nyse)
        response_nyse = requests.get(url_nyse)
        url_nasdaq = url.replace('-EXCHANGE-', 'NASDAQ')
        url_nasdaq = self.get_final_url(url_nasdaq)
        response_nasdaq = requests.get(url_nasdaq)
        nyse_df = pd.DataFrame(response_nyse.json())
        nasdaq_df = pd.DataFrame(response_nasdaq.json())
        nyse_df = nyse_df[['name','symbol', 'marketCap']]
        nasdaq_df = nasdaq_df[['name','symbol', 'marketCap']]
        all_us_stock_df = pd.concat([nyse_df, nasdaq_df])
        all_us_stock_df_sorted = all_us_stock_df.sort_values(by='marketCap', ascending=False)
        top_500_us_stocks = all_us_stock_df_sorted.head(500)
        return top_500_us_stocks.to_dict(orient='records')

    def get_all_etf(self) -> dict:
        url = self.basic_url + FMPEndpoint.LIST_ALL_ETFS
        url = self.get_final_url(url)
        response = requests.get(url)
        etfs_df = pd.DataFrame(response.json())
        etfs_df = etfs_df[['symbol','name']]
        return etfs_df.to_dict(orient='records')

    def get_stock_quote(self, symbol:str) -> dict:
        url = self.basic_url + FMPEndpoint.STOCK_QUOTE
        url = url.replace('-TICKER-', symbol)
        url = self.get_final_url(url)
        response = requests.get(url)
        return response.json()

    def get_stock_short_quote(self, symbol:str) -> dict:
        url = self.basic_url + FMPEndpoint.STOCK_SHORT_QUOTE
        url = url.replace('-TICKER-', symbol)
        url = self.get_final_url(url)
        response = requests.get(url)
        return response.json()

    def get_stock_current_price(self, symbol:str) -> dict:
        url = self.basic_url + FMPEndpoint.STOCK_SHORT_QUOTE
        url = url.replace('-TICKER-', symbol)
        url = self.get_final_url(url)
        response = requests.get(url)
        response = response.json()[0]
        return response['price']

    def get_stock_historical_quote(self, symbol:str) -> dict:
        url = self.basic_url + FMPEndpoint.HISTORICAL_QUOTE
        url = url.replace('-TICKER-', symbol)
        url = self.get_final_url(url)
        response = requests.get(url)
        response = response.json()[0]
        return response

    def get_stock_data(self, symbol:str) -> dict:
        url = self.basic_url + FMPEndpoint.COMPANY_DATA
        url = url.replace('-TICKER-', symbol)
        url = self.get_final_url(url)
        response = requests.get(url)
        return response.json()

# print(FMP().get_stock_historical_quote(symbol='AAPL'))