# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 16:52:30 2019

@author: Daniel Jarvis
OPC N3 record data to a CSV.

ADATTATO E COMPLETATO DAI RAGAZZI DEL PCTO 2024 (AKA TESTINE DI FAGIANO)

- Registra i dati dal sensore OPC N3 e dal sensore DHT22
- Controlla il livello di umidità del sensore DHT22 ed applica le correzioni ai valori dei PM con i parametri definiti in input
- Salva i valori corretti in un file CSV
- Carica il file aggiornato su GitHub

Dalla pagina web che abbiamo realizzato è possibile visionare i dati quasi in tempo reale
NOTA: sostituendo il caricamento su GitHub con il caricamento su database,
potremmo avere i dati in tempo reale sulla pagina web.

Collegare il sensore OPC N3 al Raspberry tramite Serial -> USB
Collegare il sensore DHT22 al Raspberry tramite I2C

Buona fortuna, semmai qualcuno riutilizzerà questo abominio di codice
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


#
#			FUNZIONI
#       	 OPC-N3
#		contiene GitHub


integration=5

# NAMING VARIABLES
OPCNAME = "OPC-N3-1"
OPCPORT= "/dev/ttyACM0"
LOCATION = "DatiOPC-N3"
wait=1e-06
#
# Init OPC for spi connection 

def initOPC(ser):
    #print("Init:")
    time.sleep(1)
    ser.write(bytearray([0x5A,0x01]))
    nl = ser.read(3)
    print(nl)
    time.sleep(wait)
    ser.write(bytearray([0x5A,0x03]))
    nl=ser.read(9)
    print(nl)
    time.sleep(wait)
    
        #SPI conncetion
    ser.write(bytearray([0x5A,0x02,0x92,0x07]))
    nl=ser.read(2)
    print(nl)
    time.sleep(wait)
        
       
# Turn fan 
        
def fanOff(ser):
    print("Fan turn off")
    
        #start the flow chart the flow chart
    T=0 #Triese counter
    while True:
        
        ser.write(bytearray([0x61,0x03]))
        nl = ser.read(2)
        # print(nl)
        T=T+1 
        if nl== (b"\xff\xf3" or b"xf3\xff"):
            time.sleep(wait)
            #fan off
            ser.write(bytearray([0x61,0x02]))
            nl = ser.read(2)
        #      print(nl)
            time.sleep(2)
            fan="OFF"
            print("Fan off")
            return fan
        elif T > 20:
            
            print("Reset SPI")
            time.sleep(3) #time for spi buffer to reset
            #reset SPI  conncetion 
            #initOPC(ser)
            T=0
        else:
            time.sleep(wait*10) #wait 1e-05 before next commnad 
                        
           

# Turn fan and laser on
# Turn fan and laser on
def fanOn(ser):
    print("Fan turn on")
    #start the flow chart the flow chart
    T=0 #Triese counter
    while True:   
        ser.write(bytearray([0x61,0x03]))
        nl = ser.read(2)
        #   print(nl)
        T=T+1 
        if nl== (b"\xff\xf3" or b"xf3\xff"):
            time.sleep(wait)
            #fan on
            ser.write(bytearray([0x61,0x03]))
            nl = ser.read(2)
    #        print(nl)
            time.sleep(2)
            fan="ON"
            print("Fan On")
            return fan
        elif T > 20:
            print("Reset SPI")
            time.sleep(3) #time for spi buffer to reset
            #reset SPI  conncetion 
            # initOPC(ser)
            T=0
        else:
            time.sleep(wait*10) #wait 1e-05 before next commnad 

#Lazer on   0x07 is SPI byte following 0x03 to turn laser ON.
def LazOn(ser):
    print("Lazer turn On")
    T=0 #Triese counter
    while True:   
        ser.write(bytearray([0x61,0x03]))
        nl = ser.read(2)
    #     print(nl)
        
        T=T+1 
        if nl== (b"\xff\xf3" or b"xf3\xff"):
            time.sleep(wait)
            #Lazer on
            ser.write(bytearray([0x61,0x07]))
            nl = ser.read(2)
    #          print(nl)
            time.sleep(wait)
            Laz="ON"
            print("Fan On")
            return Laz
        elif T > 20:
            print("Reset SPI")
            time.sleep(3) #time for spi buffer to reset
            #reset SPI  conncetion 
            #  initOPC(ser)
            T=0
        else:
            time.sleep(wait*10) #wait 1e-05 before next commnad 



