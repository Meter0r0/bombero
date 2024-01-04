#!/usr/bin/env python
### pylint: disable=C0116

import logging.handlers
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
import threading
import time as ti
import dao
import sql
from dao import *
from datetime import datetime
from pyfiglet import Figlet
from precio import *
import time
from binance.enums import *


def get_path_bot():
    with open('settings.yaml', 'r') as f:
        doc = yaml.safe_load(f)
    return str(doc['ENVIROMENTS']['COMMON']['PATH'])


def get_inversion():
    with open('settings.yaml', 'r') as f:
        doc = yaml.safe_load(f)
    return float(doc['ENVIROMENTS']['COMMON']['INVERSION'])


def get_hash_bot():
    with open('settings.yaml', 'r') as f:
        doc = yaml.safe_load(f)
    return str(doc['ENVIROMENTS']['COMMON']['HASH_BOT'])


## LOGGER
def loguear():
    root = logging.getLogger(__name__)
    formatter = logging.Formatter(' %(asctime)s - %(threadName)s - %(funcName)s - %(levelname)s - %(message)s ')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root.setLevel("DEBUG")
    root.addHandler(handler)

    handler1 = logging.FileHandler(get_path_bot() + "/bot.log")
    handler1.setFormatter(formatter)
    root.addHandler(handler1)

    return root


## variables globales
logger = loguear()
stopHilos = False
ALPHA1 = 4
ALPHA2 = 4
ALPHA3 = 4
ALPHA4 = 4

BETA1 = float(1)
BETA2 = float(1)

INVERSIONUSD = get_inversion()
FRECSTATS = 12

# Lista de usuarios que pueden chatear con el bot
usuarios = ['1783707249', '979088442']

## Estadisticas
listaEstadisticas = []
listaStopHilo = []


def es_flotante(variable):
    try:
        float(variable)
        return True
    except:
        return False


def es_entero(variable):
    try:
        int(variable)
        return True
    except:
        return False


# COMANDOS BOT

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, _: CallbackContext) -> None:
    if patovica(update):
        update.message.reply_text("Hola negri")
        help_command(update, _)
        logger.info(str(update))
    else:
        update.message.reply_text("A vos no te conozco.")


def help_command(update: Update, _: CallbackContext) -> None:
    if patovica(update):
        update.message.reply_text('Solo respondo a los siguientes comandos por ahora:\n'
                                  '* cruce <TICKER>\n'
                                 
                                  '\n\n\n'

                                  )


def noentiendo(update: Update, _: CallbackContext) -> None:
    if patovica(update):
        update.message.reply_text("ques se yo, chupala puto. usa /help")


def precio(update: Update, _: CallbackContext) -> None:
    logger.info(
        str(update._effective_user.id) + "-" + update._effective_user.first_name + "--> C: " + update.message.text)
    if patovica(update):
        t = update.message.text.split(' ')

        if len(t) < 2:
            update.message.reply_text("falta indicar el ticker, negri. ")
        else:
            try:
                ticker = t[1].upper()
                valorActual, variacionActual = getPrecio(ticker)

                update.message.reply_text("va negrito: {0:.4f}".format(valorActual) + " ({0:.2f}%)".format(
                    variacionActual) + ", COINBASE: {0:.4f}".format(getPrecioCoinbase(ticker)))

            except BinanceAPIException as e:
                update.message.reply_text(e.message)

    else:
        update.message.reply_text("A vos no te conozco")
        logger.warning("No permitido: " + str(update))


# Con este metodo valido el usuario del mensaje.
def patovica(update: Update) -> bool:
    id = update._effective_user.id
    if str(id) not in usuarios:
        logger.warning(str(update))
        return False
    else:
        return True

