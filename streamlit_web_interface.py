import re
import cv2
import json
import urllib.request
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import streamlit as st
import st_aggrid
from PIL import Image
import easyocr
import random
import time


def remove_delimiters(word):
    _ = []
    for i in word:
        if i != "\n" and i != "\t":
            _.append(i)
    return "".join(_)


def get_website(site_link, reg_no):
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=0.5))
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    _request = session.get(site_link + reg_no)
    return _request.status_code, _request.text


def aircraft_details_query(reg_no):
    st.title(reg_no)
    data_not_found_flag = [False, False]

    req = get_website(
        "https://api.planespotters.net/pub/photos/reg/", reg_no)
    if req[0] > 300:
        st.text("Aircraft image not available")
    else:
        data = json.loads(req[1])
        if not len(data["photos"]) == 0:
            # Load and display aircraft image
            with urllib.request.urlopen(data["photos"][0]["thumbnail_large"]["src"]) as image_url:
                st.text("Aircraft Image:")
                aircraft_image = Image.open(image_url)
                st.image(aircraft_image)
        else:
            st.text("Aircraft image not available")

    req = get_website(
        "https://flightaware.com/resources/registration/", reg_no)

    if req[0] > 300:
        data_not_found_flag[0] = True
    else:
        soup = BeautifulSoup(req[1], "lxml")
        info = soup.find("div", class_="pageContainer")
        f = info.findAll("div", class_="attribute-row")

        _dict = {}
        for i in f:
            _dict[i.find("div", class_="medium-1 columns title-text").text] = remove_delimiters(
                i.find("div", class_="medium-3 columns").text.replace("\n", " "))

        if len(_dict.items()) > 0:
            df = pd.DataFrame(_dict.items()).rename(
                columns={0: "Categories", 1: "Information"})
            st_aggrid.AgGrid(df, columns_auto_size_mode=2)
        else:
            data_not_found_flag[0] = True

    req = get_website("https://www.flightera.net/en/planes/", reg_no)
    if req[0] > 300:
        data_not_found_flag[1] = True
        if data_not_found_flag[0] is True:
            st.text("Aircraft details not found")
    else:
        st.subheader("Further Information: \n")
        html = req[1]
        soup2 = BeautifulSoup(html, "lxml")
        info2 = soup2.find("div", class_="mx-auto flex max-w-7xl")
        f = info2.find("div", class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8")
        g = f.find(
            "h1", class_="text-xl font-bold leading-tight text-gray-900 dark:text-white").text

        st.text("Aircraft: " + remove_delimiters(g))

        i = info2.find(
            "dl", class_="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2 lg:grid-cols-3")
        j = i.find("div", class_="mx-auto mb-4 sm:border-l")
        k = j.find_all(
            "td", class_="text-gray-700 dark:text-gray-200 text-sm py-2 font-medium pr-2")
        l = j.find_all(
            "td", class_="text-gray-900 dark:text-white py-2 text-sm")

        _dict = dict(zip(k, l))

        for k, v in _dict.items():
            st.text(f"{k.text.strip()}: {v.text.strip()}")

        tables = pd.read_html(html)
        df0 = tables[0]
        df0.rename(columns={0: "Item", 1: "Information"}, inplace=True)
        st_aggrid.AgGrid(df0, columns_auto_size_mode=2)

        if data_not_found_flag[0] is True and data_not_found_flag[1] is True:
            st.text("Aircraft details not found")

        st.subheader("Past Flights (If any):")
        if len(tables) < 3:
            st.text("No past flights found")
        else:
            # Drop last column
            _df = tables[2].iloc[:, :-1]

            if "TO" in _df.keys().tolist():
                i = 0
                # Clean up data in "FROM" column
                for item in _df["FROM"]:
                    l = []
                    for le in item:
                        l.append(le)
                        if le == ")":
                            break
                    _df["FROM"][i] = "".join(l)
                    i += 1

                i = 0
                # Clean up data in "TO" column
                for item in _df["TO"]:
                    l = []
                    for le in item:
                        l.append(le)
                        if le == ")":
                            break
                    _df["TO"][i] = "".join(l)
                    i += 1
                st_aggrid.AgGrid(_df, columns_auto_size_mode=2)
            else:
                st.text("No past flights found")


def display_fun_facts():
    # Fun Facts adapted from https://www.flightcentre.com.au/
    fun_facts = ["KLM Royal Dutch Airlines is the world's oldest airline, established in 1919.",
                 "In 1987 American Airlines saved $40,000 by removing one olive from each salad served in first class.",
                 "An aircraft takes off or lands every 37 seconds at Chicago O’Hare International Airport.",
                 "The wing-span of the Airbus A380 is longer than the aircraft itself. Wingspan is 80m, the length is 72.7m",
                 "Singapore Airlines spends approximately $700 million on food every year and $16 million on wine.",
                 "Travelling by air can shed up to 1.5 litres of water from the body during an average 3-hour flight.",
                 "German airline Lufthansa is the world's largest purchaser of caviar, buying over 10 tons per year.",
                 "The Boeing 747 wing-span (195 ft) is longer than the Wright Brothers' entire first flight (120 ft).",
                 "The winglets on an Airbus A330-200 are the same height as the world's tallest man (2.4m).",
                 "The Boeing 747 family has flown more than 5.6 billion people - equivalent to 80% of the world's population.",
                 "The average Boeing 747 has a whopping 240-280 kilometres of electrical wiring",
                 "In the USA, over two million passengers board over 30,000 flights each day."]

    time.sleep(1.5)
    st.markdown("####")
    st.markdown("#### While you wait -- Aviation Fun Fact:\n")
    st.text(random.choice(fun_facts))


st.set_page_config(layout="wide")
st.title("Aircraft Search")
aircraft_code = st.text_input(
    label="Enter aircraft registration number:", placeholder="Example:  F-OVAA").upper().strip()
uploaded_file = st.file_uploader(
    "Or upload an image and click on Search:", type=["jpg", "png", "jpeg"])

if st.button("Search"):
    if aircraft_code != "":
        display_fun_facts()
        aircraft_details_query(aircraft_code)

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        # Converts PIL image to OpenCv
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        # Display scaled image if size is too large
        st.text("Uploaded Image:")
        if img.shape[0] > 600 or img.shape[1] > 600:
            w, h, c = img.shape
            sf = 400 / w
            img2 = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
                              None, fx=sf, fy=sf, interpolation=cv2.INTER_AREA)
            st.image(img2)
        else:
            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        display_fun_facts()

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        reader = easyocr.Reader(["en"], gpu=True)
        text_list = list(reader.readtext(img, detail=0))

        # Remove Duplicates
        list_without_duplicates = []
        for code in text_list:
            if code not in list_without_duplicates:
                list_without_duplicates.append(code)

        # list_without_duplicates
        for code in list_without_duplicates:
            code = code.upper()
            # Substitute underscores for hyphens
            code = code.replace("_", "-")
            # Remove all characters that are not hyphens or alphanumeric
            code_with_only_alphanumeric_characters_and_hyphens = re.sub("[^\w-]", "", code)
            # Possible prefixes without hyphens: "HL, N, UK, JA, UR(with or without), HI"
            pattern = r"\w{1,4}-\w+|HL\w{4}|N\d{1,3}\w{2}|N\d{1,5}|UK\d{5}|JA\w{4}|UR\d{5}|HI\w{3,4}"
            matches = re.findall(pattern, code_with_only_alphanumeric_characters_and_hyphens)
            if len(matches) > 0:
                if len(matches[0]) == len(code):
                    aircraft_details_query(code)
                    st.markdown("---")

    if aircraft_code == "" and uploaded_file is None:
        st.markdown("#### Please enter a valid aircraft registration number or upload an image.")