#Lazer off 0x06 is SPI byte following 0x03 to turn laser off.
def LazOff(ser):
    print("Lazer Off")
    
    T=0 #Triese counter
    while True:   
        ser.write(bytearray([0x61,0x03]))
        nl = ser.read(2)
    #       print(nl)
        T=T+1 
        if nl== (b"\xff\xf3" or b"xf3\xff"):
            time.sleep(wait)
            #Lazer off
            ser.write(bytearray([0x61,0x06]))
            nl = ser.read(2)
#            print(nl)
            time.sleep(wait)
            Laz="Off"
            print("Lazer Off")
            return Laz
        elif T > 20:
            print("Reset SPI")
            time.sleep(3) #time for spi buffer to reset
            #reset SPI  conncetion 
            #   initOPC(ser)
            T=0
        else:
            time.sleep(wait*10) #wait 1e-05 before next commnad 


#add the singal to temp and RH value convertion   from the SPI data sheet

def RHcon(ans):
    #ans is  combine_bytes(ans[52],ans[53])
    RH=100*(ans/(2**16-1))
    return RH
def Tempcon(ans):
      #ans is  combine_bytes(ans[52],ans[53])
    Temp=-45+175*(ans/(2**16-1))
    return Temp
def combine_bytes(LSB, MSB):
	return (MSB << 8) | LSB       
def Histdata(ans):
#function for all the hist data, to break up the getHist
     #time.sleep(wait)  

    data={}
    data['MToF'] = struct.unpack('f',bytes(ans[48:52]))[0] #MTof is in 1/3 us, value of 10=3.33us
    data['period'] = combine_bytes(ans[52],ans[53]) 
    data['FlowRate'] = combine_bytes(ans[54],ans[55])
    data['TEMPERATURA']= Tempcon(combine_bytes(ans[56],ans[57]))
    data['UMIDITA'] = RHcon(combine_bytes(ans[58],ans[59]))
    data['pm1'] = struct.unpack('f',bytes(ans[60:64]))[0]
    data['pm2.5'] = struct.unpack('f',bytes(ans[64:68]))[0]
    data['pm10'] = struct.unpack('f',bytes(ans[68:72]))[0]

      #  print(data)
    return(data)

def read_all(self,port, chunk_size=86):
    """Read all characters on the serial port and return them."""
    if not port.timeout:
        raise TypeError('Port needs to have a timeout set!')

    read_buffer = b''

    while True:
	# Read in chunks. Each chunk will wait as long as specified by
	# timeout. Increase chunk_size to fail quicker
        byte_chunk = port.read(size=chunk_size)
        read_buffer += byte_chunk
        if not len(byte_chunk) == chunk_size:
            break

    return read_buffer

def initFile(date):
	ofile=   '/home/user/Desktop/' + LOCATION + '_' + OPCNAME + '_' + str(date).replace('-','') + ".csv"
	print("Opening Output File:")
	if(not os.path.isfile(ofile)):
		f=open(ofile,'w+')
		print("Data e ora;Temperatura;Umidità (%);PM 1;PM 2.5;PM 10",file=f)
	else:
		f=open(ofile,'a')
	return f


def rightbytes(response):
    '''
    Get ride of the 0x61 byeste responce from the hist data, returning just the wanted data
    '''
    hist_response=[]
    for j, k in enumerate(response):            # Each of the 86 bytes we expect to be returned is prefixed by 0xFF.
        if ((j + 1) % 2) == 0:                  # Throw away 0th, 2nd, 4th, 6th bytes, etc.
            hist_response.append(k)     
    return hist_response

