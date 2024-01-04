# import defi.defi_tools as dft
from binance.client import Client
from binance.client import BinanceAPIException
from coinbase.wallet.client import Client as Cl
from coinbase.wallet.error import TwoFactorRequiredError
import yaml

MONEDA = "FDUSD"
def get_api_key():
    with open('settings.yaml', 'r') as f:
        doc = yaml.safe_load(f)
    return str(doc['ENVIROMENTS']['COMMON']['API_KEY'])


def get_api_secret():
    with open('settings.yaml', 'r') as f:
        doc = yaml.safe_load(f)
    return str(doc['ENVIROMENTS']['COMMON']['API_SECRET'])


client = Client(get_api_key(), get_api_secret())

clientCoinbase = Cl('tzvlla9a7rhgahJR', '1982Tino$')



def getPrecio(ticker) -> float:
    try:
        lista = client.get_historical_klines(ticker + MONEDA, Client.KLINE_INTERVAL_1HOUR, "60 minute ago UTC")
        valor = float(lista[len(lista) - 1][4])
        valorAnterior = float(lista[len(lista) - 2][4])
        variacion = ((valor - valorAnterior) / valorAnterior) * 100
        return [valor, variacion]

        # return float(client.get_avg_price(symbol=ticker + 'USDT')['price'])
    except (BinanceAPIException):
        try:
            # return float(dft.pcsTokenInfo(ticker)['price'])
            return float(0)
        except Exception:
            return 0


def getPrecioCoinbase(ticker) -> float:
    try:
        precioS = clientCoinbase.get_buy_price(currency_pair=ticker+'-USD')['amount']
        return float(precioS)

    except TwoFactorRequiredError:
        try:
            # return float(dft.pcsTokenInfo(ticker)['price'])
            return float(0)
        except Exception:
            return 0


def getPrecio5min(ticker) -> float:
    try:
        lista = client.get_historical_klines(ticker + MONEDA, Client.KLINE_INTERVAL_5MINUTE,
                                             "60 minute ago UTC")
        valor = float(lista[len(lista) - 2][4])
        precioActual = float(lista[len(lista) - 1][4])
        openUltimo = float(lista[len(lista) - 2][1])
        valorAnterior = float(lista[len(lista) - 3][4])
        openAnterior = float(lista[len(lista) - 3][1])
        dif = (valor - openUltimo)
        variacion = (dif / valorAnterior) * 100
        print(" Ultimo valor de cierre: " + str(valor))
        print(" Ultimo valor de apertura: " + str(openUltimo))
        print(" Ante ultimo valor de cierre: " + str(valorAnterior))
        print(" Ante ultimo valor de apertura: " + str(openAnterior))
        print(" Variacion %: " + str(variacion))
        return [precioActual, variacion]

    except (BinanceAPIException):
        try:
            # return float(dft.pcsTokenInfo(ticker)['price'])
            return float(0)
        except (Exception):
            return 0


def getPrecio5minVol(ticker) -> float:
    try:

        lista = client.get_historical_klines(ticker + MONEDA, Client.KLINE_INTERVAL_5MINUTE,
                                             "60 minute ago UTC")
        tam = len(lista)
        valor = float(lista[tam - 2][4])
        precioActual = float(lista[tam - 1][4])
        openUltimo = float(lista[tam - 2][1])
        valorAnterior = float(lista[tam - 3][4])
        openAnterior = float(lista[tam - 3][1])
        dif = (valor - openUltimo)
        variacion = (dif / valorAnterior) * 100

        volumen = float(lista[tam - 2][5])

        # print(" Ultimo valor de cierre: "+str(valor))
        # print(" Ultimo valor de apertura: "+str(openUltimo))
        # print(" Ante ultimo valor de cierre: "+str(valorAnterior))
        # print(" Ante ultimo valor de apertura: "+str(openAnterior))
        # print(" Variacion %: "+str(variacion))
        return [precioActual, variacion, volumen]

    except BinanceAPIException:
        try:
            # return float(dft.pcsTokenInfo(ticker)['price'])
            return float(0)
        except (Exception):
            return 0

# Devuelve el valor de volumen y la variacion de los ultimos dos periodos en una lista


def getVolumen(ticker) -> list:
    try:
        lista = client.get_historical_klines(ticker + MONEDA, Client.KLINE_INTERVAL_5MINUTE, "30 minute ago UTC")

        variacion = ((float(lista[5][5]) - float(lista[4][5])) / float(lista[4][5])) * 100
        return [float(lista[5][5]), variacion]
    except BinanceAPIException:
        try:
            # return float(dft.pcsTokenInfo(ticker)['price'])
            return float(0)
        except Exception:
            return 0


def helper_precio(ticker, valor):
    if ticker == "BTC":
        DECIMALES_PRECIO = 2
    elif ticker == "SOL":
        DECIMALES_PRECIO = 2
    else:  # Matic and ada
        DECIMALES_PRECIO = 4

    return round(valor, DECIMALES_PRECIO)


def helper_cantidad(ticker, cantidad):
    if ticker == "BTC":
        DECIMALES_CANT = 5
    elif ticker == "SOL":
        DECIMALES_CANT = 2
    else:  # Matic and ada
        DECIMALES_CANT = 1
    return round(float(cantidad), DECIMALES_CANT)
