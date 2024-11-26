import os
from enum import StrEnum
import requests
import pandas as pd
import time
from datetime import datetime
class CoingeckoEndpoint(StrEnum):
    PING = 'ping'
    LIST_ALL_COINS = 'coins/markets?vs_currency=usd'
    COIN_PRICE = 'simple/price?ids=-COIN_ID-&vs_currencies=usd'

class CoingeckoController:
    def __init__(self):
        self.basic_url = 'https://api.coingecko.com/api/v3/'
        self.api_key = os.environ.get('COINGECKO_API_KEY')
        self.headers = {"x-cg-demo-api-key": self.api_key,
                        "accept": "application/json"}


    def get_ping(self):
        url = self.basic_url + CoingeckoEndpoint.PING
        response = requests.get(url, headers=self.headers)
        return response.ok

    def get_top_100_coins(self):
        url = self.basic_url + CoingeckoEndpoint.LIST_ALL_COINS
        response = requests.get(url, headers=self.headers)
        coins_df = pd.DataFrame(response.json())
        coins = coins_df[['name','symbol', 'image', 'market_cap']]
        sorted_coins = coins.sort_values(by='market_cap', ascending=False)
        top_100_us_stocks = sorted_coins.head(100)
        return top_100_us_stocks.to_dict(orient='records')

    def get_coin_id_by_name(self, name:str):
        url = self.basic_url + CoingeckoEndpoint.LIST_ALL_COINS
        response = requests.get(url, headers=self.headers)
        all_coins_response = response.json()
        data_dict = {coin['name'].lower(): coin for coin in all_coins_response}
        coin_result = data_dict.get(name.lower())
        return coin_result['id']

    def get_current_coin_price_by_name(self, name:str):
        url = self.basic_url + CoingeckoEndpoint.COIN_PRICE
        coin_id = self.get_coin_id_by_name(name)
        url = url.replace('-COIN_ID-', coin_id)
        response = requests.get(url, headers=self.headers)
        data = {'name': name, 'price': response.json()[f'{coin_id}']['usd'], 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'timestamp': time.time()}
        return data
