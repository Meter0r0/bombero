# -*- coding: utf-8 -*-
import pickle
from main import get_path_bot
import os

# Guardo ganancias ticker


def add(ticker, valor):
    valorp = load(ticker)
    valor = valor + valorp
    save(ticker, valor)


def save(ticker, valor):

    with open(str(ticker) + ".dat", "wb") as f:
        pickle.dump(float(valor), f)


def load(ticker)->float:
    ARCH = str(ticker) + ".dat"
    if not os.path.isfile(ARCH):
        valor = float(0)
        save(ticker, valor)
    with open(ARCH, "rb") as f:
        return float(pickle.load(f))


## proyecto anterior
def save_alertas(id_usuario, lista):
    PATH = get_path_bot()

    with open(PATH+"/alertas/"+ str(id_usuario)+ ".dat", "wb") as f:
        pickle.dump(lista, f)


def load_alertas(id_usuario):
    PATH = get_path_bot()

    ARCH = PATH+"/alertas/"+  str(id_usuario)+ ".dat"
    if not os.path.isfile(ARCH):
        l = []
        save_alertas(id_usuario, l)
    with open(ARCH, "rb") as f:
        return pickle.load(f)


def save_seguimiento(id_usuario, lista):
    PATH = get_path_bot()

    with open(PATH+"/seguimiento/"+  str(id_usuario) + ".dat", "wb") as f:
        pickle.dump(lista, f)


def load_seguimiento(id_usuario):
    PATH = get_path_bot()
    ARCH = PATH + "/seguimiento/" + str(id_usuario) + ".dat"

    if not os.path.isfile(ARCH):
        l = []
        save_seguimiento(id_usuario, l)
    with open(ARCH, "rb") as f:
        return pickle.load(f)


def load_ordenes_cerradas(id_usuario):
    PATH = get_path_bot()
    ARCH = PATH + "/ordenes_cerradas/" + str(id_usuario) + ".dat"

    if not os.path.isfile(ARCH):
        l = []
        save_seguimiento(id_usuario, l)
    with open(ARCH, "rb") as f:
        return pickle.load(f)


def save_ordenes_cerradas(id_usuario, lista):
    PATH = get_path_bot()

    with open(PATH+"/ordenes_cerradas/"+  str(id_usuario) + ".dat", "wb") as f:
        pickle.dump(lista, f)

##--------------


def load_ordenes_pendientes(id_usuario):
    PATH = get_path_bot()
    ARCH = PATH + "/ordenes_pendientes/" + str(id_usuario) + ".dat"

    if not os.path.isfile(ARCH):
        l = []
        save_seguimiento(id_usuario, l)
    with open(ARCH, "rb") as f:
        return pickle.load(f)


def save_ordenes_pendientes(id_usuario, lista):
    PATH = get_path_bot()

    with open(PATH+"/ordenes_pendientes/"+  str(id_usuario) + ".dat", "wb") as f:
        pickle.dump(lista, f)