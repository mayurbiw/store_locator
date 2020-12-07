import xlrd

import requests

from bs4 import BeautifulSoup

import re

import json

zip_codes_all = []

from datetime import datetime

now = datetime.now()
start_time = now.strftime("%H:%M:%S")

loc = ("/home/mayur/practice_projects/store_locator/zip_code_details.xls")

wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
sheet.cell_value(0, 0)

for i in range(1,sheet.nrows):
    if i==20:
        break
    z = sheet.cell_value(i, 0)
    zip_codes_all.append(z)

all_stores_us = dict()

# list of all store ids in us for unit testing. 
all_stores_us_id = []

#call request for 100 stores with current zipcode

#zip_codes_all = ['00544','00501']

for zipcode in  zip_codes_all:
    print(zipcode)
    res = requests.get('https://www.starbucks.com/store-locator?place='+zipcode)

    #if any response fails, quit immediately
    if res.status_code != 200:
        raise SystemExit

    #print(res.content)

    soup = BeautifulSoup(res.content, 'html.parser')
    #print(soup.prettify())

    #html = list(soup.children)[2]

    #print(list(html.children))

    # get all the script tags
    all_script_tags = list(soup.select("body script"))

    # get the script tag where json object corresponding to all 100 stores is located. 
    stores =  (str((all_script_tags[3])))

    #print(store_details)

    # get the json that contains store details.
    store_details = re.findall("(?s)(?<=window.__BOOTSTRAP = )(.*?)(?=window.__INTL_MESSAGES)", stores)


    # find all retuns the list of matches, above it will always return one recoed. 
    # converting json into dictionary.
    dict = json.loads(str(store_details[0]))

    # finding number of records returned by the api call 
    #returned = dict['previousAction']['payload']['data']['paging']['returned']

    check_zero = dict.get('previousAction').get('payload')

    if check_zero is None:
        returned = None
    else:
        returned = dict['previousAction']['payload']['data']['paging']['returned']

    if returned is None:
        continue

    for i in range(0,returned):

        store = dict['previousAction']['payload']['data']['stores'][i]
        
        s = {
            'store_number': store['storeNumber'] ,
            'name':  store['name'],
            'latitude': store['coordinates']['latitude']  ,
            'longitude': store['coordinates']['longitude'] ,
            'city': store['address']['city'],
            'state': store['address']['countrySubdivisionCode'],
            'phone_number': store['phoneNumber'],
            'zipcode': zipcode
        }
        
        all_stores_us[store['id']] = s
        
        if store['id'] not in all_stores_us_id:
            all_stores_us_id.append(store['id'])
    

print(all_stores_us)
print(len(all_stores_us_id))


now = datetime.now()
end_time = now.strftime("%H:%M:%S")

print(start_time)
print(end_time)


    # getting first store 
    #print(dict['previousAction']['payload']['data']['stores'][0])



    #store = dict['previousAction']['payload']['data']['stores'][49]








