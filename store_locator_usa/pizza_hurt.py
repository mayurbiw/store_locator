from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path 
import requests
import report_creator
from time import sleep
import xlrd
import xlwt

LOC = Path(__file__).resolve().parent.parent / 'zip_code_details.xls'
stores_dict_list = []
failed_requests = []

def get_lon_and_lat(zip_code):
    wb = xlrd.open_workbook(LOC)
    sheet = wb.sheet_by_index(0)
    sheet.cell_value(0, 0)
    for i in range(1,sheet.nrows):
        if sheet.cell_value(i, 0) == zip_code:
            return (sheet.cell_value(i,2),sheet.cell_value(i,1)) 

def get_states():
    states = []
    
    try:
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

    
    except requests.exceptions.Timeout:
        print("----------Requests Timeout--------------")
    
    except requests.exceptions.ConnectionError:
        print("--------Connection Error -------------\n")
    
    except Exception as e:
        print(str(e))
    
    finally:
        return states

def handle_failed_requests(failed_requests):
    retry = 0 
    while(retry!=3 and len(failed_requests)>0):
        retry = retry+1
        for url in failed_requests:
            #print("handling failed req for url " + url)
            res = requests.get(url)
            failed_requests.remove(url)
            handle_response(res)
  
def handle_response(res):
    try:
    
        if res.status_code!= 200:
                raise Exception("Status code other than 200...")
        
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
            #adding in main dictionary......
            stores_dict_list.append(store_det)
    
    except:
        failed_requests.append(res.url)

def get_stores():
    now = datetime.now()
    start_time = now.strftime("%H:%M:%S")

    city_urls = {}

    states = get_states()
    
    #print(states)

    for state in states:
        state_url = f"https://locations.pizzahut.com/{state}" 
        #print(state_url)
        tried = 0 
        while(tried==0):
            try:
                res = requests.get(state_url)
                soup = BeautifulSoup(res.content, 'html.parser')
                cities_ul = soup.find("ul", {"class": "Directory-listLinks"})
                city_a = cities_ul.findAll("a")
                for a in  city_a:
                    city_urls[a.get_text()] = a['href']
                res.close()
                tried = 1
            
            except requests.exceptions.Timeout:
                print("----------Requests Timeout for--------------")
                print(state_url)
            
            except requests.exceptions.ConnectionError:
                print("--------Connection Error for -------------\n")
                print(state_url)
        
            except Exception as e:
                print(str(e))
    
    for city in city_urls:
        url = f"https://locations.pizzahut.com/{city_urls[city]}"
        try:
            res = requests.get(url)
            handle_response(res)
                
        except requests.exceptions.Timeout:
            print("----------Requests Timeout--------------")
            failed_requests.append(url)
        
        except requests.exceptions.ConnectionError:
            print("--------Connection Error -------------\n")
            failed_requests.append(url)
    
        except Exception as e:
            print(str(e))
            failed_requests.append(url)
        
    handle_failed_requests(failed_requests)
    
    now = datetime.now()
    end_time = now.strftime("%H:%M:%S")

    print(start_time)
    print(end_time)
    
    # logging failed requests.....................
    f = open("pizza hut.log", "a")
    f.write("\n ...............Failed urls..............\n ..........Total failed requests: ")
    
    f.write(str(len(failed_requests)) + "\n")
    f.write(str(failed_requests) + "\n")
    f.close()
    
    wb = report_creator.prepare_report("pizza hut test",stores_dict_list)   
    if wb is not None:
        return wb
    else:
        False   
    
if __name__ == "__main__":
    get_stores()

