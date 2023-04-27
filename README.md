# Aircraft Search

Aircraft details provider that queries multiple sources to find and display information about a given aircraft. Data can be obtained by providing the aircraft's registration number (reg number) or image, which will be [OCR](https://en.wikipedia.org/wiki/Optical_character_recognition)d and then queried.

There are four available versions:

- Base Scraper module with OCR (module without frontend)
- Web API made with [FastAPI](https://github.com/tiangolo/fastapi/)
- HTML Web interface (Currently in progess)
- Web interface made with [Streamlit](https://github.com/streamlit/streamlit)

  Streamlit Web Interface: https://aircraft-search.streamlit.app

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

#### - API + HTML Web interface

```
uvicorn api:app
```

Visit http://127.0.0.1:8000 in a browser to view the web interface

Available endpoint(s):

- `/query?regno=<input aircraft reg number here>` Request type: GET/POST

#### - Streamlit Web Interface

```
streamlit run streamlit_web_interface.py
```

## Todo

- [ ] Enable searching for an aircraft using Flight Number by scraping the reg number from https://planefinder.net/flight/<flight number\>
- [ ] API: Enable sending image object as a POST request to `/queryByImage` so that users can search using aircraft / flight ticket's image
- [ ] Web interface: Make a web app using the API as backend with features:
- [ ] Query multiple reg numbers / flight numbers in parallel
- [ ] OCR: Switch to a faster OCR engine
- [ ] OCR: Flight ticket Flight Number -> Query
- [ ] Package aircraft_search as pip package
- [ ] Add logo image with badges to README.md

## License

> Parent repository: [04ac/Aircraft-Search](https://github.com/04ac/Aircraft-Search)
