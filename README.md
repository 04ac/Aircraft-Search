# Aircraft Search

Aircraft details provider that queries multiple sources to find and display information about a given aircraft using any one of the following inputs:

- Flight number (present on the boarding pass)
- Aircraft registration number
- Aircraft image (will be [OCR](https://en.wikipedia.org/wiki/Optical_character_recognition)d and then queried)

## Can Identify multiple aircraft in a single uploaded image

<p align="center">
  <img src="./images/aircraft_search_sample2.png" hspace="4">
</p>

## Features

The script returns the following information:

- Details about the aircraft such as Manufacturer, Engines, First flight etc.
- Image of the aircraft obtained from the [planespotters.net](https://www.planespotters.net/photo/api) API
- Recent past flights of the aircraft

<!-- There are four available versions: -->

<!-- - Base Scraper module with OCR (module without frontend)
- Web API made with [FastAPI](https://github.com/tiangolo/fastapi/)
- HTML Web interface (Currently in progess) -->

The web interface is (currently) made with [Streamlit](https://github.com/streamlit/streamlit) \
Streamlit URL: https://aircraft-search.streamlit.app

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

#### Streamlit Web Interface

```
streamlit run streamlit_web_interface.py
```

<!-- #### - Base scraper module

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

- `/query?regno=<input aircraft reg number here>` Request type: GET/POST -->

<!-- ## Todo

- [x] Enable searching for an aircraft using Flight Number
- [ ] API: Enable sending image object as a POST request to `/queryByImage` so that users can search using aircraft / flight ticket's image
- [ ] Web interface: Make a web app using the API as backend with features:
  - [ ] Query multiple reg numbers / flight numbers in parallel
  - [x] Show aviation related fun facts while the backend API fetches the results
- [ ] OCR: Switch to a faster OCR engine
- [ ] OCR: Flight ticket Flight Number -> Query
- [ ] Package aircraft_search as pip package
- [ ] Add logo image with badges to README.md -->

## License

This project is licensed under the terms of the [MIT License](LICENSE).

> Parent repository: [04ac/Aircraft-Search](https://github.com/04ac/Aircraft-Search)
