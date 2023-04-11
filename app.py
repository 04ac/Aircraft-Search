import numpy as np
import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

st.set_page_config(layout="wide")

st.title("Aircraft Search")

aircraft_code = st.text_input(label="Enter Aircraft Registration:").upper()

from bs4 import BeautifulSoup
import requests

if st.button("Search"):

    HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62'
        }
    html_text = requests.get("https://flightaware.com/resources/registration/" + aircraft_code, headers=HEADERS).text

    soup = BeautifulSoup(html_text, 'lxml')

    info = soup.find('div', class_="pageContainer")
    f = info.findAll('div', class_='attribute-row')

    def remove_delimiters(word):
        h = []
        for i in word:
            if i != '\n' and i != '\t':
                h.append(i)
        return "".join(h)


    d = {}
    for i in f:
        d[i.find('div', class_='medium-1 columns title-text').text] = remove_delimiters(i.find('div', class_='medium-3 columns').text.replace('\n', ' '))

    flag = 0
    if not len(d.items()) == 0:
        flag = 1
        st.subheader("Aircraft Information:")
        df = pd.DataFrame(d.items()).rename(columns={0:'Categories', 1:'Information'})
        AgGrid(df, columns_auto_size_mode=2)


    if flag == 0:
        st.subheader("Aircraft Information:")

    ac2 = aircraft_code.upper()
    req = requests.get("https://www.flightera.net/en/planes/"+ac2, headers=HEADERS)
    html_text = req.content



    if req.status_code < 300:
        soup2 = BeautifulSoup(html_text, 'lxml')
        info2 = soup2.find('div', class_='mx-auto flex max-w-7xl')
        f = info2.find('div', class_='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8')
        g = f.find('h1',class_='text-xl font-bold leading-tight text-gray-900 dark:text-white').text

        st.text('Aircraft - ' + remove_delimiters(g))

        i = info2.find('dl', class_='grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2 lg:grid-cols-3')
        j = i.find('div', class_='mx-auto mb-4 sm:border-l')
        k = j.find_all('td', class_='text-gray-700 dark:text-gray-200 text-sm py-2 font-medium pr-2')
        l = j.find_all('td', class_='text-gray-900 dark:text-white py-2 text-sm')

        d = dict(zip(k, l))

        for k, v in d.items():
            st.text(f"{k.text.strip()}: {v.text.strip()}")
    else:
        st.text("Not Available")


    if req.status_code < 300:
        tables = pd.read_html(html_text)
        df0 = tables[0]
        df0.rename(columns={0:"Item", 1:"Information"}, inplace=True)
        AgGrid(df0, columns_auto_size_mode=2)
    else:
        st.text("Not Available")



    import json
    import urllib.request
    from PIL import Image

    js = requests.get("https://api.planespotters.net/pub/photos/reg/"+aircraft_code)
    data = json.loads(js.text)
    if not len(data['photos']) == 0:
        urllib.request.urlretrieve(data['photos'][0]['thumbnail_large']['src'],"a.png")
        img = Image.open("a.png")
        st.image(img)


    st.subheader("Past Flights (If any):")
    if req.status_code < 300:
        if len(tables) < 3:
            st.text("No past flights found")
        else:
            # Drop last column
            df1 = tables[2].iloc[:,:-1]
            
            if 'TO' in df1.keys().tolist():
                i=0
                # Clean up data in 'FROM' column
                for item in df1['FROM']:
                    l = []
                    for le in item:
                        l.append(le)
                        if le == ')':
                            break
                    df1['FROM'][i] = "".join(l)
                    i+=1

                i=0
                # Clean up data in 'TO' column
                for item in df1['TO']:
                    l = []
                    for le in item:
                        l.append(le)
                        if le == ')':
                            break
                    df1['TO'][i] = "".join(l)
                    i+=1
                AgGrid(df1, columns_auto_size_mode=2)
            else:
                st.text("No past flights found")
    else:
        st.text("No past flights found")