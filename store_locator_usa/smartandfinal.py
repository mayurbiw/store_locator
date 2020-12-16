import json
import requests
import report_creator
import sys
import xlwt


def get_stores():
    try:
        
        session_response = requests.post("https://www.smartandfinal.com/api/m_user/sessioninit", verify=False)
        csrf_token = session_response.json()[0]
        cookies = session_response.cookies
        headers = {'x-csrf-token': csrf_token}
        headers['cookie'] = "XSRF-TOKEN="+csrf_token

        
        res = requests.get("https://www.smartandfinal.com/proxy/store/getall?store_type_ids=1,2,3",headers=headers,cookies=cookies,verify= False)
        
        if (res.status_code!=200):
            print("Recieved unexcpected status code........")
            print(res.status_code)
            print(res.content)
            return False
            
        else:
            temp_dict = json.loads(res.content)
            stores_dict = temp_dict.get('stores')
            wb = report_creator.prepare_report('smart and final',stores_dict)
            return wb
  
    except requests.exceptions.Timeout:
        print("----------Requests Timeout--------------")
    
    except requests.exceptions.ConnectionError:
        print("--------Connection Error -------------\n")
    
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    get_stores() 