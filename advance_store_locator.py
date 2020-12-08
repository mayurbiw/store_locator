import grequests
import xlrd
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import time

now = datetime.now()
start_time = now.strftime("%H:%M:%S")


zip_codes_all = []

loc = ("/home/mayur/practice_projects/store_locator/zip_code_details.xls")

wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
sheet.cell_value(0, 0)

urls = [
    
]

all_stores_us = dict()

# fetch  all zip codes from the excel file and store into a variable and create all urls 

for i in range(1,sheet.nrows):
    #if i == 5000:
     #   break
    z = sheet.cell_value(i, 0)
    if z == '':
        break
    #print(z)
    #if sheet.cell_value(i,4) == 'CA' or sheet.cell_value(i,4) == 'NY':
    zip_codes_all.append(z)
    url =  'https://www.starbucks.com/store-locator?place='+z
    urls.append(url)


print("Number of urls to hit "  + str(len(urls)))
all_stores_us_id = []
MAX_CONNECTIONS = 200
resposes = []
pages= 0 
for x in range(0,len(urls), MAX_CONNECTIONS):
    #print(f"URLS range {x} to {x + MAX_CONNECTIONS}" )
    rs = (grequests.get(u, stream=False) for u in urls[x:x+MAX_CONNECTIONS])
    
    # making all the reqest at once. 
    resposes = grequests.map(rs)

    # for each respond finding the store. 
    for res in resposes:

        if res is None:
            continue

        if res is not None and res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
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
                    'phone_number': store['phoneNumber']
                    #'zipcode': zipcode
                }
                
                all_stores_us[store['id']] = s

                #print(store['id'])
                
                if store['id'] not in all_stores_us_id:
                    all_stores_us_id.append(store['id'])
                
            res.close()
        
     
    resposes = None 
    time.sleep(1) #You can change this to whatever you see works better.
    

    
#print(all_stores_us)
print("Uniques stores found "+str(len(all_stores_us_id)))

now = datetime.now()
end_time = now.strftime("%H:%M:%S")

print(start_time)
print(end_time)
