import re
# import cv2
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
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
import time


def remove_delimiters(word):
    _ = []
    for i in word:
        if i != "\n" and i != "\t":
            _.append(i)
    return "".join(_)


## HELPER ITEMS TO GET WEBSITE
headers={"user-agent":
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
session = requests.Session()
adapter = HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=0.5))
session.mount("http://", adapter)
session.mount("https://", adapter)

def get_website(site_link, reg_no):
    _request = session.get(site_link + reg_no, headers=headers)
    return _request.status_code, _request.text



def aircraft_details_query(reg_no, dr):
    st.title(reg_no)
    data_not_found_flag = [False, False]

    # get aircraft image from planespotters.net API
    with st.spinner('Fetching aircraft image...'):
        req = get_website(
            "https://api.planespotters.net/pub/photos/reg/", reg_no)
        if req[0] > 300:
            st.text("Aircraft image not available")
        else:
            data = json.loads(req[1])
            if not len(data["photos"]) == 0:
                # Load and display aircraft image
                # st.text(data)
                try:
                    with urllib.request.urlopen(data["photos"][0]["thumbnail_large"]["src"]) as image_url:
                        st.text("Aircraft Image:")
                        aircraft_image = Image.open(image_url)
                        st.image(aircraft_image)
                except:
                    try:
                        with urllib.request.urlopen(data["photos"][0]["thumbnail"]["src"]) as image_url:
                            st.text("Aircraft Image:")
                            aircraft_image = Image.open(image_url)
                            st.image(aircraft_image)
                    except:
                        st.text("Aircraft image not available")
            else:
                st.text("Aircraft image not available")

    # gets extra info (if available) from flightaware
    with st.spinner('Fetching information from FlightAware...'):
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


    # Get additional information from flightera.net
    with st.spinner('Retrieving additional aircraft details...'):
        dr.get("https://www.flightera.net/en/planes/" + reg_no)
        
        # Add a small delay to allow the page to load
        time.sleep(3)
        
        soup2 = BeautifulSoup(dr.page_source, "lxml")

        st.subheader("Further Information: \n")
        info2 = soup2.find('div', class_='py-10 max-w-5xl mx-auto')
        if info2 == None:
            data_not_found_flag[1] = True
            st.text("Details not found")
            return
            
        f = info2.find('div', class_='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8')
        if f is None:
            data_not_found_flag[1] = True
            st.text("Aircraft details structure not found")
            return
            
        g = f.find('h1',class_='text-xl font-bold leading-tight text-gray-900 dark:text-white')
        if g is None:
            st.text("Aircraft name not found")
        else:
            st.text("Aircraft: " + remove_delimiters(g.text))

        info3 = soup2.find('div', class_='bg-white dark:bg-gray-900 shadow overflow-hidden sm:rounded-lg mx-auto p-3')
        if info3 is None:
            data_not_found_flag[1] = True
            st.text("Aircraft details section not found")
            return
            
        # st.text(info3.text)
        info_grids = info3.find('dl', class_='grid gap-x-4 gap-y-4 grid-cols-2 lg:grid-cols-3')
        if info_grids is None:
            data_not_found_flag[1] = True
            st.text("Aircraft information grid not found")
            return
            
        aircraft_info = info_grids.find_all('div', class_="col-span-1 dark:bg-gray-700 bg-gray-100 rounded-lg p-4 shadow text-center text-sm leading-5")

        d = {}
        for information in aircraft_info:
            k = information.find('dt')
            v = information.find('dd')
            if k is not None and v is not None and k.text.strip() != 'PICTURE':
                d[k.text.strip()] = v.text.strip()

        # Create a more visually appealing display
        def display_aircraft_info():
            if d:
                st.markdown("### Aircraft Properties")
                
                # Create a two-column layout for better readability
                col1, col2 = st.columns(2)
                
                # Sort the keys alphabetically for a consistent display
                sorted_keys = sorted(d.keys())
                
                # Display each property with improved formatting
                for key in sorted_keys:
                    value = d[key]
                    
                    # Alternate between columns for better layout
                    with col1 if sorted_keys.index(key) % 2 == 0 else col2:
                        # Create a card-like container for each property
                        with st.container():
                            # Display key with italic formatting
                            st.markdown(f"*{key}*")
                            
                            # Apply special formatting to certain values
                            if key == "STATUS" and "active" == value.lower():
                                st.markdown(f"<span style='color:green; font-weight:500'>{value}</span>", unsafe_allow_html=True)
                            if key == "STATUS" and any(term in value.lower() for term in ["inactive", "stored", "scrapped"]):
                                st.markdown(f"<span style='color:red; font-weight:500'>{value}</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(value)
                            
                            # Add a subtle separator between properties
                            st.markdown("<hr style='margin: 5px 0; opacity: 0.3'>", unsafe_allow_html=True)


        display_aircraft_info()

        tables = pd.read_html(dr.page_source)

        if data_not_found_flag[0] is True and data_not_found_flag[1] is True:
            st.text("Aircraft details not found")

        st.subheader("Past Flights (If any):")
        if len(tables) <= 0:
            st.text("No past flights found")
        else:
            # Drop last column
            _df = tables[0].iloc[:, :-1]

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

# Use Selenium in headless mode with Firefox
options = Options()
options.add_argument('--headless')

# Configure a random user agent using Firefox's proper method
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0"
]
options.set_preference("general.useragent.override", random.choice(user_agents))

