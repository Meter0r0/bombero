import sqlite3
import datetime
import threading
conn = sqlite3.connect('bolsero2.db', check_same_thread=False, isolation_level=None)
def creaTabla():
    # Crear un cursor para ejecutar comandos SQL
    cursor = conn.cursor()

    # Crear una tabla llamada "clientes"
    # cursor.execute('DROP TABLE stats')
    cursor.execute('CREATE TABLE stats (id INTEGER PRIMARY KEY AUTOINCREMENT,'
                   'fecha TIMESTAMP,'
                   'ticker TEXTO,'
                   'inversion REAL,'
                   'caida_real REAL,'
                   'caida_buscada REAL,'
                   'ganancia REAL,'
                   'alpha1 REAL,'
                   'alpha2 REAL,'
                   'alpha3 REAL,'
                   'alpha4 REAL,'
                   'beta1 REAL,'
                   'beta2 REAL)'
                   )
    #conn.close()

def creaTabla_variaciones():
    # Crear un cursor para ejecutar comandos SQL
    cursor = conn.cursor()

    # Crear una tabla llamada "clientes"
    # cursor.execute('DROP TABLE stats_variaciones')
    cursor.execute('CREATE TABLE stats_variaciones (id INTEGER PRIMARY KEY AUTOINCREMENT,'
                   'fecha TIMESTAMP,'
                   'ticker TEXTO,'
                   'caida REAL)'
                   )


def add_resultado(ticker, inversion=0, caida_real=0, caida_buscada=0, ganancia=0, alpha1=0, alpha2=0, alpha3=0,
                  alpha4=0, beta1=0, beta2=0):
    # Crear un cursor para ejecutar comandos SQL

    lock = threading.Lock()

    with lock:
        cursor = conn.cursor()
        current_time = datetime.datetime.now()
        msj = "INSERT INTO stats (fecha, ticker, inversion, caida_real, caida_buscada, ganancia, alpha1, alpha2," \
              " alpha3, alpha4, beta1, beta2) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
        cursor.execute(msj, (current_time, ticker, inversion, caida_real, caida_buscada, ganancia,
                             alpha1, alpha2, alpha3, alpha4, beta1, beta2))
        conn.commit()

        cursor.close()


def get_resultados():
    # Realizar una consulta a la tabla "clientes"
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stats")

    # Obtener todos los resultados de la consulta
    resultados = cursor.fetchall()

    # Imprimir los resultados
    for r in resultados:
        print("r: "+str(r))
    #conn.close()


def add_variacion(ticker, caida=0):
    # Crear un cursor para ejecutar comandos SQL

    lock = threading.Lock()

    with lock:
        cursor = conn.cursor()
        current_time = datetime.datetime.now()
        msj = "INSERT INTO stats_variaciones (fecha, ticker, caida) VALUES (?,?,?)"
        cursor.execute(msj, (current_time, ticker, caida))
        conn.commit()

        cursor.close()


def set_var(nombre, valor):

    lock = threading.Lock()

    with lock:
        cursor = conn.cursor()
        msj = "UPDATE variables set valor = "+valor+" WHERE nombre="+nombre
        cursor.execute(msj)
        conn.commit()
        cursor.close()

def get_var(nombre):
    # Realizar una consulta a la tabla "clientes"
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM variables WHERE nombre="+nombre)

    # Obtener todos los resultados de la consulta
    resultados = cursor.fetchall()

    # Imprimir los resultados
    for r in resultados:
        print("r: "+str(r))
    #conn.close()


# set_var("inversion", "200")
# get_var("inversion")

# creaTabla_variaciones()
# add_caida("BTC", 12.2)

#creaTabla()
#add_resultado("ticker",20,0.4, 0.6,12.2,1,2,3,4,5,6)
#add_resultado("ticker",4500,0.4, 0.6,12.2)
#get_resultados()
