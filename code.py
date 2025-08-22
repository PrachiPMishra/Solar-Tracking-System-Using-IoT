#libraries and packages
import network
import urequests
import time
import requests
from utime import sleep
from servo import Servo

# Set up Wi-Fi connection with these credentials
ssid= "SDP_N5"
password= "SunAlign"

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip
    
# Main loop
ip=connect()

#URL to fetch latitude and longitude with city name as an input
city_url=f"https://geocoding-api.open-meteo.com/v1/search?name=Bhubaneswar&count=10&language=en&format=json"
#fetch the current time from the device
tm = time.gmtime(time.time())

response = urequests.get(city_url)
data = response.json()
lon=data['results'][0]['longitude'] #value of longitude
lat=data['results'][0]['latitude'] #value of latitude

#URL to fetch azimuth angle and elevation angle using latitude and longitude
url = f"https://sun-seeker-api.p.rapidapi.com/sunposition?lat={lat}&lon={lon}"
headers = {
    "X-RapidAPI-Key": "37f4e1a663msh7c99fb453f31099p171523jsn85d799486a3f",
    "X-RapidAPI-Host": "sun-seeker-api.p.rapidapi.com"
}

#initialize the servo motors to 0 degree
hs=Servo(0)
vs=Servo(16)
hs.write(0)
vs.write(0)

prev_az=0
while (tm[3]>=6 and tm[3]<18):
    response = requests.get(url, headers=headers)
    data=response.json()
    print(data)
    el=data['elevation'] #value of elevation angle
    az=data['azimuth'] #value of azimuth angle
    if (az>90 and az<270):
        hs_v=(90-az) if (az - prev_az>=5) else prev_az
        hs.write(hs_v)
        prev_az=hs_v
        vs.write(180-el)
    elif (az<90):
        hs_v=(90+az) if (az - prev_az>=5) else prev_az
        hs.write(hs_v)
        prev_az=hs_v
        vs.write(el)
    elif (az>270):
        hs_v=(az-270) if (az - prev_az>=5) else prev_az
        hs.write(hs_v)
        prev_az=hs_v
        vs.write(el)
    print("Elevation angle=",el," \nAzimuth angle=",az)
    sleep(900)