# Avoid detection
options.set_preference("dom.webdriver.enabled", False)
options.set_preference('useAutomationExtension', False)

service = Service() 
dr = WebDriver(service=service, options=options)

tab1, tab2 = st.tabs(["Registration", "Flight Number"])

with tab1:
    st.header("Registration Number Lookup")
    aircraft_code = st.text_input(
        label="Enter aircraft registration number:", placeholder="Example:  F-OVAA").upper().strip()
    uploaded_file = st.file_uploader(
        "Or upload an image and click on Search:", type=["jpg", "png", "jpeg"])

    if st.button("Search", key=0):
        if aircraft_code != "":
            display_fun_facts()
            aircraft_details_query(aircraft_code, dr)

        if uploaded_file is not None:
            with st.spinner('Processing your image...'):
                img = Image.open(uploaded_file)
                # Convert PIL image to a numpy array without OpenCV
                # img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                img_array = np.array(img)
                
                # Display scaled image if size is too large
                st.text("Uploaded Image:")
                if img_array.shape[0] > 600 or img_array.shape[1] > 600:
                    w, h = img.size
                    # Determine scaling factor based on the larger dimension to maintain aspect ratio
                    max_dim = max(w, h)
                    sf = 600 / max_dim
                    # Apply same scaling factor to both dimensions
                    new_size = (int(w * sf), int(h * sf))
                    img_resized = img.resize(new_size)
                    st.image(img_resized)
                else:
                    # st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                    st.image(img)

                display_fun_facts()

            with st.spinner('Analyzing image for aircraft registration numbers...'):
                # Convert to grayscale using PIL instead of OpenCV
                # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                img_gray = img.convert('L')
                reader = easyocr.Reader(["en"], gpu=True)
                # Pass PIL grayscale image to EasyOCR
                text_list = list(reader.readtext(np.array(img_gray), detail=0))

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
                            aircraft_details_query(code, dr)
                            st.markdown("---")

        if aircraft_code == "" and uploaded_file is None:
            st.markdown(
                "#### Please enter a valid aircraft registration number or upload an image.")


## TODO Update Scraping Code for Flight Number
with tab2:
    st.header("Flight Number Lookup (Under Maintenance)")

    flight_number = st.text_input(
        label="Enter flight number:", placeholder="Example:  DL301").upper().strip()
    
    if st.button("Search", key=1):
        status_code, html_text = get_website('https://www.flightera.net/en/flight/', flight_number)

        if status_code > 300:
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


            _headings = info.findAll(
                'dt', class_='text-left text-sm leading-5 font-bold text-gray-500 dark:text-gray-300')
            plane_info_headings = []
            for i in _headings:
                plane_info_headings.append(i.text.strip())

            _headings = info.findAll(
                'dt', class_='text-right text-sm leading-5 font-bold text-gray-500 dark:text-gray-300')
            for k in _headings:
                plane_info_headings.append(k.text.strip())

            model_and_seat_config_info = info.findAll(
                'dd', class_='text-left text-sm leading-5 text-gray-500 dark:text-white')
            plane_info_items = []
            for i in model_and_seat_config_info:
                if i != None:
                    plane_info_items.append(i.text.strip())
                else:
                    plane_info_items.append("NA")

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


            plane_info_items[0] = " ".join(plane_info_items[0].split()) 
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

            st.markdown("") # For extra space below image (\n)

            # Two columns to display aircraft information
            col1, col2 = st.columns(2)
            with col1:
                for item in plane_info_dict.keys():
                    st.markdown("<h5 style='text-align: left'>" 
                            + item + "</h5>", unsafe_allow_html=True)
                    
            with col2:
                for item in plane_info_dict.values():
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