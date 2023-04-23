# Aircraft Search

Aircraft details provider that queries multiple sources to find and aggregate information about a given plane. Data can be obtained by providing a plane's registration number or image, which will be [OCRd](https://en.wikipedia.org/wiki/Optical_character_recognition) and then queried.

There are three available versions:

- Base Scraper module with OCR
- Web API made with [FastAPI](https://github.com/tiangolo/fastapi/)
- Web interface made with [Streamlit](https://github.com/streamlit/streamlit)

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

#### Base Scraper module with OCR

```
import aircraft_search
```

#### Web API made with [FastAPI](https://github.com/tiangolo/fastapi/)

```
uvicorn api:app
```

Available endpoints at http://127.0.0.1:8000:

- `/queryByReg?regno=<input aircraft registration number here>` Request type: GET/POST

- `/queryByImage?imageurl=<input aircraft's image url>` Request type: GET/POST

#### Web interface made with [Streamlit](https://github.com/streamlit/streamlit)

```
streamlit run streamlit.py
```

Visit http://localhost:8501 in a browser to see the web interface

## Todo

- [ ] Base module: Enable searching for an aircraft using Flight Number by scraping the registration number from https://planefinder.net/flight/\<flight number\>
- [ ] API: Enable sending image object as a POST request to `/queryByImage` so that users can upload image files

## License

This project is licensed under the terms of the MIT license.
