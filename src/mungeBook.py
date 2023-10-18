## Phone book generation script for XNET, by Rich DeVaul
## created on Mon Oct 16 12:38:43 PDT 2023

import csv
import requests
import json
import re
import time

def getXNETdata(url):
    response = requests.get(url)
    data = json.loads(response.text)
    return data

def rev_geocode(lat,lon):

    url=f'https://us1.locationiq.com/v1/reverse?key=pk.605cdee2ecfe08e0b12f726f13100383&lat={lat}&lon={lon}&format=json'
    response = requests.get(url)
    if response.text:
        data = json.loads(response.text)
        return data
    else:
        print(f"bad revers_geocode response for {latitude}, {longitude}")
        return {}

def reverse_geocode(latitude, longitude):
    url = f'https://geocode.maps.co/reverse?lat={latitude}&lon={longitude}'
    
    response = requests.get(url)
    if response.text:
        data = json.loads(response.text)
        return data
    else:
        print(f"bad revers_geocode response for {latitude}, {longitude}")
        return {}
    

def keyOrNull(dic,key,bad='0'):
    if key in dic:
        return dic[key]
    else:
        return bad
    
usedsn = []
def checkUnique(sn):
    if sn in usedsn:
        print(f"got duplicate sn: {sn}")
        return False
    else:
        usedsn.append(sn)
        return True

geocode_prototype= {'place_id': 224966030,
                    'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
                    'powered_by': 'Map Maker: https://maps.co', 'osm_tye': 'way',
                    'osm_id': 581364881,
                    'lat': '29.7411796', 'lon': '-95.46843373137588',
                    'display_name': '5250, Brownway Street, Uptown, Houston, Harris County, Texas, 77056, United States',
                    'address': {
                        'house_number': '5250',
                        'road': 'Brownway Street',
                        'neighbourhood': 'Uptown',
                        'city': 'Houston',
                        'county': 'Harris County',
                        'state': 'Texas',
                        'postcode': '77056',
                        'country': 'United States',
                        'country_code': 'us'},
                    'boundingbox': ['29.7408139', '29.7415487', '-95.4685749', '-95.4682879']
                    }

def makeOrderedEmpty(dct,keys):
    for key in keys:
        dct[key]='0'
    return dct

def extractFields(filename,fields):
    with open(filename) as f:
        reader = csv.DictReader(f)
        rval = []
        for row in reader:
            rdict = {}
            for key in fields:
                rdict[key]=row[key]
            #print(f"rdit: {rdict}")
            rval.append(rdict)
        return rval

def convert_to_meters(h):
    if not h:
        return 0.0
    
    match = re.search(r'([\d.]+)\s?(ft|m)?', h)

    if not match:
        return 0.0
    
    value = float(match.group(1))
    unit = match.group(2)

    if unit == 'ft':
        value *= 0.3048
    elif unit == 'm':
        pass
    else:
        # No unit, assume meters
        pass
  
    return value

def keyPriority(dic,keys,default='0'):
    rval = default
    for key in keys:
        if key in dic:
            rval = dic[key]
    return rval

def secondString(string):
    words = string.split()
    word = words[-1] if len(words) > 1 else words[0]
    return word

