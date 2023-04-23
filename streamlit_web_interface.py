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


def remove_delimiters(word):
    _ = []
    for i in word:
        if i != "\n" and i != "\t":
            _.append(i)
    return "".join(_)


def get_website(site_link, regno):
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=0.5))
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    _request = session.get(site_link + regno)
    return (_request.status_code, _request.text)


def aircraft_details_query(reg_no):
    st.title(reg_no)
    st.markdown("---\nAircraft image from planespotters.net:")
    req = get_website(
        "https://api.planespotters.net/pub/photos/reg/", reg_no)
    if req[0] > 300:
        st.text("Image not available")
    else:
        data = json.loads(req[1])
        if not len(data["photos"]) == 0:
            urllib.request.urlretrieve(
                data["photos"][0]["thumbnail_large"]["src"], "a.png")
            img = Image.open("a.png")
            st.image(img)
        else:
            st.text("Image not available")

    st.markdown("---\nQuerying flightaware.com...")
    req = get_website(
        "https://flightaware.com/resources/registration/", reg_no)

    if req[0] > 300:
        st.text("Data not available")
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
            st.text("Data not available")

    st.markdown("---\nQuerying flightera.net...")
    req = get_website("https://www.flightera.net/en/planes/", reg_no)
    if req[0] > 300:
        st.text("Data not available")
    else:
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

        st.markdown("---")
        st.subheader("Past Flights:")
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


st.set_page_config(layout="wide")
st.title("Aircraft Search")
aircraft_code = st.text_input(
    label="Enter aircraft registration number:", placeholder="N145DQ").upper().strip()
uploaded_file = st.file_uploader(
    "Or upload an image and click on Search:", type=["jpg", "png", "jpeg"])

if st.button("Search"):
    if aircraft_code != "":
        aircraft_details_query(aircraft_code)

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    # Converts PIL image to OpenCv
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    # Display scaled image if size is too large
    st.title("Uploaded Image:")
    if img.shape[0] > 600 or img.shape[1] > 600:
        w, h, c = img.shape
        sf = 400 / w
        img2 = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
                          None, fx=sf, fy=sf, interpolation=cv2.INTER_AREA)
        st.image(img2)
    else:
        st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
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
        alphanumeric_code_with_hyphens = re.sub("[^\w-]", "", code)
        # Possible prefixes without hyphens: "HL, N, UK, JA, UR(with or without), HI"
        pattern = r"\w{1,4}-\w+|HL\w{4}|N\d{1,3}\w{2}|N\d{1,5}|UK\d{5}|JA\w{4}|UR\d{5}|HI\w{3,4}"
        matches = re.findall(pattern, alphanumeric_code_with_hyphens)
        if len(matches) > 0:
            if len(matches[0]) == len(code):
                st.title(code)
                aircraft_details_query(code)
