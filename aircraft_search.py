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
import PIL
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
    aircraft_data = {}
    aircraft_data["aircraft_image_link"] = ""
    aircraft_data["aircraft_data"] = []

    print("Details for {}:".format(reg_no))
    req = get_website(
        "https://api.planespotters.net/pub/photos/reg/", reg_no)
    if req[0] > 300:
        print("Aircraft's image not available")
    else:
        data = json.loads(req[1])
        if not len(data["photos"]) == 0:
            src = data["photos"][0]["thumbnail_large"]["src"]
            aircraft_data["aircraft_image_link"] = src
            urllib.request.urlretrieve(
                src, "_most_recent_aircraft_PIL.Image.png")
            print(
                "Aircraft's image saved at ./_most_recent_aircraft_image.png")
            img = PIL.Image.open("_most_recent_aircraft_image.png")
            img.show()
        else:
            print("Aircraft's image not available")

    print("\nQuerying flightaware.com...")
    req = get_website(
        "https://flightaware.com/resources/registration/", reg_no)

    if req[0] > 300:
        print("Data not available")
    else:
        soup = BeautifulSoup(req[1], "lxml")
        info = soup.find("div", class_="pageContainer")
        data = info.findAll("div", class_="attribute-row")

        details_from_flightaware = {}
        details_from_flightaware["Source"] = "https://flightaware.com/resources/registration/"
        for i in data:
            details_from_flightaware[i.find("div", class_="medium-1 columns title-text").text] = remove_delimiters(
                i.find("div", class_="medium-3 columns").text.replace("\n", " "))
        if len(details_from_flightaware.items()) > 0:
            engine = details_from_flightaware["Engine"]
            details_from_flightaware["Engine"] = engine[:engine.find(
                "Thrust")] + " " + engine[engine.find("Thrust") + 8:] + " thrust"
            details_from_flightaware_df = pd.DataFrame(details_from_flightaware.items()).rename(
                columns={0: "Categories", 1: "Information"}).set_index("Categories")
            details_from_flightaware_json = json.loads(
                details_from_flightaware_df.to_json())
            print(details_from_flightaware_df)
            # print(json.dumps(details_from_flightaware_json, indent=4))
            aircraft_data["aircraft_data"].append(
                details_from_flightaware_json["Information"])
            aircraft_data["aircraft_data"][0]["Source"] = "https://flightaware.com/resources/registration/"
        else:
            print("Data not available")

        print("\nAircraft Owners:")
        soup.find("div", class_="airportBoardContainer")
        data = info.find("table")
        aircraft_owners_df = pd.read_html(str(data))[0]
        print(aircraft_owners_df)
        aircraft_owners_json = json.loads(
            aircraft_owners_df.to_json(orient="records"))
        # print(json.dumps(aircraft_owners_json, indent=4))
        # print(aircraft_owners_json)

        aircraft_data["aircraft_data"][0]["Aircraft Owners"] = aircraft_owners_json
        # print(json.dumps(aircraft_data, indent=4))


print("Aircraft Search\n")
# aircraft_code = input("Enter aircraft registration number:").upper().strip()
aircraft_code = "N145DQ"
aircraft_details_query(aircraft_code)
