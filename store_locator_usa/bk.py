from datetime import datetime
import json
import requests
import report_creator
from time import sleep
import xlrd
import xlwt


def get_stores():
    stores_dict_list = []
        
    try:
        res = requests.get("https://czqk28jt.apicdn.sanity.io/v1/data/query/prod_bk_us?query=*%5B%20_type%20%3D%3D%20%27restaurant%27%20%26%26%20environment%20%3D%3D%20%24environment%20%26%26%20!(%24appEnvironemnt%20in%20coalesce(hideInEnvironments%2C%20%5B%5D))%20%26%26%20latitude%20%3E%20%24minLat%20%26%26%20latitude%20%3C%20%24maxLat%20%26%26%20longitude%20%3E%20%24minLng%20%26%26%20longitude%20%3C%20%24maxLng%20%26%26%20status%20%3D%3D%20%24status%20%5D%20%7Corder((%24userLat%20-%20latitude)%20**%202%20%2B%20(%24userLng%20-%20longitude)%20**%202)%5B%24offset...(%24offset%20%2B%20%24limit)%5D%20%7B_id%2CchaseMerchantId%2CdeliveryHours%2CdiningRoomHours%2CcurbsideHours%2CdrinkStationType%2CdriveThruHours%2CdriveThruLaneType%2Cemail%2CfranchiseGroupId%2CfranchiseGroupName%2CfrontCounterClosed%2ChasBreakfast%2ChasBurgersForBreakfast%2ChasCurbside%2ChasDineIn%2ChasCatering%2ChasDelivery%2ChasDriveThru%2ChasMobileOrdering%2ChasParking%2ChasPlayground%2ChasTakeOut%2ChasWifi%2CisDarkKitchen%2Clatitude%2Clongitude%2CmobileOrderingStatus%2Cname%2Cnumber%2CparkingType%2CphoneNumber%2CphysicalAddress%2CplaygroundType%2Cpos%2CposRestaurantId%2CrestaurantPosData-%3E%7B_id%7D%2Cstatus%2CrestaurantImage%7B...%2C%20asset-%3E%7D%7D&%24appEnvironemnt=%22prod%22&%24environment=%22prod%22&%24limit=10000&%24maxLat=71.390000000000000&%24maxLng=-66.73698707245619&%24minLat=5.50920085530348&%24minLng=-179.27332119571551&%24offset=0&%24status=%22Open%22&%24userLat=40.7127753&%24userLng=-74.0059728")
        if res.status_code == 200:
            temp_dict = json.loads(res.content)
            stores_dict = temp_dict.get('result')

            for store in stores_dict:
                store_det = {}
                #print(store['name'])
                store_det['storeName'] = store.get('name')
                store_det['address'] = store.get('physicalAddress').get('address1')
                store_det['city'] = store.get('physicalAddress').get('city')
                store_det['state'] = store.get('physicalAddress').get('stateProvince')

                store_det['zip'] = store.get('physicalAddress').get('postalCode')
                if  store_det['zip'] is not None:
                    store_det['zip'] = store_det['zip'][0:5]
                
                store_det['phone'] = store.get('phoneNumber')
                store_det['longitude'] = store.get('latitude')
                store_det['latitude'] = store.get('longitude')
                
                #adding in main dictionary......
                stores_dict_list.append(store_det)
        else:
            print(f"Something went wtrong the returned status code = {res.status_code}")
    
    except requests.exceptions.Timeout:
        print("----------Requests Timeout--------------")
    
    except requests.exceptions.ConnectionError:
        print("--------Connection Error -------------\n")
    
    except Exception as e:
        print(str(e))
    
    wb = report_creator.prepare_report('Burger King',stores_dict_list)
    if wb is not None:
        return wb
    else:
        return False

        

if __name__ == "__main__":
    get_stores()