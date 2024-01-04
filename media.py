# -*- coding: utf-8 -*-
import talib
import pandas
from datetime import datetime, date, timedelta
from colorama import Fore

from binance.client import Client
from binance.client import BinanceAPIException
import yaml


def get_api_key():
    with open('settings.yaml', 'r') as f:
        doc = yaml.safe_load(f)
    return str(doc['ENVIROMENTS']['COMMON']['API_KEY'])


def get_api_secret():
    with open('settings.yaml', 'r') as f:
        doc = yaml.safe_load(f)
    return str(doc['ENVIROMENTS']['COMMON']['API_SECRET'])


def get_ema(symbol, interval, length, client):
    klines = client.get_klines(symbol=symbol, interval=interval)
    print("Klines: "+str(klines))
    closes = [float(entry[4]) for entry in klines]
    return sum(closes[-length:]) / length


client = Client(get_api_key(), get_api_secret())
#Client = Spot(get_api_key(),get_api_secret())

symbol = "ADA"
MARKET = "ADAFDUSD"

#lista = client.get_historical_klines("ADA" + "FDUSD", Client.KLINE_INTERVAL_5MINUTE,
#                                             "60 minute ago UTC")
#


ema = get_ema(MARKET, Client.KLINE_INTERVAL_5MINUTE, 5, client)
print("ema5: {0:.4f}".format(ema))

ema = get_ema(MARKET, Client.KLINE_INTERVAL_5MINUTE, 15, client)
print("ema15: {0:.4f}".format(ema))

ema = get_ema(MARKET, Client.KLINE_INTERVAL_5MINUTE, 20, client)
print("ema20: {0:.4f}".format(ema))