## SALDO
def saldo(update: Update, context: CallbackContext) -> None:
    logger.info(
        str(update._effective_user.id) + "-" + update._effective_user.first_name + "--> C: " + update.message.text)
    id_usuario = update._effective_user.id
    try:
        saldo_libre = float(client.get_asset_balance(asset='usdt')['free'])
        saldo_bloqueado = float(client.get_asset_balance(asset='usdt')['locked'])

        update.message.reply_text(
            "negri, el saldo es: {0:.5f} USDT".format(saldo_libre) + " y en ordenes: {0:.4f} USDT".format(
                saldo_bloqueado))

    except BinanceAPIException as e:
        update.message.reply_text("Fallo la consulta de saldo.")
        logger.warning(str(e.message))


saldo_libre = float(0)
saldo_libre_BTC = float(0)


## SALDO
def saldobusd(update: Update, context: CallbackContext) -> None:
    logger.info(
        str(update._effective_user.id) + "-" + update._effective_user.first_name + "--> C: " + update.message.text)
    try:
        saldo_libre_Local = float(client.get_asset_balance(asset=MONEDA)['free'])
        saldo_bloqueado = float(client.get_asset_balance(asset=MONEDA)['locked'])

        update.message.reply_text(
            "negri, el saldo es: {0:.4f} FDUSD".format(saldo_libre_Local) + " y en ordenes: {0:.4f} FDUSD".format(
                saldo_bloqueado))
    except BinanceAPIException as e:
        manda_msj(update, "Fallo la consulta de saldo FDUSD o BTC.", "FDUSD")


def ordenes(update: Update, context: CallbackContext) -> None:
    logger.info(
        str(update._effective_user.id) + "-" + update._effective_user.first_name + "--> C: " + update.message.text)
    id_usuario = update._effective_user.id
    try:

        for item in client.get_open_orders():
            precio = float(item['price'])
            ticker = str(item['symbol'])
            cant = float(item['origQty'])
            print(str(item['side']))

            update.message.reply_text(ticker + ": precio: {0:.4f} FDUSD".format(precio) + " cantidad: {0:.4f}".format(
                cant) + " total: {0:.4f}".format(cant * precio))
        update.message.reply_text("----------")

    except BinanceAPIException as e:
        manda_msj(update, "Fallo la consulta de ordenes a Binance." + e.message, ticker, 0, True)


def reset(update: Update, context: CallbackContext) -> None:
    logger.info(
        str(update._effective_user.id) + "-" + update._effective_user.first_name + "--> C: " + update.message.text)
    comando = update.message.text.split(' ')

    if len(comando) > 2 or len(comando) == 1:
        manda_msj(update, "Con el comando reset se pone en cero. el balance del ticker pasado por param.", comando[1])
        return
    elif len(comando) == 2:
        ticker = comando[1]
        dao.save(ticker, float(0))
        manda_msj(update, "El balance es: {0:.4f}".format(float(0)), ticker)


def renta(update: Update, context: CallbackContext) -> None:
    logger.info(
        str(update._effective_user.id) + "-" + update._effective_user.first_name + "--> C: " + update.message.text)

    id_usuario = update._effective_user.id
    try:
        comando = update.message.text.split(' ')

        if (len(comando) > 3):
            help_command(update, context)
            return
        elif (len(comando) == 3):
            if comando[1] == "c":
                lista_ordenes_cerradas = load_ordenes_cerradas(id_usuario)
                if comando[2] in lista_ordenes_cerradas:
                    update.message.reply_text("Abriendo orden: " + comando[2])
                    lista_ordenes_cerradas.remove(comando[2])
                else:
                    update.message.reply_text("Cerrando orden: " + comando[2])
                    lista_ordenes_cerradas.append(comando[2])
                save_ordenes_cerradas(id_usuario, lista_ordenes_cerradas)

        elif (len(comando) == 2):
            ticker = comando[1].upper()
            count = int(0)
            lista_ordenes_cerradas = load_ordenes_cerradas(id_usuario)
            # print(str(lista_ordenes))

            total = float(0)

            for item in client.get_my_trades(symbol=ticker + MONEDA):
                if (not str(item['orderId']) in lista_ordenes_cerradas) and (item['isBuyer'] == True):
                    count += 1

                    precioCompra = float(item['price'])
                    qty = float(item['qty']) - float(item['commission'])
                    qtyCompra = float(qty)

                    total = total + qtyCompra
                    precioActual = getPrecio(ticker)[0]
                    totalCompra = qtyCompra * precioCompra
                    totalActual = qtyCompra * precioActual
                    ganancia = totalActual - totalCompra

                    time = datetime.datetime.fromtimestamp(item['time'] / 1000).strftime("%d/%m/%Y %H:%m:%S")

                    update.message.reply_text("* " + str(item['orderId']) + " | " + str(time) + "\n"
                                              + "     COMPRA " + printPrecioYCantidad(precioCompra, qtyCompra,
                                                                                      totalCompra)
                                              + "       ACTUAL " + printPrecioYCantidad(precioActual, qtyCompra,
                                                                                        totalActual)
                                              + "       SALDO {0:.2f}".format(ganancia) + " | Var: {0:.2f}%".format(
                        100 * (ganancia) / totalCompra)
                                              )
            update.message.reply_text("**Cantidad Total: {0:.4f}".format(total))
            # save_ordenes_cerradas(id_usuario, lista_ordenes)

    except BinanceAPIException as e:
        manda_msj(update, "Fallo la consulta de ordenes a Binance." + e.message, ticker, 0, True)


