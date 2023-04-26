# Aircraft Search

Aircraft details provider that queries multiple sources to find and aggregate information about a given plane. Data can be obtained by providing a plane's registration number (reg number) or image, which will be [OCR](https://en.wikipedia.org/wiki/Optical_character_recognition)d and then queried.

There are three available versions:

- `aircraft_search.py`: Base Scraper module with OCR [Contains most number of features]
- `api.py`: Web API made with [FastAPI](https://github.com/tiangolo/fastapi/)
- `streamlit_web_interface.py`: Web interface made with [Streamlit](https://github.com/streamlit/streamlit)

## Features

The script returns the following information:

- Details about the aircraft such as Manufacturer, Engines, First flight etc.
- Image of the aircraft obtained from the [planespotters.net](https://www.planespotters.net/photo/api) API
- Recent past flights of the aircraft

## Requirements

Python 3.7+

- [FastAPI](https://github.com/tiangolo/fastapi/)
- [Streamlit](https://github.com/streamlit/streamlit)

## Installation

```
git clone https://github.com/04ac/Aircraft-Search.git
cd Aircraft-Search
pip install -r requirements.txt
```

## Usage

#### - Base scraper module

`example_module.py`:

```
import json
import aircraft_search

aircraft_reg_no = "N145DQ"  # aircraft registration number

# Logging is disabled by default and hence the only output
# is the data about the aircraft being returned as an JSON object
# aircraft_data = aircraft_search.aircraft_details_query(
#     aircraft_registration_number)

aircraft_data = aircraft_search.aircraft_details_query(
    aircraft_reg_no, logging=True)
print("\nJSON data:\n", json.dumps(aircraft_data, indent=4))

```

#### - Web API

```
uvicorn api:app
```

Available endpoints at http://127.0.0.1:8000:

- `/query?regno=<input aircraft reg number here>` Request type: GET/POST

- `/queryByImage?imageurl=<input aircraft's image url>` Request type: GET/POST

#### - Web interface (Streamlit)

```
streamlit run streamlit_web_interface.py
```

Visit http://localhost:8501 in a browser to see the web interface

## Todo

- [ ] Base module: Enable searching for an aircraft using Flight Number by scraping the reg number from https://planefinder.net/flight/\<flight number\>
- [ ] API: Enable sending image object as a POST request to `/queryByImage` so that users can upload image files
- [ ] Web interface: Make a web app using the API as backend with features:
  - [ ] Query multiple reg numbers / flight numbers in parallel
  - [ ] Show aviation related fun facts while the backend API fetches the results
- [ ] OCR: Switch to a faster OCR engine
- [ ] OCR: Flight ticket Flight Number -> reg number -> Query
