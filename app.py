import numpy as np
import streamlit as st
import pandas as pd
import cv2
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

st.set_page_config(layout="wide")

st.title("Aircraft Search")

aircraft_code = st.text_input(label="Enter Aircraft Registration:").upper()

from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def aircraft_search(ac):
    HEADERS = {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62'
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
    }

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    html_text = session.get("https://flightaware.com/resources/registration/" + ac).text

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
        d[i.find('div', class_='medium-1 columns title-text').text] = remove_delimiters(
            i.find('div', class_='medium-3 columns').text.replace('\n', ' '))

    flag = 0
    if not len(d.items()) == 0:
        flag = 1
        st.subheader("Aircraft Information:")
        df = pd.DataFrame(d.items()).rename(columns={0: 'Categories', 1: 'Information'})
        AgGrid(df, columns_auto_size_mode=2)

    if flag == 0:
        st.subheader("Aircraft Information:")

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    req = session.get("https://www.flightera.net/en/planes/" + ac)
    html_text = req.text

    if req.status_code < 300:
        soup2 = BeautifulSoup(html_text, 'lxml')
        info2 = soup2.find('div', class_='mx-auto flex max-w-7xl')
        f = info2.find('div', class_='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8')
        g = f.find('h1', class_='text-xl font-bold leading-tight text-gray-900 dark:text-white').text

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
        df0.rename(columns={0: "Item", 1: "Information"}, inplace=True)
        AgGrid(df0, columns_auto_size_mode=2)
    else:
        st.text("Not Available")

    import json
    import urllib.request
    from PIL import Image

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    js = session.get("https://api.planespotters.net/pub/photos/reg/" + ac).text
    data = json.loads(js)
    if not len(data['photos']) == 0:
        urllib.request.urlretrieve(data['photos'][0]['thumbnail_large']['src'], "a.png")
        img = Image.open("a.png")
        st.image(img)

    st.subheader("Past Flights (If any):")
    if req.status_code < 300:
        if len(tables) < 3:
            st.text("No past flights found")
        else:
            # Drop last column
            df1 = tables[2].iloc[:, :-1]

            if 'TO' in df1.keys().tolist():
                i = 0
                # Clean up data in 'FROM' column
                for item in df1['FROM']:
                    l = []
                    for le in item:
                        l.append(le)
                        if le == ')':
                            break
                    df1['FROM'][i] = "".join(l)
                    i += 1

                i = 0
                # Clean up data in 'TO' column
                for item in df1['TO']:
                    l = []
                    for le in item:
                        l.append(le)
                        if le == ')':
                            break
                    df1['TO'][i] = "".join(l)
                    i += 1
                AgGrid(df1, columns_auto_size_mode=2)
            else:
                st.text("No past flights found")
    else:
        st.text("No past flights found")


import easyocr
import re
from PIL import Image
uploaded_file = st.file_uploader("Or Upload Image:", type=['jpg', 'png', 'jpeg'])


if st.button("Search"):
    if aircraft_code is not "":
        aircraft_search(aircraft_code)

    if uploaded_file is not None:
        img = cv2.imread('Images/'+uploaded_file.name)
        if img.shape[0] > 600 or img.shape[1] > 600:
            w, h, c = img.shape
            sf = 400/w
            img2 = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), None, fx=sf, fy=sf, interpolation=cv2.INTER_AREA)
            st.image(img2)
        else:
            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        reader = easyocr.Reader(['en'], gpu=True)
        text_list = list(reader.readtext(img, detail=0))
        # text_list
        for item in text_list:
            item = item.upper()
            # Substitute underscores for dashes
            item = re.sub("_", "-", item)
            itemWithOnlyNumbersLettersAndDashes = re.sub("[^\w-]", "", item)
            # Prefixes with no dashes: "HL, N, UK, JA, UR(with or without), HI"
            # + signifies one or more occurrences
            pattern = r"\w+-\w+|HL\w{4}|N\d{1,3}\w{2}|N\d{1,5}|UK\d{5}|JA\w{4}|UR\d{5}|HI\w{3,4}"
            matches = re.findall(pattern, itemWithOnlyNumbersLettersAndDashes)
            if len(matches) != 0:
                if len(matches[0]) == len(item):
                    st.title(item)
                    aircraft_search(item)
