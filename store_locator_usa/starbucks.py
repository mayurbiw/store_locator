import grequests
import xlrd
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import time
import xlwt
from time import sleep
import sys, os


wb = xlwt.Workbook()
ws = wb.add_sheet('Starbucks',cell_overwrite_ok = True)

widths = [40,50,15,6,12,12,14,14]

for col_number , w in enumerate(widths):
    ws.col(col_number).width = 256*w 

ws.write(0, 0, 'Store Name')
ws.write(0, 1, 'Street Address')
ws.write(0, 2, 'City')
ws.write(0, 3, 'State')
ws.write(0, 4, 'Zip Code')
ws.write(0, 6, 'Longitude')
ws.write(0, 5, 'Phone Number')
ws.write(0, 7, 'Latitude')


row_index = 1
    
all_stores_us_id = [] 
all_stores_us_id_dict = {}

failed_requests = []

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
        #if i == 20:
         #  break
        z = sheet.cell_value(i, 0)
        # break when encounter empty cell
        if z == '':
            break
        url =  'https://www.starbucks.com/store-locator?place='+z
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
        return store_details_dict['previousAction']['payload']['data']['paging']['returned']

def exception_handler(request, exception):
    f = open("starbucks.log", "a")
    f.write("\n ...............Error..............\n")
    f.write(str(exception))
    f.close()
    failed_requests.append(request.url)
   
def handle_res(res,**kwargs):
    global ws
    global row_index
    
    if res is None:
        return

    #print(res.url)
    
    
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, 'html.parser')
        all_script_tags = list(soup.select("body script"))
        # get the script tag where json object corresponding to all 100 stores is located. 
        stores =  (str((all_script_tags[3])))
        #print(store_details)
        
        # get the json that contains store details.
        store_details = re.findall("(?s)(?<=window.__BOOTSTRAP = )(.*?)(?=window.__INTL_MESSAGES)", stores)
        # find all retuns the list of matches, above it will always return one recoed. 
        
        # converting json respod into python dictionary.
        store_details_dict = json.loads(str(store_details[0]))
        #print(store_details_dict)
        #finding number of records returned by the api call 
        
        #returned = store_details_dict['previousAction']['payload']['data']['paging']['returned']
        returned = stores_returned(store_details_dict)
        
        if returned == 0:
            return

        for i in range(0,returned):
            store = store_details_dict['previousAction']['payload']['data']['stores'][i]
            
            if store is None:
                continue
            
            #consider using hashtable inplace of a list.
            if all_stores_us_id_dict.get(store['id']) is None:
                
                # handling the case where no postal code is provided by starbucks.
                if store.get('address').get('postalCode') is None:
                    zip = res.url[46:]
                else:
                    zip = store.get('address').get('postalCode')[0:5]
                    
                all_stores_us_id_dict[store['id']] = True
                
                ws.write(row_index, 0, store.get('name'))
                ws.write(row_index,1, store.get('address').get('streetAddressLine1'))
                ws.write(row_index,2,store.get('address').get('city'))
                ws.write(row_index,3,store.get('address').get('countrySubdivisionCode'))
                ws.write(row_index,4,zip)
                ws.write(row_index,5,store.get('phoneNumber'))
                ws.write(row_index,6,store.get('coordinates').get('longitude'))
                ws.write(row_index,7,store.get('coordinates').get('latitude'))
                row_index = row_index + 1 
                
            #all_stores_us[store['id']] = s
            #global all_stores_us_id
             
            
        res.close()
    else:
        print(res.status_code)                                                                                                                 
    
    return None

def starbucks_report_us():

    all_stores_us = {}
    urls = []
    loc = ("/home/mayur/practice_projects/store_locator/zip_code_details.xls")

    now = datetime.now()
    start_time = now.strftime("%H:%M:%S")

    prepare_urls(loc,urls)
    
    print("Number of urls to hit "  + str(len(urls)))
    
    MAX_CONNECTIONS = 100
    for x in range(0,len(urls), MAX_CONNECTIONS):
        #print(f"URLS range {x} to {x + MAX_CONNECTIONS}" )
        
        #print("For the specific range started at " + str(datetime.now().strftime("%H:%M:%S")))
        
        rs = (grequests.get(u, hooks = {'response' : handle_res} ,stream=False) for u in urls[x:x+MAX_CONNECTIONS])
        
        # making all the reqest at once. 
        responses = grequests.map(rs,exception_handler=exception_handler)
        responses = None
        #sleep(1)
        
      
       
    
    #print(all_stores_us)
    
    #print("Uniques stores found "+str(len(all_stores_us_id)))

    now = datetime.now()
    end_time = now.strftime("%H:%M:%S")

    print(start_time)
    print(end_time)

    f = open("starbucks.log", "a")
    f.write("\n ...............Failed urls..............\n ..........Total failed requests: ")
    
    f.write(str(len(failed_requests)) + "\n")
    
    f.write(str(failed_requests))
    f.close()
    
    return wb
    #wb.save("Starbucks.xls")


if __name__ == "__main__": 
    starbucks_report_us() 
    
