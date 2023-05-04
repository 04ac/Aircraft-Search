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
import os





# Downloads easyocr models and creates an easyocr.Reader object
# This was done at the beginning so that the models get downloaded only once
# as the streamlit server has limited memory

reader = easyocr.Reader(["en"], gpu=True)


def remove_delimiters(word):
    _ = []
    for i in word:
        if i != "\n" and i != "\t":
            _.append(i)
    return "".join(_)


def get_website(site_link, reg_no):
    headers={"user-agent":
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=0.5))
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    _request = session.get(site_link + reg_no, headers=headers)
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

    st.text("")
    st.markdown("##### Aviation Fun Fact:\n")
    st.text(random.choice(fun_facts))


st.set_page_config(layout="wide")
st.title("Aircraft Search")

tab1, tab2, tab3 = st.tabs(["Registration", "Flight Number", "Upload Ticket"])

with tab1:
    st.header("Registration Number Lookup")
    aircraft_code = st.text_input(
        label="Enter aircraft registration number:", placeholder="Example:  F-OVAA").upper().strip()
    uploaded_file = st.file_uploader(
        "Or upload an image of the aircraft with the registration visible:",
          type=["jpg", "png", "jpeg"])

    if st.button("Search", key=0):
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
                code_with_only_alphanumeric_characters_and_hyphens = re.sub(
                    "[^\w-]", "", code)
                # Possible prefixes without hyphens: "HL, N, UK, JA, UR(with or without), HI"
                pattern = r"\w{1,4}-\w+|HL\w{4}|N\d{1,3}\w{2}|N\d{1,5}|UK\d{5}|JA\w{4}|UR\d{5}|HI\w{3,4}"
                matches = re.findall(
                    pattern, code_with_only_alphanumeric_characters_and_hyphens)
                if len(matches) > 0:
                    if len(matches[0]) == len(code):
                        aircraft_details_query(code)
                        st.markdown("---")

        if aircraft_code == "" and uploaded_file is None:
            st.markdown(
                "#### Please enter a valid aircraft registration number or upload an image.")