def getData(self,ser):
    print("Get PM data")
    T=0

    while True: #initsiate getData commnad
        ser.write([0x61,0x32])
        nl=ser.read(2) #  time.sleep(1e-05)
        T=T+1
        print(nl)
        if nl== (b'\xff\xf3', b'\xf3\xff' ):
                #write to the OPC 
                for i in range(14):        # Send the whole stream of bytes at once.
                    ser.write([0x61, 0x01])
                    time.sleep(0.00001)   
            #time.sleep(.1)
            #read the data
                ans=bytearray(ser.readall())
                # print("ans=",ans)
                ans=self.rightbytes(ans)
                # print("ans=",ans)
                b1 = ans[0:4]
                b2 = ans[4:8]
                b3 = ans[8:12]
                c1=struct.unpack('f',bytes(b1))[0]
                c2=struct.unpack('f',bytes(b2))[0]
                c3=struct.unpack('f',bytes(b3))[0]
                check=self.combine_bytes(ans[12],ans[13])
                print("Check=",check)
                return([c1,c2,c3])
        elif T > 20:
                print("Reset SPI")
                time.sleep(3) #time for spi buffer to reset
                #reset SPI  conncetion 
                self.initOPC(ser)
                T=0 
                return
        else:
                time.sleep(wait*10) #wait 1e-05 before next commnad
#get hist data 
def getHist(ser):

#OPC N2 method 
	T=0 #attemt varaible 
	while True:   
	#    print("get hist attempt ",T)

	    #reques the hist data set 
	    ser.write([0x61,0x30])
	   # time.sleep(wait*10)
	    nl = ser.read(2)
	  #  print(nl)
	    T=T+1  
	  #  print("Reading Hist data")
	 #  # print(nl)
	    if nl== (b'\xff\xf3' or b'\xf3\xff' ):
                for i in range(86):        # Send bytes one at a time 
                    ser.write([0x61, 0x01])
                    time.sleep(0.000001)   

               # ans=bytearray(ser.read(1))
            #    print("ans=",ans,"len",len(ans))
                time.sleep(wait) #delay
                ans=bytearray(ser.readall())
           #     print("ans=",ans,"len",len(ans))
                ans=rightbytes(ans) #get the wanted data bytes 
                   # ans=bytearray(test)
                #    print("ans=",ans,"len",len(ans))
                #print("test=",test,'len',len(test))
                data=Histdata(ans)
                return data 
	    if T > 20:
	     #   print("Reset SPI")
                time.sleep(wait) #time for spi buffer to reset
                #reset SPI  conncetion 
                initOPC(ser)
                print("ERROR")
                data="ERROR"
                return data
	    else:
                time.sleep(wait*10) #wait 1e-05 before next commn
		

def loadOnGithub(date, tnow):
    
    # Configura le tue credenziali GitHub e altre impostazioni
    GITHUB_TOKEN = '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'
    REPO_NAME = 'TommyFara/OPC-N3-data'
    FILE_PATH = '/home/user/Desktop/' + LOCATION + '_' + OPCNAME + '_' + str(date).replace('-','') + ".csv"
    COMMIT_MESSAGE = 'Automated commit'

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    file_path_in_repo = os.path.basename(FILE_PATH)  # Assicurati che il file sia nella root della repo

    # Leggi il contenuto del file CSV
    with open(FILE_PATH, 'r') as file:
        content = file.read()

    # Controlla se il file esiste già nella repo
    try:
        contents = repo.get_contents(file_path_in_repo)
        # Se il file esiste, aggiornalo
        repo.update_file(contents.path, COMMIT_MESSAGE, content, contents.sha)
        print(f"{tnow}: File aggiornato con successo.")
    except Exception as e:
        #if e.status == 404:
            
            # Se il file non esiste, crealo
        repo.create_file(file_path_in_repo, COMMIT_MESSAGE, content)
        print(f"{tnow}: File creato con successo.")
	    
    #except Exception as e:
	 #   print(traceback.format_exc())
	
def separafloat(numero,decimali):
    multiplier = 10 ** decimali
    return int(numero * multiplier) / multiplier

def bits_to_int(bits):
    value = 0
    for bit in bits:
        value = value * 2 + (bit > 5)
    return value


#
#			FUNZIONI
#       	 DHT22
#	

# Initial the dht device, with data pin connected to:
#dhtDevice = adafruit_dht.DHT22(board.D18)

# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

#PARAMETRI CORREZIONE
MIN_CORRECTION = 50
correction = 5
interval = 10
#Correggi del [correction]% ogni [interval]% per umidità >= [MIN_CORRECTION]%

