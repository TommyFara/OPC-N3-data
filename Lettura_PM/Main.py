# -*- coding: utf-8 -*-
"""
ADATTATO E COMPLETATO DAI RAGAZZI DEL PCTO 2024 (AKA TESTINE DI FAGIANO)

- Registra i dati dal sensore OPC N3 e dal sensore DHT22
- Controlla il livello di umidità del sensore DHT22 ed applica le correzioni ai valori dei PM con i parametri definiti in input
- Salva i valori corretti in un file CSV
- Carica il file aggiornato su GitHub (vecchio metodo)
- Apre un server e invia i dati con Weebsocket alla pagina web

Dalla pagina web che abbiamo realizzato è possibile visionare i dati quasi in tempo reale

NOTA: sostituendo il caricamento su GitHub con il caricamento su database,
potremmo avere i dati in tempo reale sulla pagina web.

Collegare il sensore OPC N3 al Raspberry tramite Serial -> USB
Collegare il sensore DHT22 al Raspberry tramite I2C

Buona fortuna, semmai qualcuno riutilizzerà questo abominio di codice

@original author: Daniel Jarvis
OPC N3 record data to a CSV.
"""

from __future__ import print_function
import serial
import time
import struct
import datetime
import RPi.GPIO as GPIO
import sys
import os.path
import traceback
import os
import board
import adafruit_dht
import subprocess
import threading
import atexit
import signal

import opc

if __name__ == "__main__":
    
    #Inizializza OPC-N3
    opc.initialize()
    
    