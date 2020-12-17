from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
import requests
import report_creator
from time import sleep
import xlwt

 
# https://www.verizon.com/stores

city_urls = {}
urls = []
failed_requests = []
stores_dict_list = []
    
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

def handle_failed_requests(failed_requests):
    retry = 0 
    while(retry!=3 and len(failed_requests)>0):
        retry = retry+1
        for url in failed_requests:
            print("handling failed req for url " + url)
            failed_requests.remove(url)
            client = requests.session()
            client.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
            res = client.get(url)
            handle_response(res)
  
def handle_response(res):
    
    try:
        if res.status_code!= 200:
            raise Exception("Status code other than 200...")
        
        soup = BeautifulSoup(res.content, 'html.parser')
        all_script_tags = list(soup.select("head script"))
        script_tag =  (str((all_script_tags[1])))
        stores = re.findall("(?s)(?<=cityJSON = )(.*?)(?=var vzwDL)", script_tag)[0]
        stores_details_dict = json.loads(stores[0:len(stores)-4])
        for store in stores_details_dict['stores']:
            store_det = {}
            #print(store.get('storeName'))
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
        failed_requests.append(res.url)

def get_stores():
    now = datetime.now()
    start_time = now.strftime("%H:%M:%S")
    url = 'https://www.verizon.com/stores/'
    client = requests.session()
    client.cookies.clear()
    #client.get(url) 
    client.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    res = client.get(url)
    
    if res.status_code == 200:
        states = find_states(res)
        for state in states:
            getCity(state)
            
        for city in city_urls:
            url_city = f'https://www.verizon.com{city_urls[city]}'  
            res = client.get(url_city)
            handle_response(res)
                
    else:
        print("Status code returned was" +res.status_code)
    
    
    handle_failed_requests(failed_requests)
    # time taking to complete the script. 
    now = datetime.now()
    end_time = now.strftime("%H:%M:%S")
    print(start_time)
    print(end_time)
    
    # logging failed requests.....................
    f = open("verizon1.log", "a")
    f.write("\n ...............Failed urls..............\n ..........Total failed requests: ")
    
    f.write(str(len(failed_requests)) + "\n")
    f.write(str(failed_requests) + "\n")
    f.close()
    
    wb = report_creator.prepare_report('verizon',stores_dict_list)
    
    if wb is not None:
        return wb
    else:
        False

if __name__ == "__main__":
    get_stores()
 