def get_dht_hum_temp():
    try:
        # Print the values to the serial port
        temperature_c = 0
        cycle = True
        attempts = 0
        while attempts < 30 and cycle:
            # NON TOCCARE I PRINT FINO A RIGA 417
            try:
                temperature_c = dhtDevice.temperature
                
                if temperature_c == None:
                    raise RuntimeError("lettura nulla") 
                
                cycle = False
                break  # Uscire dal ciclo se il codice è stato eseguito con successo
            except Exception as e:
                attempts += 1
                print(e.args[0])
                if attempts == 30:
                    print("Numero massimo di tentativi raggiunto. Codice non eseguito con successo.")
                
            time.sleep(0.5)
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity))
        return humidity, temperature_c

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
    except Exception as error:
        dhtDevice.exit()
        raise error
    
    return None, None
    #time.sleep(2.0)
    

def correzionePM(hum, pm1, pm2_5, pm10):
    print("correzione valori", correction, interval, MIN_CORRECTION)
    
    diff = hum - MIN_CORRECTION
    n = int(diff/interval) * correction/100
    
    n_pm1 = pm1 * (1.0 - n)
    n_pm2_5 = pm2_5 * (1.0 - n)
    n_pm10 = pm10 * (1.0 - n)
    return n_pm1, n_pm2_5, n_pm10

#
#			FUNZIONI
#       	 SERVER
#	

def read_server_msg(server):
    global correction
    global interval
    global MIN_CORRECTION
    global integration
    
    while True:
        msg = server.stdout.readline().strip()
        
        if msg == '':
            break
    
        command = msg.split('#')
        match command[0]:
            case 'corrVal':
                correction = float(command[1])
                
            case 'corrInt':
                interval = float(command[1])
                
            case 'corrMin':
                MIN_CORRECTION = float(command[1])
                
            case 'getState':
                #print("get state ")
                state = 'deviceState#' + str(correction) + "," + str(interval) + "," + str(MIN_CORRECTION) + "," + str(integration)
                
                server.stdin.write(state + "\n")
                server.stdin.flush()
                
                #print("responding")
                
            case 'setState':
                params = command[1].split(',')
                correction = float(params[0])
                interval = float(params[1])
                MIN_CORRECTION = float(params[2])
                integration = int(params[3])
                
                server.stdin.write("completed#\n")
                server.stdin.flush()
                
            
                
            case _:
                print(msg)


def kill_server_signal(server):
    
    def handler(sig, frame):
        server.terminate()
        server.wait()
        sys.exit(0)
    return handler
        
def kill_server(server):
    server.terminate()
    server.wait()

#
#			FUNZIONI
#       	 GPS
#	

GPS_PORT = "/dev/ttyS0"

def getPosition():
    connessione = None  # Inizializza la variabile connessione
    try:
        # Configura la connessione seriale
        connessione = serial.Serial(GPS_PORT, 9600, timeout=1)
        # Leggi i dati per il numero di tentativi specificato
        while True:
            dati = connessione.read_until('\n').decode('utf-8')
            connessione.flush()
            dati = dati.split('\n')
            #print(dati, "FINE")
            for line in dati:
                if line.startswith("$GNGLL"):
                    vettore = line.split(',')
                    if vettore[1] != '' and vettore[3] != '':
                        lat = float(vettore[1]) / 100.0
                        long = float(vettore[3]) / 100.0
                        if lat is not None and long is not None:
                            return lat, long
                
    except Exception as e: 
        print(f"Errore nella lettura da {GPS_PORT}: {e}")
        return 0,0
    finally:
        if connessione:  # Controlla se la connessione è stata stabilita
            connessione.close()
        

