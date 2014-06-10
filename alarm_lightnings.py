#!/usr/bin/env python3

import sys
import requests
import csv
from time import sleep, gmtime, strftime
from math import radians, cos, sin, asin, sqrt, atan, atan2, degrees
from subprocess import call

city_choice = int(sys.argv[1])

print(city_choice)




if round(city_choice) == 1:
    #MARBURG:
    print("Marburg")
    lat_home = 50.799
    lon_home = 8.766

if city_choice == 2:
    #GÖTTINGEN:
    print("Göttingen")
    lat_home = 51.546335
    lon_home = 9.925232

if city_choice == 3:
    #DETMOLD:
    lat_home = 51.942995
    lon_home = 8.869972

if city_choice == 4:
    print("Berlin")
    #BERLIN:
    lat_home = 52.508699
    lon_home = 13.458023

if city_choice == 5:
    print("Brüssel")
    #BRÜSSEL:
    lat_home = 50.859277
    lon_home = 4.352531


distance_thresh = 9999.9
distance_alarm_thresh = float(sys.argv[2])
distance_min = 9999.9
distance_min_old = 9999.9

direction = ""
direction_old = "xxx"

def bearing(lat1, lon1, lat2, lon2):

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)
    
    diffLong = lon2 - lon1

    x = sin(diffLong) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1) * cos(lat2) * cos(diffLong))

    initial_bearing = atan2(x, y)

    compass_bearing = (degrees(initial_bearing) + 360) % 360

    return compass_bearing

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6367 km is the radius of the Earth
    km = 6367 * c
    return km 


def get_lightnings(region):
    r = requests.get('http://www.lightningmaps.org/live/', params={'r': region}) # 1: EU, 2: OC, 3: US
    lightnings = [[strftime('%Y-%M-%d-%H-%M-%S', gmtime())] + data for data in r.json()['d']]
    serial = r.json()['s']

    return {'serial': serial, 'latlons': lightnings}

with open(sys.argv[1], 'a',  newline='') as f:
    c = csv.writer(f)
    last_serial = 0

    while True:
        lightnings = get_lightnings(1)
        distance_min=distance_thresh
        if lightnings['serial'] != last_serial:
            #c.writerows(lightnings['latlons'])
            last_serial = lightnings['serial']
            print("")
            print(last_serial)
            for i, item in enumerate(lightnings['latlons']):
                lightning_list = lightnings['latlons']
                distance = haversine(lightning_list[i][2], lightning_list[i][3], lat_home, lon_home)
                #print(distance)
                if distance <= distance_min:
                    distance_min = distance
                    lat_min = lightning_list[i][2]
                    lon_min = lightning_list[i][3]
            print("Minimale Distanz = %g Kilometer" % (distance_min))
            
            bearing_min = bearing(lat_home, lon_home, lat_min, lon_min)
            if bearing_min >= 337.5 or bearing_min < 22.5:
                direction = "Norden"
            if bearing_min >= 22.5 and bearing_min < 67.5:
                direction = "Nordosten"
            if bearing_min >= 67.5 and bearing_min < 112.5:
                direction = "Osten"
            if bearing_min >= 112.5 and bearing_min < 157.5:
                direction = "Südosten"
            if bearing_min >= 157.5 and bearing_min < 202.5:
                direction = "Süden"
            if bearing_min >= 202.5 and bearing_min < 247.5:
                direction = "Südwesten"
            if bearing_min >= 247.5 and bearing_min < 292.5:
                direction = "Westen"
            if bearing_min >= 292.5 and bearing_min < 337.5:
                direction = "Nordwesten"

            

            if distance_min < distance_alarm_thresh and distance_min != distance_min_old and distance_min != distance_thresh:
                call(["/usr/bin/aplay", "/home/sven/Documents/CODE/JAVA/lightning/Alarme.wav"])
                call(["pico2wave", "-w", "speakout.wav", "-l", "de-DE", "Blitzaktivität in "+str(round(distance_min))+" Kilometern Entfernung im "+direction])
                call(["/usr/bin/aplay", "speakout.wav"])
                if distance_min < distance_min_old and direction == direction_old:
                    print("!!! GEWITTER UNGEFÄHR AUF KURS !!!")
                    call(["pico2wave", "-w", "speakout_ontrack.wav", "-l", "de-DE", "ACHTUNG: GEWITTER UNGEFÄHR auf KURS"])
                    call(["/usr/bin/aplay", "speakout_ontrack.wav"])
                print(str("Peilung = "+str(bearing_min)))
                distance_min_old = distance_min 
                direction_old = direction
        sleep(2)
        

    f.close()
