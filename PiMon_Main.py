import configSetUp

configSetUp.configSetUp()

import adafruit_dht
import Adafruit_BMP.BMP085 as BMP085
import RPi.GPIO as GPIO
import time
import datetime
import csv
import os
import os.path
import paho.mqtt.client as mqtt
import requests
import json
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
import threading
from dotenv import load_dotenv

THINGSBOARD_HOST = 'demo.thingsboard.io'
load_dotenv('Pimon_Run/.env')
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

mcp = PCF8574_GPIO(0x27)
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

data_file_path = 'Pimon_Run/data/data.csv'
data2_file_path = 'Pimon_Run/data/data2UpLoad.csv'

fields = ["Date Time", "Temperature", "Humidity", "Pressure", "Light"]

buttonPin = 12 #set pin
LDRpin = 6 #set pin

dhtDevice = adafruit_dht.DHT11(4)

bmp = BMP085.BMP085()

leds = [20,21] #set pins [0] red-pow [1] green-network



def startUpSweep():
    ledoffFlipper(leds[0])
    ledoffFlipper(leds[1])
    GPIO.cleanup()

def cleanExit():
    client.loop_stop()
    client.disconnect()

def startConnection():
    try:
        global client
        client = mqtt.Client()
        client.username_pw_set(ACCESS_TOKEN)
        # Connect to ThingsBoard using default MQTT port ane 1 hour keepalive interval
        client.connect(THINGSBOARD_HOST, 1883, 1*60*60)
        client.loop_start()
        return True
    except TimeoutError:
        return False

def DHTcall():
    try:
        temperature = float(dhtDevice.temperature)
        humidity = float(dhtDevice.humidity)
        return temperature,humidity
    except:
        return "Error"

def BMPcall():
    try:
        pressure = float(round((bmp.read_pressure())/1000,1))
        return pressure
    except RuntimeError:
        return "Error"

def LDRcall():
    if GPIO.input(LDRpin):
        return "Off"
    else:
        return "On"

def csvSaving(data):
    file_exists = os.path.exists(data_file_path)
    with open(data_file_path, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write the header
        if file_exists == False:
            writer.writerow(fields)
        # write multiple rows
        writer.writerow(data)

def csvSaving2UpLater(data):
    with open(data2_file_path, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write multiple rows
        writer.writerow(data)

def csvRead2Up():
    with open(data2_file_path, 'r') as f:
        csvreader = csv.reader(f)
        for data in csvreader:
            dataSending(data)
    os.remove(data2_file_path)

def dataSending(data):
    ''' Sending humidity and temperature data to ThingsBoard
     change path - look up more documentation on mqtt
     changing the data array into a dictionary'''
    fields = ["Date Time", "Temperature", "Humidity", "Pressure", "Light"]
    data = dict(zip(fields, data))
    client.publish('v1/devices/me/telemetry', json.dumps(data), 1)

def destroyDisp():
    lcd.clear()

def display(data):
    mcp.output(3,1)# turn on LCD backlight
    lcd.begin(16,2)
    ft = round(time.time())+20
    for item in data:
        lcd.clear()
        lcd.setCursor(0,0)
        try:
            lcd.message(f"{item[:12]}")
        except:
            lcd.message(f"{item}")
        time.sleep(1)
        while True: #wait/button call
            if GPIO.input(buttonPin)==GPIO.LOW:
                break
            if time.time()>= ft:
                break
    mcp.output(3,0)
    destroyDisp()

def dataPullSort():
    data = [] #["Date Time", "Temperature", "Humidity", "Pressure", "Light"]

    data.append(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

    while True:
        DHTData = DHTcall()
        time.sleep(0.1)
        if DHTcall()!="Error":
            break

    while True:
        BMPData = BMPcall()
        if BMPcall()!="Error":
            break
        
    data.append(DHTData[0])
    data.append(DHTData[1])
    data.append(BMPData)
    data.append(LDRcall())
    return data

def ledonFlipper(ledF):
    GPIO.output(ledF, GPIO.HIGH)

def ledoffFlipper(ledF):
    GPIO.output(ledF, GPIO.LOW)

def conStatus():
    print("Attempring to connect")
    if(startConnection()==False):
        req = requests.get('http://clients3.google.com/generate_204')
        if req.status_code != 204:
            ledoffFlipper(leds[1]) #network led
        else:
            ledonFlipper(leds[1])

def setup():
    GPIO.setup(LDRpin, GPIO.IN)
    for x in range(len(leds)):
        GPIO.setup(leds[x], GPIO.OUT)

def buttonDetect4Theread():
    print("Button Thread active")
    mcp.output(3,1)
    lcd.begin(16,2)
    lcd.setCursor(2,0)
    lcd.message("Threads OK")
    time.sleep(2)
    mcp.output(3,0)
    destroyDisp()

    GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    while True:
        time.sleep(1)
        if GPIO.input(buttonPin)==GPIO.LOW:
            display(dataPullSort())

def dataLogSequence4Therad(multiplyer):
    while True:
        ft = round(time.time())+60*60*multiplyer
        while True:
            if time.time()>= ft:
                #callsorter,logsend
                data = dataPullSort()
                #connection check
                req = requests.get('http://clients3.google.com/generate_204')
                if req.status_code != 204:
                    #call local save backing sequence
                    ledoffFlipper(leds[1])
                    csvSaving(data)
                    csvSaving2UpLater(data)
                else:
                    ledonFlipper(leds[1])
                    csvSaving(data)
                    if os.path.exists(data2_file_path) == True:
                        csvRead2Up()
                    dataSending(data)
                break

def main(multiplyer):
    try:
        conStatus()
        TButton = threading.Thread(target=buttonDetect4Theread)
        TDataLog = threading.Thread(target=dataLogSequence4Therad, args=(multiplyer,))
        TDataLog.start()
        TButton.start()
        
    except:
        ledoffFlipper(leds[0])
        ledoffFlipper(leds[1])
        GPIO.cleanup()   

def bootSetUpStatus():
    setup()
    ledonFlipper(leds[0])
    mcp.output(3,1)
    lcd.begin(16,2)
    for i in range(16):
        lcd.setCursor(i,0)
        time.sleep(0.1)
        lcd.message("/")
    time.sleep(2)
    lcd.clear()
    lcd.setCursor(4,0)
    lcd.message("status ok")
    time.sleep(4)
    mcp.output(3,0)
    destroyDisp()

try:
    startUpSweep()
except:
    pass
bootSetUpStatus()
main(0.001)