if __name__ == "__main__":
        serial_opts = {
       
        "port": OPCPORT,
        "baudrate": 9600,
        "parity": serial.PARITY_NONE,
        "bytesize": serial.EIGHTBITS,
        "stopbits": serial.STOPBITS_ONE,
         "xonxoff": False,
        "timeout": 1
        }
	
    	# wait for opc to boot
        time.sleep(2)

        ser = serial.Serial(**serial_opts)
        
	
	#start up dance 
	
        print("**************************************************")
        print("DID YOU CHECK THE DATE/TIME ????????")
        print("**************************************************")
        print("integration time (seconds)",integration)
        print("**************************************************")
        
        print("Avvio web server...")
        
        server = subprocess.Popen(
            [sys.executable, 'script_websocket.py'],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            text = True
        )
        signal.signal(signal.SIGINT, kill_server_signal(server))
        atexit.register(kill_server, server)
        
        #attende il messaggio di avvio del server
        
        msg = server.stdout.readline()
        while msg is None:
            msg = server.stdout.readline()
            continue
        
        print(msg)
        
        messaggi = threading.Thread(target=read_server_msg, args=(server,))
        messaggi.daemon = True
        messaggi.start()
        
        
        
        
        #richiesta parametri correzione
        #correction = float(input("Valore di correzione (%): "))
        #interval = float(input("Intervallo di correzione (%): "))
        
        print("Init:")
        initOPC(ser)
        time.sleep(1)

        print("Fan Off:")
        fanOff(ser)
        LazOff(ser)
        time.sleep(5)

        print("Fan on:")
        fanOn(ser)
        LazOn(ser)
        time.sleep(5)	
	
        print(OPCNAME,"Ready")
	
	#time loop
        while time.time() % integration != 0:
            pass         # now is in form YYYYMMDD
            datestart = datetime.date.today()
            starttime = datetime.datetime.now()
            f = initFile(datestart)
    
            
            print("Looping:")
            while True:
                    t=getHist(ser)
                    ts = time.time()
                    tnow = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d  %H:%M:%S')
                    data=t
                    
                    dht_hum, dht_temp = get_dht_hum_temp()
                    #dht_hum, dht_temp = get_dht_data()
                    
                    lat, long = getPosition()
                    
                    if dht_hum != None and dht_temp != None:
                        #calcolo nuovi PM
                        #Often iff errors occre, the issues is with a failed getHist, but on the next getHist it works.
                        #The try, then except deals with that. 
                        try:
                            data['UMIDITA'] = dht_hum
                            
                            if dht_hum > MIN_CORRECTION:
                                #print("correzione valori")
                                data['pm1'], data['pm2.5'], data['pm10'] = correzionePM(data['UMIDITA'], data['pm1'], data['pm2.5'], data['pm10'])
                            
                            data['TEMPERATURA'] = separafloat(data['TEMPERATURA'], 3)
                            data['UMIDITA'] = separafloat(data['UMIDITA'], 3)
                            data['pm1'] = separafloat(data['pm1'], 3)
                            data['pm2.5'] = separafloat(data['pm2.5'], 3)
                            data['pm10'] = separafloat(data['pm10'], 3)
                            
                            print(tnow  + ";"+ str(data['TEMPERATURA']) + ";"+ str(data['UMIDITA']) + ";"  + str(data['pm1']) + ";"  + str(data['pm2.5']) + ";"  + str(data['pm10']) + ";" + str(separafloat(lat, 2)) + ";" + str(separafloat(long, 2)), file=f)
                            print(OPCNAME," Time",tnow ," Temp:",str(data['TEMPERATURA'])," RH:",str(data['UMIDITA']), " PM1:", str(data['pm1']) ,"PM2.5:", str(data['pm2.5']) ,"PM10:", str(data['pm10']), "LAT:", str(separafloat(lat, 2)), "LNG:", str(separafloat(long, 2)))
                        except: #if get gist falues and reurn NoData 
                            print("Error1")
                            print(traceback.format_exc())
                #Write nan data, need to keep track of how many time these types of errors occure for data coverage
                            print(tnow + ";" + "nan" + ";"  + "nan" + ";"  + "nan" + ";"  + "nan" + ";"  + "nan", file=f)
                            
                        pass
                        f.flush()
                        
                        
                        
                        
                        #if (data['pm1'], data['pm2.5'], data['pm10'] != 0):
                            #loadOnGithub(datestart,tnow)	# carica i dati nella repo di github
        
                        if (datetime.date.today() - datestart).days > 0:
                                f.close()
                                datestart = datetime.date.today()
                                f = initFile(datestart)
                     
                     
                    secondsToRun = (datetime.datetime.now()-starttime).total_seconds() % integration
                    time.sleep(integration-secondsToRun)

        print("Closing:")
        
        f.close()
        fanOff(ser)
        LazOff(ser)
        ser.close()
	



