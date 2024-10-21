import os
from enum import StrEnum
import requests
import pandas as pd
import time
from datetime import datetime
class FMPEndpoint(StrEnum):
    PING = 'ping'
    LIST_ALL_COINS = 'coins/list'
    COIN_PRICE = 'simple/price?ids=-COIN_ID-&vs_currencies=usd'

class Coingecko:
    def __init__(self):
        self.basic_url = 'https://api.coingecko.com/api/v3/'
        self.api_key = os.environ.get('COINGECKO_API_KEY')
        self.headers = {"x-cg-demo-api-key": self.api_key,
                        "accept": "application/json"}


    def get_ping(self):
        url = self.basic_url + FMPEndpoint.PING
        response = requests.get(url, headers=self.headers)
        return response.ok
    
    def get_all_coins(self):
        url = self.basic_url + FMPEndpoint.LIST_ALL_COINS
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_coin_id_by_name(self, name:str):
        url = self.basic_url + FMPEndpoint.LIST_ALL_COINS
        response = requests.get(url, headers=self.headers)
        all_coins_response = response.json()
        data_dict = {coin['name'].lower(): coin for coin in all_coins_response}
        coin_result = data_dict.get(name.lower())
        return coin_result['id']

    def get_current_coin_price_by_name(self, name:str):
        url = self.basic_url + FMPEndpoint.COIN_PRICE
        coin_id = self.get_coin_id_by_name(name)
        url = url.replace('-COIN_ID-', coin_id)
        response = requests.get(url, headers=self.headers)
        data = {'name': name, 'price': response.json()[f'{coin_id}']['usd'], 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'timestamp': time.time()}
        return data
print(Coingecko().get_current_coin_price_by_name('bitcoin'))