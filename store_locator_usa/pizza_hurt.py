from bs4 import BeautifulSoup
from datetime import datetime
import requests
import report_creator
#from . import report_creator
from time import sleep
import xlrd
import xlwt

def get_lon_and_lat(zip_code):
    LOC = ("/home/mayur/practice_projects/store_locator/zip_code_details.xls")
    wb = xlrd.open_workbook(LOC)
    sheet = wb.sheet_by_index(0)
    sheet.cell_value(0, 0)
    for i in range(1,sheet.nrows):
        if sheet.cell_value(i, 0) == zip_code:
            return (sheet.cell_value(i,2),sheet.cell_value(i,1)) 

def get_states():
    states = []
    res = requests.get("https://locations.pizzahut.com/")
    #print(res.status_code)
    soup = BeautifulSoup(res.content, 'html.parser')
    states_ul = soup.find("ul", {"class": "Directory-listLinks"})
    states_a = states_ul.findAll("a")
    for s in states_a:
        if '/' in s["href"]:
            ind = s["href"].index("/") 
            states.append(s["href"][0:ind])
        else:
            states.append(s["href"])

    return states

def get_stores():
    stores_dict_list = []
    now = datetime.now()
    start_time = now.strftime("%H:%M:%S")

    city_urls = {}

    states = get_states()
    
    print(states)
    for state in states:
        
        print("https://locations.pizzahut.com/"+state)
        
        res = requests.get("https://locations.pizzahut.com/"+state)

        soup = BeautifulSoup(res.content, 'html.parser')
        cities_ul = soup.find("ul", {"class": "Directory-listLinks"})

        city_a = cities_ul.findAll("a")
        
        for a in  city_a:
            city_urls[a.get_text()] = a['href']


        res.close()

    
    for city in city_urls:
        #print("inside for")
        url = f"https://locations.pizzahut.com/{city_urls[city]}"
        try:
            
            res = requests.get(url)
            if res.status_code == 200:
                #print(url)
                soup = BeautifulSoup(res.content, 'html.parser')
                stores_li = soup.findAll("li", {"class": "Directory-listTeaser"})

                for store in stores_li:
                    
                    store_det = {}
                    
                    store_det['storeName'] = 'Pizza Hut'
                    store_det['address'] = store.find("span",{"class":"LocationName-geo"}).get_text()
                    store_det['city'] = store.find("span",{"class":"c-address-city"}).get_text()
                    store_det['state'] = store.find("abbr",{"class":"c-address-state"})['title']
                    store_det['zip'] = store.find("span",{"class":"c-address-postal-code"}).get_text()
                    store_det['phone'] = store.find("a",{"class":"c-phone-main-number-link"})
                    
                    if store_det.get('phone') is not None:
                        store_det['phone'] = store_det['phone'].get_text()
                    
                    cord = get_lon_and_lat(store_det['zip'])
                    
                    lng = cord[0]
                    ltd = cord[1]
                    
                    store_det['longitude'] = lng
                    store_det['latitude'] = ltd
                    
                    #print(store_det['address'])

                    #adding in main dictionary......
                    stores_dict_list.append(store_det)
        except:
            print(f"failed request for url...{url}")
        
 
        
    #print(len(stores_li))

    now = datetime.now()
    end_time = now.strftime("%H:%M:%S")

    print(start_time)
    print(end_time)

    wb = report_creator.prepare_report("pizza hut test",stores_dict_list)   
    return wb       
    

if __name__ == "__main__":
    get_stores()


