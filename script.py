import urllib.request 
import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
from urllib3.exceptions import InsecureRequestWarning 

days_recency=14
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

vgm_url = "https://www.discgolfscene.com/tournaments/2021_NOVA_Disc_Golf_Association_Membership_Drive_2021/registration"

html_text = requests.get(vgm_url).text
soup = BeautifulSoup(html_text, 'html.parser')
combined_recent_wins = pd.DataFrame([])
combined_all_wins = pd.DataFrame([])
for link in soup.find_all('a'):
    linktext=link.get('href')
    match=re.findall("(www\.pdga\.com\/player\/\d+)",str(linktext))
    if len(match)>0:
        pdga_page=match[0]
        pdga_page = "http://"+pdga_page
        try:
            html_text = requests.get(pdga_page, verify=False).text     
            soup = BeautifulSoup(html_text, 'html.parser')
            person=re.findall("\"([^\"]+)\" property\=\"og:title\"",str(soup))    
            try:
                if type(person)==list:
                    person=person[0]
            except:
                pass
        except:
            pass
        wins_page = pdga_page+"/wins"
        try:
            r = requests.get(wins_page, verify=False)
            df=[]
            df_list = pd.read_html(r.text) # this parses all the tables in webpages to a list
            df = df_list[0]
            df['name']=person
            df['Final_Date']=df['Dates'].str.extract(r'(?:^| to )(\d{2}\-\w+\-\d{4})')
            df['Final_Date_obj']=pd.to_datetime(df['Final_Date'])
            df['days_ago_delta']=pd.to_datetime("today") - df['Final_Date_obj']
            df['days_ago_int']=df['days_ago_delta'].dt.days
            
            combined_all_wins=combined_all_wins.append(df)
            recent_wins = df[df['days_ago_int'] < days_recency]
            del recent_wins['days_ago_int']
            del recent_wins['Final_Date_obj']
            del recent_wins['Dates']
            del recent_wins['days_ago_delta']
            del recent_wins['Tier']
            del recent_wins['Prize']
            if len(recent_wins)>0:
                combined_recent_wins = combined_recent_wins.append(recent_wins)
        except:
            pass

pd.set_option('display.max_columns', None)  
pd.set_option('display.max_rows', None)
combined_all_wins=combined_all_wins.sort_values(by=['days_ago_int'])
combined_all_wins