def manda_msj(update, msj, ticker, idcompra=0, telegram=False):
    mensaje = ticker + "(" + str(idcompra) + "): " + msj
    logger.info(mensaje)
    if telegram:
        update.message.reply_text(mensaje)


# Stop hilo
def get_stopHilo(nombreHilo):
    if nombreHilo in listaStopHilo:
        listaStopHilo.remove(nombreHilo)
        return True
    else:
        return False


def get_ema(length, klines):
    closes = [float(entry[4]) for entry in klines]
    return sum(closes[-length:]) / length


def worker_bombero(ticker, update) -> None:
    nombreHilo = ticker + "-" + "bomber"
    iteraciones = 0
    global listaEstadisticas
    ema5_old = 0
    ema15_old = 0
    ema20_old = 0

    while True and not stopHilos and not get_stopHilo(nombreHilo):
        iteraciones = iteraciones + 1
        try:
            klines = client.get_klines(symbol=ticker+MONEDA, interval=Client.KLINE_INTERVAL_5MINUTE)
            ema5 =get_ema(5, klines)
            ema15 =get_ema(15, klines)
            ema20 =get_ema(20, klines)

            manda_msj( update, "Ema5: {0:.4f}".format(ema5)+ ", Ema15: {0:.4f}".format(ema15)
                      +", Ema20: {0:.4f}".format(ema20), ticker, 0, True)

            # VEO SI SE CRUZA

            if (ema5_old<ema20_old and ema5>ema20 ) or ( ema20_old<ema5_old and ema20>ema5):
                manda_msj(update, "Cruce de ema 5 y 20", ticker, 0, True)

            # pendiente de la ema15
            pen = (ema15-ema15_old)/ema15_old
            manda_msj(update, "Pendiente ema15: {0:.2f}".format(pen), ticker, 0, True)

            ema5_old = ema5
            ema15_old = ema15
            ema20_old = ema20


        except Exception as ext:
            manda_msj(update, "Algo Fallo. salteo ciclo." + str(ext), ticker, 0, True)

        # Sincroniza tiempo cada 5 minutos y 3 segundos.
        ahora = datetime.now()
        seg = (ahora.second + (ahora.minute * 60) % 300)
        espera = (300 - seg + 2)
        time.sleep(espera)
    update.message.reply_text(" Se paro el hilo: " + nombreHilo)


def estadisticas(update: Update, context: CallbackContext) -> None:
    logger.info(
        str(update._effective_user.id) + "-" + update._effective_user.first_name + "--> C:" + update.message.text)

    global FRECSTATS
    comando = update.message.text.split(' ')
    if (len(comando) == 2):
        update.message.reply_text(" FRECSTATS: " + str(FRECSTATS) + " ----> " + str(int(comando[1])))
        FRECSTATS = int(comando[1])

    update.message.reply_text("Estadisticas:\n" + str(listaEstadisticas))
    return


