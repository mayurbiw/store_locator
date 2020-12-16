from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
import requests
import report_creator
from time import sleep
import xlwt

f = open("verizon.log", "a")
f.write("\n ...............Error..............\n")
 
# https://www.verizon.com/stores

city_urls = {}

urls = []

    
def getCity(state):
    tried = 0 
    try:
        while(tried == 0):
            url = "https://www.verizon.com/stores/" + state + "/#/state" 
            client = requests.session()
            client.get(url,timeout = 3) 
            client.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
            res = client.get(url)
            soup = BeautifulSoup(res.content, 'html.parser')
            all_script_tags = list(soup.select("head script"))
            cities_script_tag =  (str((all_script_tags[1])))
            print(state)
            cities = re.findall("(?s)(?<=stateJSON = )(.*?)(?=var vzwDL)", cities_script_tag)[0]
            
            cities_details_dict = json.loads(cities[0:len(cities)-4])
            tried = 1
        for city in cities_details_dict['cities']:
            city_urls[city['name']] = city["url"]
    except:
        print("connection aborted ..retrying after sleeep...")
        sleep(5)

    
def find_states(res):
    states = []
    soup = BeautifulSoup(res.content, 'html.parser')
    store_list = soup.find("ul", {"class": "u-marginAll--0 u-flex u-flexWrap u-flexColumn height--xs640 height--md318 u-paddingAll--0 u-text--xs16 u-text--md20"})
    links = store_list.findAll("a")
    for link in links:
        states.append(link.getText())   
    return states

def get_stores():
    stores_dict_list = []
    now = datetime.now()
    start_time = now.strftime("%H:%M:%S")
    url = 'https://www.verizon.com/stores/'
    client = requests.session()
    client.cookies.clear()
    client.get(url) 
    client.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    res = client.get(url)
    
    if res.status_code == 200:
        states = find_states(res)
        for state in states:
            getCity(state)
        
        print("preparing urls.........")
        for city in city_urls:
            url = f'https://www.verizon.com{city_urls[city]}' 
            urls.append(url )
            
        for city in city_urls:
            try:
                url = f'https://www.verizon.com{city_urls[city]}'  
                res = client.get(url)
                if res is None:
                    return
                soup = BeautifulSoup(res.content, 'html.parser')
                all_script_tags = list(soup.select("head script"))
                script_tag =  (str((all_script_tags[1])))
                stores = re.findall("(?s)(?<=cityJSON = )(.*?)(?=var vzwDL)", script_tag)[0]
                stores_details_dict = json.loads(stores[0:len(stores)-4])
                for store in stores_details_dict['stores']:
                    store_det = {}
                    print(store.get('storeName'))
                    store_det['storeName'] = store.get('storeName')
                    store_det['address'] = store.get('address')
                    store_det['city'] = store.get('city') 
                    store_det['state'] = store.get('state')
                    store_det['zip'] = store.get('zip')
                    store_det['phone'] = store.get('phone')
                    store_det['longitude'] =   store.get('lat')
                    store_det['latitude'] = store.get('lng')
                    stores_dict_list.append(store_det)
                res.close()
            
            except:
                f.write(f"Error for url = https://www.verizon.com{city_urls[city]}")
                print(f"Error for url =   +https://www.verizon.com{city_urls[city]}")


        
    else:
        print("something went wrong...")
        f.write("Something went wrong....")

        
    now = datetime.now()
    end_time = now.strftime("%H:%M:%S")
    print(start_time)
    print(end_time)
    f.close()
    wb = report_creator.prepare_report('verizon',stores_dict_list)
    return wb

if __name__ == "__main__":
    get_stores()
 