if __name__ == "__main__":
    uptime_all_keys = ['pass?','rank','up %','radio','gateway','uptime']
    xnetdb_all_keys = ['user__username','xnode__xnode_name','serialNumber',
                    'eNode_mac','location_latitude','location_longitude',
                    'pointing_direction_azimuth',
                    'pointing_direction_elevation','height',
                    'wallet_address','discord_username',
                    'telegram_username','submit_date','is_sasApproved']
    sas_all_keys = ['cbsd_id','cbsd_alias','owner_id','fcc_id',
                    'cbsd_serialnumber','cbsd_category','cbsd_status',
                    'registration_id','pal_count','gaa_count',
                    'unknown_count','longitude','latitude',
                    'state_name','county_name','height','height_type',
                    'antenna_gain','antenna_azimuth','sfg','srg',
                    'grants','org_id','org_name','sub_org_id_0',
                    'sub_org_name_0','sub_org_id_1','sub_org_name_1',
                    'sub_org_id_2','sub_org_name_2','sub_org_id_3',
                    'sub_org_name_3']
    phonebook_all_keys = ['provider_name','country_name','country_code',
                          'iso_cc','operator_id','provider_id',
                          'venue_name','pref_state_region',
                          'city_district','zipcode','address',
                          'category','node_type','node_class',
                          'node_count','altitude_m','latitude','longitude']

    uptime_keys = ['up %','radio']
    xnetdb_keys = ['user__username','serialNumber','location_latitude','location_longitude',
                'height']
    sas_keys = ['cbsd_serialnumber','latitude','longitude','cbsd_category',
                'height']
    uptime_fname = "../uptime-report-dump.csv"
    xnetdb_fname = "../XNode-2023-10-16_1.csv"
    sas_fname = "../cbsd_status_sova.csv"
    outfile = "../xnet-phonebook.csv"
    
    # This is the threshold for a good radio (god help us)
    threshold = 0.2

    # Extract all radio serial numbers for radios with uptime above
    # threshold
    radios=extractFields(uptime_fname,uptime_keys)
    phonebook = []
    for row in radios:
        s = row['up %']
        num = float(s[:-1]) / 100
        radsn = secondString(row["radio"])
        if num >= threshold and checkUnique(radsn):
            rec = makeOrderedEmpty({},phonebook_all_keys)
            rec['provider_name'] = "XNETMOBILE"
            rec['country_name']="USA"
            rec['country_code']=1
            rec['iso_cc']='XNET'
            rec['radio'] = radsn
            rec['uptime'] = num
            rec['node_class']='B' # make B default
            rec['node_type'] = "macro" # make macro default
            
            phonebook.append(rec)

    print("Getting current XNET history object")
    sites = getXNETdata("https://explorer.xnetmobile.com/sites.json")
    xradios = []
    for request in sites:
        radios = request["xsite"]["radio"]["radios"]
        for radio in radios:
            xradios.append(radio)
            location = radio["status"]["location"]
            print(f'radio: {radio["vendorsn"]} lat {location["lat"]} lng {location["lng"]}')
                
    print("evaluating uptime records against SAS")
    radios = 0
    unmatched = 0
    sasrecs = extractFields(sas_fname,sas_keys)

    for rec in phonebook:
        radio = rec["radio"].split('-')[-1]
        if not radio:
            continue
        # print(f"radio {radio}")
        radios += 1
        matched = False
        antennas=0
        for sasrec in sasrecs:
            if not sasrec.get('cbsd_serialnumber') or not sasrec['cbsd_serialnumber']:
                continue
            if radio in sasrec['cbsd_serialnumber'].strip():
                antennas += 1
                # print("----> ",end="")
                lat = keyOrNull(sasrec,'latitude','0')
                lng = keyOrNull(sasrec,'longitude','0')
                rclass = rec['node_class']=keyOrNull(sasrec,'cbsd_category','B')
                if rclass == "B":
                    rec['node_type'] = "macro"
                else:
                    rec['node_type'] = "micro"

                if lat == 0 or lng == 0 or lat == "unknown" or lng == "unknown":
                    print("got bad lat/lng from SAS")
                height = convert_to_meters(keyOrNull(sasrec,'height','0'))

                rec['latitude'] = lat
                rec['longitude'] = lng 
                rec['altitude_m'] = height
                rec['node_count'] = antennas
                # print(f"lat: {lat}  lng: {lng}  height: {height}  antennas: {nodecount}")
                matched=True
        if not matched:
            unmatched+= 1;
            print(f"===> no SAS match for radio {rec['radio']} --  {radio}")
            for xrec in xradios:
                if xrec["vendorsn"] in radio or radio in xrec["vendorsn"]:
                    print("getting lat, lon from XNET status")
                    location = xrec["status"]["location"]
                    rec['latitude'] = location["lat"]
                    rec['longitude'] = location["lng"]
                    rec['altitude_m'] = "0"
                    rec['node_count'] = "1"
                  

    print(f"\n\nTotal radios: {radios}  Unmatched in SAS: {unmatched}")

    # Extract radio information and location information from XNET db

    xnetdbrecs = extractFields(xnetdb_fname,xnetdb_keys)
    radios = 0
    unmatched = 0
    for rec in phonebook:
        radio = rec["radio"]
        if not radio:
            continue
        # print(f"radio {radio}")
        radios += 1
        matched = False
        antennas = 0
        for xnetdbrec in xnetdbrecs:
            if not xnetdbrec['serialNumber']:
                continue
            if radio in xnetdbrec['serialNumber'].strip():
                # print("----> ",end="")
                rec['operator_id']= xnetdbrec['user__username']
                lat = rec['latitude']
                if lat == 'unknown' or lat == '0':
                    rec['latitude'] = keyOrNull(xnetdbrec,'location_latitude','0')
                lng = rec['longitude']
                if lng == 'unknown' or lng == '0':
                    rec['longitude'] =keyOrNull(xnetdbrec,'location_longitude','0')
                
                height = rec['altitude_m']
                if height == 'unknown':
                    rec['height'] = convert_to_meters(keyOrNull(xnetdbrec,'height','0'))
                # rec['node_count'] = antennas 
                # print(f"lat: {lat}  lng: {lng}  height: {height}  antennas: {antennas}")
                matched=True
        if not matched:
            unmatched+= 1;
            print(f"===> no Django match for radio {radio}")

    print(f"\n\nTotal radios: {radios}  Unmatched against Django database: {unmatched}")

    print("geocoding")
    for rec in phonebook:
        lat = rec['latitude']
        lng = rec['longitude']
        if lat == 'unknown' or lng == 'unknown':
            print(f"bad lat/lng for radio {rec['radio']} skipping")
            continue
        print(f"geocode revers lookup for {lat} {lng}")
        #place = reverse_geocode(rec['latitude'],rec['longitude'])
        place = rev_geocode(rec['latitude'],rec['longitude'])
        name = keyOrNull(place,'display_name')
        print(f"got {name}")
        time.sleep(0.75)
        address = keyOrNull(place,'address',{})
        hn = keyOrNull(address,'house_number','')
        street = keyOrNull(address,'road','')
        rec['pref_state_region'] = keyOrNull(address,'state')

        rec['city_district']=keyPriority(address,
                                         ['city','city_district','town',
                                          'village','suburb','hamlet'])
        rec['zipcode']=keyOrNull(address,'postcode').split('-')[0]
        rec['address']=f"{hn} {street}"
        rec['venue_name']= keyPriority(address,
                                       ['name','attraction','apartments'])
    
    print("dumping out CSV")
    with open(outfile, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=phonebook_all_keys + ['radio'],extrasaction='ignore') 
        writer.writeheader()
        writer.writerows(phonebook)
    #for phone in phonebook:
    #    print(phone)
        
#    print(phonebook)