def printPrecioYCantidad(precio, cantidad, total):
    return "Valor: {0:.4f} ".format(precio) + " | Cant: {0:.4f}".format(cantidad) + " | Total: {0:.4f} ".format(
        total) + "\n"


def posicion(update: Update, context: CallbackContext) -> None:
    logger.info(
        str(update._effective_user.id) + "-" + update._effective_user.first_name + "--> C: " + update.message.text)
    id_usuario = update._effective_user.id
    try:
        t = update.message.text.split(' ')

        if (len(t) >= 3):
            help_command(update, context)
            return
        ticker = t[1].upper()
        r = float(client.get_asset_balance(asset=ticker)['free'])
        valor = r * getPrecio(ticker)[0]
        update.message.reply_text(ticker + ": Cant: {0:.4f} ".format(r) + ", Valor actual: {0:.4f} USDT".format(valor))

    except BinanceAPIException as e:
        manda_msj(update, "Fallo la consulta de ordenes a Binance." + e.message, ticker, 0, True)


def balance(update: Update, context: CallbackContext) -> None:
    logger.info(
        str(update._effective_user.id) + "-" + update._effective_user.first_name + "--> C: " + update.message.text)
    id_usuario = update._effective_user.id
    try:
        t = update.message.text.split(' ')

        if (len(t) >= 3):
            help_command(update, context)
            return
        ticker = t[1].upper()
        cantCartera = float(client.get_asset_balance(asset=ticker)['free'])

        update.message.reply_text(ticker + ": Tenencia actual: {0:.4f} USDT".format(cantCartera * getPrecio(ticker)[0]))

        ## Calculo rentabilidad
        compra = float(0)
        venta = float(0)

        totalCompra = float(0)
        totalVenta = float(0)

        cantCompra = float(0)
        cantVenta = float(0)

        count = int(0)
        cantSaldo = float(0)

        for item in client.get_all_orders(symbol=ticker + 'USDT'):
            if item['status'] == "FILLED":
                count += 1
                # update.message.reply_text(str(item))
                cantVenta = 0
                cantCompra = 0
                cant = 0

                if item['side'] == "BUY":
                    precio = float(item['price'])
                    cant = float(item['origQty'])
                    compra = compra + (precio * cant)
                    cantCompra = cant
                    totalCompra = totalCompra + float(item['cummulativeQuoteQty'])

                else:
                    precio = float(item['price'])
                    cant = float(item['origQty'])
                    venta = venta + (precio * cant)
                    cantVenta = - cant
                    totalVenta = totalVenta + float(item['cummulativeQuoteQty'])

                cantSaldo = cantSaldo + (cantVenta + cantCompra)

                saldito = totalVenta - totalCompra
                # update.message.reply_text("Saldito: {0:.4f}".format(cantSaldo))

        if (cantSaldo >= 5):
            update.message.reply_text("* Cantidad: {0:.4f} ".format(cant) + " Valor: {0:.2f}".format(precio)
                                      + " USDT. Valor: {0:.4f}".format(float(item['cummulativeQuoteQty'])) + " USDT")

            # else: update.message.reply_text(ticker +" "+item['status'])

        totalSaldo = totalVenta - totalCompra
        prop = (totalSaldo / compra) * 100
        update.message.reply_text(
            ticker + ": Ganancia: {0:.4f} USDT".format(totalSaldo) + " ------ {0:.2f}".format(prop) + " %")

    except BinanceAPIException as e:
        manda_msj(update, "Fallo la consulta de ordenes a Binance." + e.message, ticker, 0, True)


