from bs4 import BeautifulSoup
from datetime import datetime
import grequests
import json
import re
import report_creator
from pathlib import Path 
import sys, os
import time
from time import sleep
import xlrd
import xlwt
    
all_stores_us_id = [] 
all_stores_us_id_dict = {}
failed_requests = []
stores_dict_list = []

LOC = Path(__file__).resolve().parent.parent / 'zip_code_details.xls'


def prepare_urls(loc,urls):

    """
    Inputs : location of the Excel.
    Outputs: urls to process.  
    """
    #f_urls = ['https://www.starbucks.com/store-locator?place=00601', 'https://www.starbucks.com/store-locator?place=01586', 'https://www.starbucks.com/store-locator?place=09470', 'https://www.starbucks.com/store-locator?place=09840', 'https://www.starbucks.com/store-locator?place=15339', 'https://www.starbucks.com/store-locator?place=22234', 'https://www.starbucks.com/store-locator?place=34020', 'https://www.starbucks.com/store-locator?place=53490', 'https://www.starbucks.com/store-locator?place=55581', 'https://www.starbucks.com/store-locator?place=71150']
    
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    sheet.cell_value(0, 0)
    for i in range(1,sheet.nrows):
        z = sheet.cell_value(i, 0)
        url =  f'https://www.starbucks.com/store-locator?place={z}'
        urls.append(url)   

def stores_returned(store_details_dict):
    
    """
    Description: Number of stores returned by starbucks.
    Input: dictionary containing web page response.
    Output: Total Number of stores retuned by starbucks.  
    """

    if store_details_dict.get('previousAction').get('payload') is None:
        return 0
    else:
        return store_details_dict.get('previousAction').get('payload').get('data').get('paging').get('returned') 
       
def exception_handler(request, exception):
    f = open("starbucks.log", "a")
    f.write("\n ...............Error..............\n")
    f.write(str(exception))
    f.close()
    failed_requests.append(request.url)

def handle_res(res,**kwargs):
    if res is None:
        return

    #print(res.url)
    
    
    if res.status_code == 200:
        
        soup = BeautifulSoup(res.content, 'html.parser')
        all_script_tags = list(soup.select("body script"))
        
        stores =  (str((all_script_tags[3])))
        
        #get the json that contains store details.
        store_details = re.findall("(?s)(?<=window.__BOOTSTRAP = )(.*?)(?=window.__INTL_MESSAGES)", stores)
        
        # converting json respod into python dictionary.
        store_details_dict = json.loads(str(store_details[0]))
        
        #finding number of records returned by the api call 
        returned = stores_returned(store_details_dict)
        
        if returned == 0:
            return

        for i in range(0,returned):
            store = store_details_dict.get('previousAction').get('payload').get('data').get('stores')[i]
            
            if not store:
                continue
            
            # skip if the store is already visited.....
            if all_stores_us_id_dict.get(store['id']) is None:
                
                # handling the case when postal code isn't provided by starbucks.
                if store.get('address').get('postalCode') is None:
                    zip = res.url[46:]
                else:
                    zip = store.get('address').get('postalCode')[0:5]
                    
                all_stores_us_id_dict[store['id']] = True
                store_det = {}
                store_det['storeName'] = store.get('name')
                store_det['address'] = store.get('address').get('streetAddressLine1')
                store_det['city'] = store.get('address').get('city')
                store_det['state'] = store.get('address').get('countrySubdivisionCode')
                store_det['zip'] = zip
                store_det['phone'] = store.get('phone')
                store_det['longitude'] =  store.get('coordinates').get('longitude')
                store_det['latitude'] = store.get('coordinates').get('latitude')
                
                stores_dict_list.append(store_det)
               
                
            #all_stores_us[store['id']] = s
            #global all_stores_us_id
             
            
        res.close()
    else:
        print(res.status_code)                                                                                                                 
    
    return None

def handle_failed_requests(failed_requests):
    retry = 0 
    MAX_CONNECTIONS = 100
    while(retry!=3 and len(failed_requests)>0):
        retry = retry + 1
        for x in range(0,len(failed_requests), MAX_CONNECTIONS):
            failed_requests.remove(failed_requests[x])
            rs = (grequests.get(u, hooks = {'response' : handle_res} ,stream=False) for u in failed_requests[x:x+MAX_CONNECTIONS])
            grequests.map(rs,exception_handler=exception_handler)

def starbucks_report_us():

    urls = []
    # os.get_file
    now = datetime.now()
    start_time = now.strftime("%H:%M:%S")

    prepare_urls(LOC,urls)
    
    print("Number of urls to hit "  + str(len(urls)))
    
    MAX_CONNECTIONS = 100
    for x in range(0,len(urls), MAX_CONNECTIONS):
        rs = (grequests.get(u, hooks = {'response' : handle_res} ,stream=False) for u in urls[x:x+MAX_CONNECTIONS])
        grequests.map(rs,exception_handler=exception_handler)
    
    
    if len(failed_requests) > 0:
        print("retrying failed requests....")
        handle_failed_requests(failed_requests)
    
    now = datetime.now()
    end_time = now.strftime("%H:%M:%S")

    # checking time taken to run a script...
    print(start_time)
    print(end_time)

    #logs....
    f = open("starbucks.log", "a")
    f.write("\n ...............Failed urls..............\n ..........Total failed requests: ")
    f.write(str(len(failed_requests)) + "\n")
    f.write(str(failed_requests))
    f.close()
    
    #creating a report........
    wb = report_creator.prepare_report("Starbucks_test.xls",stores_dict_list)
    return wb

if __name__ == "__main__": 
    starbucks_report_us( ) 
    