def flight_number_lookup(flight_number):
    status_code, html_text = get_website('https://www.flightera.net/en/flight/', flight_number)

    if status_code > 300:
        if ticket_image_uploaded == True:
            return
        else:
            st.text("Flight Number Information not available. Please enter a valid fight numnber.")
    else:
        soup = BeautifulSoup(html_text, 'lxml')
        info = soup.find('main', class_='flex-auto px-2 max-w-4xl mt-4 mx-auto')
        flight_number_info = info.find(
            'dt', class_='text-xl text-center leading-5 font-bold text-gray-800 dark:text-white')
        st.subheader(flight_number_info.text.strip())


        flight_status = info.find(
            'dd', class_='text-center text-sm leading-5 text-gray-900 dark:text-white mt-6')
        st.write(flight_status.text.strip())
        st.markdown("---")

        origin_and_destination = info.findAll('span', class_='text-lg font-medium')
        origin_name = origin_and_destination[0].text.strip()
        destination_name = origin_and_destination[1].text.strip()

        origin_airport_code_info = info.find(
            'dd', class_='text-left text-xs leading-5 text-gray-500 dark:text-white')
        code_string = remove_delimiters(origin_airport_code_info.text.strip())
        origin_airport_code = code_string[0:3] + "/" + code_string[-4:]

        destination_airport_code_info = info.find(
            'dd', class_='text-right text-xs leading-5 text-gray-500 dark:text-white')
        code_string = remove_delimiters(destination_airport_code_info.text.strip())
        destination_airport_code = code_string[0:3] + "/" + code_string[-4:]

        flight_info = info.find(
            'div', class_='col-span-1 text-xs text-center text-gray-600 dark:text-white mt-6')
        flight_duration_info = flight_info.findAll('span', class_='whitespace-nowrap')
        flight_duration = flight_duration_info[0].text.strip()
        flight_distance = flight_duration_info[1].text.strip()

        terminal_and_gate_origin = info.find(
            'dd', class_='text-left text-sm leading-5 text-gray-800 dark:text-white').text
        terminal_and_gate_destination = info.find(
            'dd', class_='text-right text-sm leading-5 text-gray-500 dark:text-white').text
        
        depatrure_info = info.find(
            "dt", class_="text-left text-md text-base leading-5 text-gray-800 dark:text-gray-100")
        departure = depatrure_info.find("span", class_="whitespace-nowrap").text

        arrival_info = info.find(
            "dt", class_="text-right text-md text-base leading-5 text-gray-800 dark:text-gray-100")
        arrival = arrival_info.find("span", class_="whitespace-nowrap").text


        left_headings = info.findAll(
            'dt', class_='text-left text-sm leading-5 font-bold text-gray-500 dark:text-gray-300')
        plane_info_headings = []
        for i in left_headings:
            plane_info_headings.append(i.text.strip())

        right_headings = info.findAll(
            'dt', class_='text-right text-sm leading-5 font-bold text-gray-500 dark:text-gray-300')
        for i in right_headings:
            plane_info_headings.append(i.text.strip())

        model_and_seat_config_info = info.findAll(
            'dd', class_='text-left text-sm leading-5 text-gray-500 dark:text-white')

        plane_info_items = []
        for i in model_and_seat_config_info:
            plane_info_items.append(i.text.strip())

        icao_identifier = info.find(
            'dd', class_='text-right text-sm leading-5 text-gray-900 dark:text-white')
        if icao_identifier != None:
            plane_info_items.append(icao_identifier.text.strip())
        else:
            plane_info_items.append("NA")

        first_flight = info.findAll(
            'dd', class_='text-right text-sm leading-5 text-gray-500 dark:text-white')
        if len(first_flight) >= 2:
            plane_info_items.append(first_flight[1].text.strip())
        else:
            plane_info_items.append("NA")

        if len(plane_info_items) > 0:
            if plane_info_items[0] != "NA":
                plane_info_items[0] = " ".join(plane_info_items[0].split()) 

        if len(plane_info_items) > 3:
            if plane_info_items[3] != "NA":
                plane_info_items[3] = plane_info_items[3][0:8]

        plane_info_dict = dict(zip(plane_info_headings, plane_info_items))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<h2 style='text-align: left'>"
                        + origin_name + "</h2>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: left'>" 
                        + origin_airport_code + "</h3>", unsafe_allow_html=True)
            st.markdown("<h5 style='text-align: left'>" 
                        + terminal_and_gate_origin + "</h5>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: left'>" 
                        + departure + "</h2>", unsafe_allow_html=True)

        with col2:
            st.markdown("<h5 style='text-align: center'>Duration:  " 
                        + flight_duration + "</h5>", unsafe_allow_html=True)
            st.markdown("<h5 style='text-align: center'>Distance:  " 
                        + flight_distance + "</h5>", unsafe_allow_html=True)

        with col3:
            st.markdown("<h2 style='text-align: right'>" 
                        + "To: " + destination_name + "</h2>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: right'>"
                        + destination_airport_code + "</h3>", unsafe_allow_html=True)
            st.markdown("<h5 style='text-align: right'>"
                        + terminal_and_gate_destination + "</h5>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: right'>"
                        + arrival + "</h2>", unsafe_allow_html=True)

        st.markdown("---")
        frequency_info = info.find('div', class_='col-span-1 text-left').find('dd')
        if frequency_info is not None:
            frequency = frequency_info.find('span').text
            st.markdown("<h5 style='text-align: left'>" 
                            + "Frequency: " + frequency + "</h5>", unsafe_allow_html=True)
            days_running = frequency_info.text.strip()[len(frequency):].strip()
            st.markdown("<h5 style='text-align: left'>" 
                            + days_running + "</h5>", unsafe_allow_html=True)
            st.markdown("---")

        st.markdown("<h2>Aircraft Information:</h2>", unsafe_allow_html=True)
        
        # Gets registration of aircraft
        _ = []
        for c in plane_info_items[0]:
            if c == " ":
                break
            _.append(c)
        reg_no = "".join(_)

        # Get aircraft image from planespotters.net
        if reg_no != "NA":
            req = get_website(
                "https://api.planespotters.net/pub/photos/reg/", reg_no)
            if req[0] > 300:
                st.markdown("Aircraft image not available")
            else:
                data = json.loads(req[1])
                if not len(data["photos"]) == 0:
                    # Load and display aircraft image
                    with urllib.request.urlopen(data["photos"][0]["thumbnail_large"]["src"]) as image_url:
                        aircraft_image = Image.open(image_url)
                        st.image(aircraft_image)
                else:
                    st.markdown("Aircraft image not available")

            st.markdown("")  # For extra space below image (\n)

        # Two columns to display aircraft information
        col1, col2 = st.columns(2)
        with col1:
            if len(plane_info_dict.keys()) == 0:
                st.markdown("Aircraft Information not available at the moment.")
            else:
                for item in plane_info_dict.keys():
                    st.markdown("<h5 style='text-align: left'>" 
                        + item + "</h5>", unsafe_allow_html=True)
                
        with col2:
            for item in plane_info_dict.values():
                if len(plane_info_dict) == 0:
                    break
                st.markdown("<h5 style='text-align: left'>" 
                        + item + "</h5>", unsafe_allow_html=True)
                
        st.markdown("---")
        st.markdown("<h2>Past Flights (If any):</h2>", unsafe_allow_html=True)

        tables = pd.read_html(html_text)
        past_flights_df = tables[0]

        # Remove last column
        past_flights_df = past_flights_df.iloc[:, :-1]
        if "TO" in past_flights_df.keys().tolist():
            i = 0
            # Clean up data in "FROM" column
            for item in past_flights_df["FROM"]:
                l = []
                for le in item:
                    l.append(le)
                    if le == ")":
                        break
                past_flights_df["FROM"][i] = "".join(l)
                i += 1

            i = 0
            # Clean up data in "TO" column
            for item in past_flights_df["TO"]:
                l = []
                for le in item:
                    l.append(le)
                    if le == ")":
                        break
                past_flights_df["TO"][i] = "".join(l)
                i += 1
            st_aggrid.AgGrid(past_flights_df, columns_auto_size_mode=2)
        else:
            st.markdown("No past flights found")

        st.markdown("---")

