import requests
import re
import time
import configparser
import os

from datetime import datetime

configParser = configparser.RawConfigParser()

dataLocation = "/ScriptData"
while(True):
    try:
        configParser.read(f'{dataLocation}/cloudflarescript.config')
        cloudflare_apikey = configParser.get('ScriptConfig','cloudflare_apikey')
        cloudflare_zoneId = configParser.get('ScriptConfig','cloudflare_zoneId')
        minutesToCheck = int(configParser.get('ScriptConfig','minutesToCheck'))
        break
    except Exception as e:
        if not os.path.exists(f'{dataLocation}/cloudflarescript.config'):            
            with open(f'{dataLocation}/cloudflarescript.config','w') as configFile:
                print("Creating config file and template. Edit the file with your key and zone id, then run the container again")
                configFile.write("[ScriptConfig]\n")
                configFile.write("cloudflare_apikey = your_api_key\n")
                configFile.write("cloudflare_zoneId = your_zone_id\n")
                configFile.write("minutesToCheck = 60")
                configFile.close()
                exit()
        print(f"Error with config: {e}")
        exit()

cloudflare_headers = {'Authorization': f'Bearer {cloudflare_apikey}'}

print('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now()),'Running')

def logThis(message):
    message = '[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now()) + f' {message}'
    print(message)
    with open(f'{dataLocation}/cloudflare.log', 'a') as log:
        log.write(str(message)+"\n")

def getMyIP():
    return requests.get("https://whatsmyip.dev/api/ip").json()['addr']

def getDnsRecords():    
    zone_url = f"https://api.cloudflare.com/client/v4/zones/{cloudflare_zoneId}/dns_records"
    response = requests.get(zone_url,headers=cloudflare_headers)
    if (response.status_code != 200):
        print("Error!\n",response.json())                
    return response.json()['result']

def updateRecords(incorrectDnsRecords,myIp):
    data = f'{{"content":"{myIp}"}}'

    for record in incorrectDnsRecords:
        record_url = f"https://api.cloudflare.com/client/v4/zones/{cloudflare_zoneId}/dns_records/{record}"
        response = requests.patch(record_url,data=data,headers=cloudflare_headers)
        if (response.status_code == 200):
            logThis(f"Successfully updated {response.json()['result']['name']} to new IP {myIp}")
        else:
            logThis(f"Error, response not OK {response.status_code}\n{response.json()}")

while True:
    try:
        myIp = getMyIP()
        #print(f"IP Detected: {myIp}")

        dnsRecords = getDnsRecords()
        #print(f"Found {len(dnsRecords)} records")

        incorrectDnsRecords = []

        #print("Incorrect IPs:")
        if (dnsRecords is None):
            print("Error: No DNS records found in zone:", cloudflare_zoneId)
            break
        for record in dnsRecords:
            #Regex match to ensure IP and not SRV record
            if re.match(r'(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])', record['content']):
                if myIp != record['content']:    
                    incorrectDnsRecords.append(record['id'])        
                    print("Updating",record['name'],record['content'])

        updateRecords(incorrectDnsRecords,myIp)
        time.sleep(60 * minutesToCheck)
    except Exception as e:
        print("Error getting DNS records:",e)
        break
