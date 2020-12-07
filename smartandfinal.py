import sys
import requests

import json
 

url = 'https://www.smartandfinal.com/stores/'

client = requests.session()

#x-csrf-token

# Retrieve the CSRF token first
client.get(url)  # sets cookie


#print(client.headers)


client.headers['x-csrf-token'] = '404da41ade04039770b860bfdfc6211af72108935ca5d2284a299525665241f3'
client.headers['cookie'] = '__cfduid=d60830d90c5506b0ea2679a8ac86360b81607086168; has_js=1; _ga=GA1.2.2002522175.1607086170; Srn-Auth-Token=762609da7a0bf6eebc7a0407e9faebc4b67c3276a84401be49cab82b700ae7cc; _fbp=fb.1.1607086171411.1825843387; OptanonAlertBoxClosed=2020-12-04T12:49:37.033Z; SSESS04126c102d66b37b4b663fc1a54abd9a=KzZ_zgBbDI3t4FEpJPUp4-RAp1TvMVAuYVleeV3nK4s; Thin-Proxy=1; __gads=ID=2af4c9e420f2c599:T=1607164491:S=ALNI_MYzRr1vB9wNZeqY1kf57vwJmTnmJg; _gid=GA1.2.1902862254.1607335521; _uetsid=b7ae8a50387311ebab2569b3e81baa9e; _uetvid=26fe4110362f11ebabae9924fddfcfb0; XSRF-TOKEN=404da41ade04039770b860bfdfc6211af72108935ca5d2284a299525665241f3; OptanonConsent=isIABGlobal=false&datestamp=Mon+Dec+07+2020+17%3A45%3A51+GMT%2B0530+(India+Standard+Time)&version=6.2.0&landingPath=NotLandingPage&groups=C0002%3A1%2CC0004%3A1%2CC0001%3A1%2CC0003%3A1&hosts=&legInt=&geolocation=%3B&AwaitingReconsent=false'

res = client.get("https://www.smartandfinal.com/proxy/store/getall?store_type_ids=1,2,3"
)

#print(client.cookies)

#print(res.text)

#res = requests.post("https://www.smartandfinal.com/proxy/store/getall?store_type_ids=1,2,3",data=login_data,headers=dict(Referer=URL))

#print((res.content))

stores_dict = json.loads(res.content)


if int(stores_dict['success']) == 1:

    for store in stores_dict['stores']:
        print(store['storeName'])



#print(stores_dict['storeCount'])



#print(str(client.cookies.get_dict()))