
import time
import serial

integration=5

# NAMING VARIABLES
OPCNAME = "OPC-N3-1"
OPCPORT= "/dev/ttyACM0"
LOCATION = "DatiOPC-N3"
wait=1e-06


def initialize():
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
    
    
#----------------------------------
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
    
    
#----------------------------------
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
            #print(nl)
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
            
            
#----------------------------------
def fanOn(ser):
    print("Fan turn on")
    
    #start the flow chart the flow chart
    T=0 #Triese counter
    
    while True:   
        ser.write(bytearray([0x61,0x03]))
        nl = ser.read(2)
        #print(nl)
        T=T+1 
        if nl== (b"\xff\xf3" or b"xf3\xff"):
            time.sleep(wait)
            #fan on
            ser.write(bytearray([0x61,0x03]))
            nl = ser.read(2)
            #print(nl)
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
            
            
#----------------------------------
#Lazer on   0x07 is SPI byte following 0x03 to turn laser ON.
def LazOn(ser):
    print("Lazer turn On")
    
    T=0 #Triese counter
    
    while True:   
        ser.write(bytearray([0x61,0x03]))
        nl = ser.read(2)
        #print(nl)
        
        T=T+1 
        if nl== (b"\xff\xf3" or b"xf3\xff"):
            time.sleep(wait)
            #Lazer on
            ser.write(bytearray([0x61,0x07]))
            nl = ser.read(2)
            #print(nl)
            time.sleep(wait)
            Laz="ON"
            print("Fan On")
            return Laz
        elif T > 20:
            print("Reset SPI")
            time.sleep(3) #time for spi buffer to reset
            #reset SPI  conncetion 
            #initOPC(ser)
            T=0
        else:
            time.sleep(wait*10) #wait 1e-05 before next commnad 


#----------------------------------
#Lazer off 0x06 is SPI byte following 0x03 to turn laser off.
def LazOff(ser):
    print("Lazer Off")
    
    T=0 #Triese counter
    while True:   
        ser.write(bytearray([0x61,0x03]))
        nl = ser.read(2)
        #print(nl)
        T=T+1 
        if nl== (b"\xff\xf3" or b"xf3\xff"):
            time.sleep(wait)
            #Lazer off
            ser.write(bytearray([0x61,0x06]))
            nl = ser.read(2)
            #print(nl)
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
            

#----------------------------------