with tab2:
    st.header("Flight Number Lookup")
    ticket_image_uploaded = False

    flight_number = st.text_input(
        label="Enter flight number:", placeholder="Example:  DL301").upper().strip()
    
    # Remove spaces
    flight_number = flight_number.replace(" ", "")
    # Remove hyphens
    flight_number = flight_number.replace("-", "")
    
    if st.button("Search", key=1):
        flight_number_lookup(flight_number)
        

with tab3:
    # Ticket upload feature
    st.header("Ticket Image Lookup")
    uploaded_file = st.file_uploader(
        "Upload an image of the ticket or boarding pass", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        ticket_image_uploaded = True
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

        st.markdown("---")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text_list = list(reader.readtext(img, detail=0))

        # Remove Duplicates
        list_without_duplicates = []
        for item in text_list:
            if item not in list_without_duplicates:
                list_without_duplicates.append(item)
        # list_without_duplicates

        number_of_lookups = 0
        for item in list_without_duplicates:
            item = item.upper()

            # Remove spaces
            item = item.replace(" ", "")
            # Remove hyphens
            item = item.replace("-", "")

            pattern = r"\A\w{2}\d{1,4}"
            matches = re.findall(pattern, item)

            if len(matches) > 0 and not matches[0].isdigit():
                if len(matches[0]) == len(item):
                    flight_number_lookup(matches[0])
                    number_of_lookups += 1
        if number_of_lookups == 0:
            st.markdown("Flight details not found. Please upload a clear image of the ticket.")
