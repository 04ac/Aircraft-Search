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


def get_website(site_link, regno):
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=0.5))
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    _request = session.get(site_link + regno)
    return (_request.status_code, _request.text)


def remove_delimiters(word):
    _ = []
    for i in word:
        if i != "\n" and i != "\t":
            _.append(i)
    return "".join(_)


def _print(to_print):
    try:
        if log is True:
            print(to_print)
    except NameError:
        pass


def aircraft_details_query(reg_no, logging=False, show_image=False):
    global log
    log = logging
    aircraft_data = {"success": True, "aircraft_image_link": "", "data": []}
    aircraft_data_index = -1

    if reg_no == "":
        del aircraft_data["data"]
        aircraft_data["success"] = False
        aircraft_data["message"] = "Aircraft registration number must not be blank"
        return aircraft_data
    reg_no = reg_no.upper().strip().replace(" ", "")

    _print("Details for {}:".format(reg_no))
    req = get_website(
        "https://api.planespotters.net/pub/photos/reg/", reg_no)
    if req[0] > 300:
        _print("Aircraft's image not available")
    else:
        data = json.loads(req[1])
        if not len(data["photos"]) == 0:
            src = data["photos"][0]["thumbnail_large"]["src"]
            aircraft_data["aircraft_image_link"] = src
            urllib.request.urlretrieve(
                src, "_most_recent_aircraft_image.png")
            _print(
                "Aircraft's image saved at ./_most_recent_aircraft_image.png")
            img = PIL.Image.open("_most_recent_aircraft_image.png")
            if show_image:
                img.show()
        else:
            _print("Aircraft's image not available")

    _print("\n===========================================================\n\
Querying flightaware.com...")
    req = get_website(
        "https://flightaware.com/resources/registration/", reg_no)

    if req[0] > 300:
        _print("Data not available")
    else:
        details_from_flightaware = {}
        soup = BeautifulSoup(req[1], "lxml")
        info = soup.find("div", class_="pageContainer")
        data = info.findAll("div", class_="attribute-row")
        for i in data:
            details_from_flightaware[i.find("div", class_="medium-1 columns title-text").text] = remove_delimiters(
                i.find("div", class_="medium-3 columns").text.replace("\n", " "))
        if len(details_from_flightaware.items()) > 1:
            engine = details_from_flightaware["Engine"]
            details_from_flightaware["Engine"] = engine[:engine.find(
                "Thrust")] + " " + engine[engine.find("Thrust") + 8:] + " thrust"
            details_from_flightaware_df = pd.DataFrame(details_from_flightaware.items()).rename(
                columns={0: "Parameter", 1: "Value"}).set_index("Parameter")
            details_from_flightaware_json = json.loads(
                details_from_flightaware_df.to_json())
            _print(details_from_flightaware_df)
            # _print(json.dumps(details_from_flightaware_json, indent=4))
            aircraft_data_index += 1
            aircraft_data["data"].append(
                details_from_flightaware_json["Value"])
            aircraft_data["data"][aircraft_data_index]["source"] = "https://flightaware.com/resources/registration/"
        else:
            _print("Data not available")

        soup.find("div", class_="airportBoardContainer")
        data = info.find("table")
        try:
            aircraft_owners_df = pd.read_html(str(data))[0].set_index("Date")
            _print(aircraft_owners_df)
            aircraft_owners_json = json.loads(
                aircraft_owners_df.to_json(orient="records"))
            # _print(json.dumps(aircraft_owners_json, indent=4))
            _print("\nAircraft Owners:")
            _print(aircraft_owners_json)

            aircraft_data["data"][aircraft_data_index]["Aircraft Owners"] = aircraft_owners_json
            # _print(json.dumps(aircraft_data, indent=4))
        except ValueError:
            pass

    _print("\n===========================================================\n\
Querying flightera.net...")
    req = get_website("https://www.flightera.net/en/planes/", reg_no)
    if req[0] > 300:
        _print("Data not available")
    else:
        html = req[1]
        soup = BeautifulSoup(html, "lxml")
        info = soup.find("div", class_="mx-auto flex max-w-7xl")
        f = info.find("div", class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8")
        i = info.find(
            "dl", class_="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2 lg:grid-cols-3")
        j = i.findAll("table")  # there are two tables, we need to merge them
        details_flightera_df = pd.read_html(str(j[0]), index_col=0)[
            0].rename(columns={0: "Parameter", 1: "Value"})
        try:
            details_flightera_df_2 = pd.read_html(str(j[1]), index_col=0)[
                0].rename(columns={0: "Parameter", 1: "Value"})
            details_flightera_df = pd.concat(
                [details_flightera_df, details_flightera_df_2])
        except:
            pass
        _print(details_flightera_df)
        details_flightera_json = json.loads(
            details_flightera_df.to_json())
        # _print(json.dumps(details_flightera_json, indent=4))
        aircraft_data_index += 1
        aircraft_data["data"].append(details_flightera_json["Value"])
        aircraft_data["data"][aircraft_data_index]["source"] = "https://www.flightera.net/en/planes/"

        tables = pd.read_html(html)
        if len(tables) < 3:
            _print("No past flights found")
        else:
            # Drop last column
            past_flights = tables[2].iloc[:, :-1]

            if "TO" in past_flights.keys().tolist():
                i = 0
                # Clean up data in "FROM" column
                for item in past_flights["FROM"]:
                    l = []
                    for le in item:
                        l.append(le)
                        if le == ")":
                            break
                    past_flights["FROM"][i] = "".join(l)
                    i += 1

                i = 0
                # Clean up data in "TO" column
                for item in past_flights["TO"]:
                    l = []
                    for le in item:
                        l.append(le)
                        if le == ")":
                            break
                    past_flights["TO"][i] = "".join(l)
                    i += 1
                _print("Past Flights:")
                _print(past_flights)
                past_flights_json = json.loads(
                    past_flights.to_json(orient="records"))
                # most_freq_airports_df.to_json)
                # _print(json.dumps(past_flights_json, indent=4))
                aircraft_data["data"][aircraft_data_index]["Past Flights"] = past_flights_json
            else:
                _print("No past flights found")

        try:
            info = soup.find("table", {"id": "apt-ranking"})
            most_freq_airports_df = pd.read_html(str(info), index_col=0)[
                0].iloc[:, :2]
            _print("\nMost Frequented Airports:")
            _print(most_freq_airports_df)
            most_freq_airports_json = json.loads(
                most_freq_airports_df.to_json(orient="index"))
            # _print(json.dumps(most_freq_airports_json, indent=4))
            aircraft_data["data"][aircraft_data_index]["Most Frequent Airports"] = most_freq_airports_json
        except ValueError:
            pass

        _print(json.dumps(aircraft_data, indent=4))

    if len(aircraft_data["data"]) == 0:
        del aircraft_data["data"]
        aircraft_data["success"] = False
        aircraft_data["message"] = "Data not available from any source"
    return aircraft_data


if __name__ == "__main__":
    _print("Aircraft Search\n")
    # aircraft_code = input("Enter aircraft registration number:").upper().strip()
    aircraft_code = "N145DQ"
    aircraft_details_query(aircraft_code, logging=True, show_image=True)
    # aircraft_details_query(aircraft_code, logging=True)