def status(update: Update, context: CallbackContext) -> None:
    logger.info(
        str(update._effective_user.id) + "-" + update._effective_user.first_name + "--> C: " + update.message.text)

    t = update.message.text.split(' ')
    id_usuario = update._effective_user.id

    lista_ordenes_cerradas = load_ordenes_cerradas(id_usuario)
    if len(t) >= 2:
        help_command(update, context)
        return
    for item in client.get_account()['balances']:
        cantidad = float(item['free']) + float(item['locked'])
        ticker = str(item['asset'])
        if cantidad > float(0.0001):
            # if (precioActual*cantidad) >10:
            update.message.reply_text(" * " + ticker + " Cantidad: {0:.6f} ".format(cantidad))
            try:
                count = 0

                total = 0
                for item in client.get_my_trades(symbol=ticker + 'USDT'):
                    if (not str(item['orderId']) in lista_ordenes_cerradas) and (item['isBuyer'] == True):
                        count += 1

                        # lista_ordenes.append(str(item['orderId']))

                        # print(str(item))
                        precioCompra = float(item['price'])
                        qty = float(item['qty']) - float(item['commission'])
                        qtyCompra = float(qty)

                        total = total + qtyCompra
                        precioActual = getPrecio(ticker)[0]
                        totalCompra = qtyCompra * precioCompra
                        totalActual = qtyCompra * precioActual
                        ganancia = totalActual - totalCompra

                        time = datetime.datetime.fromtimestamp(item['time'] / 1000).strftime("%d/%m/%Y %H:%m:%S")

                        update.message.reply_text("* " + str(item['orderId']) + " | " + str(time) + "\n"
                                                  + "     COMPRA " + printPrecioYCantidad(precioCompra, qtyCompra,
                                                                                          totalCompra)
                                                  + "       ACTUAL " + printPrecioYCantidad(precioActual, qtyCompra,
                                                                                            totalActual)
                                                  + "       SALDO {0:.2f}".format(ganancia) + " | Var: {0:.2f}%".format(
                            100 * (ganancia) / totalCompra)
                                                  )
                update.message.reply_text("**Cantidad Total: {0:.4f}".format(total))
                # save_ordenes_cerradas(id_usuario, lista_ordenes)

            except BinanceAPIException as e:
                manda_msj(update, "Fallo la consulta de ordenes a Binance." + e.message, ticker, 0, True)


def cruce(update: Update, context: CallbackContext) -> None:
    logger.info(
        str(update._effective_user.id) + "-" + update._effective_user.first_name + "--> C: " + update.message.text)
    comando = update.message.text.split(' ')
    try:
        if len(comando) > 3:
            help_command(update, context)
            return
        elif len(comando) == 2:
            ticker = comando[1].upper()

            update.message.reply_text("Cruce de emas (5, 15, 20): " + ticker)

            threadBombero = threading.Thread(target=worker_bombero, args=(ticker, update), name=ticker)
            threadBombero.start()


    except BinanceAPIException as e:
        manda_msj(update, "Fallo la consulta de ordenes a Binance." + e.message, ticker, 0, True)
def main() -> None:
    f = Figlet(font='slant')
    print(f.renderText('Che bombero'))

    try:
        hash = get_hash_bot()
        updater = Updater(hash)

        logger.info("Iniciando bot bombero")

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))

        ### ordenes

        dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'^precio?', re.IGNORECASE)), precio))
        dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'^saldo?', re.IGNORECASE)), saldo))
        dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'^renta?', re.IGNORECASE)), renta))
        dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'^status?', re.IGNORECASE)), status))

        dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'^busd?', re.IGNORECASE)), saldobusd))

        dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'^reset', re.IGNORECASE)), reset))

        dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'^stats', re.IGNORECASE)), estadisticas))

        dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'^posicion?', re.IGNORECASE)), posicion))
        dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'^balance?', re.IGNORECASE)), balance))


        ## COMANDOS
        dispatcher.add_handler(CommandHandler("precio", precio))
        dispatcher.add_handler(CommandHandler("p", precio))
        dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'^cruce', re.IGNORECASE)), cruce))


        # on non command i.e message - echo the message on Telegram
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, noentiendo))

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

    except Exception as e:
        print("ERROR GENERAL, " + str(e.message))
        logger.error("ERROR GENERAL, " + str(e.message))


if __name__ == '__main__':
    main()
