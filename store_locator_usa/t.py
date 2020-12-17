from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
import report_creator
from pathlib import Path 
import sys, os
import time
from time import sleep
import xlrd
import xlwt
import requests

res = requests.get("https://www.starbucks.com/store-locator?place=00601")

soup = BeautifulSoup(res.content, 'html.parser')
all_script_tags = list(soup.select("body script"))


#print(all_script_tags)

store_details = ''
for tag in all_script_tags:
    a = re.search("(?s)(?<=window.__BOOTSTRAP = )(.*?)(?=window.__INTL_MESSAGES)",str(tag))
    if a is not None:
        store_details = a
        store_details = a.group()

print(store_details)
    


#stores =  (str((all_script_tags[3])))
#store_details = re.findall("(?s)(?<=window.__BOOTSTRAP = )(.*?)(?=window.__INTL_MESSAGES)", stores)